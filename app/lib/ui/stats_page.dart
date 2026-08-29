/// 统计报表（设计方案 §3.5）：作答量/正确率/用时/近 7 日/章节分布/到期未复习
///
/// 本页只做 UI 重排：StudyStats 字段、studyStats() 查询、SQL、正确率/累计用时
/// 计算均保持不变，仅调整布局、视觉与空态引导。
library;

import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import '../models/models.dart';
import 'glass_app_bar.dart';

class StatsPage extends ConsumerStatefulWidget {
  const StatsPage({super.key});

  @override
  ConsumerState<StatsPage> createState() => _StatsPageState();
}

class _StatsPageState extends ConsumerState<StatsPage> {
  bool _loading = true;
  String? _error;
  StudyStats? _stats;
  // P2 章节掌握度：排序/筛选/折叠状态
  bool _chapterSortByAccuracy = true; // true=按正确率升序（薄弱在前），false=章节顺序
  int _chapterFilter = 0; // 0=全部 1=薄弱(<60%) 2=中等(60-80%) 3=掌握(>=80%)
  bool _chapterExpanded = false; // 超过8章时默认折叠

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

  String _fmtDuration(int ms) {
    final minutes = (ms / 60000).floor();
    if (minutes < 60) return '$minutes 分钟';
    return '${(minutes / 60).toStringAsFixed(1)} 小时';
  }

  static const List<String> _filterLabels = ['全部', '薄弱', '中等', '掌握'];

  /// P2：按筛选+排序返回章节列表；折叠时只取前8条
  List<ChapterStats> _filteredChapters(List<ChapterStats> all) {
    var list = all.where((c) {
      switch (_chapterFilter) {
        case 1: return c.accuracy < 60;
        case 2: return c.accuracy >= 60 && c.accuracy < 80;
        case 3: return c.accuracy >= 80;
        default: return true;
      }
    }).toList();
    if (_chapterSortByAccuracy) {
      list.sort((a, b) => a.accuracy.compareTo(b.accuracy));
    }
    if (!_chapterExpanded && list.length > 8) {
      list = list.sublist(0, 8);
    }
    return list;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    // 标题居中（需求）；保留状态栏 inset，避免标题顶到打孔摄像头区域
    return Scaffold(
      appBar: GlassAppBar(title: const Text('学习统计'), centerTitle: true),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
          ? _ErrorRetry(message: _error!, onRetry: _load)
          : RefreshIndicator(onRefresh: _load, child: _buildBody(theme)),
    );
  }

