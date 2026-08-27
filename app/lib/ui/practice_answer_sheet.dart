part of 'practice_page.dart';

class _AnswerSheet extends StatelessWidget {
  const _AnswerSheet({
    required this.queue,
    required this.results,
    required this.currentIndex,
    required this.onJump,
  });

  final List<Question> queue;
  final List<Grade?> results;

  /// 当前正在看的题号（完成页回顾时为 -1，无当前题高亮）
  final int currentIndex;
  final ValueChanged<int> onJump;

  // 三态底色（答题卡风格：浅底深字，深浅模式通用）
  static const _greenBg = Color(0xFFEAF3DE);
  static const _greenFg = Color(0xFF2E7D32);
  static const _redBg = Color(0xFFFCEBEB);
  static const _redFg = Color(0xFFBA1A1A);
  static const _greyBg = Color(0xFFF1EFE8);
  static const _greyFg = Color(0xFF6B6B67);
  static const _currentBorder = Color(0xFF378ADD);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final correct = results.where((g) => g == Grade.correct).length;
    final wrong =
        results.where((g) => g == Grade.wrong || g == Grade.partial).length;
    final unanswered = queue.length - correct - wrong;

    return SafeArea(
      top: false,
      child: Padding(
        padding: const EdgeInsets.only(bottom: 12),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 顶栏：左上角返回（收起）+ 标题
            Row(
              children: [
                IconButton(
                  tooltip: '收起',
                  icon: const Icon(Icons.arrow_back),
                  onPressed: () => Navigator.of(context).pop(),
                ),
                Text('答题卡', style: theme.textTheme.titleMedium),
                const Spacer(),
                Padding(
                  padding: const EdgeInsets.only(right: 16),
                  child: Text(
                    '本轮 ${queue.length} 题',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.outline,
                    ),
                  ),
                ),
              ],
            ),
            // 概览四格
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                children: [
                  _Metric(label: '已答', value: correct + wrong),
                  _Metric(label: '未答', value: unanswered),
                  _Metric(
                    label: '答对',
                    value: correct,
                    valueColor: _semantic(context, _greenFg, _kSuccessDark),
                  ),
                  _Metric(
                    label: '答错',
                    value: wrong,
                    valueColor: _semantic(context, _redFg, _kErrorDark),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            // 图例
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                children: [
                  _Legend(color: _greenBg, label: '对'),
                  const SizedBox(width: 10),
                  _Legend(color: _redBg, label: '错'),
                  const SizedBox(width: 10),
                  _Legend(color: _greyBg, label: '未答'),
                  const SizedBox(width: 10),
                  _Legend(
                    color: Colors.transparent,
                    label: '当前',
                    border: Border.all(color: _currentBorder, width: 2),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            // 按题型分区（仅展示本轮出现的题型）
            Flexible(
              child: ListView(
                shrinkWrap: true,
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
                children: [
                  for (final type in [
                    QuestionType.singleChoice,
                    QuestionType.multiChoice,
                    QuestionType.trueFalse,
                    QuestionType.blank,
                    QuestionType.shortAnswer,
                  ])
                    if (queue.any((q) => q.type == type))
                      _TypeSection(
                        type: type,
                        queue: queue,
                        results: results,
                        currentIndex: currentIndex,
                        onJump: onJump,
                      ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// 概览小指标
class _Metric extends StatelessWidget {
  const _Metric({required this.label, required this.value, this.valueColor});

  final String label;
  final int value;
  final Color? valueColor;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Expanded(
      child: Container(
        margin: const EdgeInsets.only(right: 8),
        padding: const EdgeInsets.symmetric(vertical: 10),
        decoration: BoxDecoration(
          color: theme.colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          children: [
            Text(
              '$value',
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w500,
                color: valueColor,
              ),
            ),
            Text(
              label,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.outline,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// 图例色块
class _Legend extends StatelessWidget {
  const _Legend({required this.color, required this.label, this.border});

  final Color color;
  final String label;
  final Border? border;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(3),
            border: border,
          ),
        ),
        const SizedBox(width: 3),
        Text(
          label,
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }
}

/// 单个题型分区：标题 + 题号格子网格
class _TypeSection extends StatelessWidget {
  const _TypeSection({
    required this.type,
    required this.queue,
    required this.results,
    required this.currentIndex,
    required this.onJump,
  });

  final QuestionType type;
  final List<Question> queue;
  final List<Grade?> results;
  final int currentIndex;
  final ValueChanged<int> onJump;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final indices = <int>[
      for (var i = 0; i < queue.length; i++)
        if (queue[i].type == type) i,
    ];
    final correct = indices
        .where((i) => results[i] == Grade.correct)
        .length;
    final wrong = indices
        .where((i) =>
            results[i] == Grade.wrong || results[i] == Grade.partial)
        .length;
    final unanswered = indices.length - correct - wrong;

    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                typeLabel(type),
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w500,
                ),
              ),
              Text(
                '${indices.length} 题 · 对 $correct 错 $wrong 未答 $unanswered',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.outline,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          GridView.count(
            crossAxisCount: 6,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            mainAxisSpacing: 6,
            crossAxisSpacing: 6,
            children: [
              for (final i in indices)
                _Cell(
                  index: i,
                  grade: i < results.length ? results[i] : null,
                  isCurrent: i == currentIndex,
                  onTap: () => _confirmJump(context, i),
                ),
            ],
          ),
        ],
      ),
    );
  }

  /// 点格子 → 确认弹窗 → 确认后收起并跳题
  Future<void> _confirmJump(BuildContext context, int index) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (dialogCtx) => AlertDialog(
        title: Text('跳转到第 ${index + 1} 题？'),
        content: const Text('当前题未作答将保留为未答，可随时跳回继续。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogCtx).pop(false),
            child: const Text('取消'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(dialogCtx).pop(true),
            child: const Text('跳转'),
          ),
        ],
      ),
    );
    if (ok == true && context.mounted) {
      Navigator.of(context).pop(); // 收起答题卡
      onJump(index);
    }
  }
}

/// 单个题号格子
class _Cell extends StatelessWidget {
  const _Cell({
    required this.index,
    required this.grade,
    required this.isCurrent,
    required this.onTap,
  });

  final int index;
  final Grade? grade;
  final bool isCurrent;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final Color bg;
    final Color fg;
    if (grade == Grade.correct) {
      bg = _AnswerSheet._greenBg;
      fg = _AnswerSheet._greenFg;
    } else if (grade == Grade.wrong || grade == Grade.partial) {
      bg = _AnswerSheet._redBg;
      fg = _AnswerSheet._redFg;
    } else {
      bg = _AnswerSheet._greyBg;
      fg = _AnswerSheet._greyFg;
    }
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: bg,
          borderRadius: BorderRadius.circular(8),
          border: isCurrent
              ? Border.all(color: _AnswerSheet._currentBorder, width: 2)
              : Border.all(color: Colors.transparent),
        ),
        child: Text(
          '${index + 1}',
          style: theme.textTheme.labelMedium?.copyWith(
            color: fg,
            fontWeight: isCurrent ? FontWeight.w500 : FontWeight.w400,
          ),
        ),
      ),
    );
  }
}

/// 刷题完成结算页（设计：正确率环 + 统计 + 完成；答题卡整轮回顾入口）
