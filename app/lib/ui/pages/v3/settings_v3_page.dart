/// V3 iOS 风格「我的」页（设置中心）
///
/// 对齐 `docs/prototype/ui-v3-ios.html` 的 me 页设计稿：
/// - profile 头（头像 + 昵称 + 目标 + 徽章）
/// - 学习 / 背题 / 外观 / 数据 / 关于 五组分段列表（iOS inset grouped）
/// - 深色模式三段切换（跟随系统 / 浅色 / 深色，ThemePreference，V3 §3.6）
/// - 审题🚩开关（落库 review_flags，review_mode_enabled）
/// - 存疑◆开关（会话级，待模拟考接入，当前禁用占位）
/// - 减少动效开关（reduceMotion）
///
/// 数据层复用现有 QuizRepository / ThemeController，不新增 SQL、不改 repository。
/// 旧 V2 SettingsPage 保留（lib/ui/settings_page.dart），本页为 V3 替换实现。
library;

import 'dart:math';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';

import '../../../data/quiz_repository.dart';
import '../../../models/models.dart';
import '../../../services/export_helper.dart';
import '../../app_toast.dart';
import '../../responsive.dart';
import '../../theme/ios_tokens.dart';
import '../../theme_controller.dart';
import '../../widgets/ios_button.dart';
import '../../widgets/ios_list_group.dart';
import '../../theme/ios_page_route.dart';
import 'bank_manage_v3_page.dart';
import '../../widgets/ios_action_sheet.dart';
import '../../widgets/ios_switch.dart';

class SettingsV3Page extends ConsumerStatefulWidget {
  const SettingsV3Page({super.key});

  @override
  ConsumerState<SettingsV3Page> createState() => _SettingsV3PageState();
}

