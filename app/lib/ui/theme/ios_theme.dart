/// V3 iOS 风格主题（lightTheme / darkTheme）
///
/// 基于 ThemeData 但去 Material 化：
/// - splashFactory: NoSplash.splashFactory（彻底去除水波纹）
/// - 统一 fontFamily（.SF Pro Display / .SF Pro Text，fallback 到系统默认）
/// - AppBarTheme 透明化、CardTheme 无阴影、ListTileTheme iOS 风格
/// - 所有颜色通过 IOSColors 令牌取色，禁止硬编码
///
/// 保留 V2 主题文件不删除，V3 主题独立可切换。
/// 通过 theme_controller 的 useV3 开关控制（阶段2接入设置页）。
library;

import 'package:flutter/material.dart';

import 'ios_animations.dart';
import 'ios_tokens.dart';

// ============================================================
// 字体
// ============================================================

/// iOS 字体栈：优先 SF Pro，fallback 到系统默认
///
/// 注意：实际项目中 SF Pro 仅在 Apple 平台可用，
/// 其他平台 fallback 到系统默认字体（Android: Roboto, Windows: Segoe UI）。
/// 中文字体由 main.dart 的 NotoSansSC 加载逻辑处理。
const String _kFontFamily = '.SF Pro Display';

// ============================================================
// 浅色主题
// ============================================================

