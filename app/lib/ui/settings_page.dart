/// 设置页（设计方案 §3.6）：按用户认知分组——
/// 学习设置 → 外观设置 → 数据与题库 → 关于。
/// 持久化 key（theme_config / desired_retention / show_practice_timer）与
/// repository 方法保持不变，仅做 UI 层重排与主题编辑体验优化。
library;

import 'dart:convert';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import '../data/seed_loader.dart';
import '../models/models.dart';
import '../services/export_helper.dart';
import 'theme_controller.dart';
import 'glass_app_bar.dart';
import 'question_manage_page.dart';

part 'settings_theme_panel.dart';


class SettingsPage extends ConsumerStatefulWidget {
  const SettingsPage({super.key});

  @override
  ConsumerState<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends ConsumerState<SettingsPage> {
  bool _loading = true;
  String? _error;
  List<BankInfo> _banks = const [];
  double _desiredRetention = 0.9;
  bool _showPracticeTimer = false;
  StudyGoal _studyGoal = const StudyGoal();

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      final banks = await repo.banks(includeHidden: true);
      final retention =
          double.tryParse(await repo.setting('desired_retention') ?? '') ?? 0.9;
      final showPracticeTimer = await repo.practiceTimerVisible();
      final studyGoal = await repo.studyGoal() ?? const StudyGoal();
      if (!mounted) return;
      setState(() {
        _banks = banks;
        _desiredRetention = retention;
        _showPracticeTimer = showPracticeTimer;
        _studyGoal = studyGoal;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = '加载失败：$e';
      });
    }
  }

  void _toast(String text) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(text)));
  }

  /// 打开主题定制面板（需求：高自由度自定义主题）
  Future<void> _openThemePanel() async {
    await Navigator.of(
      context,
    ).push(MaterialPageRoute(builder: (_) => const _ThemePanelPage()));
  }

  // ---------- 学习目标（P2） ----------

  Future<void> _saveStudyGoal() async {
    final repo = await ref.read(quizRepositoryProvider);
    await repo.setStudyGoal(_studyGoal);
    _toast('学习目标已保存');
  }

  Future<void> _toggleStudyGoal(bool value) async {
    setState(() => _studyGoal = StudyGoal(
      examDate: _studyGoal.examDate,
      dailyNew: _studyGoal.dailyNew,
      dailyReview: _studyGoal.dailyReview,
      enabled: value,
    ));
    await _saveStudyGoal();
  }

  Future<void> _pickExamDate() async {
    final now = DateTime.now();
    final current = _studyGoal.examDate;
    DateTime initial = DateTime(now.year + 1, now.month, now.day);
    if (current != null) {
      final parts = current.split('-');
      if (parts.length == 3) {
        initial = DateTime(int.parse(parts[0]), int.parse(parts[1]), int.parse(parts[2]));
      }
    }
    final picked = await showDatePicker(
      context: context,
      initialDate: initial,
      firstDate: DateTime(now.year - 1, now.month, now.day),
      lastDate: DateTime(now.year + 5, 12, 31),
      helpText: '选择考试日期',
    );
    if (picked == null || !mounted) return;
    final fmt =
        '${picked.year.toString().padLeft(4, '0')}-${picked.month.toString().padLeft(2, '0')}-${picked.day.toString().padLeft(2, '0')}';
    setState(() => _studyGoal = StudyGoal(
      examDate: fmt,
      dailyNew: _studyGoal.dailyNew,
      dailyReview: _studyGoal.dailyReview,
      enabled: _studyGoal.enabled,
    ));
    await _saveStudyGoal();
  }

  Future<void> _adjustDaily({required bool isNew, required int delta}) async {
    final base = isNew ? _studyGoal.dailyNew : _studyGoal.dailyReview;
    final next = (base + delta).clamp(0, 200);
    setState(() => _studyGoal = StudyGoal(
      examDate: _studyGoal.examDate,
      dailyNew: isNew ? next : _studyGoal.dailyNew,
      dailyReview: isNew ? _studyGoal.dailyReview : next,
      enabled: _studyGoal.enabled,
    ));
    await _saveStudyGoal();
  }

  /// 学习目标设置卡：启用开关 + 考试日期 + 每日新题/复习（计划倒排为建议，用户可自由覆盖）
  Widget _buildStudyGoalCard(ThemeData theme) {
    final goal = _studyGoal;
    return Card(
      clipBehavior: Clip.antiAlias,
      child: Column(
        children: [
          SwitchListTile(
            secondary: _IconBox(
              icon: Icons.event_available,
              color: theme.colorScheme.error,
            ),
            title: const Text('学习目标'),
            subtitle: Text(goal.enabled
                ? '已启用 · 首页显示倒计时与每日任务'
                : '设置考试日期与每日题量，首页显示倒计时'),
            value: goal.enabled,
            onChanged: _toggleStudyGoal,
          ),
          const Divider(height: 1, indent: 16, endIndent: 16),
          ListTile(
            enabled: goal.enabled,
            leading: const Icon(Icons.calendar_month_outlined),
            title: const Text('考试日期'),
            subtitle: Text(
              goal.examDate ?? '未设置（点击选择）',
              style: TextStyle(
                color: goal.examDate == null
                    ? theme.colorScheme.outline
                    : null,
              ),
            ),
            trailing: const Icon(Icons.chevron_right),
            onTap: _pickExamDate,
          ),
          const Divider(height: 1, indent: 16, endIndent: 16),
          ListTile(
            enabled: goal.enabled,
            leading: const Icon(Icons.add_circle_outline),
            title: const Text('每日新题目标'),
            trailing: _Stepper(
              value: goal.dailyNew,
              onChanged: (delta) => _adjustDaily(isNew: true, delta: delta),
            ),
          ),
          ListTile(
            enabled: goal.enabled,
            leading: const Icon(Icons.autorenew),
            title: const Text('每日复习目标'),
            trailing: _Stepper(
              value: goal.dailyReview,
              onChanged: (delta) => _adjustDaily(isNew: false, delta: delta),
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
            child: Text(
              '计划倒排仅为建议，可随时在首页覆盖或暂停',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.outline,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ---------- 学习设置 ----------

  Future<void> _setDesiredRetention(double value) async {
    final repo = await ref.read(quizRepositoryProvider);
    await repo.setSetting('desired_retention', value.toStringAsFixed(2));
    if (!mounted) return; // 审查修复：防 setState after dispose
    setState(() => _desiredRetention = value);
    _toast('记忆保持率已更新为 ${(value * 100).toStringAsFixed(0)}%');
  }

  Future<void> _setPracticeTimerVisible(bool value) async {
    final repo = await ref.read(quizRepositoryProvider);
    await repo.setPracticeTimerVisible(value);
    if (!mounted) return;
    setState(() => _showPracticeTimer = value);
  }

  // ---------- 题库包导入 ----------

  Future<void> _importBank() async {
    try {
      final file = await FilePicker.pickFile(
        type: FileType.custom,
        allowedExtensions: ['json', 'zip'],
        dialogTitle: '选择题库包（.json 或 .zip）',
      );
      if (file == null) return;
      final bytes = await file.readAsBytes();
      final pack = file.name.toLowerCase().endsWith('.zip')
          ? SeedLoader.parseZipBytes(bytes)
          : SeedLoader.parse(utf8.decode(bytes));
      final repo = await ref.read(quizRepositoryProvider);
      final r = await repo.importBank(pack);
      _toast('导入成功：${r.toString()}');
      await _load();
    } on FormatException catch (e) {
      _toast('题库包无效：${e.message}');
    } catch (e) {
      _toast('导入失败：$e');
    }
  }

  // ---------- 备份导出 ----------

  /// 统一导出到系统下载目录（Android→MediaStore 下载目录，其它→文档目录回退）。
  /// 备份导出与审题标记导出共用此入口，保证落盘位置与提示风格一致。
  Future<void> _exportToFile(String fileName, String json,
      {String? emptyHint, int? count}) async {
    try {
      if (emptyHint != null && count != null && count == 0) {
        _toast(emptyHint);
        return;
      }
      final path = await exportToDownloads(fileName, json);
      _toast(count != null ? '已导出 $count 条：$path' : '已导出备份：$path');
    } catch (e) {
      _toast('导出失败：$e');
    }
  }

  Future<void> _exportBackup() async {
    final repo = await ref.read(quizRepositoryProvider);
    final json = await repo.exportJson();
    final stamp = DateTime.now()
        .toIso8601String()
        .replaceAll(':', '-')
        .split('.')
        .first;
    await _exportToFile('quiz_backup_$stamp.json', json);
  }

  /// 导出审题标记清单（v7：刷题时标记的"待修改"题目；保存到公共下载目录）
  Future<void> _exportReviewFlags() async {
    final repo = await ref.read(quizRepositoryProvider);
    final json = await repo.exportReviewFlags();
    final data = const JsonDecoder().convert(json) as Map<String, dynamic>;
    final count = data['count'] as int? ?? 0;
    final stamp = DateTime.now()
        .toIso8601String()
        .replaceAll(':', '-')
        .split('.')
        .first;
    await _exportToFile(
      'review_flags_$stamp.json',
      json,
      emptyHint: '当前没有审题标记（刷题时点击题号旁的旗子即可标记）',
      count: count,
    );
  }

  // ---------- 题库包管理操作 ----------

  Future<void> _onBankAction(BankInfo bank, String action) async {
    switch (action) {
      case 'edit':
        await Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) =>
                QuestionManagePage(bankId: bank.bankId, bankName: bank.name),
          ),
        );
        return;
      case 'purge':
        await _purgeArchived(bank.bankId);
        return;
      case 'hide':
        await _hideBank(bank);
        return;
      case 'restore':
        await _restoreBank(bank);
        return;
      case 'delete':
        await _deleteBankCompletely(bank);
        return;
    }
  }

  Future<void> _hideBank(BankInfo bank) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('隐藏题库包？'),
        content: const Text(
          '题库将从列表消失（题目不再出现在刷题范围），'
          '但作答记录/复习进度/错题本/审题标记全部保留，可随时"恢复显示"。',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('取消'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('隐藏'),
          ),
        ],
      ),
    );
    if (ok != true) return;
    final repo = await ref.read(quizRepositoryProvider);
    await repo.uninstallBank(bank.bankId);
    _toast('已隐藏「${bank.name}」');
    await _load();
  }

  Future<void> _restoreBank(BankInfo bank) async {
    final repo = await ref.read(quizRepositoryProvider);
    await repo.restoreBank(bank.bankId);
    _toast('已恢复显示「${bank.name}」，请重新导入该题库包以恢复题目');
    await _load();
  }

  Future<void> _deleteBankCompletely(BankInfo bank) async {
    // 用 onChanged 存值代替 TextEditingController，避免弹窗退场动画期间 dispose 崩溃（审查修复）
    var typedName = '';
    // 三态结果：null=用户取消，false=名称不匹配，true=确认删除。
    // 不能用 bool 区分"取消"与"不匹配"，否则取消也会误报"名称不匹配"（审查修复）
    final confirmed = await showDialog<bool?>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('彻底删除题库包？'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '将删除该题库包全部题目及其作答记录、复习进度、错题本、审题标记、模拟卷，'
              '不可恢复。请输入题库包名称确认：',
            ),
            const SizedBox(height: 12),
            TextField(
              autofocus: true,
              onChanged: (v) => typedName = v.trim(),
              decoration: const InputDecoration(
                hintText: '输入名称以确认删除',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, null),
            child: const Text('取消'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: const Color(0xFFBA1A1A),
            ),
            onPressed: () => Navigator.pop(ctx, typedName == bank.name),
            child: const Text('彻底删除'),
          ),
        ],
      ),
    );
    if (confirmed != true) {
      if (confirmed == false) _toast('名称不匹配，已取消删除');
      return;
    }
    final repo = await ref.read(quizRepositoryProvider);
    await repo.deleteBankCompletely(bank.bankId);
    _toast('已彻底删除「${bank.name}」');
    await _load();
  }

  // ---------- 归档清理 ----------

  Future<void> _purgeArchived(String bankId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('清理归档题'),
        content: const Text('将彻底删除该题库包的已归档题目及其作答记录，不可恢复。继续？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('取消'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('清理'),
          ),
        ],
      ),
    );
    if (confirmed != true) return;
    final repo = await ref.read(quizRepositoryProvider);
    final n = await repo.purgeArchived(bankId);
    _toast('已清理 $n 道归档题');
    await _load();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    // 标题居中（需求）；保留状态栏 inset，避免标题顶到打孔摄像头区域
    return Scaffold(
      appBar: GlassAppBar(title: const Text('设置'), centerTitle: true),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
          ? _ErrorRetry(message: _error!, onRetry: _load)
          : ListView(
              // 底部留 96 安全空间，防沉浸式导航遮挡（需求）
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
              children: [
                // ---------- 学习目标（P2） ----------
                const _SectionHeader(
                  title: '学习目标',
                  helperText: '考试倒计时与每日任务（计划倒排为建议，可自由覆盖）',
                ),
                _buildStudyGoalCard(theme),
                const SizedBox(height: 16),
                // ---------- 学习设置 ----------
                const _SectionHeader(title: '学习设置', helperText: '刷题时的显示与复习节奏'),
                Card(
                  clipBehavior: Clip.antiAlias,
                  child: Column(
                    children: [
                      SwitchListTile(
                        secondary: _IconBox(
                          icon: Icons.timer_outlined,
                          color: theme.colorScheme.primary,
                        ),
                        // 标题与说明保持现有文本不变
                        title: const Text('刷题页显示计时'),
                        subtitle: const Text('关闭则静默计时，仅在统计页查看耗时'),
                        value: _showPracticeTimer,
                        onChanged: _setPracticeTimerVisible,
                      ),
                      const Divider(height: 1, indent: 16, endIndent: 16),
                      ListTile(
                        leading: _IconBox(
                          icon: Icons.psychology_outlined,
                          color: theme.colorScheme.primary,
                        ),
                        title: const Text('记忆保持率'),
                        subtitle: Text(
                          '当前 ${(_desiredRetention * 100).toStringAsFixed(0)}% · 调低（如冲刺期 80%）复习间隔拉长，把时间留给刷新题',
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
                        child: Slider(
                          value: _desiredRetention,
                          min: 0.7,
                          max: 0.95,
                          divisions: 5,
                          label:
                              '${(_desiredRetention * 100).toStringAsFixed(0)}%',
                          onChanged: (v) =>
                              setState(() => _desiredRetention = v),
                          onChangeEnd: _setDesiredRetention,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                // ---------- 外观设置 ----------
                const _SectionHeader(
                  title: '外观设置',
                  helperText: '自定义主色、背景与圆角风格',
                ),
                Card(
                  child: ListTile(
                    leading: _IconBox(
                      icon: Icons.palette_outlined,
                      color: theme.colorScheme.tertiary,
                    ),
                    title: const Text('主题定制'),
                    subtitle: const Text('主色 / 背景 / 透明度 / 圆角 / 深色模式'),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => _openThemePanel(),
                  ),
                ),
                const SizedBox(height: 16),
                // ---------- 数据与题库 ----------
                const _SectionHeader(title: '数据与题库', helperText: '题库包管理与数据备份'),
                Card(
                  clipBehavior: Clip.antiAlias,
                  child: Column(
                    children: [
                      // 题库包区块：可折叠，默认收起（用户要求）
                      ExpansionTile(
                        initiallyExpanded: false,
                        leading: _IconBox(
                          icon: Icons.folder_open_outlined,
                          color: theme.colorScheme.tertiary,
                        ),
                        title: const Text(
                          '题库包管理',
                          style: TextStyle(fontWeight: FontWeight.w600),
                        ),
                        subtitle: Text('${_banks.length} 个已导入 · 点开管理'),
                        childrenPadding: const EdgeInsets.only(bottom: 8),
                        children: [
                          ListTile(
                            leading: _IconBox(
                              icon: Icons.add_box_outlined,
                              color: theme.colorScheme.tertiary,
                            ),
                            title: const Text('导入题库包'),
                            subtitle: const Text(
                              '支持 .json 或 .zip（manifest + questions）',
                            ),
                            trailing: const Icon(Icons.chevron_right),
                            onTap: _importBank,
                          ),
                          if (_banks.isEmpty)
                            const Padding(
                              padding: EdgeInsets.all(16),
                              child: Text('未导入题库包'),
                            )
                          else
                            for (final bank in _banks)
                              ListTile(
                                leading: _IconBox(
                                  icon: bank.hidden
                                      ? Icons.folder_off_outlined
                                      : Icons.folder_outlined,
                                  color: theme.colorScheme.secondary,
                                ),
                                title: Text(
                                  bank.hidden ? '${bank.name}（已隐藏）' : bank.name,
                                ),
                                subtitle: Text(
                                  '${bank.bankId} · v${bank.version} · 共 ${bank.total} 题'
                                  '${bank.archived > 0 ? '（归档 ${bank.archived}）' : ''}'
                                  '${bank.userEdited > 0 ? '（本地修改 ${bank.userEdited}）' : ''}',
                                ),
                                trailing: PopupMenuButton<String>(
                                  tooltip: '题库包管理',
                                  onSelected: (v) => _onBankAction(bank, v),
                                  itemBuilder: (_) => [
                                    const PopupMenuItem(
                                      value: 'edit',
                                      child: Text('编辑题目'),
                                    ),
                                    if (bank.archived > 0)
                                      const PopupMenuItem(
                                        value: 'purge',
                                        child: Text('清理归档题'),
                                      ),
                                    PopupMenuItem(
                                      value: bank.hidden ? 'restore' : 'hide',
                                      child: Text(bank.hidden ? '恢复显示' : '隐藏（保留数据）'),
                                    ),
                                    PopupMenuItem(
                                      value: 'delete',
                                      child: Text(
                                        '彻底删除',
                                        style: TextStyle(
                                          color: Theme.of(context).colorScheme.error,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                        ],
                      ),
                      const Divider(height: 1, indent: 16, endIndent: 16),
                      ListTile(
                        leading: _IconBox(
                          icon: Icons.backup_outlined,
                          color: theme.colorScheme.primary,
                        ),
                        title: const Text('导出备份'),
                        subtitle: const Text('全部题目/作答/复习进度导出为 JSON 文件'),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: _exportBackup,
                      ),
                      if (reviewModeEnabled)
                        ListTile(
                          leading: _IconBox(
                            icon: Icons.flag_outlined,
                            color: theme.colorScheme.error,
                          ),
                          title: const Text('导出审题标记'),
                          subtitle: const Text('刷题时标记的"待修改"题目清单，导出为 JSON 文件'),
                          trailing: const Icon(Icons.chevron_right),
                          onTap: _exportReviewFlags,
                        ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                // ---------- 关于 ----------
                const _SectionHeader(
                  title: '关于',
                  helperText: '本地优先 · 学习数据仅保存在设备',
                ),
                Card(
                  child: ListTile(
                    leading: _IconBox(
                      icon: Icons.school_outlined,
                      color: theme.colorScheme.tertiary,
                    ),
                    title: const Text('考研刷题'),
                    subtitle: const Text('本地离线刷题 · 学习数据不出设备'),
                  ),
                ),
              ],
            ),
    );
  }
}

/// 区块标题（AppSectionHeader 风格：titleMedium w700 + 可选说明）
///
/// widgets/ 目录由其他 agent 独占，此处私有实现相同视觉，避免跨文件依赖。
class _SectionHeader extends StatelessWidget {
  const _SectionHeader({required this.title, this.helperText});

  final String title;
  final String? helperText;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Expanded(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                  height: 1.3,
                ),
              ),
              if (helperText != null && helperText!.isNotEmpty) ...[
                const SizedBox(height: 4),
                Text(
                  helperText!,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }
}

/// 统一错误态 + 重试（审查 P1-3）
class _ErrorRetry extends StatelessWidget {
  const _ErrorRetry({required this.message, required this.onRetry});

  final String message;
  final Future<void> Function() onRetry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error_outline, size: 48, color: theme.colorScheme.error),
          const SizedBox(height: 12),
          Text(
            message,
            style: theme.textTheme.bodyMedium,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          FilledButton.tonal(onPressed: onRetry, child: const Text('重试')),
        ],
      ),
    );
  }
}

/// 统一图标容器（与首页/错题本风格一致）
class _IconBox extends StatelessWidget {
  const _IconBox({required this.icon, required this.color});

  final IconData icon;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Icon(icon, color: color, size: 22),
    );
  }
}

/// 主题定制面板：顶部实时预览 + 主色/背景/透明度/圆角/深色（需求：高自由度）
///
/// 滑块拖动过程中只更新本地状态（预览卡实时变化），松手（onChangeEnd）才持久化，
/// 避免拖动每帧写库并触发全局主题刷新。
class _Stepper extends StatelessWidget {
  const _Stepper({required this.value, required this.onChanged});

  final int value;
  final void Function(int delta) onChanged;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        IconButton(
          visualDensity: VisualDensity.compact,
          iconSize: 20,
          onPressed: value > 0 ? () => onChanged(-1) : null,
          icon: const Icon(Icons.remove_circle_outline),
        ),
        SizedBox(
          width: 36,
          child: Text(
            '$value',
            textAlign: TextAlign.center,
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
        IconButton(
          visualDensity: VisualDensity.compact,
          iconSize: 20,
          onPressed: value < 200 ? () => onChanged(1) : null,
          icon: const Icon(Icons.add_circle_outline),
        ),
      ],
    );
  }
}