class _SettingsV3PageState extends ConsumerState<SettingsV3Page> {
  bool _loading = true;
  StudyGoal _goal = const StudyGoal();
  bool _reviewEnabled = false;
  bool _doubtEnabled = true;
  int _bankCount = 0;
  int _streak = 0;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      final goal = await repo.studyGoal() ?? const StudyGoal();
      final review = await repo.reviewModeEnabled();
      final doubt = await repo.doubtEnabled();
      final banks = await repo.banks(includeHidden: true);
      final stats = await repo.studyStats();
      if (!mounted) return;
      setState(() {
        _goal = goal;
        _reviewEnabled = review;
        _doubtEnabled = doubt;
        _bankCount = banks.fold<int>(0, (s, b) => s + b.active);
        _streak = _calcStreak(stats.daily);
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() => _loading = false);
    }
  }

  /// 连续学习天数：从最近有记录的一天往回数连续 count>0 的天数。
  static int _calcStreak(List<DailyData> daily) {
    if (daily.isEmpty) return 0;
    final counts = <String, int>{for (final d in daily) d.day: d.count};
    final keys = counts.keys.toList()..sort();
    final last = DateTime.tryParse(keys.last);
    if (last == null) return 0;
    String key(DateTime t) =>
        '${t.year.toString().padLeft(4, '0')}-${t.month.toString().padLeft(2, '0')}-${t.day.toString().padLeft(2, '0')}';
    var cursor = last;
    var streak = 0;
    while (true) {
      final c = counts[key(cursor)];
      if (c == null || c <= 0) break;
      streak++;
      cursor = cursor.subtract(const Duration(days: 1));
    }
    return streak;
  }

  String get _goalSub {
    final school = _goal.school?.trim();
    final hasSchool = school != null && school.isNotEmpty;
    final days = _goal.daysUntilExam(DateTime.now());
    final datePart = days == null
        ? '未设置考试日期'
        : (days < 0 ? '考试已结束 · ${-days} 天前' : '距考试 $days 天');
    return hasSchool ? '$school · $datePart' : datePart;
  }

  Future<void> _saveTheme(AppThemeConfig config) async {
    await ref.read(themeControllerProvider.notifier).apply(config);
  }

  void _pickThemePreference(IOSColorScheme colors) async {
    final config = await ref.read(themeControllerProvider.future);
    if (!mounted) return;
    final current = config.themePreference;
    final picked = await showIOSActionSheet<ThemePreference>(
      context: context,
      title: '深色模式',
      selectedValue: current,
      items: const [
        IOSActionItem(
          value: ThemePreference.system,
          title: '跟随系统',
          subtitle: '自动匹配系统深色模式',
        ),
        IOSActionItem(
          value: ThemePreference.light,
          title: '浅色',
          subtitle: '始终使用浅色外观',
        ),
        IOSActionItem(
          value: ThemePreference.dark,
          title: '深色',
          subtitle: '始终使用深色外观',
        ),
      ],
    );
    if (picked == null || picked == current || !mounted) return;
    await _saveTheme(config.copyWith(themePreference: picked));
  }

  void _pickExamDate(IOSColorScheme colors) async {
    final repo = await ref.read(quizRepositoryProvider);
    if (!mounted) return;
    final now = DateTime.now();
    var picked = now;
    final init = _goal.examDate;
    final parsed = init == null ? null : DateTime.tryParse(init);
    if (parsed != null) picked = parsed;
    final schoolController = TextEditingController(text: _goal.school ?? '');
    await showIOSModalSheet<void>(
      context: context,
      builder: (sheetCtx) {
        final sheetColors = IOSColors.of(sheetCtx);
        return Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Padding(
                padding: const EdgeInsets.symmetric(
                  vertical: IOSSpacing.s16,
                  horizontal: IOSSpacing.s24,
                ),
                child: Text('目标院校 · 考试日期',
                    style: IOSTypography.title3(color: sheetColors.text)),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: IOSSpacing.s20,
                ),
                child: CupertinoTextField(
                  controller: schoolController,
                  textInputAction: TextInputAction.done,
                  placeholder: '目标院校（如：陕西师范大学）',
                  prefix: const Padding(
                    padding: EdgeInsets.only(left: 8),
                    child: Icon(Icons.school_outlined, size: 20),
                  ),
                  padding: const EdgeInsets.symmetric(
                    horizontal: IOSSpacing.s12,
                    vertical: IOSSpacing.s8,
                  ),
                ),
              ),
              const SizedBox(height: IOSSpacing.s8),
              SizedBox(
                height: 220,
                child: CupertinoDatePicker(
                  mode: CupertinoDatePickerMode.date,
                  initialDateTime: picked,
                  minimumDate: DateTime(now.year - 1),
                  maximumDate: DateTime(now.year + 3),
                  onDateTimeChanged: (v) => picked = v,
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(IOSSpacing.s16),
                child: Row(
                  children: [
                    Expanded(
                      child: IOSButton(
                        type: IOSButtonType.text,
                        label: '取消',
                        onPressed: () => Navigator.of(sheetCtx).pop(),
                      ),
                    ),
                    const SizedBox(width: IOSSpacing.s8),
                    Expanded(
                      child: IOSButton(
                        type: IOSButtonType.primary,
                        label: '保存',
                        onPressed: () async {
                          final date = picked;
                          Navigator.of(sheetCtx).pop();
                          final goal = StudyGoal(
                            examDate:
                                '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}',
                            school: schoolController.text.trim(),
                            dailyNew: _goal.dailyNew,
                            dailyReview: _goal.dailyReview,
                            enabled: _goal.enabled,
                          );
                          await repo.setStudyGoal(goal);
                          if (!mounted) return;
                          setState(() => _goal = goal);
                        },
                      ),
                    ),
                  ],
                ),
              ),
            ],
        );
      },
    );
    schoolController.dispose();
  }

  /// 每日目标编辑面板：启用开关 + 每日新题/复习步进器（步长 10，0~200）
  void _pickDailyGoal(IOSColorScheme colors) async {
    var enabled = _goal.enabled;
    var dailyNew = _goal.dailyNew;
    var dailyReview = _goal.dailyReview;
    await showIOSModalSheet<void>(
      context: context,
      builder: (sheetCtx) {
        final sheetColors = IOSColors.of(sheetCtx);
        return StatefulBuilder(
          builder: (ctx, setSheet) => Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Padding(
                  padding: const EdgeInsets.symmetric(
                    vertical: IOSSpacing.s16,
                    horizontal: IOSSpacing.s24,
                  ),
                  child: Text('每日目标',
                      style: IOSTypography.title3(color: sheetColors.text)),
                ),
                Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('启用每日目标',
                              style: IOSTypography.body(color: sheetColors.text)),
                          const SizedBox(height: IOSSpacing.s4),
                          Text('首页显示今日进度与考试倒计时',
                              style: IOSTypography.caption1(color: sheetColors.text2)),
                        ],
                      ),
                    ),
                    IOSSwitch(
                      value: enabled,
                      onChanged: (v) => setSheet(() => enabled = v),
                    ),
                  ],
                ),
                _stepperRow(
                  label: '每日新题',
                  value: dailyNew,
                  enabled: enabled,
                  colors: sheetColors,
                  onChanged: (v) => setSheet(() => dailyNew = v),
                ),
                _stepperRow(
                  label: '每日复习',
                  value: dailyReview,
                  enabled: enabled,
                  colors: sheetColors,
                  onChanged: (v) => setSheet(() => dailyReview = v),
                ),
                Padding(
                  padding: const EdgeInsets.all(IOSSpacing.s16),
                  child: Row(
                    children: [
                      Expanded(
                        child: IOSButton(
                          type: IOSButtonType.text,
                          label: '取消',
                          onPressed: () => Navigator.of(ctx).pop(),
                        ),
                      ),
                      const SizedBox(width: IOSSpacing.s8),
                      Expanded(
                        child: IOSButton(
                          type: IOSButtonType.primary,
                          label: '保存',
                          onPressed: () async {
                            final goal = StudyGoal(
                              examDate: _goal.examDate,
                              school: _goal.school,
                              dailyNew: dailyNew,
                              dailyReview: dailyReview,
                              enabled: enabled,
                            );
                            final repo =
                                await ref.read(quizRepositoryProvider);
                            await repo.setStudyGoal(goal);
                            if (!mounted) return;
                            setState(() => _goal = goal);
                            if (ctx.mounted) Navigator.of(ctx).pop();
                          },
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
        );
      },
    );
  }

  Widget _stepperRow({
    required String label,
    required int value,
    required bool enabled,
    required IOSColorScheme colors,
    required ValueChanged<int> onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: IOSSpacing.s16,
        vertical: IOSSpacing.s4,
      ),
      child: Row(
        children: [
          Text(label,
              style: IOSTypography.body(
                  color: enabled ? colors.text : colors.text3)),
          const Spacer(),
          IconButton(
            icon: Icon(Icons.remove_circle_outline,
                color: enabled ? colors.primary : colors.text3, size: 28),
            onPressed: enabled && value > 0
                ? () => onChanged(max(0, value - 10))
                : null,
          ),
          SizedBox(
            width: 48,
            child: Text('$value',
                textAlign: TextAlign.center,
                style: IOSTypography.title3(
                    color: enabled ? colors.text : colors.text3)),
          ),
          IconButton(
            icon: Icon(Icons.add_circle_outline,
                color: enabled ? colors.primary : colors.text3, size: 28),
            onPressed: enabled
                ? () => onChanged(min(200, value + 10))
                : null,
          ),
        ],
      ),
    );
  }

  Future<void> _exportBackup() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      if (!mounted) return;
      final bytes = await repo.exportArchive();
      final stamp = DateTime.now()
          .toIso8601String()
          .replaceAll(':', '-')
          .split('.')
          .first;
      final msg = await exportBackupFile(
        'quiz_archive_$stamp.zip',
        bytes,
      );
      if (!mounted) return;
      showAppToast(context, msg);
    } catch (e) {
      if (!mounted) return;
      showAppToast(context, '导出失败：$e');
    }
  }

  /// 导入存档：支持 .zip（v3）与 .json（v1/v2 旧备份）。
  /// 解析预览 → iOS 弹层确认（含题库版本不匹配提示）→ 全量恢复用户状态（不动题库）。
  Future<void> _importBackup() async {
    try {
      final file = await FilePicker.pickFile(
        type: FileType.custom,
        allowedExtensions: const ['zip', 'json'],
        dialogTitle: '选择存档文件（.zip 或 .json）',
      );
      if (file == null) return;
      final bytes = await file.readAsBytes();
      if (!mounted) return;
      final repo = await ref.read(quizRepositoryProvider);
      final preview = await repo.parseArchive(bytes);
      final mismatches = preview.bankMismatches;
      if (!mounted) return;
      final ok = await showIOSModalSheet<bool>(
        context: context,
        builder: (sheetCtx) {
          final c = IOSColors.of(sheetCtx);
          return Padding(
            padding: const EdgeInsets.all(IOSSpacing.s20),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('导入存档？', style: IOSTypography.headline(color: c.text)),
                const SizedBox(height: IOSSpacing.s12),
                Text(
                  '将恢复存档中的全部用户状态（做题记录、复习进度、背题进度、'
                  '错题本、模拟考记录、设置），题库以本机为准。不可撤销。',
                  style: IOSTypography.footnote(color: c.text2)
                      .copyWith(height: 1.5),
                ),
                if (mismatches.isNotEmpty) ...[
                  const SizedBox(height: IOSSpacing.s12),
                  Text("题库版本不一致：${mismatches.join('；')}",
                      style: IOSTypography.footnote(color: c.warning)),
                ],
                const SizedBox(height: IOSSpacing.s16),
                Row(
                  children: [
                    Expanded(
                      child: IOSButton(
                        label: '取消',
                        type: IOSButtonType.text,
                        expand: true,
                        onPressed: () => Navigator.of(sheetCtx).pop(false),
                      ),
                    ),
                    const SizedBox(width: IOSSpacing.s12),
                    Expanded(
                      child: IOSButton(
                        label: '导入并覆盖',
                        type: IOSButtonType.danger,
                        expand: true,
                        onPressed: () => Navigator.of(sheetCtx).pop(true),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          );
        },
      );
      if (ok != true) return;
      final result = await repo.restoreArchive(bytes);
      if (!mounted) return;
      showAppToast(context, '已恢复：做题记录 ${result.restoredLogs} 条、复习卡 ${result.restoredCards} 张');
      await _load();
    } on FormatException catch (e) {
      if (mounted) showAppToast(context, '存档文件无效：${e.message}');
    } catch (e) {
      if (mounted) showAppToast(context, '导入存档失败：$e');
    }
  }

  void _showMemorizeModeInfo(IOSColorScheme colors) {
    showIOSModalSheet<void>(
      context: context,
      builder: (sheetCtx) {
        final c = IOSColors.of(sheetCtx);
        return Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: IOSSpacing.s16),
            Text('背题模式', style: IOSTypography.title3(color: c.text)),
            const SizedBox(height: IOSSpacing.s12),
            Text(
              '背题支持两种学习形态：\n\n'
              '• 知识卡片：正面题目 / 背面答案，点击翻转记忆\n'
              '• 题目模式：直接显示题干与选项，自测后判分\n\n'
              '进入背题页后可在顶部切换模式。当前版本默认题目模式。',
              style: IOSTypography.footnote(color: c.text2),
            ),
            const SizedBox(height: IOSSpacing.s20),
            IOSButton(
              expand: true,
              label: '知道了',
              onPressed: () => Navigator.of(sheetCtx).pop(),
            ),
          ],
        );
      },
    );
  }

  void _showHelp(IOSColorScheme colors) {
    showIOSModalSheet<void>(
      context: context,
      // P2-3：内容少，maxHeightFactor 从 0.82 降到 0.5，避免下方大片空白
      maxHeightFactor: 0.5,
      builder: (sheetCtx) {
        final c = IOSColors.of(sheetCtx);
        return Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: IOSSpacing.s16),
            Text('使用帮助', style: IOSTypography.title3(color: c.text)),
            const SizedBox(height: IOSSpacing.s16),
            // P2-3：footnote 小字 -> body，列表化排版（每条独立行 + 间距）
            _helpItem(c, '1', '「今日」页查看待复习与新题队列，点击开始练习'),
            _helpItem(c, '2', '答题后四档评分，系统按间隔重复调度'),
            _helpItem(c, '3', '「背题」进入科目背诵，支持翻转记忆'),
            _helpItem(c, '4', '「统计」查看正确率、近 7 日趋势与薄弱章节'),
            _helpItem(c, '5', '「我的」设置深色模式、审题标记与每日目标'),
            const SizedBox(height: IOSSpacing.s12),
            Text(
              '数据全部保存在本机，自动存档。',
              style: IOSTypography.footnote(color: c.text3),
            ),
            const SizedBox(height: IOSSpacing.s20),
            IOSButton(
              expand: true,
              label: '好的',
              onPressed: () => Navigator.of(sheetCtx).pop(),
            ),
          ],
        );
      },
    );
  }

  /// P2-3：帮助条目（序号 + 正文，body 字号，行间距清晰）
  Widget _helpItem(IOSColorScheme c, String num, String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: IOSSpacing.s8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 22,
            child: Text(
              num,
              style: IOSTypography.body(color: c.primary)
                  .copyWith(fontWeight: FontWeight.w600),
            ),
          ),
          Expanded(
            child: Text(
              text,
              style: IOSTypography.body(color: c.text2),
            ),
          ),
        ],
      ),
    );
  }

  void _showFeedback(IOSColorScheme colors) {
    showIOSModalSheet<void>(
      context: context,
      maxHeightFactor: 0.5,
      builder: (sheetCtx) {
        final c = IOSColors.of(sheetCtx);
        return Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: IOSSpacing.s16),
            Text('意见反馈', style: IOSTypography.title3(color: c.text)),
            const SizedBox(height: IOSSpacing.s12),
            Text(
              '遇到问题或有改进建议？',
              style: IOSTypography.body(color: c.text),
            ),
            const SizedBox(height: IOSSpacing.s8),
            Text(
              '当前版本为本地单机应用，反馈渠道建设中。',
              style: IOSTypography.footnote(color: c.text3),
            ),
            const SizedBox(height: IOSSpacing.s16),
            _helpItem(c, '•', '记录问题截图与复现步骤'),
            _helpItem(c, '•', '在 GitHub 仓库提交 Issue'),
            _helpItem(c, '•', '后续版本将内置反馈表单'),
            const SizedBox(height: IOSSpacing.s20),
            IOSButton(
              expand: true,
              label: '好的',
              onPressed: () => Navigator.of(sheetCtx).pop(),
            ),
          ],
        );
      },
    );
  }

  void _showAbout(IOSColorScheme colors) {
    showIOSModalSheet<void>(
      context: context,
      maxHeightFactor: 0.45,
      builder: (sheetCtx) {
        final c = IOSColors.of(sheetCtx);
        return Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: IOSSpacing.s16),
            Text('关于', style: IOSTypography.title3(color: c.text)),
            const SizedBox(height: IOSSpacing.s16),
            Text(
              '考研刷题',
              style: IOSTypography.title2(color: c.text),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: IOSSpacing.s8),
            Text(
              'v$kArchiveAppVersion · iOS 风格',
              style: IOSTypography.body(color: c.text2),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: IOSSpacing.s16),
            Text(
              '五科题库 · 数据自动存档\n学习数据与进度仅保存在本机。',
              style: IOSTypography.footnote(color: c.text3),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: IOSSpacing.s20),
            IOSButton(
              expand: true,
              label: '好的',
              onPressed: () => Navigator.of(sheetCtx).pop(),
            ),
          ],
        );
      },
    );
  }

  String _themeLabel(ThemePreference pref) => switch (pref) {
        ThemePreference.system => '跟随系统',
        ThemePreference.light => '浅色',
        ThemePreference.dark => '深色',
      };

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    final themeConfig = ref.watch(themeControllerProvider).value;

    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    final pref = themeConfig?.themePreference ?? ThemePreference.system;
    final reduceMotion = themeConfig?.reduceMotion ?? false;

    return Center(
      child: ConstrainedBox(
        constraints: BoxConstraints(maxWidth: effectiveContentWidth(context)),
        child: ListView(
      padding: EdgeInsets.only(
        left: IOSBreakpoint.compactPadding,
        right: IOSBreakpoint.compactPadding,
        top: IOSSpacing.s20,
        bottom: IOSFloatingBar.kTContentBottomInset,
      ),
      children: [
        Text('我的', style: IOSTypography.largeTitle(color: colors.text)),
        const SizedBox(height: IOSSpacing.s4),
        Text('学习设置与资料',
            style: IOSTypography.footnote(color: colors.text2)),
        const SizedBox(height: IOSSpacing.s20),

        // ---------- profile 头 ----------
        _ProfileHead(
          goalSub: _goalSub,
          streak: _streak,
          bankCount: _bankCount,
          colors: colors,
        ),
        const SizedBox(height: IOSSpacing.s20),

        // ---------- 学习 ----------
        IOSListGroup(
          title: '学习',
          items: [
            IOSListItem(
              title: '目标院校',
              subtitle: _goalSub,
              leading: _circleIcon(colors.primary, Icons.school_outlined),
              showChevron: true,
              onTap: () => _pickExamDate(colors),
            ),
            IOSListItem(
              title: '每日目标',
              subtitle: _goal.enabled
                  ? '新题 ${_goal.dailyNew} · 复习 ${_goal.dailyReview} / 天'
                  : '未开启',
              leading: _circleIcon(colors.success, Icons.flag_outlined),
              showChevron: true,
              onTap: () => _pickDailyGoal(colors),
            ),
          ],
        ),
        const SizedBox(height: IOSSpacing.s16),

        // ---------- 背题 ----------
        IOSListGroup(
          title: '背题',
          items: [
            IOSListItem(
              title: '背题模式',
              subtitle: '知识卡片 / 题目 双模式',
              leading: _circleIcon(colors.warning, Icons.style_outlined),
              showChevron: true,
              onTap: () => _showMemorizeModeInfo(colors),
            ),
            IOSListItem(
              title: '审题标记 🚩',
              subtitle: '练习重点题 · 落库 review_flags',
              leading: _circleIcon(colors.primary, Icons.flag_outlined),
              trailing: IOSSwitch(
                value: _reviewEnabled,
                onChanged: (v) async {
                  setState(() => _reviewEnabled = v);
                  final repo = await ref.read(quizRepositoryProvider);
                  await repo.setReviewModeEnabled(v);
                },
              ),
            ),
            IOSListItem(
              title: '存疑标记 ◆',
              subtitle: '模拟考答题时标记存疑题目',
              leading: _circleIcon(colors.primary, Icons.diamond_outlined),
              trailing: IOSSwitch(
                value: _doubtEnabled,
                onChanged: (v) async {
                  setState(() => _doubtEnabled = v);
                  try {
                    final repo = await ref.read(quizRepositoryProvider);
                    await repo.setDoubtEnabled(v);
                  } catch (_) {}
                },
              ),
            ),
          ],
        ),
        const SizedBox(height: IOSSpacing.s16),

        // ---------- 外观 ----------
        IOSListGroup(
          title: '外观',
          items: [
            IOSListItem(
              title: '深色模式',
              subtitle: '跟随系统 / 手动',
              leading: _circleIcon(colors.primary, Icons.dark_mode_outlined),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(_themeLabel(pref),
                      style: IOSTypography.footnote(color: colors.text2)),
                  const SizedBox(width: IOSSpacing.s4),
                  Icon(Icons.chevron_right,
                      color: colors.text3, size: 20),
                ],
              ),
              onTap: () => _pickThemePreference(colors),
            ),
            IOSListItem(
              title: '减少动效',
              subtitle: '弱化过渡动画 · 更流畅',
              leading: _circleIcon(colors.warning, Icons.speed_outlined),
              trailing: IOSSwitch(
                value: reduceMotion,
                onChanged: (v) async {
                  final config =
                      await ref.read(themeControllerProvider.future);
                  await _saveTheme(config.copyWith(reduceMotion: v));
                },
              ),
            ),
          ],
        ),
        const SizedBox(height: IOSSpacing.s16),

        // ---------- 数据 ----------
        IOSListGroup(
          title: '数据',
          items: [
            IOSListItem(
              title: '题库管理',
              subtitle: '导入题库包 · 隐藏 / 删除 / 编辑题目',
              leading: _circleIcon(colors.primary, Icons.library_books_outlined),
              showChevron: true,
              onTap: () => Navigator.of(context).push(
                iosPageRoute<dynamic>((_) => const BankManageV3Page()),
              ),
            ),
            IOSListItem(
              title: '导出与存档',
              subtitle: '自动存档 · 备份',
              leading: _circleIcon(colors.success, Icons.ios_share_outlined),
              showChevron: true,
              onTap: _exportBackup,
            ),
            IOSListItem(
              title: '导入备份',
              subtitle: '从 .zip / .json 存档恢复学习记录',
              leading: _circleIcon(colors.primary, Icons.file_download_outlined),
              showChevron: true,
              onTap: _importBackup,
            ),
            IOSListItem(
              title: '数据统计',
              subtitle: '行为分析',
              leading: _circleIcon(colors.warning, Icons.bar_chart_outlined),
              showChevron: true,
              onTap: () => showAppToast(context, '数据统计已迁移至「统计」页'),
            ),
          ],
        ),
        const SizedBox(height: IOSSpacing.s16),

        // ---------- 关于 ----------
        IOSListGroup(
          title: '关于',
          items: [
            IOSListItem(
              title: '使用帮助',
              leading: _circleIcon(colors.primary, Icons.help_outline),
              showChevron: true,
              onTap: () => _showHelp(colors),
            ),
            IOSListItem(
              title: '意见反馈',
              leading: _circleIcon(colors.warning, Icons.chat_outlined),
              showChevron: true,
              onTap: () => _showFeedback(colors),
            ),
            IOSListItem(
              title: '关于',
              subtitle: 'v$kArchiveAppVersion · iOS 风格',
              leading: _circleIcon(colors.success, Icons.info_outline),
              showChevron: true,
              onTap: () => _showAbout(colors),
            ),
          ],
        ),
      ],
        ),
      ),
    );
  }

  Widget _circleIcon(Color color, IconData icon) {
    return Container(
      width: 30,
      height: 30,
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(IOSRadius.tag),
      ),
      child: Icon(icon, color: color, size: 17),
    );
  }
}

