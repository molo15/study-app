/// 应用根（UI v2 · 冷磨砂）：今日 / 题库 / [背题] / 统计 / 我的。
///
/// 沉浸式交互（需求）：
/// - FrostBackground 共享冷磨砂背景，所有 Tab 共用同一背景层，切换不露背景
/// - 上滑滚动内容时隐藏底栏（滑出屏幕底部），下滑时显示（滑回）
///
/// 多端导航（P1 侧边栏）：compact（手机）用底部 GlassTabBar（含中央背题圆钮）；
/// medium / expanded（平板 / 桌面）用左侧 AppSidebar（66px 图标 / 可展开 / 232px 全宽），
/// 隐藏底部 dock。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import '../services/archive_store.dart';
import '../services/auto_archive_service.dart';
import 'bank_home_page.dart';
import 'home_page.dart';
import 'memorize_home_page.dart';
import 'responsive.dart';
import 'settings_page.dart';
import 'stats_page.dart';
import 'widgets/app_sidebar.dart';
import 'widgets/glass_tab_bar.dart';
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
  final GlobalKey<HomePageState> _homeKey = GlobalKey();
  final GlobalKey<StatsPageState> _statsKey = GlobalKey();

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

  /// tab 选择（dock 与侧边栏共用）：切页 + 刷新今日/统计
  void _select(int i) {
    setState(() => _index = i);
    if (i == 0) _homeKey.currentState?.refresh();
    if (i == 3) _statsKey.currentState?.refresh();
  }

  @override
  Widget build(BuildContext context) {
    final layout = appLayoutOf(context);
    final useSidebar = layout != AppLayout.compact;

    final content = NotificationListener<ScrollNotification>(
      onNotification: _onScroll,
      // IndexedStack 常驻五页（状态保留、切换零重建）+ 慢速轻微上滑过渡（v1.1.3）
      // 背景由 main.dart _BackgroundStack 统一提供（冷磨砂渐变+光斑全局共享）
      child: _SmoothTabView(
        index: _index,
        children: [
          HomePage(key: _homeKey),      // 今日信息流
          const BankHomePage(),  // 题库
          const MemorizeHomePage(), // 背题（中央圆钮入口）
          StatsPage(key: _statsKey),     // 统计
          const SettingsPage(),  // 我的（替代设置）
        ],
      ),
    );

    return Scaffold(
      // 沉浸式融合：body 内容延伸到底部导航区域下方（仅手机 dock 形态）
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
              // 隐藏时（动画到透明）忽略点击，防止透明区域仍可命中（需求：导航隐藏不可点击）
              ignoring: !_navVisible,
              child: GlassTabBar(
                index: _index,
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
