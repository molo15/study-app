/// 全局轻提示（统一 SnackBar 行为）
///
/// 复用 theme 的 SnackBarTheme floating 圆角样式；先隐藏当前条再展示新条
/// （防连续操作堆积横幅，对应"减少频繁弹横幅"诉求）；默认时长 2s。
library;

import 'package:flutter/material.dart';

void showAppToast(BuildContext context, String message, {Duration? duration}) {
  ScaffoldMessenger.of(context)
    ..hideCurrentSnackBar()
    ..showSnackBar(
      SnackBar(
        content: Text(message),
        duration: duration ?? const Duration(seconds: 2),
      ),
    );
}
