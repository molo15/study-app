import 'package:flutter/material.dart';

/// web 平台：无本地文件背景图（浏览器没有文件系统路径），返回空占位。
/// 用户可选用冷磨砂渐变背景（frost）或纯色。
class AppBackgroundImage extends StatelessWidget {
  const AppBackgroundImage({
    super.key,
    required this.path,
    required this.opacity,
  });

  final String path;
  final double opacity;

  @override
  Widget build(BuildContext context) => const SizedBox.shrink();
}
