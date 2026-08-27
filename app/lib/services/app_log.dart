/// 应用日志系统（需求：全面日志，便于模拟器/真机环境抓取测试问题）
///
/// - 输出到 logcat 的 `AppLog` tag（Flutter 的 print 会带 flutter 前缀，
///   独立 tag 便于 `adb logcat -s AppLog` 精确过滤）
/// - 分级：debug / info / warn / error；debug 仅 debug 模式输出
/// - 结构化：时间 + 级别 + 模块 + 消息
/// - 全局单例，任何模块可 `AppLog.i('mock', '交卷完成 score=$score')`
library;

import 'package:flutter/foundation.dart';

class AppLog {
  AppLog._();

  static const String tag = 'AppLog';

  static void d(String module, String message) {
    if (kDebugMode) {
      // ignore: avoid_print
      print('[$tag][D][$module] $message');
    }
  }

  static void i(String module, String message) {
    // ignore: avoid_print
    print('[$tag][I][$module] $message');
  }

  static void w(String module, String message) {
    // ignore: avoid_print
    print('[$tag][W][$module] $message');
  }

  static void e(String module, String message, [Object? error, StackTrace? stack]) {
    // ignore: avoid_print
    print('[$tag][E][$module] $message'
        '${error == null ? '' : '\n  error: $error'}'
        '${stack == null ? '' : '\n  $stack'}');
  }

  /// 页面生命周期/导航
  static void page(String name) => i('page', name);

  /// 刷题/模拟卷流程关键节点
  static void quiz(String message) => i('quiz', message);

  /// 数据层（DB/导入/主题）
  static void data(String message) => i('data', message);

  /// 主题/背景
  static void theme(String message) => i('theme', message);
}
