/// 多端断点系统（P2 响应式适配）
///
/// 按窗口宽度（而非设备类型）分档，遵循 Flutter 官方自适应最佳实践：
/// - compact（<600）：手机竖屏，内容区最大 560
/// - medium（600–1200）：平板 / 小桌面，内容区最大 760
/// - expanded（≥1200）：桌面宽屏，内容区最大 920
///
/// 内容区不再固定 560：宽屏时加宽以利用屏幕，同时保留限宽避免
/// 大屏上文字行过长、信息密度过低。
library;

import 'package:flutter/material.dart';

/// 布局档位
enum AppLayout { compact, medium, expanded }

/// 按窗口宽度判定布局档位（纯函数，可单元测试）
AppLayout appLayoutFromWidth(double w) {
  if (w >= 1200) return AppLayout.expanded;
  if (w >= 600) return AppLayout.medium;
  return AppLayout.compact;
}

/// 当前布局档位（按窗口宽度）
AppLayout appLayoutOf(BuildContext context) =>
    appLayoutFromWidth(MediaQuery.sizeOf(context).width);

/// 按窗口宽度给出内容区最大宽度（纯函数，可单元测试）
double contentWidthFromWidth(double w) {
  switch (appLayoutFromWidth(w)) {
    case AppLayout.compact:
      return 560;
    case AppLayout.medium:
      return 760;
    case AppLayout.expanded:
      return 920;
  }
}

/// 内容区最大宽度（断点分级）
double contentWidthOf(BuildContext context) =>
    contentWidthFromWidth(MediaQuery.sizeOf(context).width);

/// 是否为宽屏（≥medium），列表可切换多列布局
bool isWideScreen(BuildContext context) =>
    appLayoutOf(context) != AppLayout.compact;

/// 实际内容宽度：取「断点宽度」与「视口宽度」较小者（窄屏退回视口宽）
double effectiveContentWidth(BuildContext context) {
  final viewport = MediaQuery.sizeOf(context).width;
  final capped = contentWidthOf(context);
  return viewport < capped ? viewport : capped;
}
