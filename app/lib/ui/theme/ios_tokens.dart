/// V3 iOS 风格设计令牌（Design Tokens）
///
/// 全部值从 `docs/prototype/ui-v3-ios.html` 精确提取，禁止魔法数字。
/// 后续所有页面/组件必须通过本文件取色/取尺寸，不得硬编码。
///
/// 命名规范：
/// - 颜色：`IOSColors.of(context).xxx` 或 `IOSColors.light.xxx` / `IOSColors.dark.xxx`
/// - 字号：`IOSFontSize.xxx`
/// - 间距：`IOSSpacing.xxx`
/// - 圆角：`IOSRadius.xxx`
/// - 阴影：`IOSShadow.xxx`
/// - 断点：`IOSBreakpoint.xxx`
/// - 液态玻璃：`IOSGlass.xxx`
library;

import 'package:flutter/material.dart';

// ============================================================
// 颜色令牌（浅色 / 深色双套，规格 §2.1）
// ============================================================

/// iOS 系统色板（功能色，深浅通用）
abstract final class IOSSystemColors {
  static const Color blue = Color(0xFF007AFF);
  static const Color green = Color(0xFF34C759);
  static const Color orange = Color(0xFFFF9500);
  static const Color red = Color(0xFFFF3B30);
  static const Color purple = Color(0xFFAF52DE);
  static const Color teal = Color(0xFF5AC8FA);
  static const Color yellow = Color(0xFFFFCC00);
  static const Color indigo = Color(0xFF5856D6);
  static const Color pink = Color(0xFFFF2D55);
  static const Color mint = Color(0xFF00C7BE);
}

/// 五科功能色（科目图标区分，属功能色非装饰）
abstract final class IOSSubjectColors {
  static const Color education = IOSSystemColors.blue; // 教育学
  static const Color psychology = IOSSystemColors.orange; // 心理学
  static const Color ancientChinese = IOSSystemColors.green; // 古代汉语
  static const Color literaryTheory = IOSSystemColors.purple; // 文学理论
  static const Color politics = IOSSystemColors.red; // 政治

  // ---- 背题页科目渐变（浅 → 深），与首页纯色同源，统一在令牌管理 ----
  static const (Color, Color) modernChineseGrad = (
    Color(0xFF8FB1F0),
    Color(0xFF5B7FD0),
  ); // 现代汉语
  static const (Color, Color) ancientChineseGrad = (
    IOSSystemColors.green,
    Color(0xFF4BA38C),
  ); // 古代汉语
  static const (Color, Color) modernLitGrad = (
    Color(0xFFE8B26B),
    Color(0xFFD08A3E),
  ); // 现代文学
  static const (Color, Color) contemporaryLitGrad = (
    IOSSystemColors.purple,
    Color(0xFF8A5FC4),
  ); // 当代文学
  static const (Color, Color) ancientLitGrad = (
    Color(0xFFE08FB0),
    Color(0xFFC45F8A),
  ); // 古代文学
  static const (Color, Color) defaultGrad = (
    IOSSystemColors.blue,
    Color(0xFF4F7CD4),
  ); // 兜底
}

/// 颜色方案公共接口（浅色/深色均实现此接口）
///
/// 用法：`final colors = IOSColors.of(context); colors.primary`
abstract class IOSColorScheme {
  Color get bg;
  Color get card;
  Color get fill;
  Color get fill2;
  Color get text;
  Color get text2;
  Color get text3;
  Color get placeholder;
  Color get primary;
  Color get primaryPressed;
  Color get primaryBg;
  Color get success;
  Color get successBg;
  Color get warning;
  Color get warningBg;
  Color get danger;
  Color get dangerBg;
  Color get separator;
  Color get cardBorder;
  Color get glass;
  Color get glassThin;
  Color get glassBorder;
  Color get glassHighlight;
}

/// 浅色主题颜色集
class IOSLightColors implements IOSColorScheme {
  const IOSLightColors();

