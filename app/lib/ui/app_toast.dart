/// 全局 iOS 风格悬浮胶囊轻提示（替代 Material SnackBar）
///
/// B4 审查修复：SnackBar 底部弹出会与浮动底栏/手势条冲突且带 Material 水波纹，
/// 改为悬浮胶囊（深色半透明底 + 白字 + pill 圆角），自动淡入淡出，新提示替换旧条。
/// 函数签名不变，所有调用方无需改动。
library;

import 'package:flutter/material.dart';

import 'theme/ios_animations.dart';
import 'theme/ios_tokens.dart';

OverlayEntry? _toastEntry;

void showAppToast(BuildContext context, String message, {Duration? duration}) {
  final overlay = Overlay.of(context);
  _toastEntry?.remove();
  late final OverlayEntry entry;
  entry = OverlayEntry(
    builder: (_) => _IOSToastView(
      message: message,
      duration: duration ?? const Duration(seconds: 2),
      onDismiss: () {
        if (_toastEntry == entry) {
          _toastEntry = null;
          entry.remove();
        }
      },
    ),
  );
  _toastEntry = entry;
  overlay.insert(entry);
}

class _IOSToastView extends StatefulWidget {
  const _IOSToastView({
    required this.message,
    required this.duration,
    required this.onDismiss,
  });

  final String message;
  final Duration duration;
  final VoidCallback onDismiss;

  @override
  State<_IOSToastView> createState() => _IOSToastViewState();
}

class _IOSToastViewState extends State<_IOSToastView>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(
    vsync: this,
    duration: IOSDuration.standard,
  );

  @override
  void initState() {
    super.initState();
    _controller.forward();
    Future.delayed(widget.duration + IOSDuration.standard, () {
      if (mounted) {
        _controller.reverse().then((_) => widget.onDismiss());
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final bottom = MediaQuery.of(context).padding.bottom;
    final isDark = MediaQuery.platformBrightnessOf(context) == Brightness.dark;
    return Positioned(
      left: 0,
      right: 0,
      bottom: bottom + 132,
      child: IgnorePointer(
        child: Center(
          child: FadeTransition(
            opacity: CurvedAnimation(
              parent: _controller,
              curve: Curves.easeOut,
            ),
            child: SlideTransition(
              position: Tween<Offset>(
                begin: const Offset(0, 0.25),
                end: Offset.zero,
              ).animate(
                CurvedAnimation(parent: _controller, curve: Curves.easeOut),
              ),
              child: Container(
                constraints: const BoxConstraints(maxWidth: 420),
                margin: const EdgeInsets.symmetric(horizontal: 24),
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 10,
                ),
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: isDark ? 0.85 : 0.72),
                  borderRadius: BorderRadius.circular(IOSRadius.pill),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: isDark ? 0.3 : 0.18),
                      blurRadius: 20,
                      offset: const Offset(0, 6),
                    ),
                  ],
                ),
                child: Text(
                  widget.message,
                  textAlign: TextAlign.center,
                  style: IOSTypography.subheadline(color: Colors.white)
                      .copyWith(fontWeight: FontWeight.w500),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}