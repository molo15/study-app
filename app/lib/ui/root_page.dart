/// 应用根：底部导航（首页 / 统计 / 设置）
///
/// 沉浸式交互（需求）：
/// - edge-to-edge 边缘绘制（main.dart 设置），body 内容延伸到底部区域
/// - 上滑滚动内容时隐藏底栏（滑出屏幕底部），下滑时显示（滑回）
library;

import 'package:flutter/material.dart';

import 'home_page.dart';
import 'settings_page.dart';
import 'stats_page.dart';

class RootPage extends StatefulWidget {
  const RootPage({super.key});

  @override
  State<RootPage> createState() => _RootPageState();
}

class _RootPageState extends State<RootPage> {
  int _index = 0;
  bool _navVisible = true; // 上滑隐藏底栏、下滑显示（需求）

  /// 监听页面滚动：手指上滑（内容下滚）隐藏底栏，下滑（内容上滚）显示
  bool _onScroll(ScrollNotification notification) {
    if (notification is ScrollUpdateNotification) {
      final delta = notification.scrollDelta ?? 0;
      if (delta > 1.0 && _navVisible) {
        setState(() => _navVisible = false);
      } else if (delta < -1.0 && !_navVisible) {
        setState(() => _navVisible = true);
      }
    }
    return false;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // 沉浸式融合：body 内容延伸到底部导航区域下方（需求）
      extendBody: true,
      body: NotificationListener<ScrollNotification>(
        onNotification: _onScroll,
        // IndexedStack 常驻三页（状态保留、切换零重建）+ 慢速轻微上滑过渡（v1.1.3）
        child: _SmoothTabView(
          index: _index,
          children: const [
            HomePage(),
            StatsPage(),
            SettingsPage(),
          ],
        ),
      ),
      bottomNavigationBar: IgnorePointer(
        // 隐藏时（动画到透明）忽略点击，防止透明区域仍可命中（需求：导航隐藏不可点击）
        ignoring: !_navVisible,
        child: AnimatedSlide(
          // 上滑隐藏：底栏滑出屏幕底部（需求）
          offset: _navVisible ? Offset.zero : const Offset(0, 1.2),
          duration: const Duration(milliseconds: 260),
          curve: Curves.easeOutCubic,
          child: AnimatedOpacity(
            opacity: _navVisible ? 1 : 0,
            duration: const Duration(milliseconds: 200),
            child: NavigationBar(
              selectedIndex: _index,
              onDestinationSelected: (i) => setState(() => _index = i),
              destinations: const [
                NavigationDestination(
                  icon: Icon(Icons.home_outlined),
                  selectedIcon: Icon(Icons.home_outlined),
                  label: '首页',
                ),
                NavigationDestination(
                  icon: Icon(Icons.bar_chart_outlined),
                  selectedIcon: Icon(Icons.bar_chart),
                  label: '统计',
                ),
                NavigationDestination(
                  icon: Icon(Icons.settings_outlined),
                  selectedIcon: Icon(Icons.settings_outlined),
                  label: '设置',
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Tab 切换容器：IndexedStack 常驻三页（状态保留、切换零重建）+ 慢速淡入上滑过渡。
///
/// 相比 AnimatedSwitcher + ValueKey 重建整页，IndexedStack 避免切 Tab 时
/// 重复读库/重建，动画期间无卡顿；切换时新页轻微上滑（300ms 慢速档，
/// 无透明度变化，切换不露背景）。
class _SmoothTabView extends StatefulWidget {
  const _SmoothTabView({required this.index, required this.children});

  final int index;
  final List<Widget> children;

  @override
  State<_SmoothTabView> createState() => _SmoothTabViewState();
}

class _SmoothTabViewState extends State<_SmoothTabView>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 300), // 慢速档
  );

  @override
  void initState() {
    super.initState();
    _controller.value = 1; // 首屏不播动画，直接完整显示
  }

  @override
  void didUpdateWidget(covariant _SmoothTabView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.index != widget.index) {
      _controller.forward(from: 0); // 切换 Tab：淡入上滑
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final curved = CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOutCubic,
    );
    // 仅轻微上滑过渡（v1.1.3：去掉透明度淡入，避免切换瞬间背景透出，显得卡顿）
    return SlideTransition(
      position: Tween<Offset>(
        begin: const Offset(0, 0.012),
        end: Offset.zero,
      ).animate(curved),
      child: IndexedStack(index: widget.index, children: widget.children),
    );
  }
}
