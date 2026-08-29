import 'package:flutter/material.dart';

import 'animation_constants.dart';

/// 列表交错入场组件（P1 视觉优化）
///
/// 包裹列表项，首次构建时按 [index] 延迟淡入+上滑。
/// 用于章节列表、首页卡片等，提升页面进入时的层次感。
/// [reduceMotion] 开启时直接显示，无动画。
class StaggeredItem extends StatefulWidget {
  const StaggeredItem({
    super.key,
    required this.child,
    required this.index,
    this.delay = const Duration(milliseconds: 50),
    this.duration = const Duration(milliseconds: 280),
    this.reduceMotion = false,
  });

  final Widget child;
  final int index;
  final Duration delay;
  final Duration duration;
  final bool reduceMotion;

  @override
  State<StaggeredItem> createState() => _StaggeredItemState();
}

class _StaggeredItemState extends State<StaggeredItem>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(vsync: this, duration: widget.duration);
    if (!widget.reduceMotion) {
      Future.delayed(widget.delay * widget.index, () {
        if (mounted) _ctrl.forward();
      });
    } else {
      _ctrl.value = 1;
    }
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (widget.reduceMotion) return widget.child;
    return FadeTransition(
      opacity: CurvedAnimation(parent: _ctrl, curve: AppAnim.standard),
      child: SlideTransition(
        position: Tween<Offset>(
          begin: const Offset(0, 0.08),
          end: Offset.zero,
        ).animate(CurvedAnimation(parent: _ctrl, curve: AppAnim.standard)),
        child: widget.child,
      ),
    );
  }
}
