import 'dart:io';

import 'package:flutter/material.dart';

/// io 平台（Android / Windows / 桌面）：本地文件背景图
class AppBackgroundImage extends StatelessWidget {
  const AppBackgroundImage({
    super.key,
    required this.path,
    required this.opacity,
  });

  final String path;
  final double opacity;

  @override
  Widget build(BuildContext context) {
    return Image.file(
      File(path),
      fit: BoxFit.cover,
      opacity: AlwaysStoppedAnimation(opacity),
      // 文件不存在/不可读时优雅回退，不白屏
      errorBuilder: (_, _, _) => const SizedBox.shrink(),
    );
  }
}
