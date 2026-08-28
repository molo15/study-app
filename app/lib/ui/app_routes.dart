/// 统一路由转场（界面切换优化）
///
/// 全局转场风格由 theme_controller 的 PageTransitionsTheme 统一为 iOS 式横向滑动；
/// 本文件提供统一的慢速时长与页面跳转入口，保证全 App 转场时长一致、可一处调整。
library;

import 'package:flutter/material.dart';

/// 页面 push 转场时长（慢档）：400ms 正向 / 350ms 返回
const Duration routeDuration = Duration(milliseconds: 400);
const Duration routeReverseDuration = Duration(milliseconds: 350);

/// 慢速 MaterialPageRoute：继承 Material 路由全部行为（含 theme 的 iOS 横向滑动转场），
/// 仅覆盖转场时长。
class AppPageRoute<T> extends MaterialPageRoute<T> {
  AppPageRoute({required super.builder, super.settings});

  @override
  Duration get transitionDuration => routeDuration;

  @override
  Duration get reverseTransitionDuration => routeReverseDuration;
}

/// 统一页面跳转：iOS 式横向滑动 + 慢速过渡
Future<T?> pushPage<T>(BuildContext context, Widget page) {
  return Navigator.of(context).push(AppPageRoute<T>(builder: (_) => page));
}
