/// V3 iOS 分组列表（inset grouped）
///
/// 圆角分组容器，组内 0.5px 分割线，组标题（footnote 大写）。
/// 列表项按压高亮 #F2F2F7（浅色）/ #1C1C1E（深色），无缩放。
///
/// 用法：
/// ```dart
/// IOSListGroup(
///   title: '学习',
///   items: [
///     IOSListItem(title: '目标院校', subtitle: '学科教学（语文）', onTap: () {}),
///     IOSListItem(title: '每日目标', subtitle: '60 题/天', onTap: () {}),
///   ],
/// )
/// ```
library;

import 'package:flutter/material.dart';

import '../theme/ios_animations.dart';
import '../theme/ios_tokens.dart';

/// 分组列表容器
class IOSListGroup extends StatelessWidget {
  const IOSListGroup({
    super.key,
    this.title,
    required this.items,
    this.footer,
    this.margin,
    this.padding,
  });

  /// 组标题（footnote 大小，大写风格）
  final String? title;

  /// 列表项
  final List<Widget> items;

  /// 组底部说明文字
  final String? footer;

  final EdgeInsetsGeometry? margin;
  final EdgeInsetsGeometry? padding;

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final colors = dark ? IOSColors.dark : IOSColors.light;

    return Padding(
      padding: margin ?? EdgeInsets.zero,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 组标题
          if (title != null)
            Padding(
              padding: const EdgeInsets.fromLTRB(
                IOSSpacing.s16,
                IOSSpacing.s24,
                IOSSpacing.s16,
                IOSSpacing.s8,
              ),
              child: Text(
                title!,
                style: IOSTypography.footnote(color: colors.text2).copyWith(
                  letterSpacing: 0.03 * IOSFontSize.footnote,
                ),
              ),
            ),
          // 分组容器
          Container(
            margin: padding ??
                const EdgeInsets.symmetric(horizontal: IOSSpacing.s16),
            decoration: BoxDecoration(
              color: colors.card,
              borderRadius: BorderRadius.circular(IOSRadius.sm),
              border: Border.all(
                color: colors.cardBorder,
                width: IOSGlass.borderWidth,
              ),
            ),
            clipBehavior: Clip.antiAlias,
            child: Column(
              children: [
                for (var i = 0; i < items.length; i++) ...[
                  items[i],
                  if (i < items.length - 1)
                    Divider(
                      height: IOSGlass.borderWidth,
                      thickness: IOSGlass.borderWidth,
                      color: colors.separator,
                      indent: IOSSpacing.s16,
                    ),
                ],
              ],
            ),
          ),
          // 组底部说明
          if (footer != null)
            Padding(
              padding: const EdgeInsets.fromLTRB(
                IOSSpacing.s16,
                IOSSpacing.s8,
                IOSSpacing.s16,
                0,
              ),
              child: Text(
                footer!,
                style: IOSTypography.caption1(color: colors.text3),
              ),
            ),
        ],
      ),
    );
  }
}

/// 列表项
class IOSListItem extends StatefulWidget {
  const IOSListItem({
    super.key,
    required this.title,
    this.subtitle,
    this.leading,
    this.trailing,
    this.onTap,
    this.showChevron = false,
    this.padding = const EdgeInsets.symmetric(
      horizontal: IOSSpacing.s16,
      vertical: IOSSpacing.s12,
    ),
    this.minHeight = 44,
  });

  final String title;
  final String? subtitle;
  final Widget? leading;
  final Widget? trailing;
  final VoidCallback? onTap;
  final bool showChevron;
  final EdgeInsetsGeometry padding;
  final double minHeight;

  @override
  State<IOSListItem> createState() => _IOSListItemState();
}

class _IOSListItemState extends State<IOSListItem> {
  bool _pressed = false;

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final colors = dark ? IOSColors.dark : IOSColors.light;
    final anim = IOSAnimations.of(context);

    return GestureDetector(
      onTapDown: (_) {
        if (widget.onTap != null) setState(() => _pressed = true);
      },
      onTapUp: (_) {
        if (widget.onTap != null) setState(() => _pressed = false);
      },
      onTapCancel: () {
        if (widget.onTap != null) setState(() => _pressed = false);
      },
      onTap: widget.onTap,
      behavior: HitTestBehavior.opaque,
      child: AnimatedContainer(
        duration: anim.effectiveDuration(IOSDuration.highlight),
        curve: anim.effectiveCurve(IOSCurve.press),
        color: _pressed ? colors.fill : Colors.transparent,
        padding: widget.padding,
        constraints: BoxConstraints(minHeight: widget.minHeight),
        child: Row(
          children: [
            if (widget.leading != null) ...[
              widget.leading!,
              const SizedBox(width: IOSSpacing.s12),
            ],
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    widget.title,
                    style: IOSTypography.body(color: colors.text),
                  ),
                  if (widget.subtitle != null) ...[
                    const SizedBox(height: 2),
                    Text(
                      widget.subtitle!,
                      style: IOSTypography.footnote(color: colors.text2),
                    ),
                  ],
                ],
              ),
            ),
            if (widget.trailing != null) ...[
              const SizedBox(width: IOSSpacing.s8),
              widget.trailing!,
            ],
            if (widget.showChevron) ...[
              const SizedBox(width: IOSSpacing.s4),
              Icon(
                Icons.chevron_right,
                size: 14,
                color: colors.placeholder,
              ),
            ],
          ],
        ),
      ),
    );
  }
}
