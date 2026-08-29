import 'package:flutter/material.dart';

import 'animation_constants.dart';

/// 点按微动效卡片（P0 手感优化）
///
/// 按下时缩放至 [scale]（默认 0.97），抬起回弹。纯 UI 反馈，不碰状态。
/// [reduceMotion] 开启时缩放幅度减半。
class PressableCard extends StatefulWidget {
  const PressableCard({
    super.key,
    required this.child,
    this.onTap,
    this.scale = 0.97,
    this.padding,
    this.margin,
    this.decoration,
    this.reduceMotion = false,
    this.behavior = HitTestBehavior.opaque,
  });

  final Widget child;
  final VoidCallback? onTap;
  final double scale;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final Decoration? decoration;
  final bool reduceMotion;
  final HitTestBehavior behavior;

  @override
  State<PressableCard> createState() => _PressableCardState();
}

class _PressableCardState extends State<PressableCard> {
  bool _pressed = false;

  @override
  Widget build(BuildContext context) {
    final effectiveScale = _pressed
        ? (widget.reduceMotion
            ? 1 - (1 - widget.scale) * 0.5
            : widget.scale)
        : 1.0;
    return GestureDetector(
      behavior: widget.behavior,
      onTapDown: (_) {
        if (widget.onTap != null) setState(() => _pressed = true);
      },
      onTapUp: (_) {
        if (widget.onTap != null) setState(() => _pressed = false);
      },
      onTapCancel: () => setState(() => _pressed = false),
      onTap: widget.onTap,
      child: AnimatedScale(
        scale: effectiveScale,
        duration: _pressed ? AppAnim.press : AppAnim.release,
        curve: AppAnim.standard,
        child: Container(
          padding: widget.padding,
          margin: widget.margin,
          decoration: widget.decoration,
          child: widget.child,
        ),
      ),
    );
  }
}
