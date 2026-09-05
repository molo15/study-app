/// V3 iOS 风格按钮
///
/// 四种类型：
/// - primary：蓝色填充
/// - text：纯文字
/// - icon：图标按钮
/// - danger：红色
///
/// 按压动效：scale(0.985) + 颜色变化，150ms，使用 ios_animations.dart 常量。
/// 支持 loading 状态、禁用状态。
library;

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

import '../theme/ios_animations.dart';
import '../theme/ios_tokens.dart';

/// 按钮类型
enum IOSButtonType { primary, text, icon, danger }

class IOSButton extends StatefulWidget {
  const IOSButton({
    super.key,
    required this.onPressed,
    this.label,
    this.icon,
    this.type = IOSButtonType.primary,
    this.loading = false,
    this.enabled = true,
    this.expand = false,
    this.height,
    this.padding,
    this.borderRadius,
    this.color,
    this.textColor,
  });

  /// 点击回调
  final VoidCallback? onPressed;

  /// 文字标签
  final String? label;

  /// 图标（icon 类型或 primary 带图标）
  final IconData? icon;

  /// 按钮类型
  final IOSButtonType type;

  /// loading 状态
  final bool loading;

  /// 是否启用
  final bool enabled;

  /// 是否撑满宽度
  final bool expand;

  /// 自定义高度
  final double? height;

  /// 自定义内边距
  final EdgeInsetsGeometry? padding;

  /// 自定义圆角
  final BorderRadius? borderRadius;

  /// 自定义背景色
  final Color? color;

  /// 自定义文字色
  final Color? textColor;

  @override
  State<IOSButton> createState() => _IOSButtonState();
}

class _IOSButtonState extends State<IOSButton>
    with SingleTickerProviderStateMixin {
  bool _pressed = false;
  late final IOSAnimations _anim;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _anim = IOSAnimations.of(context);
  }

  bool get _canPress => widget.enabled && !widget.loading && widget.onPressed != null;

  void _handleTapDown(TapDownDetails _) {
    if (!_canPress) return;
    setState(() => _pressed = true);
  }

  void _handleTapUp(TapUpDetails _) {
    if (!_canPress) return;
    setState(() => _pressed = false);
  }

  void _handleTapCancel() {
    if (!_canPress) return;
    setState(() => _pressed = false);
  }

  void _handleTap() {
    if (!_canPress) return;
    widget.onPressed?.call();
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final colors = dark ? IOSColors.dark : IOSColors.light;

    // 按类型确定样式
    final (bgColor, fgColor, pressedBg, defaultHeight, defaultPadding, defaultRadius) =
        switch (widget.type) {
      IOSButtonType.primary => (
          widget.color ?? colors.primary,
          widget.textColor ?? Colors.white,
          colors.primaryPressed,
          50.0,
          const EdgeInsets.symmetric(horizontal: IOSSpacing.s20, vertical: IOSSpacing.s12),
          BorderRadius.circular(IOSRadius.sm),
        ),
      IOSButtonType.text => (
          Colors.transparent,
          widget.textColor ?? colors.primary,
          colors.primaryBg,
          44.0,
          const EdgeInsets.symmetric(horizontal: IOSSpacing.s16),
          BorderRadius.circular(IOSRadius.xs),
        ),
      IOSButtonType.icon => (
          Colors.transparent,
          widget.textColor ?? colors.primary,
          colors.fill,
          40.0,
          EdgeInsets.zero,
          BorderRadius.circular(IOSRadius.xs),
        ),
      IOSButtonType.danger => (
          Colors.transparent,
          widget.textColor ?? colors.danger,
          colors.dangerBg,
          44.0,
          const EdgeInsets.symmetric(horizontal: IOSSpacing.s16),
          BorderRadius.circular(IOSRadius.xs),
        ),
    };

    final effectiveBg = _pressed ? pressedBg : bgColor;
    final effectiveFg = _canPress ? fgColor : colors.placeholder;
    final height = widget.height ?? defaultHeight;
    final padding = widget.padding ?? defaultPadding;
    final radius = widget.borderRadius ?? defaultRadius;

    // 按压缩放：0.985
    final scale = _pressed ? 0.985 : 1.0;

    Widget content;
    if (widget.loading) {
      content = CupertinoActivityIndicator(radius: 10, color: effectiveFg);
    } else if (widget.type == IOSButtonType.icon) {
      content = Icon(widget.icon, size: 22, color: effectiveFg);
    } else {
      final children = <Widget>[];
      if (widget.icon != null) {
        children.add(Icon(widget.icon, size: 18, color: effectiveFg));
        children.add(const SizedBox(width: IOSSpacing.s8));
      }
      if (widget.label != null) {
        children.add(Text(
          widget.label!,
          style: TextStyle(
            fontSize: IOSFontSize.body,
            fontWeight: widget.type == IOSButtonType.primary
                ? FontWeight.w600
                : FontWeight.w400,
            color: effectiveFg,
          ),
        ));
      }
      content = Row(
        mainAxisSize: MainAxisSize.min,
        mainAxisAlignment: MainAxisAlignment.center,
        children: children,
      );
    }

    final button = AnimatedScale(
      scale: scale,
      duration: _anim.effectiveDuration(IOSDuration.fast),
      curve: _anim.effectiveCurve(IOSCurve.press),
      child: AnimatedContainer(
        duration: _anim.effectiveDuration(IOSDuration.fast),
        curve: _anim.effectiveCurve(IOSCurve.press),
        height: height,
        padding: padding,
        decoration: BoxDecoration(
          color: effectiveBg,
          borderRadius: radius,
        ),
        alignment: Alignment.center,
        child: content,
      ),
    );

    final result = GestureDetector(
      onTapDown: _handleTapDown,
      onTapUp: _handleTapUp,
      onTapCancel: _handleTapCancel,
      onTap: _handleTap,
      behavior: HitTestBehavior.opaque,
      child: widget.expand ? SizedBox(width: double.infinity, child: button) : button,
    );

    return result;
  }
}
