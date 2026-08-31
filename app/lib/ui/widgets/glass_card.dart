/// 毛玻璃卡片（UI v2 冷磨砂核心组件）。
///
/// 三层结构：阴影容器 → ClipRRect → BackdropFilter 模糊 → 半透明白渐变。
/// 支持三档玻璃强度（strong/默认/light），顶部高光描边，按压反馈。
/// 颜色与圆角取自主题配置（frost 关闭时回退为普通白色卡片）。
library;

import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../theme_controller.dart';

enum GlassDepth { strong, normal, light }

/// 冷磨砂毛玻璃卡片
class GlassCard extends ConsumerWidget {
  const GlassCard({
    super.key,
    required this.child,
    this.depth = GlassDepth.normal,
    this.padding,
    this.margin,
    this.radius,
    this.onTap,
    this.color,
    this.highlight = true,
    this.borderColor,
  });

  final Widget child;
  final GlassDepth depth;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final double? radius;
  final VoidCallback? onTap;
  final Color? color;
  final bool highlight;
  final Color? borderColor;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final config = ref.watch(themeControllerProvider).asData?.value;
    final frost = config?.frost ?? false;
    final r = radius ?? (config?.cornerRadius ?? 18);
    final ink = config?.darkMode ?? false;

    // 玻璃三档参数
    final (double alphaTop, double alphaBottom, double blur, double shadowA) =
        switch (depth) {
      GlassDepth.strong => (0.78, 0.45, 26.0, 0.16),
      GlassDepth.normal => (0.68, 0.34, 22.0, 0.13),
      GlassDepth.light => (0.50, 0.20, 14.0, 0.09),
    };

    Widget content = child;
    if (padding != null) content = Padding(padding: padding!, child: content);

    Widget glass;
    if (!frost) {
      // 回退：普通卡片（旧主题）
      glass = Material(
        color: color ?? (ink ? const Color(0xFF1E2428) : Colors.white),
        borderRadius: BorderRadius.circular(r),
        child: content,
      );
    } else {
      final base = color ?? Colors.white;
      glass = Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              base.withValues(alpha: alphaTop),
              base.withValues(alpha: alphaBottom),
            ],
          ),
          borderRadius: BorderRadius.circular(r),
          border: Border.all(
            color: borderColor ?? Colors.white.withValues(alpha: 0.62),
          ),
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(r),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: blur, sigmaY: blur),
            child: content,
          ),
        ),
      );
    }

    final outer = Container(
      margin: margin,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(r),
        boxShadow: [
          BoxShadow(
            color: Color(0xFF263A5C).withValues(alpha: shadowA),
            blurRadius: 28,
            offset: const Offset(0, 10),
          ),
        ],
        // 顶部高光描边（质感）
        border: highlight && frost
            ? Border(top: BorderSide(color: Colors.white.withValues(alpha: 0.85)))
            : null,
      ),
      child: glass,
    );

    if (onTap == null) return outer;
    return GestureDetector(
      onTap: onTap,
      child: outer,
    );
  }
}
