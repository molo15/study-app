/// 毛玻璃底部导航（UI v2）：今日 / 题库 / [背题·中央圆钮] / 统计 / 我的。
///
/// 冷磨砂底栏：BackdropFilter 毛玻璃 + 顶部 1px 白边 + 选中态强调色上浮。
/// 中央圆形"背题"凸起快捷入口（对应不背单词式背题模式）。
library;

import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../theme_controller.dart';

class GlassTabBar extends ConsumerWidget {
  const GlassTabBar({
    super.key,
    required this.index,
    required this.onSelect,
    this.hidden = false,
  });

  final int index;
  final ValueChanged<int> onSelect;

  /// 上滑隐藏（滑出底部）
  final bool hidden;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final config = ref.watch(themeControllerProvider).asData?.value;
    final accent = config?.accent ?? const Color(0xFF4F7CD4);
    final ink = config?.darkMode ?? false;
    final ink2 = ink ? Colors.white70 : const Color(0xFF56647C);

    Widget bar = Container(
      padding: EdgeInsets.only(top: 10, bottom: 24),
      decoration: BoxDecoration(
        // 毛玻璃底栏
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            ink ? const Color(0x88FFFFFF) : const Color(0x7FEAF1FB),
            ink ? const Color(0xCC0F1418) : const Color(0xC6E5EEFA),
          ],
        ),
        border: Border(
          top: BorderSide(color: Colors.white.withValues(alpha: 0.5)),
        ),
      ),
      child: ClipRect(
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 26, sigmaY: 26),
          child: Row(
            children: [
              _Tab(icon: Icons.today_outlined, label: '今日', on: index == 0, color: accent, ink: ink2, onTap: () => onSelect(0)),
              _Tab(icon: Icons.folder_outlined, label: '题库', on: index == 1, color: accent, ink: ink2, onTap: () => onSelect(1)),
              // 中央凸起圆钮：背题
              Expanded(
                child: GestureDetector(
                  onTap: () => onSelect(2),
                  child: Container(
                    margin: const EdgeInsets.only(top: -30, bottom: 4),
                    alignment: Alignment.center,
                    child: Container(
                      width: 58,
                      height: 58,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        gradient: LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [accent, Color.lerp(accent, Colors.black, 0.18)!],
                        ),
                        border: Border.all(color: Colors.white.withValues(alpha: 0.6), width: 2),
                        boxShadow: [
                          BoxShadow(
                            color: accent.withValues(alpha: 0.45),
                            blurRadius: 24,
                            offset: const Offset(0, 8),
                          ),
                        ],
                      ),
                      child: const Icon(Icons.auto_awesome, color: Colors.white, size: 24),
                    ),
                  ),
                ),
              ),
              _Tab(icon: Icons.insights_outlined, label: '统计', on: index == 3, color: accent, ink: ink2, onTap: () => onSelect(3)),
              _Tab(icon: Icons.person_outline, label: '我的', on: index == 4, color: accent, ink: ink2, onTap: () => onSelect(4)),
            ],
          ),
        ),
      ),
    );

    // 上滑隐藏动画
    return AnimatedSlide(
      offset: hidden ? const Offset(0, 1.2) : Offset.zero,
      duration: const Duration(milliseconds: 260),
      curve: Curves.easeOutCubic,
      child: AnimatedOpacity(
        opacity: hidden ? 0 : 1,
        duration: const Duration(milliseconds: 200),
        child: bar,
      ),
    );
  }
}

class _Tab extends StatelessWidget {
  const _Tab({
    required this.icon,
    required this.label,
    required this.on,
    required this.color,
    required this.ink,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final bool on;
  final Color color;
  final Color ink;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 220),
          curve: Curves.easeOut,
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              AnimatedScale(
                scale: on ? 1.12 : 1.0,
                duration: const Duration(milliseconds: 220),
                child: Icon(icon, size: 21, color: on ? color : ink),
              ),
              const SizedBox(height: 3),
              Text(
                label,
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: on ? FontWeight.w700 : FontWeight.w600,
                  color: on ? color : ink,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