  Widget _buildBody(ThemeData theme) {
    final s = _stats!;
    // 首次使用 / 无任何作答：整页给引导文案（数据来源与计算不变）
    if (s.totalAnswered == 0) {
      return ListView(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
        children: const [_EmptyGuide()],
      );
    }
    return ListView(
      // 底部留 96 安全空间，防沉浸式导航遮挡（需求）
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
      children: [
        // 总览卡
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const _SectionHeader(title: '总览', helperText: '整体学习进度汇总'),
                const SizedBox(height: 12),
                // 响应式指标：窄屏每行 2 个，宽屏每行 4 个，大字体不溢出
                LayoutBuilder(
                  builder: (context, constraints) {
                    final columns = constraints.maxWidth >= 480 ? 4 : 2;
                    const spacing = 8.0;
                    final itemWidth =
                        (constraints.maxWidth - spacing * (columns - 1)) /
                        columns;
                    return Wrap(
                      spacing: spacing,
                      runSpacing: 12,
                      children: [
                        for (final stat in [
                          _Stat(
                            icon: Icons.edit_outlined,
                            label: '做题',
                            value: '${s.totalAnswered}',
                          ),
                          _Stat(
                            icon: Icons.done_all,
                            label: '正确率',
                            value: '${s.accuracy.toStringAsFixed(0)}%',
                          ),
                          _Stat(
                            icon: Icons.timer_outlined,
                            label: '累计用时',
                            value: _fmtDuration(s.totalTimeMs),
                          ),
                          _Stat(
                            icon: Icons.event_repeat,
                            label: '待复习',
                            value: '${s.dueCount}',
                          ),
                        ])
                          SizedBox(width: itemWidth, child: stat),
                      ],
                    );
                  },
                ),
                const SizedBox(height: 12),
                Text(
                  '正确 ${s.correctCount} · 部分正确 ${s.partialCount} · 错误 ${s.wrongCount}',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.outline,
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        // 近 7 日做题量
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const _SectionHeader(title: '近 7 日做题量', helperText: '每日完成题数变化'),
                const SizedBox(height: 16),
                _DailyBars(daily: s.daily),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        // 题型分布圆饼图（需求：饼图+柱形图结合）
        if (s.typeDistribution.isNotEmpty)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const _SectionHeader(title: '题型分布', helperText: '各题型已作答数量占比'),
                  const SizedBox(height: 16),
                  _PieChartCard(
                    data: {
                      for (final e in s.typeDistribution.entries)
                        _typeLabel(e.key): e.value,
                    },
                  ),
                ],
              ),
            ),
          ),
        const SizedBox(height: 16),
        // 作答结果分布圆饼图
        if (s.resultDistribution.isNotEmpty)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const _SectionHeader(
                    title: '作答结果分布',
                    helperText: '正确 / 错误 / 部分正确 / 未答占比',
                  ),
                  const SizedBox(height: 16),
                  _PieChartCard(
                    data: {
                      for (final e in s.resultDistribution.entries)
                        _resultLabel(e.key): e.value,
                    },
                  ),
                ],
              ),
            ),
          ),
        const SizedBox(height: 16),
        // P2 章节掌握度：排序+筛选+折叠+分档着色
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Expanded(
                      child: _SectionHeader(title: '章节掌握度', helperText: '各章节作答量与正确率'),
                    ),
                    // 排序切换：薄弱在前 / 章节顺序
                    IconButton(
                      icon: Icon(
                        _chapterSortByAccuracy ? Icons.sort : Icons.menu_open,
                        size: 20,
                      ),
                      tooltip: _chapterSortByAccuracy ? '按章节顺序' : '按薄弱程度排序',
                      onPressed: s.byChapter.isEmpty
                          ? null
                          : () => setState(() => _chapterSortByAccuracy = !_chapterSortByAccuracy),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                if (s.byChapter.isEmpty)
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    child: Center(
                      child: Text(
                        '暂无作答记录，去刷几题吧',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.outline,
                        ),
                      ),
                    ),
                  )
                else ...[
                  // 筛选标签：全部/薄弱/中等/掌握
                  Wrap(
                    spacing: 8,
                    children: [
                      for (var i = 0; i < _filterLabels.length; i++)
                        ChoiceChip(
                          label: Text(_filterLabels[i]),
                          selected: _chapterFilter == i,
                          onSelected: (_) => setState(() => _chapterFilter = i),
                        ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  // 过滤+排序后的章节列表
                  for (final c in _filteredChapters(s.byChapter))
                    _ChapterRow(stats: c),
                  // 折叠/展开：超过8章时默认只显示8条
                  if (_filteredChapters(s.byChapter).length > 8 && !_chapterExpanded) ...[
                    const SizedBox(height: 4),
                    TextButton(
                      onPressed: () => setState(() => _chapterExpanded = true),
                      child: Text('展开全部（共 ${_filteredChapters(s.byChapter).length} 章）'),
                    ),
                  ] else if (_chapterExpanded && _filteredChapters(s.byChapter).length > 8) ...[
                    const SizedBox(height: 4),
                    TextButton(
                      onPressed: () => setState(() => _chapterExpanded = false),
                      child: const Text('收起'),
                    ),
                  ],
                ],
              ],
            ),
          ),
        ),
      ],
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

/// 总览指标单元（图标 + 数值 + 标签），数值超宽时自动缩放防溢出
class _Stat extends StatelessWidget {
  const _Stat({required this.icon, required this.label, required this.value});

  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 20, color: theme.colorScheme.primary),
        const SizedBox(height: 4),
        FittedBox(
          fit: BoxFit.scaleDown,
          child: Text(
            value,
            style: theme.textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.bold,
              color: theme.colorScheme.primary,
            ),
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: theme.textTheme.bodySmall,
        ),
      ],
    );
  }
}

/// 整页空态引导（无任何作答时展示，不改变数据来源）
class _EmptyGuide extends StatelessWidget {
  const _EmptyGuide();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 56),
      child: Column(
        children: [
          Icon(
            Icons.insights_outlined,
            size: 56,
            color: theme.colorScheme.outline,
          ),
          const SizedBox(height: 16),
          Text(
            '暂无作答记录',
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '去刷几题吧，作答后这里会展示做题量、正确率与学习趋势',
            textAlign: TextAlign.center,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.outline,
            ),
          ),
        ],
      ),
    );
  }
}

