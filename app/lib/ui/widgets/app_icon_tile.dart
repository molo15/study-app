/// 统一图标容器（需求：列表行 leading 复用）
///
/// 40dp 圆角方形图标容器，用于 `ListTile.leading` 等场景统一视觉，
/// 圆角默认 8dp（见《界面UI改版设计方案》4.5 节小标签圆角）。
/// 浅色 / 深色模式自动适配：
/// - 未传 [color] 时使用主题 `primaryContainer`，图标取 `onPrimaryContainer`；
/// - 传入自定义 [color] 时按背景亮度自动选择黑白前景，保证可读
///   （需求：自定义主色做前景对比保障）。
///
/// 用法：
/// ```dart
/// ListTile(
///   leading: AppIconTile(icon: Icons.book_outlined),
///   title: Text('章节名称'),
/// )
/// ```
library;

import 'package:flutter/material.dart';

import '../theme_controller.dart' show AppRadius;

class AppIconTile extends StatelessWidget {
  const AppIconTile({
    super.key,
    required this.icon,
    this.color,
    this.size = 40,
    this.iconSize = 22,
    this.borderRadius = AppRadius.small,
  });

  /// 图标
  final IconData icon;

  /// 容器背景色（默认主题 `primaryContainer`，深色自动适配；可传自定义色）
  final Color? color;

  /// 容器边长（默认 40dp）
  final double size;

  /// 图标大小（默认 22dp）
  final double iconSize;

  /// 容器圆角（默认 8dp）
  final double borderRadius;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final bg = color ?? colorScheme.primaryContainer;
    // 前景对比：默认容器配 onPrimaryContainer；
    // 自定义色时按背景亮度取黑白前景，保证主色下仍可读
    final onBg = color == null
        ? colorScheme.onPrimaryContainer
        : (ThemeData.estimateBrightnessForColor(bg) == Brightness.dark
              ? Colors.white
              : colorScheme.onSurface);
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(borderRadius),
      ),
      child: Icon(icon, size: iconSize, color: onBg),
    );
  }
}
