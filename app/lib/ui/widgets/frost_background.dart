/// 冷磨砂背景（UI v2）：渐变 + 漂浮光斑。
///
/// 沉浸原则：背景放在页面最底层，所有 Tab/二级页共享同一背景层，
/// 切换时背景永不跳动（解决"背景浮现其他页面"问题）。
/// 光斑用模糊圆（BoxShadow）实现，随玻璃卡片透出，营造毛玻璃质感。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

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

/// 冷磨砂背景：冷灰蓝渐变 + 漂浮光斑。
///
/// 用法：放在 Scaffold body 最外层（Stack 底层），页面内容叠加其上。
/// 颜色来自主题配置（frost 关闭时回退为纯色背景）。
class FrostBackground extends ConsumerWidget {
  const FrostBackground({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final config = ref.watch(themeControllerProvider).asData?.value;
    if (config == null || !config.frost) return child;

    final top = config.frostTop;
    final bottom = config.frostBottom;
    final accent = config.accent;
    final warm = Color.lerp(accent, Colors.white, 0.62)!;
    final cool = Color.lerp(accent, Colors.white, 0.5)!;

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
        _FrostBlob(color: cool, size: 200, left: -60, bottom: -55),
        // 中右（偏白，弱化）
        Positioned(
          right: 18,
          top: 0,
          bottom: 0,
          child: IgnorePointer(
            child: Align(
              alignment: Alignment(0.85, 0.15),
              child: Container(
                width: 130,
                height: 130,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.white.withValues(alpha: 0.5),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.white.withValues(alpha: 0.5),
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