  @override
  final Color bg = const Color(0xFFF2F2F7);
  @override
  final Color card = const Color(0xFFFFFFFF);
  @override
  final Color fill = const Color(0xFFF2F2F7);
  @override
  final Color fill2 = const Color(0xFFE9E9EA);
  @override
  final Color text = const Color(0xFF000000);
  @override
  final Color text2 = const Color(0xFF8E8E93);
  @override
  final Color text3 = const Color(0xFFAEAEB2);
  @override
  final Color placeholder = const Color(0xFFC7C7CC);
  @override
  final Color primary = const Color(0xFF007AFF);
  @override
  final Color primaryPressed = const Color(0xFF0066D6);
  @override
  final Color primaryBg = const Color(0x1A007AFF);
  @override
  final Color success = IOSSystemColors.green;
  @override
  final Color successBg = const Color(0x1F34C759);
  @override
  final Color warning = IOSSystemColors.orange;
  @override
  final Color warningBg = const Color(0x24FF9500);
  @override
  final Color danger = IOSSystemColors.red;
  @override
  final Color dangerBg = const Color(0x1FFF3B30);
  @override
  final Color separator = const Color(0xFFC6C6C8);
  @override
  final Color cardBorder = const Color(0x0F000000);
  @override
  final Color glass = const Color(0x9EFFFFFF);
  @override
  final Color glassThin = const Color(0x8CFFFFFF);
  @override
  final Color glassBorder = const Color(0x66FFFFFF);
  @override
  final Color glassHighlight = const Color(0x59FFFFFF);
}

/// 深色主题颜色集
class IOSDarkColors implements IOSColorScheme {
  const IOSDarkColors();

  @override
  final Color bg = const Color(0xFF000000);
  @override
  final Color card = const Color(0xFF2C2C2E);
  @override
  final Color fill = const Color(0xFF1C1C1E);
  @override
  final Color fill2 = const Color(0xFF3A3A3C);
  @override
  final Color text = const Color(0xFFFFFFFF);
  @override
  final Color text2 = const Color(0xFF98989E);
  @override
  final Color text3 = const Color(0xFF6E6E73);
  @override
  final Color placeholder = const Color(0xFF48484A);
  @override
  final Color primary = const Color(0xFF0A84FF);
  @override
  final Color primaryPressed = const Color(0xFF409CFF);
  @override
  final Color primaryBg = const Color(0x290A84FF);
  @override
  final Color success = IOSSystemColors.green;
  @override
  final Color successBg = const Color(0x1F34C759);
  @override
  final Color warning = IOSSystemColors.orange;
  @override
  final Color warningBg = const Color(0x24FF9500);
  @override
  final Color danger = IOSSystemColors.red;
  @override
  final Color dangerBg = const Color(0x1FFF3B30);
  @override
  final Color separator = const Color(0xFF38383A);
  @override
  final Color cardBorder = const Color(0x14FFFFFF);
  @override
  final Color glass = const Color(0x9E1C1C1E);
  @override
  final Color glassThin = const Color(0x8C1C1C1E);
  @override
  final Color glassBorder = const Color(0x33FFFFFF);
  @override
  final Color glassHighlight = const Color(0x1FFFFFFF);
}

/// 统一颜色入口：按 Brightness 返回对应色集
///
/// 用法：
/// ```dart
/// final colors = IOSColors.of(context); // 自动适配深浅
/// colors.primary // 主色
/// ```
/// 或直接使用常量：
/// ```dart
/// IOSColors.light.primary // 浅色主色
/// IOSColors.dark.primary  // 深色主色
/// ```
abstract final class IOSColors {
  static const IOSColorScheme light = IOSLightColors();
  static const IOSColorScheme dark = IOSDarkColors();

  /// 根据当前主题亮度获取颜色集
  static IOSColorScheme of(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark ? dark : light;
}

// ============================================================
// 字号令牌（iOS 字体层级，规格 §2.2）
// ============================================================

abstract final class IOSFontSize {
  static const double largeTitle = 34;
  static const double title1 = 28;
  static const double title2 = 22;
  static const double title3 = 20;
  static const double body = 17;
  static const double callout = 16;
  static const double subheadline = 15;
  static const double footnote = 13;
  static const double caption1 = 12;
  static const double caption2 = 11;
}

/// iOS 字体层级（含字号+字重+行高），供 TextTheme 使用
class IOSTypography {
  const IOSTypography._();

  static TextStyle largeTitle({Color? color}) => TextStyle(
        fontSize: IOSFontSize.largeTitle,
        fontWeight: FontWeight.w700,
        height: 1.2,
        letterSpacing: 0.01 * IOSFontSize.largeTitle,
        color: color,
      );

  static TextStyle title1({Color? color}) => TextStyle(
        fontSize: IOSFontSize.title1,
        fontWeight: FontWeight.w700,
        height: 1.2,
        color: color,
      );

  static TextStyle title2({Color? color}) => TextStyle(
        fontSize: IOSFontSize.title2,
        fontWeight: FontWeight.w700,
        height: 1.2,
        color: color,
      );

  static TextStyle title3({Color? color}) => TextStyle(
        fontSize: IOSFontSize.title3,
        fontWeight: FontWeight.w600,
        height: 1.2,
        color: color,
      );

