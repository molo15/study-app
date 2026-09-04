/// V3 iOS 全屏滑动返回 PageRoute
///
/// 用户需求："不需要在边界向右滑动仍可返回"——Flutter 默认 CupertinoPageRoute
/// 只支持左边缘滑动返回（gestureWidth 默认为屏幕宽度的 1/10，约 40pt）。
/// 本类扩展手势识别区域到全屏（或至少 90% 屏幕宽度），实现 iOS 17+ 风格的
/// 全屏交互式返回。
///
/// 阶段1实现：定义 IOSPageRoute 类骨架和接口，继承 CupertinoPageRoute
/// 保持标准 iOS 右滑入转场。全屏手势识别区域通过 _FullScreenBackGestureDetector
/// 包裹实现，使用 HorizontalDragGestureRecognizer 在全屏区域监听拖动手势。
///
/// 手势冲突处理（阶段4完善细节）：
/// - 与 ListView 水平滚动冲突：通过 gestureWidthRatio 控制识别区域
/// - 与滑动删除冲突：Dismissible 在其 item 区域优先消费
/// - 与选项卡切换冲突：TabBarView 通过 dragStartBehavior 控制
///
/// 用法：
/// ```dart
/// Navigator.of(context).push(IOSPageRoute(builder: (_) => NextPage()));
/// ```
library;

import 'package:flutter/cupertino.dart';
import 'package:flutter/gestures.dart';

/// 全屏滑动返回 PageRoute
///
/// 继承 CupertinoPageRoute，保持 iOS 标准右滑入转场效果。
/// 通过 [gestureWidthRatio] 控制返回手势识别区域占屏幕宽度的比例。
class IOSPageRoute<T> extends CupertinoPageRoute<T> {
  IOSPageRoute({
    required super.builder,
    super.settings,
    super.maintainState = true,
    super.fullscreenDialog = false,
    this.gestureWidthRatio = 0.4,
  });

  /// 手势识别区域占屏幕宽度的比例
  /// - 0.4 = 左侧 40% 屏宽（默认：兼顾"非边缘右滑"与页面内部横向交互）
  /// - 0.9 = 90% 屏幕宽度
  /// - 0.1 = iOS 默认（约 40pt 左边缘）
  final double gestureWidthRatio;

  @override
  Widget buildTransitions(
    BuildContext context,
    Animation<double> animation,
    Animation<double> secondaryAnimation,
    Widget child,
  ) {
    // 标准 iOS 页面切换效果（右滑入 + 下层缩放/淡出）
    final transitions =
        super.buildTransitions(context, animation, secondaryAnimation, child);

    // fullscreenDialog 或首页不启用返回手势
    if (fullscreenDialog || isFirst) {
      return transitions;
    }

    // 用全屏手势检测器包裹
    return LayoutBuilder(
      builder: (context, constraints) {
        final gestureWidth = constraints.maxWidth * gestureWidthRatio;
        return _FullScreenBackGestureDetector<T>(
          gestureWidth: gestureWidth,
          route: this,
          child: transitions,
        );
      },
    );
  }
}

/// 全屏返回手势检测器
///
/// 在屏幕左侧 [gestureWidth] 区域内监听水平拖动手势，
/// 触发时调用 route 的 pop 手势控制器。
///
/// 注意：CupertinoPageRoute 内部的 _CupertinoBackGestureController 是私有类，
/// 无法直接实例化。阶段1通过监听手势并调用 Navigator.maybePop 实现基础返回，
/// 阶段4将通过复制 CupertinoPageRoute 的手势控制器实现交互式拖拽返回。
class _FullScreenBackGestureDetector<T> extends StatefulWidget {
  const _FullScreenBackGestureDetector({
    required this.gestureWidth,
    required this.route,
    required this.child,
  });

  final double gestureWidth;
  final IOSPageRoute<T> route;
  final Widget child;

  @override
  State<_FullScreenBackGestureDetector<T>> createState() =>
      _FullScreenBackGestureDetectorState<T>();
}

