/// 顶部毛玻璃 AppBar（需求：高斯模糊玻璃效果，下方内容过渡柔和不生硬）
///
/// 实现：AppBar backgroundColor 透明，flexibleSpace 放
/// BackdropFilter 高斯模糊 + 半透明表面色——内容滚动到 AppBar 下方时
/// 被模糊柔化，形成玻璃质感。深色模式自动适配。
library;

import 'dart:ui';

import 'package:flutter/material.dart';

class GlassAppBar extends StatelessWidget implements PreferredSizeWidget {
  const GlassAppBar({
    super.key,
    this.title,
    this.actions,
    this.bottom,
    this.leading,
    this.blurSigma = 18.0,
    this.backgroundColor,
    this.showBottomBorder = true,
    this.centerTitle = false,
  });

  final Widget? title;
  final List<Widget>? actions;
  final PreferredSizeWidget? bottom;
  final Widget? leading;

  /// 高斯模糊强度
  final double blurSigma;

  /// 毛玻璃底色（默认主题 surface 半透明，深色自动适配）
  final Color? backgroundColor;

  /// 是否显示底部细分隔线（柔和玻璃边缘）
  final bool showBottomBorder;

  /// 标题是否居中（需求：设置页标题顶部居中）
  final bool centerTitle;

  @override
  Size get preferredSize =>
      Size.fromHeight(kToolbarHeight + (bottom?.preferredSize.height ?? 0));

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final glassColor = backgroundColor ??
        (isDark
            ? const Color(0xCC1A2024) // 深色玻璃（近不透明，保证可读）
            : Colors.white.withValues(alpha: 0.72)); // 浅色玻璃（半透明）
    return AppBar(
      leading: leading,
      title: title,
      actions: actions,
      bottom: bottom,
      centerTitle: centerTitle,
      backgroundColor: Colors.transparent,
      elevation: 0,
      surfaceTintColor: Colors.transparent,
      scrolledUnderElevation: 0,
      flexibleSpace: ClipRect(
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: blurSigma, sigmaY: blurSigma),
          child: Container(
            decoration: BoxDecoration(
              color: glassColor,
              border: showBottomBorder
                  ? Border(
                      bottom: BorderSide(
                        color: scheme.outlineVariant.withValues(alpha: 0.4),
                        width: 0.5,
                      ),
                    )
                  : null,
            ),
          ),
        ),
      ),
    );
  }
}
