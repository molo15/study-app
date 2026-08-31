import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../theme_controller.dart';
import 'pressable_card.dart';

/// 统一卡片组件（P1 视觉优化 / UI v2 冷磨砂）
///
/// - 冷磨砂模式（frost=true，UI v2 默认）：毛玻璃样式（BackdropFilter +
///   半透明白渐变 + 白边 + 顶部高光 + 柔和阴影），全 App 卡片统一玻璃质感。
/// - 旧模式（frost=false）：保持原实色卡片。
///
/// 所有页面的章节卡、统计卡、设置项卡统一使用此组件。
class AppCard extends ConsumerWidget {
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
    this.radius,
    this.depth = 0,
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

  /// 自定义圆角（默认取主题 cornerRadius）
  final double? radius;

  /// 玻璃强度档位（0=normal 1=strong 2=light；仅冷磨砂模式生效）
  final int depth;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final config = ref.watch(themeControllerProvider).asData?.value;
    final frost = config?.frost ?? false;
    if (!frost) return _buildLegacy(context, config);
    return _buildGlass(context, config, ref);
  }

  /// 旧模式：实色卡片（原逻辑）
  Widget _buildLegacy(BuildContext context, AppThemeConfig? config) {
    final theme = Theme.of(context);
    final shape = theme.cardTheme.shape;
    final r = shape is RoundedRectangleBorder
        ? shape.borderRadius
        : BorderRadius.circular(16);

    final decoration = BoxDecoration(
      color: color ?? theme.cardColor,
      borderRadius: r,
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

  /// 冷磨砂：毛玻璃卡片
  Widget _buildGlass(
    BuildContext context,
    AppThemeConfig? config,
    WidgetRef ref,
  ) {
    final r = radius ?? (config?.cornerRadius ?? 18);
    // 深色模式：深色玻璃（白底 + 深色主题浅字会不可读）
    final dark = config?.darkMode ?? false;
    final glassBase = color ?? (dark ? const Color(0xFF2B3646) : Colors.white);
    final glassBorder = border ??
        Border.all(color: Colors.white.withValues(alpha: dark ? 0.18 : 0.62));
    final (double aTop, double aBottom, double blur, double shadowA) =
        switch (depth) {
      1 => (0.78, 0.45, 26.0, 0.16),
      2 => (0.50, 0.20, 14.0, 0.09),
      _ => (0.66, 0.32, 22.0, 0.13),
    };

    Widget body = child;
    if (onTap == null) {
      body = Container(
        margin: margin,
        padding: padding,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              glassBase.withValues(alpha: aTop),
              glassBase.withValues(alpha: aBottom),
            ],
          ),
          borderRadius: BorderRadius.circular(r),
          border: glassBorder,
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(r),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: blur, sigmaY: blur),
            child: body,
          ),
        ),
      );
    }

    final outer = Container(
      margin: margin,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(r),
        boxShadow: elevation
            ? [
                BoxShadow(
                  color: const Color(0xFF263A5C).withValues(alpha: shadowA),
                  blurRadius: 28,
                  offset: const Offset(0, 10),
                ),
              ]
            : null,
        // 顶部高光描边（质感）
        border: Border(
          top: BorderSide(
            color: Colors.white.withValues(alpha: dark ? 0.22 : 0.85),
          ),
        ),
      ),
      child: body,
    );

    if (onTap == null) return outer;
    return PressableCard(
      // 审查修复：此前硬编码 margin: null，导致所有带 onTap 的卡片
      // （如首页题库卡 margin bottom:10）外间距丢失、卡片紧贴粘连。
      // 与无 onTap 分支的 outer(Container(margin: margin)) 行为保持一致。
      margin: margin,
      padding: EdgeInsets.zero,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(r),
        boxShadow: elevation
            ? [
                BoxShadow(
                  color: const Color(0xFF263A5C).withValues(alpha: shadowA),
                  blurRadius: 28,
                  offset: const Offset(0, 10),
                ),
              ]
            : null,
      ),
      reduceMotion: reduceMotion,
      onTap: onTap,
      child: Container(
        padding: padding,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              glassBase.withValues(alpha: aTop),
              glassBase.withValues(alpha: aBottom),
            ],
          ),
          borderRadius: BorderRadius.circular(r),
          border: glassBorder,
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(r),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: blur, sigmaY: blur),
            child: child,
          ),
        ),
      ),
    );
  }
}
