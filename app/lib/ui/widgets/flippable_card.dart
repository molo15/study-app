/// 3D 翻转卡（UI v2 · 背题卡内反转）。
///
/// 正面 front / 背面 back，由外部 flipped 状态控制翻转方向；
/// 点击卡面触发 onTap（通常由外层切换 flipped）。带透视的 Y 轴旋转。
/// 半程切换面：前半显示正面，后半显示背面，反转时背面前后镜像翻转。
library;

import 'package:flutter/material.dart';

class FlippableCard extends StatefulWidget {
  const FlippableCard({
    super.key,
    required this.front,
    required this.back,
    required this.flipped,
    this.onTap,
    this.height = 320,
    this.borderRadius = 24,
  });

  final Widget front;
  final Widget back;
  final bool flipped;
  final VoidCallback? onTap;
  final double height;
  final double borderRadius;

  @override
  State<FlippableCard> createState() => _FlippableCardState();
}

class _FlippableCardState extends State<FlippableCard>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 520),
  );
  late final CurvedAnimation _curved = CurvedAnimation(
    parent: _controller,
    curve: Curves.easeInOutCubic,
  );

  @override
  void initState() {
    super.initState();
    _controller.value = widget.flipped ? 1 : 0;
  }

  @override
  void didUpdateWidget(covariant FlippableCard oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.flipped != widget.flipped) {
      widget.flipped ? _controller.forward() : _controller.reverse();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _curved,
      builder: (context, _) {
        final angle = _curved.value * 3.14159265;
        final showFront = _controller.value < 0.5;
        final isAtRest = _controller.isDismissed || _controller.isCompleted;

        return GestureDetector(
          onTap: widget.onTap,
          child: Transform(
            alignment: Alignment.center,
            transform: Matrix4.identity()
              ..setEntry(3, 2, 0.0015) // 透视
              ..rotateY(angle),
            child: Stack(
              fit: StackFit.expand,
              children: [
                // 正面（flipped=false 显示）
                Opacity(
                  opacity: showFront ? 1 : 0,
                  child: widget.front,
                ),
                // 背面（flipped=true 显示，前后镜像）
                Transform(
                  alignment: Alignment.center,
                  transform: Matrix4.identity()..rotateY(3.14159265),
                  child: Opacity(
                    opacity: showFront ? 0 : 1,
                    child: widget.back,
                  ),
                ),
                // 待翻转（angle 0.5~π 时不可点击）
                if (!isAtRest) const IgnorePointer(child: SizedBox.expand()),
              ],
            ),
          ),
        );
      },
    );
  }
}