String _typeLabel(String type) => switch (type) {
  'single_choice' => '单选',
  'multi_choice' => '多选',
  'blank' => '填空',
  'short_answer' => '简答',
  'true_false' => '判断',
  _ => type,
};

String _resultLabel(String result) => switch (result) {
  'correct' => '正确',
  'wrong' => '错误',
  'partial' => '部分正确',
  'skip' => '未答',
  _ => result,
};

/// fl_chart 圆饼图（带图例）；深色模式使用提亮后的配色
class _PieChartCard extends StatelessWidget {
  const _PieChartCard({required this.data});

  final Map<String, int> data;

  /// 浅色模式保持现用配色
  static const _lightColors = [
    Color(0xFF00696D),
    Color(0xFF525E7D),
    Color(0xFF7D5260),
    Color(0xFFB2780A),
    Color(0xFF2E7D32),
    Color(0xFFBA1A1A),
  ];

  /// 深色模式提亮变体，保证深色背景下的可见度
  static const _darkColors = [
    Color(0xFF4DB6AC),
    Color(0xFF90A4AE),
    Color(0xFFF48FB1),
    Color(0xFFFFB74D),
    Color(0xFF81C784),
    Color(0xFFE57373),
  ];

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final colors = isDark ? _darkColors : _lightColors;
    final total = data.values.fold(0, (a, b) => a + b);
    if (total == 0) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 12),
        child: Center(
          child: Text(
            '暂无数据',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.outline,
            ),
          ),
        ),
      );
    }
    final entries = data.entries.toList();
    return Column(
      children: [
        SizedBox(
          height: 180,
          child: PieChart(
            PieChartData(
              sectionsSpace: 2,
              centerSpaceRadius: 40,
              sections: [
                for (var i = 0; i < entries.length; i++)
                  PieChartSectionData(
                    value: entries[i].value.toDouble(),
                    color: colors[i % colors.length],
                    radius: 50,
                    title: entries[i].value == 0
                        ? ''
                        : '${(entries[i].value / total * 100).toStringAsFixed(0)}%',
                    // 提亮配色上改用深色文字保证对比度
                    titleStyle: TextStyle(
                      color: isDark ? const Color(0xFF101418) : Colors.white,
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        // 图例
        Wrap(
          spacing: 12,
          runSpacing: 6,
          children: [
            for (var i = 0; i < entries.length; i++)
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 10,
                    height: 10,
                    decoration: BoxDecoration(
                      color: colors[i % colors.length],
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '${entries[i].key} ${entries[i].value}',
                    style: theme.textTheme.bodySmall,
                  ),
                ],
              ),
          ],
        ),
      ],
    );
  }
}

/// 简单柱状图（近 7 日）
class _DailyBars extends StatelessWidget {
  const _DailyBars({required this.daily});

  final List<DailyData> daily;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final max = daily.fold(0, (m, d) => d.count > m ? d.count : m);
    return Row(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        for (final d in daily)
          Expanded(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('${d.count}', style: theme.textTheme.bodySmall),
                const SizedBox(height: 4),
                Container(
                  height: max == 0 ? 4 : 8 + 40 * d.count / max,
                  margin: const EdgeInsets.symmetric(horizontal: 3),
                  decoration: BoxDecoration(
                    color: d.count == 0
                        ? theme.colorScheme.surfaceContainerHighest
                        : theme.colorScheme.primary,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                const SizedBox(height: 4),
                Text(d.day, style: theme.textTheme.labelSmall),
              ],
            ),
          ),
      ],
    );
  }
}

class _ChapterRow extends StatelessWidget {
  const _ChapterRow({required this.stats});

  final ChapterStats stats;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Expanded(
            child: Text(
              stats.chapter,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          const SizedBox(width: 12),
          Text('${stats.total} 题', style: theme.textTheme.bodySmall),
          const SizedBox(width: 8),
          SizedBox(
            width: 80,
            child: LinearProgressIndicator(
              value: stats.accuracy / 100,
              backgroundColor: theme.colorScheme.surfaceContainerHighest,
              color: stats.accuracy < 60
                  ? theme.colorScheme.error
                  : stats.accuracy < 80
                      ? Colors.orange
                      : theme.colorScheme.primary,
            ),
          ),
          const SizedBox(width: 8),
          SizedBox(
            width: 40,
            child: Text(
              '${stats.accuracy.toStringAsFixed(0)}%',
              textAlign: TextAlign.right,
              style: theme.textTheme.bodySmall,
            ),
          ),
        ],
      ),
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
