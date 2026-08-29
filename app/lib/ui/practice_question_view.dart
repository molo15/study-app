part of 'practice_page.dart';

class _QuestionView extends StatelessWidget {
  const _QuestionView({
    required this.reduceMotion,
    required this.question,
    required this.selection,
    required this.submitted,
    required this.grade,
    required this.index,
    required this.total,
    required this.flagged,
    required this.showFlag,
    required this.onToggleFlag,
    required this.showRating,
    required this.showRemoveWrong,
    required this.onSelect,
    required this.onSubmit,
    required this.onFreeSubmit,
    required this.onRate,
    required this.onRemoveWrong,
  });

  /// 减少动效（P0 手感优化）
  final bool reduceMotion;

  final Question question;
  final Set<String> selection;
  final bool submitted;
  final Grade grade;
  final int index;
  final int total;
  final bool flagged;

  /// 审题标记开关（关闭时隐藏旗子，默认关）
  final bool showFlag;
  final Future<void> Function() onToggleFlag;
  final bool showRating;
  final bool showRemoveWrong;
  final void Function(String) onSelect;
  final void Function() onSubmit;
  final void Function(List<String>) onFreeSubmit;
  final Future<void> Function(Rating) onRate;
  final Future<void> Function() onRemoveWrong;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final tc = typeColor(context, question.type);
    // 判断题选项单一数据源：库里无 options 时回退固定「正确/错误」
    // （审查 P0-1/P1-A：避免与 seed 补齐的 options 双渲染）
    final tfOptions =
        question.type == QuestionType.trueFalse && question.options.isEmpty
        ? const [
            QuestionOption(key: '正确', text: '正确'),
            QuestionOption(key: '错误', text: '错误'),
          ]
        : question.options;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // 题型徽章 + 章节 + 进度
        Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: tc.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                typeLabel(question.type),
                style: theme.textTheme.labelMedium?.copyWith(
                  color: tc,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                question.chapter,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.outline,
                ),
                overflow: TextOverflow.ellipsis,
              ),
            ),
            // 稳定题号（供审题反馈定位）；加 ellipsis 防窄屏溢出
            Flexible(
              child: Text(
                question.id.split(':').last,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: theme.textTheme.labelSmall?.copyWith(
                  color: theme.colorScheme.outlineVariant,
                  fontFamily: 'monospace',
                ),
              ),
            ),
            if (showFlag) ...[
              const SizedBox(width: 6),
              // 审题标记按钮（v7）
              IconButton(
                tooltip: flagged ? '取消标记' : '标记为待修改',
                visualDensity: VisualDensity.compact,
                iconSize: 20,
                color: flagged
                    ? Theme.of(context).colorScheme.error
                    : theme.colorScheme.outline,
                icon: Icon(flagged ? Icons.flag : Icons.flag_outlined),
                onPressed: onToggleFlag,
              ),
            ],
            const SizedBox(width: 4),
            Text(
              '$index / $total',
              style: theme.textTheme.labelMedium?.copyWith(
                color: theme.colorScheme.outline,
              ),
            ),
          ],
        ),
        const SizedBox(height: 20),
        // 题干（titleLarge + 行高 1.6，与选项区间距 20dp，设计方案 §3.4）
        Text(
          question.stem,
          style: theme.textTheme.titleLarge?.copyWith(
            height: 1.6,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 20),
        // 判断题选项（合并单一数据源，审查 P1-A）
        for (final option in tfOptions)
          _OptionTile(
            option: option,
            question: question,
            selected: selection.contains(option.key),
            submitted: submitted,
            reduceMotion: reduceMotion,
            onTap: () => onSelect(option.key),
          ),
        for (final type in [QuestionType.blank, QuestionType.shortAnswer])
          if (question.type == type)
            _FreeAnswerField(
              // 按题目重建输入框，避免相邻自由作答题串题（审查 P1-5）
              key: ValueKey('answer-${question.id}'),
              question: question,
              submitted: submitted,
              onSubmit: onFreeSubmit,
            ),
        const SizedBox(height: 20),
        if (submitted) ...[
          _ResultCard(question: question, grade: grade, reduceMotion: reduceMotion),
          const SizedBox(height: 16),
          if (showRating) ...[
            Text(
              '记住效果',
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                for (final (rating, label) in const [
                  (Rating.again, '重来'),
                  (Rating.hard, '困难'),
                  (Rating.good, '良好'),
                  (Rating.easy, '简单'),
                ])
                  Expanded(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 3),
                      child: FilledButton.tonal(
                        style: FilledButton.styleFrom(
                          backgroundColor: _semantic(
                            context,
                            switch (rating) {
                              Rating.again => _kError,
                              Rating.hard => _kWarning,
                              _ => _kSuccess,
                            },
                            switch (rating) {
                              Rating.again => _kErrorDark,
                              Rating.hard => _kWarningDark,
                              _ => _kSuccessDark,
                            },
                          ).withValues(alpha: 0.12),
                          foregroundColor: _semantic(
                            context,
                            switch (rating) {
                              Rating.again => _kError,
                              Rating.hard => _kWarning,
                              _ => _kSuccess,
                            },
                            switch (rating) {
                              Rating.again => _kErrorDark,
                              Rating.hard => _kWarningDark,
                              _ => _kSuccessDark,
                            },
                          ),
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          // 四档评分按钮统一最小高度 48dp（设计方案 §4.4）
                          minimumSize: const Size(0, 48),
                        ),
                        onPressed: () => onRate(rating),
                        child: Text(label),
                      ),
                    ),
                  ),
              ],
            ),
            if (showRemoveWrong) ...[
              const SizedBox(height: 8),
              Center(
                child: TextButton.icon(
                  onPressed: onRemoveWrong,
                  icon: const Icon(Icons.delete_outline, size: 18),
                  label: const Text('移出错题本'),
                ),
              ),
            ],
          ],
        ] else
          FilledButton.icon(
            onPressed: selection.isEmpty ? null : onSubmit,
            style: FilledButton.styleFrom(
              minimumSize: const Size.fromHeight(48),
            ),
            icon: const Icon(Icons.check),
            label: const Text('提交'),
          ),
      ],
    );
  }
}

