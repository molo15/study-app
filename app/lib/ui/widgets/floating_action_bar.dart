/// V3 iOS 底部悬浮操作栏
///
/// 三种状态：
/// - 答题：上一题/进度/下一题（含答题卡入口）
/// - 背题：忘记/环形进度/记住（含显示答案）
/// - 模拟考：上一题/进度/交卷（含标记）
///
/// 液态玻璃材质（thin 模糊 18），安全区适配。
/// 宽度规则与 Tab Bar 一致：compact 宽−48，medium 宽−64 上限 680。
library;

import 'package:flutter/material.dart';

import '../theme/ios_animations.dart';
import '../theme/ios_tokens.dart';
import 'liquid_glass.dart';

/// 操作栏模式
enum FloatingActionBarMode {
  /// 答题模式：上一题 / 进度 / 下一题
  practice,

  /// 背题模式：忘记 / 进度 / 记住（或显示答案）
  memorize,

  /// 模拟考模式：上一题 / 进度 / 交卷
  exam,
}

class FloatingActionBar extends StatelessWidget {
  const FloatingActionBar({
    super.key,
    required this.mode,
    this.leftLabel = '上一题',
    this.rightLabel = '下一题',
    this.centerWidget,
    this.centerText,
    this.onLeft,
    this.onRight,
    this.leftEnabled = true,
    this.rightEnabled = true,
    this.hidden = false,
    this.showAnswerSheet = false,
    this.onAnswerSheet,
  });

  /// 操作栏模式
  final FloatingActionBarMode mode;

  /// 左侧按钮文字
  final String leftLabel;

  /// 右侧按钮文字
  final String rightLabel;

  /// 中央自定义 widget（如环形进度）
  final Widget? centerWidget;

  /// 中央文字（如 "12 / 50"）
  final String? centerText;

  /// 左侧按钮回调
  final VoidCallback? onLeft;

  /// 右侧按钮回调
  final VoidCallback? onRight;

  /// 左侧是否启用
  final bool leftEnabled;

  /// 右侧是否启用
  final bool rightEnabled;

  /// 是否隐藏
  final bool hidden;

  /// 是否显示答题卡入口（答题模式）
  final bool showAnswerSheet;

  /// 答题卡入口回调
  final VoidCallback? onAnswerSheet;

