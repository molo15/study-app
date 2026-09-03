/// V3 iOS 纯白无阴影卡片
///
/// 浅色 #FFFFFF / 深色 #2C2C2E
/// 圆角 16，无阴影（iOS 风格靠分组和间距区分层次）
/// 可选 0.5px 极淡边框。
library;

import 'package:flutter/material.dart';

import '../theme/ios_tokens.dart';

class IOSCard extends StatelessWidget {
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
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final colors = dark ? IOSColors.dark : IOSColors.light;
    final radius = borderRadius ?? BorderRadius.circular(IOSRadius.md);

    final card = Container(
      width: width,
      height: height,
      padding: padding,
      decoration: BoxDecoration(
        color: color ?? colors.card,
        borderRadius: radius,
        border: showBorder
            ? Border.all(
                color: colors.cardBorder,
                width: IOSGlass.borderWidth,
              )
            : null,
      ),
      child: child,
    );

    final wrapped = margin != null ? Padding(padding: margin!, child: card) : card;

    if (onTap != null) {
      return GestureDetector(
        onTap: onTap,
        behavior: HitTestBehavior.opaque,
        child: wrapped,
      );
    }
    return wrapped;
  }
}