ThemeData buildIOSLightTheme() {
  final colors = IOSColors.light;
  final textTheme = _buildTextTheme(colors.text, colors.text2, colors.text3);

  return ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    fontFamily: _kFontFamily,
    scaffoldBackgroundColor: colors.bg,

    // 彻底去除 Material 水波纹
    splashFactory: NoSplash.splashFactory,
    highlightColor: Colors.transparent,
    hoverColor: Colors.transparent,
    focusColor: Colors.transparent,
    splashColor: Colors.transparent,

    // 颜色方案
    colorScheme: ColorScheme.light(
      primary: colors.primary,
      onPrimary: Colors.white,
      secondary: colors.primary,
      surface: colors.card,
      onSurface: colors.text,
      error: colors.danger,
      onError: Colors.white,
      outline: colors.separator,
      outlineVariant: colors.cardBorder,
    ),

    // AppBar：透明、无 elevation、大标题风格
    appBarTheme: AppBarTheme(
      backgroundColor: Colors.transparent,
      foregroundColor: colors.text,
      elevation: 0,
      scrolledUnderElevation: 0,
      centerTitle: false,
      titleTextStyle: textTheme.titleLarge,
      iconTheme: IconThemeData(color: colors.primary, size: 22),
      actionsIconTheme: IconThemeData(color: colors.primary, size: 22),
    ),

    // 卡片：纯白、无阴影、16px 圆角
    cardTheme: CardThemeData(
      elevation: 0,
      color: colors.card,
      shadowColor: Colors.transparent,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(IOSRadius.md),
        side: BorderSide(color: colors.cardBorder, width: IOSGlass.borderWidth),
      ),
      margin: EdgeInsets.zero,
    ),

    // 分割线：0.5px
    dividerTheme: DividerThemeData(
      color: colors.separator,
      thickness: IOSGlass.borderWidth,
      space: IOSGlass.borderWidth,
    ),

    // 列表项：iOS 风格
    listTileTheme: ListTileThemeData(
      iconColor: colors.text2,
      textColor: colors.text,
      dense: false,
      contentPadding: const EdgeInsets.symmetric(
        horizontal: IOSSpacing.s16,
        vertical: IOSSpacing.s4,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(IOSRadius.sm),
      ),
      tileColor: Colors.transparent,
      selectedTileColor: colors.fill,
    ),

    // 文本主题
    textTheme: textTheme,
    primaryTextTheme: textTheme,

    // 按钮主题
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: colors.primary,
        textStyle: textTheme.bodyLarge,
        padding: const EdgeInsets.symmetric(
          horizontal: IOSSpacing.s16,
          vertical: IOSSpacing.s8,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(IOSRadius.xs),
        ),
      ),
    ),

    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: colors.primary,
        foregroundColor: Colors.white,
        textStyle: textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w600),
        padding: const EdgeInsets.symmetric(
          horizontal: IOSSpacing.s20,
          vertical: IOSSpacing.s12,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(IOSRadius.sm),
        ),
        elevation: 0,
      ),
    ),

    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: colors.primary,
        side: BorderSide(color: colors.separator),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(IOSRadius.sm),
        ),
      ),
    ),

    iconTheme: IconThemeData(color: colors.text, size: 24),
    primaryIconTheme: IconThemeData(color: colors.primary),

    // 输入框
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: colors.card,
      hintStyle: textTheme.bodyLarge?.copyWith(color: colors.placeholder),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(IOSRadius.sm),
        borderSide: BorderSide(color: colors.separator, width: IOSGlass.borderWidth),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(IOSRadius.sm),
        borderSide: BorderSide(color: colors.separator, width: IOSGlass.borderWidth),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(IOSRadius.sm),
        borderSide: BorderSide(color: colors.primary, width: 1),
      ),
      contentPadding: const EdgeInsets.symmetric(
        horizontal: IOSSpacing.s16,
        vertical: IOSSpacing.s12,
      ),
    ),

    // 弹窗：iOS 风格
    dialogTheme: DialogThemeData(
      backgroundColor: colors.card,
      surfaceTintColor: Colors.transparent,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(IOSRadius.lg),
        side: BorderSide(color: colors.cardBorder, width: IOSGlass.borderWidth),
      ),
      titleTextStyle: textTheme.titleMedium,
      contentTextStyle: textTheme.bodyLarge,
    ),

    bottomSheetTheme: BottomSheetThemeData(
      backgroundColor: colors.card,
      surfaceTintColor: Colors.transparent,
      elevation: 0,
      showDragHandle: false,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(IOSRadius.lg)),
      ),
    ),

    // 开关：Cupertino 风格
    switchTheme: SwitchThemeData(
      thumbColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) return Colors.white;
        return Colors.white;
      }),
      trackColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) return colors.success;
        return colors.fill2;
      }),
    ),

    // 滑块
    sliderTheme: SliderThemeData(
      activeTrackColor: colors.primary,
      inactiveTrackColor: colors.fill2,
      thumbColor: colors.primary,
      overlayColor: colors.primary.withValues(alpha: 0.12),
    ),

    // 进度条
    progressIndicatorTheme: ProgressIndicatorThemeData(
      color: colors.primary,
      linearTrackColor: colors.fill2,
      circularTrackColor: colors.fill2,
    ),

    // 页面切换：iOS 风格右滑入
    pageTransitionsTheme: const PageTransitionsTheme(
      builders: {
        TargetPlatform.android: _IOSPageTransitionsBuilder(),
        TargetPlatform.iOS: _IOSPageTransitionsBuilder(),
        TargetPlatform.windows: _IOSPageTransitionsBuilder(),
        TargetPlatform.macOS: _IOSPageTransitionsBuilder(),
        TargetPlatform.linux: _IOSPageTransitionsBuilder(),
      },
    ),

    // SnackBar：浮动风格
    snackBarTheme: SnackBarThemeData(
      behavior: SnackBarBehavior.floating,
      backgroundColor: colors.text.withValues(alpha: 0.85),
      contentTextStyle: textTheme.bodyMedium?.copyWith(color: colors.bg),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(IOSRadius.sm),
      ),
    ),

    // 底部导航：透明（V3 使用自定义 FloatingTabBar）
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: Colors.transparent,
      elevation: 0,
      surfaceTintColor: Colors.transparent,
      indicatorColor: Colors.transparent,
      height: IOSFloatingBar.tabBarHeight,
    ),

    // 芯片
    chipTheme: ChipThemeData(
      backgroundColor: colors.fill,
      labelStyle: textTheme.bodySmall?.copyWith(color: colors.text2),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(IOSRadius.pill),
      ),
      side: BorderSide.none,
    ),

    // 底部弹窗
    bottomAppBarTheme: const BottomAppBarThemeData(
      elevation: 0,
      color: Colors.transparent,
    ),
  );
}

// ============================================================
// 深色主题
// ============================================================

