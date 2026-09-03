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
    this.gestureWidthRatio = 1.0,
  });

  /// 手势识别区域占屏幕宽度的比例
  /// - 1.0 = 全屏（默认，用户需求）
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
    extends State<_FullScreenBackGestureDetector<T>> {
  late final HorizontalDragGestureRecognizer _recognizer;
  bool _gestureActive = false;

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
    _recognizer.dispose();
    super.dispose();
  }

  void _handleDragStart(DragStartDetails details) {
    _gestureActive = true;
  }

  void _handleDragUpdate(DragUpdateDetails details) {
    // 阶段1：仅记录手势，阶段4实现交互式拖拽
    // CupertinoPageRoute 内部已有手势控制器，此处不重复驱动
  }

  void _handleDragEnd(DragEndDetails details) {
    _gestureActive = false;
    // 阶段1：向右快速滑动时触发 pop
    // 阶段4：根据拖拽进度和速度决定是否完成返回
    if (details.primaryVelocity != null && details.primaryVelocity! > 300) {
      Navigator.of(context).maybePop();
    }
  }

  void _handleDragCancel() {
    _gestureActive = false;
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        widget.child,
        // 全屏手势识别区域：从左边缘延伸到 gestureWidth
        Positioned(
          left: 0,
          top: 0,
          bottom: 0,
          width: widget.gestureWidth,
          child: Listener(
            onPointerDown: (event) {
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
  double gestureWidthRatio = 1.0,
}) =>
    IOSPageRoute<T>(
      builder: builder,
      settings: settings,
      fullscreenDialog: fullscreenDialog,
      gestureWidthRatio: gestureWidthRatio,
    );
