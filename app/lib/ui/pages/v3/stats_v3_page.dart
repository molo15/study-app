/// V3 iOS 风格统计页：学习统计报表。
///
/// 对齐 `docs/prototype/ui-v3-ios.html` 统计页：
/// - 顶部大标题（largeTitle 34pt）"统计"
/// - 总览 4 指标（做题 / 正确率 / 累计用时 / 待复习）
/// - 近 7 日做题量柱状图（自绘，无外部图表库）
/// - 题型分布（横向进度条）
/// - 章节掌握度（inset grouped + 进度条）
///
/// 数据层复用 QuizRepository.studyStats()，不新增 SQL、不改 repository。
/// 旧 V2 StatsPage 保留（lib/ui/stats_page.dart）。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../data/quiz_repository.dart';
import '../../../models/models.dart';
import '../../theme/ios_tokens.dart';
import '../../widgets/ios_card.dart';
import '../../widgets/ios_list_group.dart';

class StatsV3Page extends ConsumerStatefulWidget {
  const StatsV3Page({super.key});

  @override
  ConsumerState<StatsV3Page> createState() => StatsV3PageState();
}

class StatsV3PageState extends ConsumerState<StatsV3Page> {
  bool _loading = true;
  String? _error;
  StudyStats? _stats;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      final stats = await repo.studyStats();
      if (!mounted) return;
      setState(() {
        _stats = stats;
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

  /// 供 root_page tab 切换时调用（IndexedStack 常驻页面不重建）
  Future<void> refresh() async {
    await _load();
  }

  String _fmtDuration(int ms) {
    final minutes = (ms / 60000).floor();
    if (minutes < 60) return '$minutes 分钟';
    return '${(minutes / 60).toStringAsFixed(1)} 小时';
  }

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    if (_loading) {
      return const Center(child: CircularProgressIndicator(strokeWidth: 2.5));
    }
    if (_error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.cloud_off_outlined, size: 44, color: colors.danger),
            const SizedBox(height: IOSSpacing.s12),
            Text(_error!, style: IOSTypography.callout(color: colors.text2)),
            const SizedBox(height: IOSSpacing.s16),
            IOSRetryButton(onTap: _load),
          ],
        ),
      );
    }
    final s = _stats!;
    // 首次使用 / 无作答：空态引导
    if (s.totalAnswered == 0) {
      return ListView(
        padding: const EdgeInsets.fromLTRB(
          IOSSpacing.s16,
          IOSSpacing.s8,
          IOSSpacing.s16,
          IOSFloatingBar.kTContentBottomInset,
        ),
        children: [
          Text('统计', style: IOSTypography.largeTitle(color: colors.text)),
          const SizedBox(height: IOSSpacing.s32),
          IOSCard(
            padding: const EdgeInsets.all(IOSSpacing.s24),
            child: Column(
              children: [
                Icon(Icons.insights_outlined,
                    size: 48, color: colors.placeholder),
                const SizedBox(height: IOSSpacing.s12),
                Text('还没有学习数据',
                    style: IOSTypography.title3(color: colors.text)),
                const SizedBox(height: IOSSpacing.s4),
                Text('完成几道题后，这里会展示你的学习统计',
                    style: IOSTypography.footnote(color: colors.text2)),
              ],
            ),
          ),
        ],
      );
    }

    final chapters = s.byChapter
      ..sort((a, b) => a.accuracy.compareTo(b.accuracy));
    final shownChapters = chapters.length > 8
        ? chapters.sublist(0, 8)
        : chapters;

    return ListView(
      padding: const EdgeInsets.fromLTRB(
        IOSSpacing.s16,
        IOSSpacing.s8,
        IOSSpacing.s16,
        IOSFloatingBar.kTContentBottomInset,
      ),
      children: [
        Text('统计', style: IOSTypography.largeTitle(color: colors.text)),
        const SizedBox(height: IOSSpacing.s8),
        // 总览 4 指标
        IOSCard(
          padding: const EdgeInsets.all(IOSSpacing.s16),
          child: Column(
            children: [
              Row(
                children: [
                  _overviewStat('做题', '${s.totalAnswered}', colors.primary),
                  _overviewStat('正确率', '${s.accuracy.toStringAsFixed(0)}%',
                      IOSSystemColors.green),
                ],
              ),
              const SizedBox(height: IOSSpacing.s16),
              Row(
                children: [
                  _overviewStat(
                      '累计用时', _fmtDuration(s.totalTimeMs), colors.warning),
                  _overviewStat('待复习', '${s.dueCount}', colors.danger),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: IOSSpacing.s4),
        // 近 7 日做题量
        IOSCard(
          padding: const EdgeInsets.all(IOSSpacing.s16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('近 7 日做题量',
                  style: IOSTypography.headline(color: colors.text)),
              const SizedBox(height: IOSSpacing.s12),
              _DailyBars(daily: s.daily, colors: colors),
            ],
          ),
        ),
        const SizedBox(height: IOSSpacing.s4),
        // 题型分布
        if (s.typeDistribution.isNotEmpty)
          IOSCard(
            padding: const EdgeInsets.all(IOSSpacing.s16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('题型分布',
                    style: IOSTypography.headline(color: colors.text)),
                const SizedBox(height: IOSSpacing.s12),
                _TypeDistribution(
                  dist: s.typeDistribution,
                  total: s.typeDistribution.values.fold(
                      0, (a, b) => a + b),
                  colors: colors,
                ),
              ],
            ),
          ),
        const SizedBox(height: IOSSpacing.s4),
        // 章节掌握度（薄弱在前，超8章折叠显示前8）
        IOSListGroup(
          title: '章节掌握度 · 薄弱优先',
          items: [
            for (final c in shownChapters)
              IOSListItem(
                title: c.chapter,
                subtitle: '${c.correct} 对 / ${c.wrong} 错 · ${c.total} 题',
                leading: _accuracyBadge(c.accuracy, colors),
                trailing: _accuracyText(c.accuracy, colors),
              ),
          ],
        ),
        if (chapters.length > 8)
          Padding(
            padding: const EdgeInsets.only(
              top: IOSSpacing.s8,
              left: IOSSpacing.s16,
            ),
            child: Text(
              '共 ${chapters.length} 个章节，仅显示最薄弱 8 个',
              style: IOSTypography.caption1(color: colors.text3),
            ),
          ),
      ],
    );
  }

  Widget _overviewStat(String label, String value, Color color) {
    final colors = IOSColors.of(context);
    return Expanded(
      child: Column(
        children: [
          Text(value,
              style: IOSTypography.title2(color: colors.text)
                  .copyWith(fontWeight: FontWeight.w700)),
          const SizedBox(height: IOSSpacing.s4),
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 6,
                height: 6,
                decoration: BoxDecoration(
                  color: color,
                  borderRadius: BorderRadius.circular(3),
                ),
              ),
              const SizedBox(width: IOSSpacing.s4),
              Text(label, style: IOSTypography.caption1(color: colors.text2)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _accuracyBadge(double accuracy, IOSColorScheme colors) {
    final color = accuracy >= 80
        ? colors.success
        : accuracy >= 60
            ? colors.warning
            : colors.danger;
    return Container(
      width: 30,
      height: 30,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(IOSRadius.tag),
      ),
      child: Text(
        '${accuracy.toStringAsFixed(0)}%',
        style: IOSTypography.caption2(color: color)
            .copyWith(fontWeight: FontWeight.w700),
      ),
    );
  }

  Widget _accuracyText(double accuracy, IOSColorScheme colors) {
    final color = accuracy >= 80
        ? colors.success
        : accuracy >= 60
            ? colors.warning
            : colors.danger;
    return Text(
      '掌握',
      style: IOSTypography.caption1(color: color),
    );
  }
}

/// 重试按钮（V3 简约风格）
class IOSRetryButton extends StatelessWidget {
  const IOSRetryButton({super.key, required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: IOSSpacing.s20,
          vertical: IOSSpacing.s12,
        ),
        decoration: BoxDecoration(
          color: colors.primary,
          borderRadius: BorderRadius.circular(IOSRadius.pill),
        ),
        child: Text(
          '重试',
          style: IOSTypography.callout(color: Colors.white)
              .copyWith(fontWeight: FontWeight.w600),
        ),
      ),
    );
  }
}

/// 近 7 日做题量柱状图（自绘，无外部图表库）
class _DailyBars extends StatelessWidget {
  const _DailyBars({required this.daily, required this.colors});

  final List<DailyData> daily;
  final IOSColorScheme colors;

  @override
  Widget build(BuildContext context) {
    final max = daily.fold<int>(0, (m, d) => d.count > m ? d.count : m);
    final barMaxHeight = 80.0;
    final minBarHeight = 3.0;
    return SizedBox(
      height: 110,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          for (final d in daily)
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  if (d.count > 0)
                    Text(
                      '${d.count}',
                      style: IOSTypography.caption2(color: colors.text3),
                    ),
                  const SizedBox(height: 4),
                  Container(
                    width: 14,
                    height: max == 0
                        ? minBarHeight
                        : (barMaxHeight * d.count / max).clamp(
                            minBarHeight, barMaxHeight),
                    decoration: BoxDecoration(
                      color: d.count == 0
                          ? colors.fill2
                          : colors.primary,
                      borderRadius: const BorderRadius.vertical(
                        top: Radius.circular(4),
                      ),
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    d.day,
                    style: IOSTypography.caption2(color: colors.text3),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

/// 题型分布横向进度条
class _TypeDistribution extends StatelessWidget {
  const _TypeDistribution({
    required this.dist,
    required this.total,
    required this.colors,
  });

  final Map<String, int> dist;
  final int total;
  final IOSColorScheme colors;

  static const Map<String, String> _labels = {
    'single_choice': '单选',
    'multiple_choice': '多选',
    'true_false': '判断',
    'fill_blank': '填空',
    'short_answer': '简答',
  };

  @override
  Widget build(BuildContext context) {
    final entries = dist.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));
    return Column(
      children: [
        for (final e in entries)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 4),
            child: Row(
              children: [
                SizedBox(
                  width: 40,
                  child: Text(
                    _labels[e.key] ?? e.key,
                    style: IOSTypography.footnote(color: colors.text2),
                  ),
                ),
                const SizedBox(width: IOSSpacing.s8),
                Expanded(
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(3),
                    child: LinearProgressIndicator(
                      value: total == 0 ? 0 : e.value / total,
                      minHeight: 8,
                      backgroundColor: colors.fill2,
                      color: colors.primary,
                    ),
                  ),
                ),
                const SizedBox(width: IOSSpacing.s8),
                SizedBox(
                  width: 34,
                  child: Text(
                    '${e.value}',
                    textAlign: TextAlign.right,
                    style: IOSTypography.footnote(color: colors.text),
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }
}
