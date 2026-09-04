/// V3 iOS 风格统一动效系统
///
/// 所有动效常量集中在此文件，后续所有页面/组件禁止硬编码 Duration 或 Curve。
/// 必须引用本文件中的常量，保证全应用动效一致性。
///
/// 核心特性：
/// - 三档时长：fast / standard / slow
/// - iOS 标准缓动曲线 easeOutCubic
/// - iOS 弹簧参数
/// - Reduce Motion 支持：检测 MediaQuery.disableAnimations，开启时所有动效即时切换
/// - 静态驱动方法：animateWith / effectiveDuration / effectiveCurve
library;

import 'package:flutter/material.dart';

// ============================================================
// 时长常量（规格 §3.8）
// ============================================================

abstract final class IOSDuration {
  /// 快速 150ms：按钮按压、开关、Tab 切换、列表项高亮
  static const Duration fast = Duration(milliseconds: 150);

  /// 标准 250ms：页面切换、弹窗、分段控件、进度动画
  static const Duration standard = Duration(milliseconds: 250);

  /// 慢速 350ms：卡片翻转、大动画、弹窗底部弹簧滑入
  static const Duration slow = Duration(milliseconds: 350);

  /// 背题卡 3D 翻转 500ms（规格 §7）
  static const Duration cardFlip = Duration(milliseconds: 500);

  /// 页面进入 300ms（规格 §7：右滑入+淡入）
  static const Duration pageEnter = Duration(milliseconds: 300);

  /// 列表项按压高亮 100ms（规格 §3.4）
  static const Duration highlight = Duration(milliseconds: 100);

  /// 进度条 300ms ease-out（规格 §7）
  static const Duration progress = Duration(milliseconds: 300);

  /// 零时长（Reduce Motion 开启时使用）
  static const Duration zero = Duration.zero;
}

// ============================================================
// 缓动曲线常量
// ============================================================

abstract final class IOSCurve {
  /// iOS 标准缓动：cubic-bezier(0.25, 0.1, 0.25, 1) ≈ easeOutCubic
  static const Curve standard = Curves.easeOutCubic;

  /// 页面进入：cubic-bezier(0, 0, 0.2, 1)（规格 §7 pageIn）
  static const Curve pageEnter = Curves.easeOut;

  /// 弹窗底部弹簧：cubic-bezier(0.2, 0.9, 0.3, 1.2)（规格 sheetUp）
  static const Curve sheetSpring = Cubic(0.2, 0.9, 0.3, 1.2);

  /// 按钮按压回弹
  static const Curve press = Curves.easeOut;

  /// 淡入
  static const Curve fadeIn = Curves.easeOut;
}

// ============================================================
// 弹簧参数
// ============================================================

abstract final class IOSSpring {
  /// iOS 标准弹簧：mass 1, stiffness 300, damping 30
  static const SpringDescription description = SpringDescription(
    mass: 1,
    stiffness: 300,
    damping: 30,
  );

  /// 弹窗底部滑入弹簧模拟（规格 sheetUp .35s cubic-bezier(.2,.9,.3,1.2)）
  static const SpringDescription sheet = SpringDescription(
    mass: 1,
    stiffness: 220,
    damping: 18,
  );
}

// ============================================================
// Reduce Motion 支持 + 统一驱动
// ============================================================

/// 动效配置：根据 Reduce Motion 设置返回有效时长/曲线
///
/// 用法：
/// ```dart
/// final anim = IOSAnimations.of(context);
/// AnimatedContainer(
///   duration: anim.effectiveDuration(IOSDuration.standard),
///   curve: anim.effectiveCurve(IOSCurve.standard),
/// );
/// ```
class IOSAnimations {
  const IOSAnimations._({required this.reduceMotion});

  /// 是否开启减少动态效果
  final bool reduceMotion;

  /// 从 BuildContext 获取动效配置（检测 MediaQuery.disableAnimations）
  factory IOSAnimations.of(BuildContext context) {
    final reduce = MediaQuery.maybeDisableAnimationsOf(context) ?? false;
    return IOSAnimations._(reduceMotion: reduce);
  }

  /// 直接从 MediaQueryData 获取
  factory IOSAnimations.fromMediaQuery(MediaQueryData data) =>
      IOSAnimations._(reduceMotion: data.disableAnimations);

  /// 有效时长：Reduce Motion 开启时返回 Duration.zero
  Duration effectiveDuration(Duration nominal) =>
      reduceMotion ? Duration.zero : nominal;

  /// 有效曲线：Reduce Motion 开启时返回 Curves.linear（即时切换无视觉差）
  Curve effectiveCurve(Curve nominal) =>
      reduceMotion ? Curves.linear : nominal;

  /// 有效弹簧：Reduce Motion 开启时返回极硬弹簧（近似即时）
  SpringDescription effectiveSpring(SpringDescription nominal) =>
      reduceMotion
          ? const SpringDescription(mass: 1, stiffness: 10000, damping: 1000)
          : nominal;

  /// 统一驱动动画：创建一个使用标准时长和曲线的 AnimationController
  ///
  /// 注意：调用方负责 dispose controller。
  /// Reduce Motion 开启时 duration 为 0，动画瞬时完成。
  static AnimationController createController(
    TickerProvider vsync, {
    Duration duration = IOSDuration.standard,
    bool reduceMotion = false,
  }) {
    return AnimationController(
      vsync: vsync,
      duration: reduceMotion ? Duration.zero : duration,
    );
  }

  /// 统一驱动：返回一个 CurvedAnimation，使用 iOS 标准曲线
  static CurvedAnimation curved(
    Animation<double> parent, {
    Curve curve = IOSCurve.standard,
  }) =>
      CurvedAnimation(parent: parent, curve: curve);
}

// ============================================================
// 各场景标准动效配置（供后续 agent 直接引用）
// ============================================================

/// 场景化动效预设：每个场景定义时长+曲线，确保全应用一致
abstract final class IOSAnimationPresets {
  /// 按钮按压：scale 0.985→1.0，150ms
  static const (Duration, Curve) buttonPress = (
    IOSDuration.fast,
    IOSCurve.press,
  );

  /// 页面切换：右滑入+淡入，300ms
  static const (Duration, Curve) pageTransition = (
    IOSDuration.pageEnter,
    IOSCurve.pageEnter,
  );

  /// Tab 切换：内容淡入，150ms
  static const (Duration, Curve) tabSwitch = (
    IOSDuration.fast,
    IOSCurve.fadeIn,
  );

  /// 弹窗底部滑入：弹簧，350ms
  static const (Duration, Curve) sheetSlideUp = (
    IOSDuration.slow,
    IOSCurve.sheetSpring,
  );

  /// 背题卡 3D 翻转：500ms
  static const (Duration, Curve) cardFlip = (
    IOSDuration.cardFlip,
    IOSCurve.standard,
  );

  /// 列表项高亮：浅灰背景，100ms
  static const (Duration, Curve) listHighlight = (
    IOSDuration.highlight,
    IOSCurve.press,
  );

  /// 进度条动画：300ms ease-out
  static const (Duration, Curve) progress = (
    IOSDuration.progress,
    Curves.easeOut,
  );

  /// 导航栏滚动渐变：跟随滚动（无固定时长）
  static const (Duration, Curve) navFade = (
    IOSDuration.fast,
    IOSCurve.standard,
  );

  /// 开关切换：200ms
  static const (Duration, Curve) switchToggle = (
    Duration(milliseconds: 200),
    IOSCurve.standard,
  );
}