ThemeData buildIOSDarkTheme() {
  final colors = IOSColors.dark;
  final textTheme = _buildTextTheme(colors.text, colors.text2, colors.text3);

  return ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    fontFamily: _kFontFamily,
    scaffoldBackgroundColor: colors.bg,

    // 彻底去除 Material 水波纹
    splashFactory: NoSplash.splashFactory,
    highlightColor: Colors.transparent,
    hoverColor: Colors.transparent,
    focusColor: Colors.transparent,
    splashColor: Colors.transparent,

    colorScheme: ColorScheme.dark(
      primary: colors.primary,
      onPrimary: Colors.white,
      secondary: colors.primary,
      surface: colors.card,
      onSurface: colors.text,
      error: colors.danger,
      onError: Colors.white,
      outline: colors.separator,
      outlineVariant: colors.cardBorder,
    ),

    appBarTheme: AppBarTheme(
      backgroundColor: Colors.transparent,
      foregroundColor: colors.text,
      elevation: 0,
      scrolledUnderElevation: 0,
      centerTitle: false,
      titleTextStyle: textTheme.titleLarge,
      iconTheme: IconThemeData(color: colors.primary, size: 22),
      actionsIconTheme: IconThemeData(color: colors.primary, size: 22),
    ),

    cardTheme: CardThemeData(
      elevation: 0,
      color: colors.card,
      shadowColor: Colors.transparent,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(IOSRadius.md),
        side: BorderSide(color: colors.cardBorder, width: IOSGlass.borderWidth),
      ),
      margin: EdgeInsets.zero,
    ),

    dividerTheme: DividerThemeData(
      color: colors.separator,
      thickness: IOSGlass.borderWidth,
      space: IOSGlass.borderWidth,
    ),

    listTileTheme: ListTileThemeData(
      iconColor: colors.text2,
      textColor: colors.text,
      dense: false,
      contentPadding: const EdgeInsets.symmetric(
        horizontal: IOSSpacing.s16,
        vertical: IOSSpacing.s4,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(IOSRadius.sm),
      ),
      tileColor: Colors.transparent,
      selectedTileColor: colors.fill,
    ),

    textTheme: textTheme,
    primaryTextTheme: textTheme,

    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: colors.primary,
        textStyle: textTheme.bodyLarge,
        padding: const EdgeInsets.symmetric(
          horizontal: IOSSpacing.s16,
          vertical: IOSSpacing.s8,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(IOSRadius.xs),
        ),
      ),
    ),

    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: colors.primary,
        foregroundColor: Colors.white,
        textStyle: textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w600),
        padding: const EdgeInsets.symmetric(
          horizontal: IOSSpacing.s20,
          vertical: IOSSpacing.s12,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(IOSRadius.sm),
        ),
        elevation: 0,
      ),
    ),

    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: colors.primary,
        side: BorderSide(color: colors.separator),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(IOSRadius.sm),
        ),
      ),
    ),

    iconTheme: IconThemeData(color: colors.text, size: 24),
    primaryIconTheme: IconThemeData(color: colors.primary),

    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: colors.card,
      hintStyle: textTheme.bodyLarge?.copyWith(color: colors.placeholder),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(IOSRadius.sm),
        borderSide: BorderSide(color: colors.separator, width: IOSGlass.borderWidth),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(IOSRadius.sm),
        borderSide: BorderSide(color: colors.separator, width: IOSGlass.borderWidth),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(IOSRadius.sm),
        borderSide: BorderSide(color: colors.primary, width: 1),
      ),
      contentPadding: const EdgeInsets.symmetric(
        horizontal: IOSSpacing.s16,
        vertical: IOSSpacing.s12,
      ),
    ),

    dialogTheme: DialogThemeData(
      backgroundColor: colors.card,
      surfaceTintColor: Colors.transparent,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(IOSRadius.lg),
        side: BorderSide(color: colors.cardBorder, width: IOSGlass.borderWidth),
      ),
      titleTextStyle: textTheme.titleMedium,
      contentTextStyle: textTheme.bodyLarge,
    ),

    bottomSheetTheme: BottomSheetThemeData(
      backgroundColor: colors.card,
      surfaceTintColor: Colors.transparent,
      elevation: 0,
      showDragHandle: false,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(IOSRadius.lg)),
      ),
    ),

    switchTheme: SwitchThemeData(
      thumbColor: WidgetStateProperty.resolveWith((states) => Colors.white),
      trackColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) return colors.success;
        return colors.fill2;
      }),
    ),

    sliderTheme: SliderThemeData(
      activeTrackColor: colors.primary,
      inactiveTrackColor: colors.fill2,
      thumbColor: colors.primary,
      overlayColor: colors.primary.withValues(alpha: 0.12),
    ),

    progressIndicatorTheme: ProgressIndicatorThemeData(
      color: colors.primary,
      linearTrackColor: colors.fill2,
      circularTrackColor: colors.fill2,
    ),

    pageTransitionsTheme: const PageTransitionsTheme(
      builders: {
        TargetPlatform.android: _IOSPageTransitionsBuilder(),
        TargetPlatform.iOS: _IOSPageTransitionsBuilder(),
        TargetPlatform.windows: _IOSPageTransitionsBuilder(),
        TargetPlatform.macOS: _IOSPageTransitionsBuilder(),
        TargetPlatform.linux: _IOSPageTransitionsBuilder(),
      },
    ),

    snackBarTheme: SnackBarThemeData(
      behavior: SnackBarBehavior.floating,
      backgroundColor: colors.text.withValues(alpha: 0.85),
      contentTextStyle: textTheme.bodyMedium?.copyWith(color: colors.bg),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(IOSRadius.sm),
      ),
    ),

    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: Colors.transparent,
      elevation: 0,
      surfaceTintColor: Colors.transparent,
      indicatorColor: Colors.transparent,
      height: IOSFloatingBar.tabBarHeight,
    ),

    chipTheme: ChipThemeData(
      backgroundColor: colors.fill,
      labelStyle: textTheme.bodySmall?.copyWith(color: colors.text2),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(IOSRadius.pill),
      ),
      side: BorderSide.none,
    ),

    bottomAppBarTheme: const BottomAppBarThemeData(
      elevation: 0,
      color: Colors.transparent,
    ),
  );
}

