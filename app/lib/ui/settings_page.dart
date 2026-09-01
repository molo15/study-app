/// 设置页（设计方案 §3.6）：按用户认知分组——
/// 学习设置 → 外观设置 → 数据与题库 → 关于。
/// 持久化 key（theme_config / desired_retention / show_practice_timer）与
/// repository 方法保持不变，仅做 UI 层重排与主题编辑体验优化。
library;

import 'dart:convert';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../data/quiz_repository.dart';
import '../data/seed_loader.dart';
import '../models/models.dart';
import '../services/archive_store.dart';
import '../services/auto_archive_service.dart';
import '../services/export_helper.dart';
import 'theme_controller.dart';
import 'glass_app_bar.dart';
import 'widgets/app_section_header.dart';
import 'widgets/app_state_view.dart';
import 'widgets/app_card.dart';
import 'widgets/ios_install_guide.dart';
import 'app_toast.dart';
import 'app_routes.dart';

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
  bool _reviewEnabled = false; // 审题标记开关（默认关）
  StudyGoal _studyGoal = const StudyGoal();
  bool _autoArchiveEnabled = true; // 自动存档开关（默认开）
  int _autoArchiveKeep = 5; // 自动存档保留份数
  int _autoArchiveCount = 0; // 本地已有自动存档份数

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
      final reviewEnabled = await repo.reviewModeEnabled();
      final studyGoal = await repo.studyGoal() ?? const StudyGoal();
      final autoEnabled =
          (await repo.setting('auto_archive_enabled')) != 'false';
      final autoKeep =
          int.tryParse(await repo.setting('auto_archive_keep') ?? '') ?? 5;
      final autoCount = (await FileArchiveStore().listAutoArchives()).length;
      if (!mounted) return;
      setState(() {
        _banks = banks;
        _desiredRetention = retention;
        _showPracticeTimer = showPracticeTimer;
        _reviewEnabled = reviewEnabled;
        _studyGoal = studyGoal;
        _autoArchiveEnabled = autoEnabled;
        _autoArchiveKeep = autoKeep;
        _autoArchiveCount = autoCount;
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
    showAppToast(context, text);
  }

  /// 打开主题定制面板（需求：高自由度自定义主题）
  Future<void> _openThemePanel() async {
    await Navigator.of(
      context,
    ).push(AppPageRoute(builder: (_) => const _ThemePanelPage()));
  }

  // ---------- 学习目标（P2） ----------

  Future<void> _saveStudyGoal() async {
    final repo = await ref.read(quizRepositoryProvider);
    await repo.setStudyGoal(_studyGoal);
    // 静默保存：学习目标为高频微调操作（开关/日期/步进/输入），不弹横幅打扰
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

  /// 学习目标设置卡：启用开关 + 考试日期 + 每日新题/复习（计划倒排为建议，用户可自由覆盖）
  /// 个人卡（UI v2 · 我的）：头像 + 身份 + 象征性考试倒计时
  Widget _buildProfileCard(ThemeData theme) {
    final config = ref.watch(themeControllerProvider).asData?.value;
    final accent = config?.accent ?? const Color(0xFF4F7CD4);
    final ink2 = theme.colorScheme.onSurfaceVariant;
    final days = _studyGoal.daysUntilExam(DateTime.now());

    return AppCard(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 18),
        child: Row(
          children: [
            // 头像
            Container(
              width: 54,
              height: 54,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [Color.lerp(accent, Colors.white, 0.3)!, accent],
                ),
                border: Border.all(color: Colors.white.withValues(alpha: 0.7), width: 2),
              ),
              alignment: Alignment.center,
              child: const Icon(Icons.school_outlined, color: Colors.white, size: 26),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('考研人', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800)),
                  const SizedBox(height: 3),
                  Text('学科语文 · 五科备考', style: TextStyle(fontSize: 12, color: ink2)),
                ],
              ),
            ),
            // 象征性考试倒计时
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(20),
                gradient: LinearGradient(
                  colors: [accent.withValues(alpha: 0.14), accent.withValues(alpha: 0.24)],
                ),
              ),
              child: Text(
                days != null ? '距考试 $days 天' : '未设考试日期',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: accent,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStudyGoalCard(ThemeData theme) {
    final goal = _studyGoal;
    return AppCard(padding: EdgeInsets.zero, margin: const EdgeInsets.symmetric(vertical: 6), 
      child: Column(
        children: [
          SwitchListTile(
            secondary: _IconBox(
              icon: Icons.event_available,
              color: theme.colorScheme.error,
            ),
            title: const Text('学习目标'),
            subtitle: Text(goal.enabled
                ? '已启用 · 首页显示考试倒计时'
                : '设置考试日期，首页显示倒计时'),
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
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
            child: Text(
              '设置考试日期后，首页会显示距离考试的天数',
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

  /// 导出存档（v3：zip 压缩，含全部用户状态，不含题库；多端方案 §2）
  Future<void> _exportBackup() async {
    final repo = await ref.read(quizRepositoryProvider);
    final bytes = await repo.exportArchive();
    final stamp = DateTime.now()
        .toIso8601String()
        .replaceAll(':', '-')
        .split('.')
        .first;
    try {
      final path = await exportToDownloadsBytes(
          'quiz_archive_$stamp.zip', bytes);
      _toast('已导出存档：$path');
    } catch (e) {
      _toast('导出失败：$e');
    }
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

  /// 导入存档：支持 .zip（v3 存档）与 .json（v1/v2 旧备份）。
  /// 解析预览 → 确认（含题库版本不匹配提示）→ 全量恢复用户状态（不动题库）。
  Future<void> _importBackup() async {
    try {
      final file = await FilePicker.pickFile(
        type: FileType.custom,
        allowedExtensions: ['zip', 'json'],
        dialogTitle: '选择存档文件（.zip 或 .json）',
      );
      if (file == null) return;
      final bytes = await file.readAsBytes();
      if (!mounted) return;
      final repo = await ref.read(quizRepositoryProvider);
      final preview = await repo.parseArchive(bytes);
      final mismatches = preview.bankMismatches;
      if (!mounted) return;
      final ok = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Text('导入存档？'),
          content: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  '将恢复存档中的全部用户状态（做题记录、复习进度、背题进度、'
                  '错题本、模拟考记录、审题标记、设置），题库以本机内置包为准。'
                  '不可撤销，建议先「导出存档」留存当前数据。',
                  style: const TextStyle(fontSize: 13, height: 1.5),
                ),
                if (mismatches.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  const Text('⚠ 题库版本不一致：',
                      style: TextStyle(fontWeight: FontWeight.w700)),
                  for (final m in mismatches)
                    Padding(
                      padding: const EdgeInsets.only(top: 2),
                      child: Text('· $m',
                          style: const TextStyle(fontSize: 12.5)),
                    ),
                  const SizedBox(height: 6),
                  const Text('记录可能无法匹配到题，建议先在两端统一题库版本。',
                      style: TextStyle(fontSize: 12.5)),
                ],
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('取消'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('导入并覆盖'),
            ),
          ],
        ),
      );
      if (ok != true) return;
      final result = await repo.restoreArchive(bytes);
      _toast('已恢复：做题记录 ${result.restoredLogs} 条、复习卡 ${result.restoredCards} 张');
      await _load();
    } on FormatException catch (e) {
      _toast('存档文件无效：${e.message}');
    } catch (e) {
      _toast('导入存档失败：$e');
    }
  }

  /// 切换自动存档开关（写设置 + 重启服务）
  Future<void> _toggleAutoArchive(bool enabled) async {
    setState(() => _autoArchiveEnabled = enabled);
    final service = ref.read(autoArchiveServiceProvider);
    await service.setEnabled(enabled);
    if (enabled) {
      final repo = await ref.read(quizRepositoryProvider);
      await service.start(repo, FileArchiveStore());
    } else {
      service.stop();
    }
  }

  /// 选择保留份数
  Future<void> _pickKeepCount() async {
    final choices = [3, 5, 10];
    final picked = await showDialog<int>(
      context: context,
      builder: (ctx) => SimpleDialog(
        title: const Text('保留存档份数'),
        children: [
          for (final n in choices)
            SimpleDialogOption(
              onPressed: () => Navigator.pop(ctx, n),
              child: Text(
                '$n 份',
                style: TextStyle(
                  fontWeight:
                      n == _autoArchiveKeep ? FontWeight.w700 : FontWeight.normal,
                ),
              ),
            ),
        ],
      ),
    );
    if (picked == null) return;
    setState(() => _autoArchiveKeep = picked);
    final service = ref.read(autoArchiveServiceProvider);
    await service.setKeepCount(picked);
    _toast('已设置：本地最多保留 $picked 份');
    await _load();
  }

  /// 立即存档一次
  Future<void> _triggerAutoArchive() async {
    final service = ref.read(autoArchiveServiceProvider);
    final repo = await ref.read(quizRepositoryProvider);
    await service.start(repo, FileArchiveStore());
    final path = await service.trigger();
    if (path != null) {
      _toast('已存档：$path');
    } else if (kIsWeb) {
      _toast('存档失败：浏览器本地存储可能已满，请使用「导出备份」保存到文件');
    } else {
      _toast('存档失败，请检查存储空间后重试');
    }
    await _load();
  }

  /// 关于：题库导入格式说明弹窗
  void _showImportFormat() {
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('题库导入格式'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: const [
              Text('支持两种题库包容器：', style: TextStyle(fontWeight: FontWeight.w700)),
              SizedBox(height: 6),
              Text('· .json：单文件，顶层含 manifest 字段 + questions 数组'),
              Text('· .zip：manifest.json + questions/ 目录（可按章节分文件）'),
              SizedBox(height: 12),
              Text('题目必填字段：', style: TextStyle(fontWeight: FontWeight.w700)),
              SizedBox(height: 6),
              Text('· id：全局唯一，如 bank-xxx:q_00001'),
              Text('· type：single_choice / multi_choice / true_false / blank / short_answer'),
              Text('· stem：题干'),
              Text('· answer：答案（选择题为选项 key 或正确项文本）'),
              Text('· options：选择题选项数组 [{"key":"A","text":"..."}]'),
              SizedBox(height: 12),
              Text('可选字段：', style: TextStyle(fontWeight: FontWeight.w700)),
              SizedBox(height: 6),
              Text('· explanation：解析、chapter：章节、purpose：basic/test'),
              Text('· formatVersion：1-4（缺省按基础格式解析）'),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('知道了'),
          ),
        ],
      ),
    );
  }

  // ---------- 题库包管理操作 ----------

  Future<void> _onBankAction(BankInfo bank, String action) async {
    switch (action) {
      case 'edit':
        context.go('/me/questions/${bank.bankId}');
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
    final iosBanner = iosInstallGuideBanner();
    // 标题居中（需求）；保留状态栏 inset，避免标题顶到打孔摄像头区域
    return Scaffold(
      appBar: GlassAppBar(title: const Text('我的'), centerTitle: true),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
          ? AppStateView.error(message: _error!, onRetry: _load)
          : ListView(
              // 底部留 96 安全空间，防沉浸式导航遮挡（需求）
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
              children: [
                // ---------- iOS 数据保护提示（仅 iOS Web） ----------
                ?iosBanner,
                // ---------- 个人卡（UI v2 · 我的） ----------
                _buildProfileCard(theme),
                const SizedBox(height: 6),
                // ---------- 学习目标（P2） ----------
                const AppSectionHeader(
                  title: '学习目标',
                  helperText: '设置考试日期，首页显示倒计时',
                ),
                _buildStudyGoalCard(theme),
                const SizedBox(height: 16),
                // ---------- 学习设置 ----------
                const AppSectionHeader(title: '学习设置', helperText: '刷题时的显示与复习节奏'),
                AppCard(padding: EdgeInsets.zero, margin: const EdgeInsets.symmetric(vertical: 6), 
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
                const AppSectionHeader(
                  title: '外观设置',
                  helperText: '自定义主色、背景与圆角风格',
                ),
                AppCard(padding: EdgeInsets.zero, margin: const EdgeInsets.symmetric(vertical: 6), 
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
                const AppSectionHeader(title: '数据与题库', helperText: '题库包管理与数据备份'),
                AppCard(padding: EdgeInsets.zero, margin: const EdgeInsets.symmetric(vertical: 6), 
                  child: Column(
                    children: [
                      // 题库包区块：可折叠，默认收起（用户要求）
                      ExpansionTile(
                        initiallyExpanded: true,
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
                        subtitle: const Text('导出做题记录/复习进度/背题进度为 zip 存档（不含题库）'),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: _exportBackup,
                      ),
                      const Divider(height: 1, indent: 16, endIndent: 16),
                      ListTile(
                        leading: _IconBox(
                          icon: Icons.restore_outlined,
                          color: theme.colorScheme.primary,
                        ),
                        title: const Text('导入存档'),
                        subtitle: const Text('从存档文件（.zip/.json）恢复全部用户状态，题库以本机为准'),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: _importBackup,
                      ),
                      const Divider(height: 1, indent: 16, endIndent: 16),
                      ListTile(
                        leading: _IconBox(
                          icon: Icons.schedule_outlined,
                          color: theme.colorScheme.primary,
                        ),
                        title: Row(
                          children: [
                            const Text('自动存档'),
                            const Spacer(),
                            Switch(
                              value: _autoArchiveEnabled,
                              onChanged: _toggleAutoArchive,
                            ),
                          ],
                        ),
                        subtitle: Text(
                          _autoArchiveEnabled
                              ? '每 30 分钟 + 退出时自动保存到本地，已存 $_autoArchiveCount 份'
                              : '已关闭（可随时手动导出/立即存档）',
                        ),
                      ),
                      if (!kIsWeb)
                        ListTile(
                          leading: _IconBox(
                            icon: Icons.inventory_2_outlined,
                            color: theme.colorScheme.primary,
                          ),
                          title: const Text('保留存档份数'),
                          subtitle:
                              Text('本地最多保留 $_autoArchiveKeep 份，超出自动删最旧'),
                          trailing: const Icon(Icons.chevron_right),
                          onTap: _pickKeepCount,
                        ),
                      ListTile(
                        leading: _IconBox(
                          icon: Icons.save_outlined,
                          color: theme.colorScheme.primary,
                        ),
                        title: const Text('立即存档'),
                        subtitle: Text(
                          kIsWeb
                              ? '手动把当前状态保存到浏览器本地'
                              : '手动把当前状态保存到本地 archives/',
                        ),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: _triggerAutoArchive,
                      ),
                      if (_reviewEnabled)
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
                const AppSectionHeader(
                  title: '关于',
                  helperText: '本地优先 · 学习数据仅保存在设备',
                ),
                AppCard(padding: EdgeInsets.zero, margin: const EdgeInsets.symmetric(vertical: 6), 
                  child: Column(
                    children: [
                      ListTile(
                        leading: _IconBox(
                          icon: Icons.school_outlined,
                          color: theme.colorScheme.tertiary,
                        ),
                        title: const Text('考研刷题'),
                        subtitle: const Text('本地离线刷题 · 学习数据不出设备'),
                      ),
                      const Divider(height: 1, indent: 16, endIndent: 16),
                      ListTile(
                        leading: _IconBox(
                          icon: Icons.input_outlined,
                          color: theme.colorScheme.tertiary,
                        ),
                        title: const Text('题库导入格式'),
                        subtitle: const Text('自制题库包的 .json / .zip 格式要求'),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: _showImportFormat,
                      ),
                    ],
                  ),
                ),
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
