/// V3 iOS 纯白无阴影卡片
///
/// 浅色 #FFFFFF / 深色 #2C2C2E
/// 圆角 16，无阴影（iOS 风格靠分组和间距区分层次）
/// 可选 0.5px 极淡边框。
///
/// B4 审查修复：onTap 增加 iOS 按压缩放反馈（AnimatedScale 0.98，IOSAnimations 令牌）。
library;

import 'package:flutter/material.dart';

import '../theme/ios_animations.dart';
import '../theme/ios_tokens.dart';

class IOSCard extends StatefulWidget {
  const IOSCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(IOSSpacing.s16),
    this.margin,
    this.borderRadius,
    this.showBorder = true,
    this.color,
    this.onTap,
    this.width,
    this.height,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;
  final EdgeInsetsGeometry? margin;
  final BorderRadius? borderRadius;
  final bool showBorder;
  final Color? color;
  final VoidCallback? onTap;
  final double? width;
  final double? height;

  @override
  State<IOSCard> createState() => _IOSCardState();
}

class _IOSCardState extends State<IOSCard> {
  bool _pressed = false;

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final colors = dark ? IOSColors.dark : IOSColors.light;
    final radius = widget.borderRadius ?? BorderRadius.circular(IOSRadius.md);
    final anim = IOSAnimations.of(context);

    final card = Container(
      width: widget.width,
      height: widget.height,
      padding: widget.padding,
      decoration: BoxDecoration(
        color: widget.color ?? colors.card,
        borderRadius: radius,
        border: widget.showBorder
            ? Border.all(
                color: colors.cardBorder,
                width: IOSGlass.borderWidth,
              )
            : null,
      ),
      child: widget.child,
    );

    var wrapped = widget.margin != null
        ? Padding(padding: widget.margin!, child: card)
        : card;

    if (widget.onTap != null) {
      wrapped = GestureDetector(
        onTapDown: (_) => setState(() => _pressed = true),
        onTapUp: (_) => setState(() => _pressed = false),
        onTapCancel: () => setState(() => _pressed = false),
        onTap: widget.onTap,
        behavior: HitTestBehavior.opaque,
        child: AnimatedScale(
          scale: _pressed ? 0.98 : 1.0,
          duration: anim.effectiveDuration(IOSDuration.fast),
          curve: anim.effectiveCurve(IOSCurve.press),
          child: wrapped,
        ),
      );
    }
    return wrapped;
  }
}