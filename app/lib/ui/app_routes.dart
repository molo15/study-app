/// 统一路由转场（界面切换优化）
///
/// 全局转场风格由 V3 iOS 设计系统统一为 iOS 式横向滑动；
/// 本文件提供统一的慢速时长与页面跳转入口，保证全 App 转场时长一致、可一处调整。
///
/// 继承 IOSPageRoute（CupertinoPageRoute 子类），自动获得全屏右滑返回手势
/// （gestureWidthRatio=0.4，左侧 40% 屏宽可触发返回）。
library;

import 'package:flutter/material.dart';

import 'theme/ios_page_route.dart';

/// 页面 push 转场时长（慢档）：400ms 正向 / 350ms 返回
const Duration routeDuration = Duration(milliseconds: 400);
const Duration routeReverseDuration = Duration(milliseconds: 350);

/// 统一页面路由：iOS 式横向滑动 + 全屏右滑返回 + 慢速过渡
///
/// 继承 [IOSPageRoute]（CupertinoPageRoute 子类），保留 Cupertino 标准转场动画，
/// 并通过 [IOSPageRoute.buildTransitions] 包裹全屏返回手势检测器。
class AppPageRoute<T> extends IOSPageRoute<T> {
  AppPageRoute({required super.builder, super.settings})
      : super(gestureWidthRatio: 0.4);

  @override
  Duration get transitionDuration => routeDuration;

  @override
  Duration get reverseTransitionDuration => routeReverseDuration;
}

/// 统一页面跳转：iOS 式横向滑动 + 全屏右滑返回 + 慢速过渡
Future<T?> pushPage<T>(BuildContext context, Widget page) {
  return Navigator.of(context).push(AppPageRoute<T>(builder: (_) => page));
}
