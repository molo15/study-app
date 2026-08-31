/// 环形进度（UI v2 · 冷磨砂）：生长动画 + 渐变描边。
///
/// 用于首页 Hero、统计总掌握度、背题总览知识点进度。
/// progress 0~1；首次出现从 0 生长到目标值（TweenAnimationBuilder）。
library;

import 'package:flutter/material.dart';

class CircularRing extends StatelessWidget {
  const CircularRing({
    super.key,
    required this.progress,
    this.size = 120,
    this.strokeWidth = 10,
    this.color = const Color(0xFF4F7CD4),
    this.trackColor,
    this.center,
    this.duration = const Duration(milliseconds: 900),
    this.curve = Curves.easeOutCubic,
  });

  /// 0~1 完成度
  final double progress;
  final double size;
  final double strokeWidth;
  final Color color;
  final Color? trackColor;
  final Widget? center;

  /// 生长动画时长
  final Duration duration;
  final Curve curve;

  @override
  Widget build(BuildContext context) {
    final track = trackColor ?? color.withValues(alpha: 0.14);
    final p = progress.clamp(0.0, 1.0);

    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: p),
      duration: duration,
      curve: curve,
      builder: (context, value, _) {
        return SizedBox(
          width: size,
          height: size,
          child: Stack(
            fit: StackFit.expand,
            children: [
              // 轨道
              _Ring(
                progress: 1,
                color: track,
                strokeWidth: strokeWidth,
              ),
              // 前景（渐变描边）
              ShaderMask(
                shaderCallback: (rect) => LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Color.lerp(color, Colors.white, 0.35)!,
                    color,
                    Color.lerp(color, Colors.black, 0.15)!,
                  ],
                ).createShader(rect),
                child: _Ring(
                  progress: value,
                  color: Colors.white,
                  strokeWidth: strokeWidth,
                ),
              ),
              if (center != null) Center(child: center),
            ],
          ),
        );
      },
    );
  }
}

class _Ring extends StatelessWidget {
  const _Ring({
    required this.progress,
    required this.color,
    required this.strokeWidth,
  });

  final double progress;
  final Color color;
  final double strokeWidth;

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: _RingPainter(
        progress: progress,
        color: color,
        strokeWidth: strokeWidth,
      ),
    );
  }
}

class _RingPainter extends CustomPainter {
  _RingPainter({
    required this.progress,
    required this.color,
    required this.strokeWidth,
  });

  final double progress;
  final Color color;
  final double strokeWidth;

  @override
  void paint(Canvas canvas, Size size) {
    final center = size.center(Offset.zero);
    final radius = (size.shortestSide - strokeWidth) / 2;
    final rect = Rect.fromCircle(center: center, radius: radius);
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round
      ..color = color;
    // 从顶部顺时针
    canvas.drawArc(
      rect,
      -1.57079633, // -90°
      6.28318531 * progress,
      false,
      paint,
    );
  }

  @override
  bool shouldRepaint(covariant _RingPainter old) =>
      old.progress != progress || old.color != color;
}