class _OptionTile extends StatefulWidget {
  const _OptionTile({
    required this.option,
    required this.question,
    required this.selected,
    required this.submitted,
    required this.reduceMotion,
    required this.onTap,
  });

  final QuestionOption option;
  final Question question;
  final bool selected;
  final bool submitted;
  final bool reduceMotion;
  final VoidCallback onTap;

  @override
  State<_OptionTile> createState() => _OptionTileState();
}

class _OptionTileState extends State<_OptionTile>
    with SingleTickerProviderStateMixin {
  late final AnimationController _shakeCtrl;

  @override
  void initState() {
    super.initState();
    _shakeCtrl = AnimationController(vsync: this, duration: AppAnim.shake);
  }

  @override
  void didUpdateWidget(covariant _OptionTile oldWidget) {
    super.didUpdateWidget(oldWidget);
    final isCorrect = widget.question.answer.contains(widget.option.key);
    if (!oldWidget.submitted &&
        widget.submitted &&
        widget.selected &&
        !isCorrect &&
        !widget.reduceMotion) {
      _shakeCtrl.forward(from: 0);
    }
  }

  @override
  void dispose() {
    _shakeCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isChoice = widget.question.type == QuestionType.singleChoice ||
        widget.question.type == QuestionType.multiChoice ||
        widget.question.type == QuestionType.trueFalse;
    final isCorrect = widget.question.answer.contains(widget.option.key);

    Color? borderColor;
    Color? fillColor;
    IconData? trailing;
    if (isChoice && widget.submitted) {
      if (isCorrect) {
        borderColor = _semantic(context, _kSuccess, _kSuccessDark);
        fillColor = borderColor.withValues(alpha: 0.08);
        trailing = Icons.check_circle;
      } else if (widget.selected) {
        borderColor = _semantic(context, _kError, _kErrorDark);
        fillColor = borderColor.withValues(alpha: 0.06);
        trailing = Icons.cancel;
      }
    } else if (isChoice && widget.selected && !widget.submitted) {
      borderColor = theme.colorScheme.primary;
      fillColor = theme.colorScheme.primary.withValues(alpha: 0.14);
    }

    // P0 手感：错误选中时水平抖动（sin 波 × 4px，衰减）
    final shakeDx = widget.reduceMotion
        ? 0.0
        : _shakeCtrl.value == 0
            ? 0.0
            : (1 - _shakeCtrl.value) * 4 * math.sin(_shakeCtrl.value * 3 * math.pi);
    // P0 手感：判题正确→1.03 弹性放大；选中未提交→1.01 微弹
    final scale = widget.submitted && isCorrect
        ? (widget.reduceMotion ? 1.0 : 1.03)
        : (widget.selected && !widget.submitted ? 1.01 : 1.0);
    final scaleCurve =
        widget.submitted && isCorrect ? AppAnim.elastic : AppAnim.standard;

    return Transform.translate(
      offset: Offset(shakeDx, 0),
      child: AnimatedScale(
        scale: scale,
        duration: widget.reduceMotion ? Duration.zero : AppAnim.grade,
        curve: scaleCurve,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          curve: Curves.easeOut,
          margin: const EdgeInsets.symmetric(vertical: 5),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: borderColor ?? theme.colorScheme.outlineVariant,
              width: borderColor == null ? 1 : 1.8,
            ),
          ),
          child: Material(
            color: fillColor ?? Colors.transparent,
            borderRadius: BorderRadius.circular(13),
            child: ConstrainedBox(
              constraints: const BoxConstraints(minHeight: 52),
              child: ListTile(
                leading: isChoice
                    ? Icon(
                        widget.selected
                            ? Icons.check_circle_outlined
                            : Icons.circle_outlined,
                        color: widget.selected
                            ? (borderColor ?? theme.colorScheme.primary)
                            : theme.colorScheme.outline,
                      )
                    : null,
                title: Text(
                  widget.question.type == QuestionType.trueFalse
                      ? widget.option.text
                      : '${widget.option.key}. ${widget.option.text}',
                  style: TextStyle(
                    fontWeight:
                        widget.selected && !widget.submitted ? FontWeight.w600 : null,
                  ),
                ),
                trailing: trailing == null
                    ? null
                    : Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          if (trailing == Icons.check_circle) ...[
                            Text('正确',
                                style: theme.textTheme.labelMedium?.copyWith(
                                    color: borderColor, fontWeight: FontWeight.w700)),
                            const SizedBox(width: 4),
                          ] else if (trailing == Icons.cancel) ...[
                            Text('错误',
                                style: theme.textTheme.labelMedium?.copyWith(
                                    color: borderColor, fontWeight: FontWeight.w700)),
                            const SizedBox(width: 4),
                          ],
                          Icon(trailing, color: borderColor, size: 20),
                        ],
                      ),
                onTap: widget.onTap,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// 填空/简答的自由作答区（P2：填空多空按空数生成多个输入框）
class _FreeAnswerField extends StatefulWidget {
  const _FreeAnswerField({
    super.key,
    required this.question,
    required this.submitted,
    required this.onSubmit,
  });

  final Question question;
  final bool submitted;

  /// 提交所有输入框文本（填空多空按序；简答单框）
  final void Function(List<String>) onSubmit;

  @override
  State<_FreeAnswerField> createState() => _FreeAnswerFieldState();
}

class _FreeAnswerFieldState extends State<_FreeAnswerField> {
  late final List<TextEditingController> _controllers;

  /// 空数：填空且存在等价答案分组时按组数生成多框；否则单框（简答/单空填空）
  int get _slotCount {
    if (widget.question.type != QuestionType.blank) return 1;
    final variants = widget.question.answerVariants;
    if (variants.isNotEmpty) return variants.length;
    return 1;
  }

  @override
  void initState() {
    super.initState();
    _controllers = List.generate(_slotCount, (_) => TextEditingController());
  }

  @override
  void dispose() {
    for (final c in _controllers) {
      c.dispose();
    }
    super.dispose();
  }

  void _submit() {
    final texts = _controllers.map((c) => c.text.trim()).toList();
    if (texts.every((t) => t.isEmpty)) return;
    widget.onSubmit(texts);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isShortAnswer = widget.question.type == QuestionType.shortAnswer;
    final multiSlot = _slotCount > 1;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 答题格式提示（v3：answerFormat，如名解/翻译/论述的作答格式）
        if (isShortAnswer &&
            (widget.question.answerFormat?.isNotEmpty ?? false))
          Container(
            margin: const EdgeInsets.only(bottom: 8),
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: theme.colorScheme.primaryContainer.withValues(alpha: 0.5),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  Icons.lightbulb_outline,
                  size: 16,
                  color: theme.colorScheme.onPrimaryContainer,
                ),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    widget.question.answerFormat!,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onPrimaryContainer,
                      height: 1.4,
                    ),
                  ),
                ),
              ],
            ),
          ),
        if (multiSlot)
          Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Text(
              '共 $_slotCount 空 · 逐空填写，全部填完再提交',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.outline,
              ),
            ),
          ),
        for (var i = 0; i < _controllers.length; i++) ...[
          if (i > 0) const SizedBox(height: 8),
          TextField(
            controller: _controllers[i],
            enabled: !widget.submitted,
            minLines: isShortAnswer ? 3 : 1,
            maxLines: isShortAnswer ? 5 : 1,
            decoration: InputDecoration(
              labelText: multiSlot ? '第 ${i + 1} 空' : null,
              hintText: isShortAnswer ? '作答后点击「作答完成」进入判分' : '填写答案',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              filled: true,
              // 深色模式适配（UI 复审 P0-1）：用主题表面色而非纯白
              fillColor: Theme.of(context).colorScheme.surfaceContainerHighest,
            ),
          ),
        ],
        const SizedBox(height: 8),
        if (!widget.submitted)
          Align(
            alignment: Alignment.centerLeft,
            child: FilledButton.tonal(
              onPressed: _submit,
              style: FilledButton.styleFrom(minimumSize: const Size(0, 48)),
              child: Text(isShortAnswer ? '作答完成' : '填入答案'),
            ),
          ),
      ],
    );
  }
}
/// 判分与解析卡片（左侧色条，含来源出处展示）
/// P0 手感：提交后从底部滑入 + 淡入
class _ResultCard extends StatelessWidget {
  const _ResultCard(
      {required this.question, required this.grade, required this.reduceMotion});

