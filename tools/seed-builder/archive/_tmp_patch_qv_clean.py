# -*- coding: utf-8 -*-
"""P0 手感优化：practice_question_view.dart 完整补丁（干净版）"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ===== 1. practice_page.dart 加 dart:math import =====
pp = r'D:\study_app\app\lib\ui\practice_page.dart'
sp = open(pp, encoding='utf-8').read()
if "import 'dart:math' as math;" not in sp:
    sp = sp.replace(
        "import 'dart:async';\nimport 'dart:convert';",
        "import 'dart:async';\nimport 'dart:convert';\nimport 'dart:math' as math;"
    )
    open(pp, 'w', encoding='utf-8', newline='').write(sp)
    print('practice_page.dart: 加 dart:math import')
else:
    print('practice_page.dart: dart:math 已存在')

# ===== 2. practice_question_view.dart =====
p = r'D:\study_app\app\lib\ui\practice_question_view.dart'
s = open(p, encoding='utf-8').read()

# --- 2a. _QuestionView 加 reduceMotion ---
s = s.replace(
    "  const _QuestionView({\n    required this.question,",
    "  const _QuestionView({\n    required this.reduceMotion,\n    required this.question,"
)
s = s.replace(
    "  final Question question;\n  final Set<String> selection;",
    "  /// 减少动效（P0 手感优化）\n  final bool reduceMotion;\n\n  final Question question;\n  final Set<String> selection;"
)
s = s.replace(
    "          _OptionTile(\n            option: option,\n            question: question,\n            selected: selection.contains(option.key),\n            submitted: submitted,\n            onTap: () => onSelect(option.key),\n          ),",
    "          _OptionTile(\n            option: option,\n            question: question,\n            selected: selection.contains(option.key),\n            submitted: submitted,\n            reduceMotion: reduceMotion,\n            onTap: () => onSelect(option.key),\n          ),"
)
s = s.replace(
    "          _ResultCard(question: question, grade: grade),",
    "          _ResultCard(question: question, grade: grade, reduceMotion: reduceMotion),"
)

# --- 2b. 替换整个 _OptionTile 类 ---
old_opt_start = "class _OptionTile extends StatelessWidget {"
old_opt_end = "/// 填空/简答的自由作答区"
idx_os = s.index(old_opt_start)
idx_oe = s.index(old_opt_end, idx_os)

new_option_tile = '''class _OptionTile extends StatefulWidget {
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

'''

s = s[:idx_os] + new_option_tile + s[idx_oe:]

# --- 2c. 替换整个 _ResultCard 类 ---
old_res_start = "/// 判分与解析卡片（左侧色条，含来源出处展示）\nclass _ResultCard extends StatelessWidget {"
old_res_end = "/// 结算页：本次正确率/知识点分布"
idx_rs = s.index(old_res_start)
idx_re = s.index(old_res_end, idx_rs)

new_result_card = '''/// 判分与解析卡片（左侧色条，含来源出处展示）
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

'''

s = s[:idx_rs] + new_result_card + s[idx_re:]

open(p, 'w', encoding='utf-8', newline='').write(s)
print('practice_question_view.dart: _OptionTile Stateful化 + _ResultCard 滑入 完成')
print('  _QuestionView reduceMotion:', 'required this.reduceMotion' in s)
print('  _OptionTile Stateful:', 'class _OptionTile extends StatefulWidget' in s)
print('  _ResultCard TweenAnimationBuilder:', 'TweenAnimationBuilder<double>' in s)
print('  math.sin 使用:', 'math.sin(' in s)
