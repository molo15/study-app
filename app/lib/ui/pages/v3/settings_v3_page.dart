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

import '../../../data/quiz_repository.dart';
import '../../../models/models.dart';
import '../../../services/export_helper.dart';
import '../../app_toast.dart';
import '../../responsive.dart';
import '../../theme/ios_tokens.dart';
import '../../theme_controller.dart';
import '../../widgets/ios_list_group.dart';

class SettingsV3Page extends ConsumerStatefulWidget {
  const SettingsV3Page({super.key});

  @override
  ConsumerState<SettingsV3Page> createState() => _SettingsV3PageState();
}

class _SettingsV3PageState extends ConsumerState<SettingsV3Page> {
  bool _loading = true;
  StudyGoal _goal = const StudyGoal();
  bool _reviewEnabled = false;
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
      final banks = await repo.banks(includeHidden: true);
      final stats = await repo.studyStats();
      if (!mounted) return;
      setState(() {
        _goal = goal;
        _reviewEnabled = review;
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
    final days = _goal.daysUntilExam(DateTime.now());
    if (days == null) return '未设置考试日期';
    if (days < 0) return '考试已结束 · ${-days} 天前';
    return '距考试 $days 天';
  }

  Future<void> _saveTheme(AppThemeConfig config) async {
    await ref.read(themeControllerProvider.notifier).apply(config);
  }

  void _pickThemePreference(IOSColorScheme colors) async {
    final config = await ref.read(themeControllerProvider.future);
    if (!mounted) return;
    final current = config.themePreference;
    final options = [
      (ThemePreference.system, '跟随系统', '自动匹配系统深色模式'),
      (ThemePreference.light, '浅色', '始终使用浅色外观'),
      (ThemePreference.dark, '深色', '始终使用深色外观'),
    ];
    await showModalBottomSheet<void>(
      context: context,
      builder: (sheetCtx) {
        final sheetColors = IOSColors.of(sheetCtx);
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Padding(
                padding: const EdgeInsets.symmetric(
                  vertical: IOSSpacing.s16,
                  horizontal: IOSSpacing.s24,
                ),
                child: Text(
                  '深色模式',
                  style: IOSTypography.title3(color: sheetColors.text),
                ),
              ),
              for (final (mode, label, sub) in options)
                ListTile(
                  title: Text(label,
                      style: IOSTypography.body(color: sheetColors.text)),
                  subtitle: Text(sub,
                      style: IOSTypography.caption1(
                          color: sheetColors.text2)),
                  trailing: mode == current
                      ? Icon(Icons.check_circle,
                          color: sheetColors.primary, size: 22)
                      : Icon(Icons.circle_outlined,
                          color: sheetColors.text3, size: 22),
                  onTap: () async {
                    Navigator.of(sheetCtx).pop();
                    if (mode == current) return;
                    await _saveTheme(config.copyWith(themePreference: mode));
                  },
                ),
              const SizedBox(height: IOSSpacing.s8),
            ],
          ),
        );
      },
    );
  }

  void _pickExamDate(IOSColorScheme colors) async {
    final repo = await ref.read(quizRepositoryProvider);
    if (!mounted) return;
    final now = DateTime.now();
    var picked = now;
    final init = _goal.examDate;
    final parsed = init == null ? null : DateTime.tryParse(init);
    if (parsed != null) picked = parsed;
    await showModalBottomSheet<void>(
      context: context,
      builder: (sheetCtx) {
        final sheetColors = IOSColors.of(sheetCtx);
        return SafeArea(
          child: Column(
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
                      child: TextButton(
                        onPressed: () => Navigator.of(sheetCtx).pop(),
                        child: Text('取消',
                            style: IOSTypography.body(
                                color: sheetColors.text2)),
                      ),
                    ),
                    Expanded(
                      child: FilledButton(
                        onPressed: () async {
                          final date = picked;
                          Navigator.of(sheetCtx).pop();
                          final goal = StudyGoal(
                            examDate:
                                '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}',
                            dailyNew: _goal.dailyNew,
                            dailyReview: _goal.dailyReview,
                            enabled: _goal.enabled,
                          );
                          await repo.setStudyGoal(goal);
                          if (!mounted) return;
                          setState(() => _goal = goal);
                        },
                        child: Text('保存',
                            style: IOSTypography.body(
                                color: sheetColors.text)),
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

  /// 每日目标编辑面板：启用开关 + 每日新题/复习步进器（步长 10，0~200）
  void _pickDailyGoal(IOSColorScheme colors) async {
    var enabled = _goal.enabled;
    var dailyNew = _goal.dailyNew;
    var dailyReview = _goal.dailyReview;
    await showModalBottomSheet<void>(
      context: context,
      builder: (sheetCtx) {
        final sheetColors = IOSColors.of(sheetCtx);
        return StatefulBuilder(
          builder: (ctx, setSheet) => SafeArea(
            child: Column(
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
                SwitchListTile(
                  title: Text('启用每日目标',
                      style: IOSTypography.body(color: sheetColors.text)),
                  subtitle: Text('首页显示今日进度与考试倒计时',
                      style: IOSTypography.caption1(color: sheetColors.text2)),
                  value: enabled,
                  activeTrackColor: sheetColors.primary,
                  onChanged: (v) => setSheet(() => enabled = v),
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
                        child: TextButton(
                          onPressed: () => Navigator.of(ctx).pop(),
                          child: Text('取消',
                              style: IOSTypography.body(
                                  color: sheetColors.text2)),
                        ),
                      ),
                      Expanded(
                        child: FilledButton(
                          onPressed: () async {
                            final goal = StudyGoal(
                              examDate: _goal.examDate,
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
                          child: Text('保存',
                              style: IOSTypography.body(
                                  color: sheetColors.text)),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
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
      final path =
          await exportToDownloadsBytes('quiz_archive_$stamp.zip', bytes);
      if (!mounted) return;
      showAppToast(context, '已导出存档：$path');
    } catch (e) {
      if (!mounted) return;
      showAppToast(context, '导出失败：$e');
    }
  }

  void _showMemorizeModeInfo(IOSColorScheme colors) {
    showDialog<void>(
      context: context,
      builder: (dialogCtx) {
        final c = IOSColors.of(dialogCtx);
        return AlertDialog(
          title: Text('背题模式',
              style: IOSTypography.title3(color: c.text)),
          content: Text(
            '背题支持两种学习形态：\n\n'
            '• 知识卡片：正面题目 / 背面答案，点击翻转记忆\n'
            '• 题目模式：直接显示题干与选项，自测后判分\n\n'
            '进入背题页后可在顶部切换模式。当前版本默认题目模式。',
            style: IOSTypography.footnote(color: c.text2),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogCtx).pop(),
              child: Text('知道了',
                  style: IOSTypography.body(color: c.primary)),
            ),
          ],
        );
      },
    );
  }

  void _showHelp(IOSColorScheme colors) {
    showDialog<void>(
      context: context,
      builder: (dialogCtx) {
        final c = IOSColors.of(dialogCtx);
        return AlertDialog(
          title: Text('使用帮助',
              style: IOSTypography.title3(color: c.text)),
          content: Text(
            '快速上手：\n\n'
            '1. 「今日」页查看待复习与新题队列，点击开始练习\n'
            '2. 答题后四档评分（忘记/模糊/良好/完美），系统按间隔重复调度\n'
            '3. 「背题」中央圆钮进入科目背诵，支持翻转记忆\n'
            '4. 「统计」查看正确率、近 7 日趋势与薄弱章节\n'
            '5. 「我的」设置深色模式、审题标记与每日目标\n\n'
            '数据全部保存在本机，自动存档。',
            style: IOSTypography.footnote(color: c.text2),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogCtx).pop(),
              child: Text('好的',
                  style: IOSTypography.body(color: c.primary)),
            ),
          ],
        );
      },
    );
  }

  void _showFeedback(IOSColorScheme colors) {
    showDialog<void>(
      context: context,
      builder: (dialogCtx) {
        final c = IOSColors.of(dialogCtx);
        return AlertDialog(
          title: Text('意见反馈',
              style: IOSTypography.title3(color: c.text)),
          content: Text(
            '遇到问题或有改进建议？\n\n'
            '当前版本为本地单机应用，反馈渠道建设中。\n\n'
            '你可以：\n'
            '• 记录问题截图与复现步骤\n'
            '• 在 GitHub 仓库提交 Issue\n'
            '• 或直接在使用中留意，后续版本将内置反馈表单',
            style: IOSTypography.footnote(color: c.text2),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogCtx).pop(),
              child: Text('好的',
                  style: IOSTypography.body(color: c.primary)),
            ),
          ],
        );
      },
    );
  }

  void _showAbout(IOSColorScheme colors) {
    showDialog<void>(
      context: context,
      builder: (dialogCtx) {
        final dialogColors = IOSColors.of(dialogCtx);
        return AlertDialog(
          title: Text('关于',
              style: IOSTypography.title3(color: dialogColors.text)),
          content: Text(
            '考研刷题\n\nv3.0 · iOS 风格\n\n五科题库 4504 题 · 数据自动存档\n学习数据与进度仅保存在本机。',
            style: IOSTypography.footnote(color: dialogColors.text2),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogCtx).pop(),
              child: Text('好的',
                  style: IOSTypography.body(color: dialogColors.primary)),
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
              trailing: CupertinoSwitch(
                value: _reviewEnabled,
                activeTrackColor: colors.primary,
                onChanged: (v) async {
                  setState(() => _reviewEnabled = v);
                  final repo = await ref.read(quizRepositoryProvider);
                  await repo.setReviewModeEnabled(v);
                },
              ),
            ),
            IOSListItem(
              title: '存疑标记 ◆',
              subtitle: '模拟考会话级 · 待接入',
              leading: _circleIcon(colors.primary, Icons.diamond_outlined),
              trailing: CupertinoSwitch(
                value: false,
                activeTrackColor: colors.primary,
                onChanged: (_) =>
                    showAppToast(context, '存疑标记将在模拟考功能接入后开放'),
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
              trailing: CupertinoSwitch(
                value: reduceMotion,
                activeTrackColor: colors.primary,
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
              title: '导出与存档',
              subtitle: '自动存档 · 备份',
              leading: _circleIcon(colors.success, Icons.ios_share_outlined),
              showChevron: true,
              onTap: _exportBackup,
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
              subtitle: 'v3.0 · iOS',
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
