/// 应用根（UI v3 · iOS 风格）：今日 / 题库 / [背题] / 统计 / 我的。
///
/// V3 导航：
/// - compact / medium（手机 / 平板）：底部胶囊悬浮 TabBar（统一一行 5 Tab）
/// - expanded（桌面 ≥1200）：左侧 AppSidebar（66px 图标 / 可展开 / 232px 全宽）
library;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import '../services/archive_store.dart';
import '../services/auto_archive_service.dart';
import 'bank_home_page.dart';
import 'pages/v3/home_v3_page.dart';
import 'pages/v3/memorize_v3_page.dart';
import 'pages/v3/settings_v3_page.dart';
import 'pages/v3/stats_v3_page.dart';
import 'responsive.dart';
import 'theme/ios_animations.dart';
import 'widgets/app_sidebar.dart';
import 'widgets/floating_tab_bar.dart';
import 'widgets/ios_install_guide.dart';

class RootPage extends ConsumerStatefulWidget {
  const RootPage({super.key});

  @override
  ConsumerState<RootPage> createState() => _RootPageState();
}

class _RootPageState extends ConsumerState<RootPage> {
  int _index = 0;
  bool _navVisible = true; // 上滑隐藏底栏、下滑显示（需求）

  // tab 切换时触发对应页面刷新（IndexedStack 常驻页面不重建，缺陷 #1）
  final GlobalKey<HomeV3PageState> _homeKey = GlobalKey();
  final GlobalKey<BankHomePageState> _bankKey = GlobalKey();
  final GlobalKey<StatsV3PageState> _statsKey = GlobalKey();
  final GlobalKey<MemorizeV3PageState> _memorizeKey = GlobalKey();

  @override
  void initState() {
    super.initState();
    _startAutoArchive();
    // iOS Web 首次启动「添加到主屏幕」引导（仅一次，标记存设置表）
    WidgetsBinding.instance.addPostFrameCallback((_) {
      maybeShowIosInstallGuide(ref, context);
    });
  }

  /// 挂载自动存档服务（定时 + 生命周期暂停触发；开关读设置）
  Future<void> _startAutoArchive() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      final service = ref.read(autoArchiveServiceProvider);
      await service.start(repo, FileArchiveStore());
    } catch (e) {
      debugPrint('自动存档启动失败: $e');
    }
  }
  /// 监听页面滚动：手指上滑（浏览下文）隐藏底栏，下滑（回上文）/回到顶部显示。
  ///
  /// 用 UserScrollNotification.direction 判断手势方向，比 scrollDelta 稳：
  /// 不受 iOS BouncingScrollPhysics 惯性回弹的反向 delta 干扰。
  bool _onScroll(ScrollNotification notification) {
    final metrics = notification.metrics;
    if (metrics.minScrollExtent == metrics.maxScrollExtent) {
      if (!_navVisible) setState(() => _navVisible = true);
      return false;
    }
    if (metrics.pixels <= metrics.minScrollExtent + 2) {
      if (!_navVisible) setState(() => _navVisible = true);
      return false;
    }
    if (notification is UserScrollNotification) {
      switch (notification.direction) {
        case ScrollDirection.reverse:
          if (_navVisible) setState(() => _navVisible = false);
        case ScrollDirection.forward:
          if (!_navVisible) setState(() => _navVisible = true);
        case ScrollDirection.idle:
          break;
      }
    }
    return false;
  }

  /// tab 选择（dock 与侧边栏共用）：切页 + 刷新今日/统计
  void _select(int i) {
    setState(() {
      _index = i;
      _navVisible = true; // 切换到新页时底栏复位显示
    });
    if (i == 0) _homeKey.currentState?.refresh();
    if (i == 1) _bankKey.currentState?.refresh();
    if (i == 2) _memorizeKey.currentState?.refresh();
    if (i == 3) _statsKey.currentState?.refresh();
  }

  @override
  Widget build(BuildContext context) {
    final layout = appLayoutOf(context);
    // V3：仅桌面（expanded ≥1200）用侧边栏；手机 / 平板用底部悬浮 TabBar
    final useSidebar = layout == AppLayout.expanded;

    final content = NotificationListener<ScrollNotification>(
      onNotification: _onScroll,
      // IndexedStack 常驻五页（状态保留、切换零重建）+ 慢速轻微上滑过渡（v1.1.3）
      // 背景由 main.dart _BackgroundStack 统一提供
      child: SafeArea(
        // B3 审查修复：Tab 页顶部统一安全区（修复题库/今日标题与状态栏重叠）
        bottom: false,
        child: _SmoothTabView(
        index: _index,
        children: [
          HomeV3Page(key: _homeKey),      // 今日信息流（V3）
          BankHomePage(key: _bankKey),   // 题库
          MemorizeV3Page(key: _memorizeKey), // 背题（V3）
          StatsV3Page(key: _statsKey),     // 统计（V3）
          const SettingsV3Page(), // 我的（V3 设置中心）
          ],
        ),
      ),
    );

    return Scaffold(
      // 沉浸式融合：body 内容延伸到底部导航区域下方（仅悬浮 dock 形态）
      extendBody: !useSidebar,
      body: useSidebar
          ? Row(
              children: [
                AppSidebar(index: _index, onSelect: _select),
                Expanded(child: content),
              ],
            )
          : content,
      bottomNavigationBar: useSidebar
          ? null
          : IgnorePointer(
              // 隐藏时（动画到透明）忽略点击，防止透明区域仍可命中
              ignoring: !_navVisible,
              child: FloatingTabBar(
                currentIndex: _index,
                hidden: !_navVisible,
                onSelect: _select,
              ),
            ),
    );
  }
}

/// Tab 切换容器：IndexedStack 常驻五页（状态保留、切换零重建）+ 慢速淡入上滑过渡。
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
    duration: IOSDuration.fast, // Tab 切换：150ms 快速响应（规格 tabSwitch）
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
    final anim = IOSAnimations.of(context);
    // Reduce Motion：跳过 Tab 切换上滑动画，直接显示
    if (anim.reduceMotion) {
      return IndexedStack(index: widget.index, children: widget.children);
    }
    final curved = CurvedAnimation(
      parent: _controller,
      curve: anim.effectiveCurve(IOSCurve.standard),
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