class _FullScreenBackGestureDetectorState<T>
    extends State<_FullScreenBackGestureDetector<T>>
    with TickerProviderStateMixin {
  late final HorizontalDragGestureRecognizer _recognizer;
  bool _isBackGesture = false; // 方向锁定后接管（规避横向滚动冲突）
  double _dragOffset = 0; // 当前右移距离
  AnimationController? _snap; // 未超阈回弹动画

  /// 接管返回手势所需的最小右移距离（pt），避免误触
  static const double _lockThreshold = 12;
  /// 右滑速度阈值（pt/s）
  static const double _velocityThreshold = 300;
  /// 松手时决定是否 pop 的位移阈值（相对屏幕宽度比例）
  static const double _popRatio = 0.25;

  @override
  void initState() {
    super.initState();
    _recognizer = HorizontalDragGestureRecognizer()
      ..onStart = _handleDragStart
      ..onUpdate = _handleDragUpdate
      ..onEnd = _handleDragEnd
      ..onCancel = _handleDragCancel;
  }

  @override
  void dispose() {
    _snap?.dispose();
    _recognizer.dispose();
    super.dispose();
  }

  void _handleDragStart(DragStartDetails details) {
    // 弹窗/对话框（modal barrier）在场时禁用手势：bottom sheet 等 overlay 会盖住当前路由，
    // 此时右滑应作用于弹窗自身的关闭手势，而非页面返回。
    if (!widget.route.isCurrent || widget.route.animation?.status != AnimationStatus.completed) {
      _isBackGesture = false;
      _dragOffset = 0;
      return;
    }
    _isBackGesture = false;
    _dragOffset = 0;
    _snap?.dispose();
    _snap = null;
  }

  void _handleDragUpdate(DragUpdateDetails details) {
    final delta = details.primaryDelta ?? 0;
    if (!_isBackGesture) {
      // 方向锁定：左滑透传给内部横向滚动；右滑超阈值才接管为返回手势
      if (delta < 0) return;
      _dragOffset += delta;
      if (_dragOffset > _lockThreshold) {
        _isBackGesture = true;
        setState(() {});
      }
      return;
    }
    _dragOffset += delta;
    if (_dragOffset < 0) _dragOffset = 0;
    setState(() {});
  }

  void _handleDragEnd(DragEndDetails details) {
    if (!_isBackGesture) return;
    final v = details.primaryVelocity ?? 0;
    final width = MediaQuery.of(context).size.width;
    final threshold = width * _popRatio;
    if (v > _velocityThreshold || _dragOffset > threshold) {
      Navigator.of(context).pop();
      return;
    }
    // 未超阈：回弹到原位
    final from = _dragOffset;
    _snap = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 180),
    );
    _snap!.addListener(() {
      if (mounted) {
        setState(() => _dragOffset = from * (1 - _snap!.value));
      }
    });
    _snap!.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        _snap?.dispose();
        _snap = null;
        if (mounted) setState(() => _dragOffset = 0);
      }
    });
    _snap!.forward();
  }

  void _handleDragCancel() {
    _isBackGesture = false;
    _dragOffset = 0;
    _snap?.dispose();
    _snap = null;
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    final progress = width == 0
        ? 0.0
        : (_dragOffset / (width * 0.4)).clamp(0.0, 1.0);
    return Stack(
      children: [
        // 下层渐显：右侧露出暗色底（模拟下层页面压暗，随拖拽加深）
        Positioned.fill(
          child: IgnorePointer(
            child: ColoredBox(
              color: CupertinoColors.black.withValues(alpha: 0.35 * progress),
            ),
          ),
        ),
        Transform.translate(
          offset: Offset(_dragOffset, 0),
          child: widget.child,
        ),
        // 全屏手势识别区域：从左边缘延伸到 gestureWidth
        Positioned(
          left: 0,
          top: 0,
          bottom: 0,
          width: widget.gestureWidth,
          child: Listener(
            onPointerDown: (event) {
              // 变灰卡死根因修复：弹窗（bottom sheet/dialog/overlay）在场时，
              // 当前路由不再 isCurrent，此时不把指针加入手势识别器。
              // 原实现无条件 addPointer，HorizontalDragGestureRecognizer 会在竞技场中
              // 阻止 ModalBarrier 的 tap 识别，导致 barrier 出现但点不动、用户卡死。
              if (!widget.route.isCurrent) return;
              _recognizer.addPointer(event);
            },
            behavior: HitTestBehavior.translucent,
            child: const SizedBox.expand(),
          ),
        ),
      ],
    );
  }
}

/// 便捷函数：创建全屏返回路由
IOSPageRoute<T> iosPageRoute<T>(
  WidgetBuilder builder, {
  RouteSettings? settings,
  bool fullscreenDialog = false,
  double gestureWidthRatio = 0.4,
}) =>
    IOSPageRoute<T>(
      builder: builder,
      settings: settings,
      fullscreenDialog: fullscreenDialog,
      gestureWidthRatio: gestureWidthRatio,
    );
