/// V3 iOS 胶囊形悬浮 Tab Bar（统一一行版）
///
/// 底部 5 Tab 等宽排列：今日 / 题库 / 背题 / 统计 / 我的
/// 无中央凸起圆钮（对齐酷安底栏：统一一行、液态玻璃胶囊）。
///
/// 关键约束：
/// - compact 宽度=屏宽−48px，medium 宽度=屏宽−64px 且 maxWidth 680px 居中
/// - expanded（桌面）隐藏，改用侧边栏
/// - 液态玻璃材质，选中态颜色变化+轻微缩放
/// - 滚动隐藏由父级传入 hidden，AnimatedSlide+AnimatedOpacity 平滑过渡
library;

import 'package:flutter/material.dart';

import '../theme/ios_animations.dart';
import '../theme/ios_tokens.dart';
import 'liquid_glass.dart';

/// Tab 项定义
class FloatingTabItem {
  const FloatingTabItem({
    required this.icon,
    required this.label,
    this.activeIcon,
  });

  final IconData icon;
  final IconData? activeIcon;
  final String label;
}

class FloatingTabBar extends StatelessWidget {
  const FloatingTabBar({
    super.key,
    required this.currentIndex,
    required this.onSelect,
    this.items = _defaultItems,
    this.hidden = false,
  });

  /// 当前选中索引（0-4）
  final int currentIndex;

  /// Tab 选中回调
  final ValueChanged<int> onSelect;

  /// 5 个 Tab 项
  final List<FloatingTabItem> items;

  /// 是否隐藏（上滑隐藏动画）
  final bool hidden;

  static const List<FloatingTabItem> _defaultItems = [
    FloatingTabItem(icon: Icons.wb_sunny_outlined, label: '今日'),
    FloatingTabItem(icon: Icons.folder_outlined, label: '题库'),
    FloatingTabItem(icon: Icons.layers_outlined, activeIcon: Icons.layers, label: '背题'),
    FloatingTabItem(icon: Icons.insights_outlined, label: '统计'),
    FloatingTabItem(icon: Icons.person_outline, label: '我的'),
  ];

  @override
  Widget build(BuildContext context) {
    final layout = _LayoutInfo.of(context);
    final anim = IOSAnimations.of(context);

    // expanded 隐藏 Tab Bar（桌面用侧边栏）
    if (layout.isExpanded) return const SizedBox.shrink();

    // 宽度规则：compact 宽−48，medium 宽−64 上限 680
    final horizontalInset = layout.isCompact
        ? IOSBreakpoint.compactBarHorizontalInset
        : IOSBreakpoint.mediumBarHorizontalInset;
    final barWidth = (layout.width - horizontalInset).clamp(
      0.0,
      IOSBreakpoint.floatingBarMaxWidth,
    );

    final safeBottom = MediaQuery.paddingOf(context).bottom;

    return AnimatedSlide(
      offset: hidden ? const Offset(0, 1.5) : Offset.zero,
      duration: anim.effectiveDuration(IOSDuration.standard),
      curve: anim.effectiveCurve(IOSCurve.standard),
      child: AnimatedOpacity(
        opacity: hidden ? 0 : 1,
        duration: anim.effectiveDuration(IOSDuration.fast),
        child: Padding(
          padding: EdgeInsets.only(
            bottom: IOSFloatingBar.bottomOffset + safeBottom,
          ),
          child: Align(
            alignment: Alignment.bottomCenter,
            child: SizedBox(
              width: barWidth,
              height: IOSFloatingBar.tabBarHeight,
              child: LiquidGlass(
                variant: LiquidGlassVariant.regular,
                borderRadius: BorderRadius.circular(IOSRadius.pill),
                showShadow: true,
                padding: EdgeInsets.zero,
                child: Row(
                  children: [
                    for (var i = 0; i < items.length; i++)
                      _TabButton(
                        item: items[i],
                        selected: currentIndex == i,
                        onTap: () => onSelect(i),
                      ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// 单个 Tab 按钮（统一一行，等宽）
class _TabButton extends StatelessWidget {
  const _TabButton({
    required this.item,
    required this.selected,
    required this.onTap,
  });

  final FloatingTabItem item;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final colors = dark ? IOSColors.dark : IOSColors.light;
    final anim = IOSAnimations.of(context);

    final color = selected ? colors.primary : colors.text2;

    return Expanded(
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: onTap,
        child: AnimatedScale(
          scale: selected ? 1.06 : 1.0,
          duration: anim.effectiveDuration(IOSDuration.fast),
          curve: anim.effectiveCurve(IOSCurve.press),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                selected ? (item.activeIcon ?? item.icon) : item.icon,
                size: IOSFloatingBar.tabIconSize,
                color: color,
              ),
              const SizedBox(height: 3),
              Text(
                item.label,
                style: TextStyle(
                  fontSize: IOSFloatingBar.tabLabelSize,
                  fontWeight: selected ? FontWeight.w500 : FontWeight.w400,
                  color: color,
                  letterSpacing: 0.02 * IOSFloatingBar.tabLabelSize,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// 布局信息辅助类
class _LayoutInfo {
  const _LayoutInfo({
    required this.width,
    required this.isCompact,
    required this.isExpanded,
  });

  final double width;
  final bool isCompact;
  final bool isExpanded;

  factory _LayoutInfo.of(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    return _LayoutInfo(
      width: w,
      isCompact: w < IOSBreakpoint.compactMax,
      isExpanded: w >= IOSBreakpoint.mediumMax,
    );
  }
}