  final Question question;
  final Grade grade;
  final bool reduceMotion;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final (color, label, icon) = switch (grade) {
      Grade.correct => (
        _semantic(context, _kSuccess, _kSuccessDark),
        '回答正确',
        Icons.check_circle,
      ),
      Grade.partial => (
        _semantic(context, _kWarning, _kWarningDark),
        '部分正确',
        Icons.help_outline,
      ),
      Grade.wrong => (
        _semantic(context, _kError, _kErrorDark),
        '回答错误',
        Icons.cancel,
      ),
      Grade.skip => (
        Theme.of(context).colorScheme.outline,
        '未作答',
        Icons.help_outline,
      ),
    };
    final sourceText = [
      if (question.sourceDocPath != null && question.sourceDocPath!.isNotEmpty)
        '出处：${question.sourceDocPath}',
      if (question.sourceBlockId != null && question.sourceBlockId!.isNotEmpty)
        '块 ${question.sourceBlockId}',
    ].join(' · ');
    final card = Container(
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: color.withValues(alpha: 0.4), width: 1),
      ),
      child: IntrinsicHeight(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Container(
              width: 5,
              decoration: BoxDecoration(
                color: color,
                borderRadius:
                    const BorderRadius.horizontal(left: Radius.circular(14)),
              ),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(children: [
                      Icon(icon, color: color, size: 20),
                      const SizedBox(width: 6),
                      Text(label,
                          style: theme.textTheme.titleSmall?.copyWith(
                              color: color, fontWeight: FontWeight.w700)),
                    ]),
                    const SizedBox(height: 8),
                    if (question.type == QuestionType.singleChoice ||
                        question.type == QuestionType.trueFalse ||
                        question.type == QuestionType.multiChoice)
                      Text('正确答案：${question.answer.join('、')}',
                          style: theme.textTheme.bodyMedium
                              ?.copyWith(fontWeight: FontWeight.w600)),
                    if (question.type == QuestionType.blank ||
                        question.type == QuestionType.shortAnswer)
                      Text('参考答案：${question.answer.join('；')}',
                          style: theme.textTheme.bodyMedium
                              ?.copyWith(fontWeight: FontWeight.w600)),
                    const SizedBox(height: 8),
                    if (question.explanation.isNotEmpty)
                      Text('解析：${question.explanation}',
                          style: theme.textTheme.bodyMedium?.copyWith(height: 1.5)),
                    if (sourceText.isNotEmpty) ...[
                      const SizedBox(height: 8),
                      Text(sourceText,
                          style: theme.textTheme.bodySmall
                              ?.copyWith(color: theme.colorScheme.outline)),
                    ],
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
    // P0 手感：滑入 + 淡入（reduceMotion 时直接显示）
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: reduceMotion ? Duration.zero : AppAnim.slideIn,
      curve: AppAnim.standard,
      builder: (context, value, child) => Opacity(
        opacity: value,
        child: Transform.translate(
          offset: Offset(0, (1 - value) * 24),
          child: child,
        ),
      ),
      child: card,
    );
  }
}

/// 结算页：本次正确率/知识点分布
/// 答题卡弹层（设计：按题型分区展示本轮作答，红绿灰三态，点格子确认后跳题）