// ============================================================
// 文本主题构建
// ============================================================

TextTheme _buildTextTheme(Color text, Color text2, Color text3) {
  return TextTheme(
    // 大标题 34 bold
    displayLarge: IOSTypography.largeTitle(color: text),
    // 标题1 28 bold
    displayMedium: IOSTypography.title1(color: text),
    // 标题2 22 bold
    displaySmall: IOSTypography.title2(color: text),
    // 标题3 20 semibold
    headlineMedium: IOSTypography.title3(color: text),
    headlineSmall: IOSTypography.headline(color: text),
    // 正文 17
    titleLarge: IOSTypography.headline(color: text),
    titleMedium: IOSTypography.body(color: text),
    titleSmall: IOSTypography.callout(color: text2),
    // body
    bodyLarge: IOSTypography.body(color: text),
    bodyMedium: IOSTypography.subheadline(color: text),
    bodySmall: IOSTypography.footnote(color: text2),
    // label
    labelLarge: IOSTypography.callout(color: text),
    labelMedium: IOSTypography.caption1(color: text2),
    labelSmall: IOSTypography.caption2(color: text3),
  );
}

// ============================================================
// iOS 页面切换动画（右滑入 + 下层淡出）
// ============================================================

class _IOSPageTransitionsBuilder extends PageTransitionsBuilder {
  const _IOSPageTransitionsBuilder();

  @override
  Widget buildTransitions<T>(
    PageRoute<T> route,
    BuildContext context,
    Animation<double> animation,
    Animation<double> secondaryAnimation,
    Widget child,
  ) {
    final anim = IOSAnimations.of(context);
    final curved = CurvedAnimation(
      parent: animation,
      curve: anim.effectiveCurve(IOSCurve.standard),
    );

    // 新页：从右侧滑入
    final slide = SlideTransition(
      position: Tween<Offset>(
        begin: const Offset(1, 0),
        end: Offset.zero,
      ).animate(curved),
      child: FadeTransition(
        opacity: Tween<double>(begin: 0.85, end: 1.0).animate(curved),
        child: child,
      ),
    );

    // 下层：转场中淡出
    return FadeTransition(
      opacity: Tween<double>(begin: 1, end: 0.85).animate(
        CurvedAnimation(
          parent: secondaryAnimation,
          curve: anim.effectiveCurve(IOSCurve.fadeIn),
        ),
      ),
      child: slide,
    );
  }
}
