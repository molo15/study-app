/// 冷磨砂背景（UI v2）：渐变 + 漂浮光斑。
///
/// 沉浸原则：背景放在 Navigator 最底层（main.dart _BackgroundStack），
/// 所有 Tab 页与二级页（push 路由）共享同一背景层，切换永不跳背景
/// （解决"背景浮现其他页面"问题）。
/// 光斑用模糊圆（BoxShadow）实现，随玻璃卡片透出，营造毛玻璃质感。
library;

import 'package:flutter/material.dart';

import '../theme_controller.dart';

/// 单个模糊光斑（左上/右上/左下/中右 4 个，位置由参数控制）
class _FrostBlob extends StatelessWidget {
  const _FrostBlob({
    required this.color,
    required this.size,
    this.left,
    this.top,
    this.right,
    this.bottom,
    this.opacity = 0.45,
  });

  final Color color;
  final double size;
  final double? left;
  final double? top;
  final double? right;
  final double? bottom;
  final double opacity;

  @override
  Widget build(BuildContext context) {
    final c = color.withValues(alpha: opacity);
    return Positioned(
      left: left,
      top: top,
      right: right,
      bottom: bottom,
      child: IgnorePointer(
        child: Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: c,
            boxShadow: [
              BoxShadow(color: c, blurRadius: size * 0.6, spreadRadius: size * 0.2),
            ],
          ),
        ),
      ),
    );
  }
}

/// 冷磨砂背景：冷灰蓝渐变 + 漂浮光斑（位置固定最底层，全 App 共享）。
class FrostBackground extends StatelessWidget {
  const FrostBackground({super.key, required this.config, required this.child});

  final AppThemeConfig config;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    if (!config.frost) return child;

    // 深色模式：冷磨砂用深色渐变，避免浅色背景 + 深色主题浅色文字不可读
    final dark = config.darkMode;
    final top = dark ? const Color(0xFF131B28) : config.frostTop;
    final bottom = dark ? const Color(0xFF1E2B3C) : config.frostBottom;
    final accent = config.accent;
    final mixTarget = dark ? Colors.black : Colors.white;
    final warm = Color.lerp(accent, mixTarget, dark ? 0.45 : 0.62)!;
    final cool = Color.lerp(accent, mixTarget, dark ? 0.35 : 0.5)!;

    return Stack(
      fit: StackFit.expand,
      children: [
        // 冷灰蓝渐变底
        DecoratedBox(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [top, bottom],
            ),
          ),
        ),
        // 左上
        _FrostBlob(color: warm, size: 210, left: -45, top: -55),
        // 右上
        _FrostBlob(color: cool, size: 180, right: -50, top: -40, opacity: 0.42),
        // 左下
        _FrostBlob(color: cool, size: 200, left: -60, bottom: -55, opacity: dark ? 0.22 : 0.45),
        // 中右（偏白，弱化；深色模式下用冷色调暗）
        Positioned(
          right: 18,
          top: 0,
          bottom: 0,
          child: IgnorePointer(
            child: Align(
              alignment: const Alignment(0.85, 0.15),
              child: Container(
                width: 130,
                height: 130,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: dark ? cool.withValues(alpha: 0.3) : Colors.white.withValues(alpha: 0.5),
                  boxShadow: [
                    BoxShadow(
                      color: dark ? cool.withValues(alpha: 0.3) : Colors.white.withValues(alpha: 0.5),
                      blurRadius: 70,
                      spreadRadius: 24,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
        // 内容
        child,
      ],
    );
  }
}
