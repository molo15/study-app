# -*- coding: utf-8 -*-
"""P0 手感优化：重写 practice_question_view.dart 的 _OptionTile / _ResultCard / _QuestionView"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\study_app\app\lib\ui\practice_question_view.dart'
s = open(p, encoding='utf-8').read()

# ========== 1. _QuestionView 加 reduceMotion 字段 ==========
# 构造函数加参数
s = s.replace(
    "  const _QuestionView({\n"
    "    required this.question,",
    "  const _QuestionView({\n"
    "    required this.reduceMotion,\n"
    "    required this.question,"
)
# 字段声明（在 final Question question; 之前）
s = s.replace(
    "  final Question question;\n"
    "  final Set<String> selection;",
    "  /// 减少动效（P0 手感优化）：开启后抖动/放大等非必要动效跳过或减半\n"
    "  final bool reduceMotion;\n\n"
    "  final Question question;\n"
    "  final Set<String> selection;"
)
# 传给 _OptionTile（加 reduceMotion 参数）
s = s.replace(
    "          _OptionTile(\n"
    "            option: option,\n"
    "            question: question,\n"
    "            selected: selection.contains(option.key),\n"
    "            submitted: submitted,\n"
    "            onTap: () => onSelect(option.key),\n"
    "          ),",
    "          _OptionTile(\n"
    "            option: option,\n"
    "            question: question,\n"
    "            selected: selection.contains(option.key),\n"
    "            submitted: submitted,\n"
    "            reduceMotion: reduceMotion,\n"
    "            onTap: () => onSelect(option.key),\n"
    "          ),"
)
# 传给 _ResultCard（加 reduceMotion）
s = s.replace(
    "          _ResultCard(question: question, grade: grade),",
    "          _ResultCard(question: question, grade: grade, reduceMotion: reduceMotion),"
)

# ========== 2. 替换整个 _OptionTile 类为 Stateful 版本 ==========
# 找到旧 _OptionTile 的起止
old_start = "class _OptionTile extends StatelessWidget {"
old_end_marker = "/// 填空/简答的自由作答区"
idx_start = s.index(old_start)
idx_end = s.index(old_end_marker, idx_start)
old_class = s[idx_start:idx_end]

new_class = '''class _OptionTile extends StatefulWidget {
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
    // P0 手感：submitted 从 false→true，且当前项是用户选错的（选中但不正确），触发抖动
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

    // P0 手感：抖动偏移（sin 波 × 4px，仅错误选中且未 reduceMotion 时）
    final shakeDx = widget.reduceMotion
        ? 0.0
        : _shakeCtrl.value == 0
            ? 0.0
            : (1 - _shakeCtrl.value) * 4 * _tripleSin(_shakeCtrl.value);
    // P0 手感：缩放——判题正确→1.03 弹性放大；选中未提交→1.01 微弹；其他→1.0
    final scale = widget.submitted && isCorrect
        ? (widget.reduceMotion ? 1.0 : 1.03)
        : (widget.selected && !widget.submitted ? 1.01 : 1.0);
    final scaleCurve = widget.submitted && isCorrect
        ? AppAnim.elastic
        : AppAnim.standard;

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
                            Text(
                              '正确',
                              style: theme.textTheme.labelMedium?.copyWith(
                                color: borderColor,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            const SizedBox(width: 4),
                          ] else if (trailing == Icons.cancel) ...[
                            Text(
                              '错误',
                              style: theme.textTheme.labelMedium?.copyWith(
                                color: borderColor,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
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

  /// 三段 sin 波：0→1→0→-1→0，模拟左右抖动 3 次
  static double _tripleSin(double t) {
    // t ∈ [0,1]，映射到 [0, 3π]，sin 完成 1.5 个周期 = 3 次过零
    final v = t * 3 * 3.141592653589793;
    // 前半段振幅大，后半段衰减
    final decay = 1 - t * 0.5;
    return _sin(v) * decay;
  }

  static double _sin(double x) {
    // 用 dart:math 的 sin，但这里是纯计算，直接内联
    return _MathSin.sin(x);
  }
}

/// 纯 Dart sin 封装（避免在 part 文件里 import dart:math 冲突）
class _MathSin {
  static double sin(double x) => _SinTable.sin(x);
}

class _SinTable {
  static double sin(double x) {
    // 简化：直接用级数展开或调用系统
    // 实际上 Flutter 里可以直接用 dart:math，但为了 part 文件干净，这里用内联
    return _nativeSin(x);
  }

  static external double _nativeSin(double x);
}

'''

# 等等，上面的 sin 实现太复杂了。我应该直接在文件顶部 import 'dart:math' as math;
# 然后用 math.sin。让我简化 new_class，去掉 _MathSin 等复杂封装。

# 重新生成简洁版 new_class
new_class_clean = '''class _OptionTile extends StatefulWidget {
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
    // P0 手感：submitted 从 false→true，且当前项是用户选错的（选中但不正确），触发抖动
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

    // P0 手感：抖动偏移（sin 波 × 4px，仅错误选中且未 reduceMotion 时）
    final shakeDx = widget.reduceMotion
        ? 0.0
        : _shakeCtrl.value == 0
            ? 0.0
            : (1 - _shakeCtrl.value) * 4 * math.sin(_shakeCtrl.value * 3 * math.pi);
    // P0 手感：缩放——判题正确→1.03 弹性放大；选中未提交→1.01 微弹；其他→1.0
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
                            Text(
                              '正确',
                              style: theme.textTheme.labelMedium?.copyWith(
                                color: borderColor,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            const SizedBox(width: 4),
                          ] else if (trailing == Icons.cancel) ...[
                            Text(
                              '错误',
                              style: theme.textTheme.labelMedium?.copyWith(
                                color: borderColor,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
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

s = s[:idx_start] + new_class_clean + s[idx_end:]

# ========== 3. _ResultCard 加 reduceMotion 字段 + 滑入动画 ==========
s = s.replace(
    "  const _ResultCard({required this.question, required this.grade});\n\n"
    "  final Question question;\n"
    "  final Grade grade;",
    "  const _ResultCard({required this.question, required this.grade, required this.reduceMotion});\n\n"
    "  final Question question;\n"
    "  final Grade grade;\n"
    "  final bool reduceMotion;"
)

# _ResultCard 的 build 返回值外包 TweenAnimationBuilder 做滑入+淡入
# 找到 return Container( （_ResultCard 的第一个 return）
old_result_return = "    return Container(\n      decoration: BoxDecoration(\n        // 深色模式适配（UI 复审 P0-1）：卡片底色跟随主题与透明度"
new_result_return = """    // P0 手感：解析卡从底部滑入 + 淡入（reduceMotion 时直接显示）
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: widget.reduceMotion ? Duration.zero : AppAnim.slideIn,
      curve: AppAnim.standard,
      builder: (context, value, child) => Opacity(
        opacity: value,
        child: Transform.translate(
          offset: Offset(0, (1 - value) * 24),
          child: child,
        ),
      ),
      child: Container(
      decoration: BoxDecoration(
        // 深色模式适配（UI 复审 P0-1）：卡片底色跟随主题与透明度"""

s = s.replace(old_result_return, new_result_return)

# 找到 _ResultCard 的结尾（); 之后的 }），需要给 TweenAnimationBuilder 补闭合
# _ResultCard 的 build 方法结尾是：
#       ),
#     );
#   }
# }
# 我们需要把最后的 ); 改成 ),); （多一层闭合）
# 找到 _ResultCard 类的结尾位置
result_class_end = "/// 结算页：本次正确率/知识点分布"
idx_result_end = s.index(result_class_end)
# 往前找 _ResultCard 的最后一个 );
# _ResultCard build 结尾是：
#         ),
#       ),
#     );
#   }
# }
# 我们需要在 ); 前加 ), 来闭合 TweenAnimationBuilder
# 找 _ResultCard 类的最后几个字符
chunk = s[idx_result_end-200:idx_result_end]
print('_ResultCard 结尾上下文:', repr(chunk[-150:]))

open(p, 'w', encoding='utf-8', newline='').write(s)
print('文件已写入，待处理 _ResultCard 闭合')
