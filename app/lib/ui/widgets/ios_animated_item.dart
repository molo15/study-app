/// V3 iOS 风格列表项入场动效
///
/// 用法：
/// ```dart
/// ListView.builder(
///   itemBuilder: (context, index) => IOSAnimatedItem(
///     index: index,
///     child: MyCard(),
///   ),
/// )
/// ```
///
/// 特性：
/// - stagger 延迟入场（每项 40ms 递增）
/// - fadeIn + 轻微上移（12px）
/// - 统一 IOSDuration.standard + IOSCurve.standard
/// - Reduce Motion 开启时直接显示（无动画）
/// - 首次构建后不再重复动画（TweenAnimationBuilder 仅触发一次）
library;

import 'package:flutter/material.dart';
import '../theme/ios_animations.dart';

class IOSAnimatedItem extends StatelessWidget {
  const IOSAnimatedItem({
    super.key,
    required this.child,
    required this.index,
    this.staggerMs = 40,
    this.slideDistance = 12.0,
  });

  final Widget child;

  /// 列表项索引（决定 stagger 延迟）
  final int index;

  /// 每项递增延迟（毫秒），默认 40ms
  final int staggerMs;

  /// 上移距离（px），默认 12
  final double slideDistance;

  @override
  Widget build(BuildContext context) {
    final anim = IOSAnimations.of(context);

    // Reduce Motion：直接显示，无动画
    if (anim.reduceMotion) return child;

    final duration = anim.effectiveDuration(IOSDuration.standard);
    final curve = anim.effectiveCurve(IOSCurve.standard);

    // 用 Interval curve 实现 stagger 延迟
    final totalMs = duration.inMilliseconds + staggerMs * index;
    final startFraction = (staggerMs * index) / totalMs;
    final staggeredCurve = Interval(
      startFraction.clamp(0.0, 0.95),
      1.0,
      curve: curve,
    );

    return TweenAnimationBuilder<double>(
      tween: Tween<double>(begin: 0, end: 1),
      duration: Duration(milliseconds: totalMs),
      curve: staggeredCurve,
      builder: (context, value, child) {
        return Opacity(
          opacity: value,
          child: Transform.translate(
            offset: Offset(0, (1 - value) * slideDistance),
            child: child,
          ),
        );
      },
      child: child,
    );
  }
}
