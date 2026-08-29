import 'package:flutter/material.dart';

/// 全局动效时长与曲线常量（P0 手感优化）
///
/// 所有自定义动效应引用此处常量，避免各页面硬编码时长漂移。
/// reduceMotion 开启时，调用方应将时长减半或跳过非必要动效。
abstract final class AppAnim {
  /// 点按反馈（按下）
  static const Duration press = Duration(milliseconds: 100);

  /// 点按反馈（抬起回弹）
  static const Duration release = Duration(milliseconds: 150);

  /// 判题反馈（颜色/缩放）
  static const Duration grade = Duration(milliseconds: 200);

  /// 错误抖动
  static const Duration shake = Duration(milliseconds: 320);

  /// 卡片/解析滑入
  static const Duration slideIn = Duration(milliseconds: 250);

  /// 标准曲线
  static const Curve standard = Curves.easeOutCubic;

  /// 弹性曲线（判题正确放大）
  static const Curve elastic = Curves.elasticOut;

  /// 回弹曲线（选中弹动）
  static const Curve bounce = Curves.easeOutBack;
}