/// profile 头：头像 + 昵称 + 目标 + 徽章
class _ProfileHead extends StatelessWidget {
  const _ProfileHead({
    required this.goalSub,
    required this.streak,
    required this.bankCount,
    required this.colors,
  });

  final String goalSub;
  final int streak;
  final int bankCount;
  final IOSColorScheme colors;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 56,
          height: 56,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: colors.primaryBg,
            shape: BoxShape.circle,
          ),
          child: Text('考',
              style: IOSTypography.title2(color: colors.primary)),
        ),
        const SizedBox(width: IOSSpacing.s16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('考研人',
                  style: IOSTypography.title3(color: colors.text)),
              const SizedBox(height: 2),
              Text(goalSub,
                  style: IOSTypography.footnote(color: colors.text2)),
              const SizedBox(height: IOSSpacing.s8),
              Wrap(
                spacing: IOSSpacing.s8,
                runSpacing: IOSSpacing.s4,
                children: [
                  if (streak > 0)
                    _Badge(
                      text: '🔥 连续 $streak 天',
                      bg: colors.successBg,
                      fg: colors.success,
                    ),
                  _Badge(
                    text: '$bankCount 题池',
                    bg: colors.fill,
                    fg: colors.text2,
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _Badge extends StatelessWidget {
  const _Badge({
    required this.text,
    required this.bg,
    required this.fg,
  });

  final String text;
  final Color bg;
  final Color fg;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: IOSSpacing.s8,
        vertical: 3,
      ),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(IOSRadius.tag),
      ),
      child: Text(text,
          style: IOSTypography.caption1(color: fg).copyWith(
            fontWeight: FontWeight.w600,
          )),
    );
  }
}
