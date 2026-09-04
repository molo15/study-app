/// V3 iOS 液态玻璃容器（Liquid Glass）
///
/// 结构：BackdropFilter(blur) + 半透明底 + 0.5px 边框 + 顶部 40% 高光渐变 + 阴影
/// 三档模糊强度：thin(18) / regular(24) / thick(32)
///
/// 用 RepaintBoundary 包裹避免模糊区域重绘影响性能。
/// 支持浅色/深色自适应（通过 IOSColors 令牌）。
library;

import 'dart:ui';

import 'package:flutter/material.dart';

import '../theme/ios_tokens.dart';

/// 液态玻璃模糊强度
enum LiquidGlassVariant {
  /// thin：sigma 18，透明度 0.55（导航栏、操作栏）
  thin,

  /// regular：sigma 24，透明度 0.62（Tab Bar、侧边栏）
  regular,

  /// thick：sigma 32，透明度 0.62+高光（弹窗/ActionSheet）
  thick,
}

class LiquidGlass extends StatelessWidget {
  const LiquidGlass({
    super.key,
    required this.child,
    this.variant = LiquidGlassVariant.regular,
    this.borderRadius,
    this.blurSigma,
    this.opacity,
    this.showHighlight = true,
    this.showShadow = true,
    this.padding,
    this.margin,
    this.width,
    this.height,
    this.alignment,
    this.clipBehavior = Clip.antiAlias,
  });

  final Widget child;

  /// 模糊强度预设
  final LiquidGlassVariant variant;

  /// 自定义圆角（默认 16）
  final BorderRadius? borderRadius;

  /// 自定义模糊 sigma（覆盖 variant）
  final double? blurSigma;

  /// 自定义背景透明度（覆盖 variant）
  final double? opacity;

  /// 是否显示顶部高光渐变
  final bool showHighlight;

  /// 是否显示阴影
  final bool showShadow;

  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final double? width;
  final double? height;
  final AlignmentGeometry? alignment;
  final Clip clipBehavior;

  /// 获取模糊 sigma
  double get _sigma {
    if (blurSigma != null) return blurSigma!;
    return switch (variant) {
      LiquidGlassVariant.thin => IOSGlass.blurThin,
      LiquidGlassVariant.regular => IOSGlass.blurRegular,
      LiquidGlassVariant.thick => IOSGlass.blurThick,
    };
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final colors = dark ? IOSColors.dark : IOSColors.light;
    final radius = borderRadius ?? BorderRadius.circular(IOSRadius.md);
    final sigma = _sigma;

    // 背景色：thin 用 glassThin，regular/thick 用 glass
    final bgColor = switch (variant) {
      LiquidGlassVariant.thin => colors.glassThin,
      _ => colors.glass,
    };

    // 应用自定义透明度
    final effectiveBg = opacity != null
        ? bgColor.withValues(alpha: opacity!)
        : bgColor;

    Widget content = Container(
      width: width,
      height: height,
      padding: padding,
      alignment: alignment,
      decoration: BoxDecoration(
        color: effectiveBg,
        borderRadius: radius,
        border: Border.all(
          color: colors.glassBorder,
          width: IOSGlass.borderWidth,
        ),
        boxShadow: showShadow ? IOSShadow.glass(dark: dark) : null,
      ),
      child: Stack(
        children: [
          // 内容层
          Positioned.fill(child: child),
          // 顶部高光渐变（40% 高度）
          if (showHighlight)
            Positioned(
              top: 0,
              left: 0,
              right: 0,
              height: null,
              child: IgnorePointer(
                child: Container(
                  height: 100,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.vertical(
                      top: radius.topLeft,
                    ),
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        colors.glassHighlight,
                        colors.glassHighlight.withValues(alpha: 0),
                      ],
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );

    // BackdropFilter 需要 ClipRect 包裹
    final filtered = ClipRRect(
      borderRadius: radius,
      clipBehavior: clipBehavior,
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: sigma, sigmaY: sigma),
        child: content,
      ),
    );

    // RepaintBoundary 隔离模糊重绘
    final isolated = RepaintBoundary(child: filtered);

    if (margin != null) {
      return Padding(padding: margin!, child: isolated);
    }
    return isolated;
  }
}