  @override
  Widget build(BuildContext context) {
    final layout = _BarLayoutInfo.of(context);
    final anim = IOSAnimations.of(context);
    final dark = Theme.of(context).brightness == Brightness.dark;
    final colors = dark ? IOSColors.dark : IOSColors.light;

    final horizontalInset = layout.isCompact
        ? IOSBreakpoint.compactBarHorizontalInset
        : IOSBreakpoint.mediumBarHorizontalInset;
    final barWidth = (layout.width - horizontalInset).clamp(
      0.0,
      IOSBreakpoint.floatingBarMaxWidth,
    );

    final safeBottom = MediaQuery.paddingOf(context).bottom;

    // 按模式确定右侧按钮颜色
    final rightBgColor = switch (mode) {
      FloatingActionBarMode.practice => colors.primary,
      FloatingActionBarMode.memorize => colors.success,
      FloatingActionBarMode.exam => colors.success,
    };
    final rightFgColor = Colors.white;

    // 左侧按钮颜色
    final leftFgColor = switch (mode) {
      FloatingActionBarMode.memorize => colors.danger,
      _ => colors.text2,
    };

    return AnimatedSlide(
      offset: hidden ? const Offset(0, 1.5) : Offset.zero,
      duration: anim.effectiveDuration(IOSDuration.standard),
      curve: anim.effectiveCurve(IOSCurve.standard),
      child: AnimatedOpacity(
        opacity: hidden ? 0 : 1,
        duration: anim.effectiveDuration(IOSDuration.fast),
        child: Padding(
          padding: EdgeInsets.only(
            bottom: IOSFloatingBar.bottomOffset + safeBottom,
          ),
          child: Align(
            alignment: Alignment.bottomCenter,
            child: SizedBox(
              width: barWidth,
              height: IOSFloatingBar.actionBarHeight,
              child: LiquidGlass(
                variant: LiquidGlassVariant.thin,
                borderRadius: BorderRadius.circular(IOSRadius.pill),
                padding: const EdgeInsets.only(left: IOSSpacing.s16, right: IOSSpacing.s8),
                child: Row(
                  children: [
                    // 左侧按钮
                    _BarTextButton(
                      label: leftLabel,
                      onTap: leftEnabled ? onLeft : null,
                      fgColor: leftFgColor,
                      disabledColor: colors.placeholder,
                    ),
                    // 中央
                    Expanded(
                      child: Center(
                        child: centerWidget ??
                            (centerText != null
                                ? Text(
                                    centerText!,
                                    style: TextStyle(
                                      fontSize: IOSFontSize.subheadline,
                                      color: colors.text2,
                                      fontFamily: 'SF Mono',
                                      letterSpacing: 0.03 * IOSFontSize.subheadline,
                                    ),
                                  )
                                : const SizedBox.shrink()),
                      ),
                    ),
                    // 答题卡入口（答题模式）
                    if (showAnswerSheet && mode == FloatingActionBarMode.practice)
                      _BarIconButton(
                        icon: Icons.grid_view,
                        onTap: onAnswerSheet,
                        fgColor: colors.text2,
                      ),
                    // 右侧按钮
                    _BarFilledButton(
                      label: rightLabel,
                      onTap: rightEnabled ? onRight : null,
                      bgColor: rightBgColor,
                      fgColor: rightFgColor,
                      pressedColor: colors.primaryPressed,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// 文字按钮（左侧）
class _BarTextButton extends StatefulWidget {
  const _BarTextButton({
    required this.label,
    required this.onTap,
    required this.fgColor,
    required this.disabledColor,
  });

  final String label;
  final VoidCallback? onTap;
  final Color fgColor;
  final Color disabledColor;

  @override
  State<_BarTextButton> createState() => _BarTextButtonState();
}

class _BarTextButtonState extends State<_BarTextButton> {
  bool _pressed = false;

  @override
  Widget build(BuildContext context) {
    final anim = IOSAnimations.of(context);
    final enabled = widget.onTap != null;
    final color = enabled
        ? (_pressed ? widget.fgColor.withValues(alpha: 0.6) : widget.fgColor)
        : widget.disabledColor;

    return GestureDetector(
      onTapDown: (_) {
        if (enabled) setState(() => _pressed = true);
      },
      onTapUp: (_) {
        if (enabled) setState(() => _pressed = false);
      },
      onTapCancel: () {
        if (enabled) setState(() => _pressed = false);
      },
      onTap: widget.onTap,
      behavior: HitTestBehavior.opaque,
      child: AnimatedContainer(
        duration: anim.effectiveDuration(IOSDuration.fast),
        curve: anim.effectiveCurve(IOSCurve.press),
        height: 36,
        padding: const EdgeInsets.symmetric(horizontal: IOSSpacing.s12),
        decoration: BoxDecoration(
          color: _pressed ? IOSColors.light.fill : Colors.transparent,
          borderRadius: BorderRadius.circular(IOSRadius.xs),
        ),
        alignment: Alignment.center,
        child: Text(
          widget.label,
          style: TextStyle(
            fontSize: IOSFontSize.subheadline,
            color: color,
          ),
        ),
      ),
    );
  }
}

/// 图标按钮（答题卡入口）
class _BarIconButton extends StatefulWidget {
  const _BarIconButton({
    required this.icon,
    required this.onTap,
    required this.fgColor,
  });

  final IconData icon;
  final VoidCallback? onTap;
  final Color fgColor;

  @override
  State<_BarIconButton> createState() => _BarIconButtonState();
}

class _BarIconButtonState extends State<_BarIconButton> {
  bool _pressed = false;

  @override
  Widget build(BuildContext context) {
    final anim = IOSAnimations.of(context);

    return GestureDetector(
      onTapDown: (_) => setState(() => _pressed = true),
      onTapUp: (_) => setState(() => _pressed = false),
      onTapCancel: () => setState(() => _pressed = false),
      onTap: widget.onTap,
      behavior: HitTestBehavior.opaque,
      child: AnimatedContainer(
        duration: anim.effectiveDuration(IOSDuration.fast),
        curve: anim.effectiveCurve(IOSCurve.press),
        width: 36,
        height: 36,
        margin: const EdgeInsets.symmetric(horizontal: 4),
        decoration: BoxDecoration(
          color: _pressed ? IOSColors.light.fill : Colors.transparent,
          borderRadius: BorderRadius.circular(IOSRadius.xs),
        ),
        alignment: Alignment.center,
        child: Icon(widget.icon, size: 20, color: widget.fgColor),
      ),
    );
  }
}

/// 填充按钮（右侧：下一题/记住/交卷）
class _BarFilledButton extends StatefulWidget {
  const _BarFilledButton({
    required this.label,
    required this.onTap,
    required this.bgColor,
    required this.fgColor,
    required this.pressedColor,
  });

  final String label;
  final VoidCallback? onTap;
  final Color bgColor;
  final Color fgColor;
  final Color pressedColor;

  @override
  State<_BarFilledButton> createState() => _BarFilledButtonState();
}

class _BarFilledButtonState extends State<_BarFilledButton> {
  bool _pressed = false;

  @override
  Widget build(BuildContext context) {
    final anim = IOSAnimations.of(context);
    final enabled = widget.onTap != null;
    final bg = enabled
        ? (_pressed ? widget.pressedColor : widget.bgColor)
        : widget.bgColor.withValues(alpha: 0.4);

    return GestureDetector(
      onTapDown: (_) {
        if (enabled) setState(() => _pressed = true);
      },
      onTapUp: (_) {
        if (enabled) setState(() => _pressed = false);
      },
      onTapCancel: () {
        if (enabled) setState(() => _pressed = false);
      },
      onTap: widget.onTap,
      behavior: HitTestBehavior.opaque,
      child: AnimatedScale(
        scale: _pressed ? 0.96 : 1.0,
        duration: anim.effectiveDuration(IOSDuration.fast),
        curve: anim.effectiveCurve(IOSCurve.press),
        child: Container(
          height: 36,
          padding: const EdgeInsets.symmetric(horizontal: IOSSpacing.s20),
          margin: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: bg,
            borderRadius: BorderRadius.circular(IOSRadius.xs),
          ),
          alignment: Alignment.center,
          child: Text(
            widget.label,
            style: TextStyle(
              fontSize: IOSFontSize.subheadline,
              fontWeight: FontWeight.w600,
              color: widget.fgColor,
            ),
          ),
        ),
      ),
    );
  }
}

/// 布局信息
class _BarLayoutInfo {
  const _BarLayoutInfo({required this.width, required this.isCompact});

  final double width;
  final bool isCompact;

  factory _BarLayoutInfo.of(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    return _BarLayoutInfo(
      width: w,
      isCompact: w < IOSBreakpoint.compactMax,
    );
  }
}