  static TextStyle headline({Color? color}) => TextStyle(
        fontSize: IOSFontSize.body,
        fontWeight: FontWeight.w600,
        height: 1.5,
        color: color,
      );

  static TextStyle body({Color? color}) => TextStyle(
        fontSize: IOSFontSize.body,
        fontWeight: FontWeight.w400,
        height: 1.5,
        color: color,
      );

  static TextStyle callout({Color? color}) => TextStyle(
        fontSize: IOSFontSize.callout,
        fontWeight: FontWeight.w400,
        height: 1.4,
        color: color,
      );

  static TextStyle subheadline({Color? color}) => TextStyle(
        fontSize: IOSFontSize.subheadline,
        fontWeight: FontWeight.w400,
        height: 1.4,
        color: color,
      );

  static TextStyle footnote({Color? color}) => TextStyle(
        fontSize: IOSFontSize.footnote,
        fontWeight: FontWeight.w400,
        height: 1.4,
        color: color,
      );

  static TextStyle caption1({Color? color}) => TextStyle(
        fontSize: IOSFontSize.caption1,
        fontWeight: FontWeight.w400,
        height: 1.3,
        color: color,
      );

  static TextStyle caption2({Color? color}) => TextStyle(
        fontSize: IOSFontSize.caption2,
        fontWeight: FontWeight.w400,
        height: 1.3,
        color: color,
      );
}

// ============================================================
// 间距令牌（8 的倍数，规格 §2.3）
// ============================================================

abstract final class IOSSpacing {
  static const double s4 = 4;
  static const double s8 = 8;
  static const double s12 = 12;
  static const double s16 = 16;
  static const double s20 = 20;
  static const double s24 = 24;
  static const double s32 = 32;
  static const double s40 = 40;
}

// ============================================================
// 圆角令牌（连续圆角体系，规格 §2.3）
// ============================================================

abstract final class IOSRadius {
  static const double lg = 18;
  static const double md = 16;
  static const double sm = 12;
  static const double xs = 10;
  static const double tag = 8;
  static const double pill = 999;
  static const double centerDial = 20;
}

// ============================================================
// 阴影令牌（克制，仅悬浮元素，规格 §2.4）
// ============================================================

class IOSShadow {
  const IOSShadow._();

  static List<BoxShadow> glass({bool dark = false}) => [
        BoxShadow(
          color: dark ? const Color(0x80000000) : const Color(0x1A000000),
          blurRadius: 32,
          offset: const Offset(0, 8),
        ),
      ];

  static List<BoxShadow> tab({bool dark = false}) => [
        BoxShadow(
          color: dark ? const Color(0x80000000) : const Color(0x1F000000),
          blurRadius: 32,
          offset: const Offset(0, 8),
        ),
      ];

  static List<BoxShadow> alert() => const [
        BoxShadow(
          color: Color(0x26000000),
          blurRadius: 48,
          offset: Offset(0, 16),
        ),
      ];

  static List<BoxShadow> primary() => const [
        BoxShadow(
          color: Color(0x4D007AFF),
          blurRadius: 24,
          offset: Offset(0, 8),
        ),
      ];
}

// ============================================================
// 液态玻璃令牌（规格 §2.5）
// ============================================================

abstract final class IOSGlass {
  static const double blurThin = 18;
  static const double blurRegular = 24;
  static const double blurThick = 32;
  static const double saturate = 180;
  static const double highlightHeightRatio = 0.4;
  static const double borderWidth = 0.5;
}

// ============================================================
// 断点令牌（规格 §3.5，与 responsive.dart 对齐）
// ============================================================

abstract final class IOSBreakpoint {
  static const double compactMax = 600;
  static const double mediumMax = 1200;
  static const double compactPadding = 16;
  static const double mediumPadding = 24;
  static const double expandedPadding = 32;
  static const double mediumContentMax = 760;
  static const double expandedContentMax = 920;
  static const double floatingBarMaxWidth = 680;
  static const double compactBarHorizontalInset = 48;
  static const double mediumBarHorizontalInset = 64;
}

// ============================================================
// 底部悬浮系统常量（规格 §3.3）
// ============================================================

abstract final class IOSFloatingBar {
  static const double tabBarHeight = 60;
  static const double actionBarHeight = 52;
  static const double bottomOffset = 20;
  static const double centerDialSize = 58;
  static const double centerDialRaise = 32;
  static const int centerDialZIndex = 60;
  static const double kTContentBottomInset = 80;
  static const double tabIconSize = 24;
  static const double tabLabelSize = 11;
}
