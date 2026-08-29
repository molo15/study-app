import 'package:flutter/material.dart';

import 'pressable_card.dart';

/// 统一卡片组件（P1 视觉优化）
///
/// 全局统一的卡片样式：主题圆角 + 柔和阴影 + 内边距，
/// 支持点按动效（集成 [PressableCard]）。
/// 所有页面的章节卡、统计卡、设置项卡应统一使用此组件。
class AppCard extends StatelessWidget {
  const AppCard({
    super.key,
    required this.child,
    this.onTap,
    this.padding = const EdgeInsets.all(16),
    this.margin,
    this.color,
    this.border,
    this.reduceMotion = false,
    this.elevation = true,
  });

  final Widget child;
  final VoidCallback? onTap;
  final EdgeInsetsGeometry padding;
  final EdgeInsetsGeometry? margin;
  final Color? color;
  final BoxBorder? border;
  final bool reduceMotion;

  /// 是否显示柔和阴影（默认 true；设置页等不需要阴影的卡片可关）
  final bool elevation;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final shape = theme.cardTheme.shape;
    final radius = shape is RoundedRectangleBorder
        ? shape.borderRadius
        : BorderRadius.circular(16);

    final decoration = BoxDecoration(
      color: color ?? theme.cardColor,
      borderRadius: radius,
      border: border,
      boxShadow: elevation
          ? [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.06),
                blurRadius: 12,
                spreadRadius: -4,
                offset: const Offset(0, 2),
              ),
            ]
          : null,
    );

    if (onTap == null) {
      return Container(
        margin: margin,
        padding: padding,
        decoration: decoration,
        child: child,
      );
    }

    return PressableCard(
      margin: margin,
      padding: padding,
      decoration: decoration,
      reduceMotion: reduceMotion,
      onTap: onTap,
      child: child,
    );
  }
}
