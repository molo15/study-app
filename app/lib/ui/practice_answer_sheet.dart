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
                Text('答题卡',
                    style: IOSTypography.title3(
                        color: IOSColors.of(context).text)),
                const Spacer(),
                Padding(
                  padding: const EdgeInsets.only(right: 16),
                  child: Text(
                    '本轮 ${queue.length} 题',
                    style: IOSTypography.footnote(
                        color: IOSColors.of(context).text2),
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
                  // B4 审查修复：按题型分组 staggered 入场（每分组延迟 70ms）
                  for (final e in <QuestionType>[
                    QuestionType.singleChoice,
                    QuestionType.multiChoice,
                    QuestionType.trueFalse,
                    QuestionType.blank,
                    QuestionType.shortAnswer,
                  ].where((t) => queue.any((q) => q.type == t)).toList().indexed)
                    _StaggerIn(
                      index: e.$1,
                      child: _TypeSection(
                        type: e.$2,
                        queue: queue,
                        results: results,
                        currentIndex: currentIndex,
                        onJump: onJump,
                      ),
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
    final colors = IOSColors.of(context);
    return Expanded(
      child: Container(
        margin: const EdgeInsets.only(right: 8),
        padding: const EdgeInsets.symmetric(vertical: 10),
        decoration: BoxDecoration(
          color: colors.fill2,
          borderRadius: BorderRadius.circular(IOSRadius.sm),
        ),
        child: Column(
          children: [
            Text(
              '$value',
              style: IOSTypography.title2(color: valueColor ?? colors.text)
                  .copyWith(fontWeight: FontWeight.w600),
            ),
            Text(
              label,
              style: IOSTypography.caption1(color: colors.text2),
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
    final colors = IOSColors.of(context);
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
          style: IOSTypography.caption1(color: colors.text2),
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
                style: IOSTypography.title3(
                  color: IOSColors.of(context).text,
                ).copyWith(fontWeight: FontWeight.w600),
              ),
              Text(
                '${indices.length} 题 · 对 $correct 错 $wrong 未答 $unanswered',
                style: IOSTypography.footnote(
                  color: IOSColors.of(context).text2,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          LayoutBuilder(
            builder: (ctx, constraints) {
              // B2 审查修复：列数随容器宽度自适应（每格最小约 42pt）
              final cols = (constraints.maxWidth / 48).floor().clamp(4, 10);
              return GridView.count(
                crossAxisCount: cols,
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
              );
            },
          ),
        ],
      ),
    );
  }

  /// 点格子 → 确认弹窗 → 确认后收起并跳题
  Future<void> _confirmJump(BuildContext context, int index) async {
    final ok = await showIOSActionSheet<bool>(
      context: context,
      title: '跳转到第 ${index + 1} 题？',
      items: [
        IOSActionItem(
          value: true,
          title: '跳转',
          subtitle: '当前题未作答将保留为未答',
          icon: Icons.north_east,
        ),
      ],
      cancelLabel: '取消',
    );
    if (ok == true && context.mounted) {
      Navigator.of(context).pop(); // 收起答题卡
      onJump(index);
    }
  }
}

/// 单个题号格子
/// B2 审查修复：InkWell 水波纹 → 无涟漪按压（缩放 0.9 + 120ms）
class _Cell extends StatefulWidget {
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
  State<_Cell> createState() => _CellState();
}

class _CellState extends State<_Cell> {
  bool _pressed = false;

  @override
  Widget build(BuildContext context) {
    final grade = widget.grade;
    final isCurrent = widget.isCurrent;
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
    return GestureDetector(
      onTapDown: (_) => setState(() => _pressed = true),
      onTapUp: (_) => setState(() => _pressed = false),
      onTapCancel: () => setState(() => _pressed = false),
      onTap: widget.onTap,
      child: AnimatedScale(
        scale: _pressed ? 0.9 : 1.0,
        duration: const Duration(milliseconds: 120),
        curve: Curves.easeOut,
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
            '${widget.index + 1}',
            style: IOSTypography.caption1(color: fg).copyWith(
              fontWeight: isCurrent ? FontWeight.w600 : FontWeight.w400,
            ),
          ),
        ),
      ),
    );
  }
}

/// B4 审查修复：分组 stagger 入场动画（淡入 + 轻微上移，指数递增延迟）
class _StaggerIn extends StatefulWidget {
  const _StaggerIn({required this.index, required this.child});

  final int index;
  final Widget child;

  @override
  State<_StaggerIn> createState() => _StaggerInState();
}

class _StaggerInState extends State<_StaggerIn>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(
    vsync: this,
    duration: IOSDuration.standard,
  );

  @override
  void initState() {
    super.initState();
    if (widget.index == 0) {
      _controller.value = 1;
    } else {
      Future.delayed(Duration(milliseconds: 70 * widget.index), () {
        if (mounted) _controller.forward();
      });
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final anim = IOSAnimations.of(context);
    if (anim.reduceMotion) return widget.child;
    return FadeTransition(
      opacity: _controller.drive(CurveTween(curve: IOSCurve.fadeIn)),
      child: SlideTransition(
        position: _controller.drive(
          Tween<Offset>(
            begin: const Offset(0, 0.05),
            end: Offset.zero,
          ).chain(CurveTween(curve: IOSCurve.standard)),
        ),
        child: widget.child,
      ),
    );
  }
}

/// 刷题完成结算页（设计：正确率环 + 统计 + 完成；答题卡整轮回顾入口）
