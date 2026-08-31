/// 主题配置模型 + 控制器（需求：用户高自由度定义主题）
///
/// 可配置项：主色、背景色、背景图（asset 路径，空 = 无）、卡片透明度、
/// 卡片圆角、深色模式。持久化到 settings 表（key: theme_config，JSON）。
library;

import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';

/// 解析 "#RRGGBB" / "#AARRGGBB"（审查 P2-4：严格校验长度与合法性）
Color parseHexColor(String hex, {Color fallback = const Color(0xFF00696D)}) {
  var value = hex.replaceFirst('#', '');
  if (value.length == 6) value = 'FF$value';
  if (value.length != 8) return fallback;
  final parsed = int.tryParse(value, radix: 16);
  if (parsed == null || (parsed & 0xFF000000) == 0) return fallback; // 全透明视为非法
  return Color(parsed);
}

String colorToHex(Color color) =>
    '#${color.toARGB32().toRadixString(16).padLeft(8, '0')}';

class AppThemeConfig {
  const AppThemeConfig({
    this.primaryColor = '#4F7CD4',
    this.backgroundColor = '#E7EEF7',
    this.backgroundImagePath = '',
    this.backgroundOpacity = 0.55,
    this.cardOpacity = 0.72,
    this.cornerRadius = 18.0,
    this.darkMode = false,
    this.hideStatusBar = false,
    this.reduceMotion = false,
    this.frost = true,
    this.frostBgTop = '#E7EEF7',
    this.frostBgBottom = '#C9D7EA',
    this.frostAccent = '#4F7CD4',
    this.glassOpacity = 0.62,
  });

  final String primaryColor;
  final String backgroundColor;

  /// 背景图片路径（本地文件路径，空 = 无背景图；需求：全局背景图）
  final String backgroundImagePath;

  /// 背景图透明度（0.0~1.0，需求：允许用户自己调节）
  final double backgroundOpacity;
  final double cardOpacity;
  final double cornerRadius;
  final bool darkMode;

  /// 隐藏系统状态栏（沉浸模式；默认显示）
  final bool hideStatusBar;

  /// 减少动效（P0 手感优化）：开启后非必要动效时长减半或跳过，
  /// 仅保留判题颜色反馈，照顾低性能设备与专注用户。默认关。
  final bool reduceMotion;

  /// 冷磨砂（UI v2）：开启后背景用渐变+光斑（FrostBackground），
  /// 卡片用毛玻璃（GlassCard），关闭则回退纯色/背景图旧逻辑。默认开。
  final bool frost;

  /// 冷磨砂背景渐变端点色（顶部 / 底部）
  final String frostBgTop;
  final String frostBgBottom;

  /// 冷磨砂强调色（冷青蓝）
  final String frostAccent;

  /// 玻璃强度（0~1，BackdropFilter 半透明层不透明度，供 GlassCard 使用）
  final double glassOpacity;

  Color get primary => parseHexColor(primaryColor);

  Color get background =>
      parseHexColor(backgroundColor, fallback: const Color(0xFFE7EEF7));

  Color get frostTop =>
      parseHexColor(frostBgTop, fallback: const Color(0xFFE7EEF7));

  Color get frostBottom =>
      parseHexColor(frostBgBottom, fallback: const Color(0xFFC9D7EA));

  Color get accent => parseHexColor(frostAccent, fallback: const Color(0xFF4F7CD4));

  /// UI v2 默认：冷磨砂
  factory AppThemeConfig.defaults() => AppThemeConfig();

  /// P1 主题预设：一键切换整套主题（冷磨砂/墨绿/纸米/经典蓝/夜间）
  static const List<(String, AppThemeConfig)> presets = [
    ('冷磨砂', AppThemeConfig(
      primaryColor: '#4F7CD4',
      backgroundColor: '#E7EEF7',
      frostBgTop: '#E7EEF7',
      frostBgBottom: '#C9D7EA',
      frostAccent: '#4F7CD4',
      glassOpacity: 0.62,
      cornerRadius: 18,
      frost: true,
    )),
    ('墨绿', AppThemeConfig(
      primaryColor: '#00696D',
      backgroundColor: '#F4F7F6',
      cornerRadius: 16,
      frost: false,
    )),
    ('纸米', AppThemeConfig(
      primaryColor: '#8B6F47',
      backgroundColor: '#F5EFE3',
      cornerRadius: 18,
      frost: false,
    )),
    ('经典蓝', AppThemeConfig(
      primaryColor: '#1A56DB',
      backgroundColor: '#F5F7FA',
      cornerRadius: 14,
      frost: false,
    )),
    ('夜间', AppThemeConfig(
      primaryColor: '#4DB6AC',
      backgroundColor: '#101418',
      darkMode: true,
      cornerRadius: 16,
      frost: false,
    )),
  ];

  AppThemeConfig copyWith({
    String? primaryColor,
    String? backgroundColor,
    String? backgroundImagePath,
    double? backgroundOpacity,
    double? cardOpacity,
    double? cornerRadius,
    bool? darkMode,
    bool? hideStatusBar,
    bool? reduceMotion,
    bool? frost,
    String? frostBgTop,
    String? frostBgBottom,
    String? frostAccent,
    double? glassOpacity,
  }) => AppThemeConfig(
    primaryColor: primaryColor ?? this.primaryColor,
    backgroundColor: backgroundColor ?? this.backgroundColor,
    backgroundImagePath: backgroundImagePath ?? this.backgroundImagePath,
    backgroundOpacity: backgroundOpacity ?? this.backgroundOpacity,
    cardOpacity: cardOpacity ?? this.cardOpacity,
    cornerRadius: cornerRadius ?? this.cornerRadius,
    darkMode: darkMode ?? this.darkMode,
    hideStatusBar: hideStatusBar ?? this.hideStatusBar,
    reduceMotion: reduceMotion ?? this.reduceMotion,
    frost: frost ?? this.frost,
    frostBgTop: frostBgTop ?? this.frostBgTop,
    frostBgBottom: frostBgBottom ?? this.frostBgBottom,
    frostAccent: frostAccent ?? this.frostAccent,
    glassOpacity: glassOpacity ?? this.glassOpacity,
  );

  Map<String, dynamic> toJson() => {
    'primaryColor': primaryColor,
    'backgroundColor': backgroundColor,
    'backgroundImagePath': backgroundImagePath,
    'backgroundOpacity': backgroundOpacity,
    'cardOpacity': cardOpacity,
    'cornerRadius': cornerRadius,
    'darkMode': darkMode,
    'hideStatusBar': hideStatusBar,
    'reduceMotion': reduceMotion,
    'frost': frost,
    'frostBgTop': frostBgTop,
    'frostBgBottom': frostBgBottom,
    'frostAccent': frostAccent,
    'glassOpacity': glassOpacity,
  };

  factory AppThemeConfig.fromJson(Map<String, dynamic> json) => AppThemeConfig(
    primaryColor: json['primaryColor'] as String? ?? '#4F7CD4',
    backgroundColor: json['backgroundColor'] as String? ?? '#E7EEF7',
    backgroundImagePath: json['backgroundImagePath'] as String? ?? '',
    backgroundOpacity: (json['backgroundOpacity'] as num?)?.toDouble() ?? 0.55,
    cardOpacity: (json['cardOpacity'] as num?)?.toDouble() ?? 0.72,
    cornerRadius: (json['cornerRadius'] as num?)?.toDouble() ?? 18.0,
    darkMode: json['darkMode'] as bool? ?? false,
    hideStatusBar: json['hideStatusBar'] as bool? ?? false,
    reduceMotion: json['reduceMotion'] as bool? ?? false,
    frost: json['frost'] as bool? ?? false,
    frostBgTop: json['frostBgTop'] as String? ?? '#E7EEF7',
    frostBgBottom: json['frostBgBottom'] as String? ?? '#C9D7EA',
    frostAccent: json['frostAccent'] as String? ?? '#4F7CD4',
    glassOpacity: (json['glassOpacity'] as num?)?.toDouble() ?? 0.62,
  );

  /// 由配置构建 ThemeData（迁移自 app_theme.dart，支持深色）
  ThemeData buildThemeData() {
    final brightness = darkMode ? Brightness.dark : Brightness.light;
    final scheme = ColorScheme.fromSeed(
      seedColor: primary,
      brightness: brightness,
      surface: darkMode ? const Color(0xFF121212) : const Color(0xFFFAFDFC),
    );
    final bg = darkMode ? const Color(0xFF101418) : background;
    // 冷磨砂或背景图时 Scaffold 用透明，让 FrostBackground/main.dart 背景层可见
    final effectiveBg = (frost || backgroundImagePath.isNotEmpty)
        ? Colors.transparent
        : bg;
    final cardColor = (darkMode ? const Color(0xFF1E2428) : Colors.white)
        .withValues(alpha: cardOpacity);
    // 中文字体：内置 NotoSansSC（OFL 授权），web 端避免依赖 Google Fonts CDN
    //（被墙导致文字不渲染，Phase 2.2 修复）；桌面/移动端同样统一观感。
    return ThemeData(
      colorScheme: scheme,
      useMaterial3: true,
      // Web 端用系统字体栈（中文回退到系统字体），省去 17.7MB NotoSansSC-VF.ttf 首屏下载（启动加载优化）；
      // io 端保留内置字体统一观感。
      fontFamily: 'NotoSansSC',
      scaffoldBackgroundColor: effectiveBg,
      appBarTheme: AppBarTheme(
        backgroundColor: effectiveBg,
        foregroundColor: scheme.onSurface,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.w700,
          color: scheme.onSurface,
        ),
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: cardColor,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(cornerRadius),
        ),
        margin: const EdgeInsets.symmetric(vertical: 6),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(cornerRadius * 0.75),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
        ),
      ),
      navigationBarTheme: NavigationBarThemeData(
        // 沉浸式融合：导航栏无独立底板，透明悬浮叠加在内容之上（需求）
        backgroundColor: Colors.transparent,
        elevation: 0,
        surfaceTintColor: Colors.transparent,
        indicatorColor: Colors.transparent, // 选中不用彩色指示器
        height: 68,
        labelTextStyle: WidgetStateProperty.resolveWith((states) {
          final selected = states.contains(WidgetState.selected);
          return TextStyle(
            fontSize: 12,
            fontWeight: selected ? FontWeight.w600 : FontWeight.w400,
            // 黑色系深浅区分选中/未选中（需求：不用彩色）
            color: darkMode
                ? (selected ? Colors.white : Colors.white54)
                : (selected
                      ? const Color(0xE6000000)
                      : const Color(0x73000000)),
          );
        }),
        iconTheme: WidgetStateProperty.resolveWith((states) {
          final selected = states.contains(WidgetState.selected);
          return IconThemeData(
            size: 22,
            color: darkMode
                ? (selected ? Colors.white : Colors.white54)
                : (selected
                      ? const Color(0xE6000000)
                      : const Color(0x73000000)),
          );
        }),
      ),
      chipTheme: ChipThemeData(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(cornerRadius * 0.5),
        ),
        side: BorderSide(color: scheme.outlineVariant),
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
      // 覆盖式横滑（v1.1.3）：新页右滑入，下层完全静止，消除转场时背景浮现其他页面；
      // 慢速由 app_routes.routeDuration 控制（400ms 正向 / 350ms 返回）
      pageTransitionsTheme: PageTransitionsTheme(
        builders: {
          TargetPlatform.android: const _CoverSlideTransitionsBuilder(),
          TargetPlatform.iOS: const _CoverSlideTransitionsBuilder(),
          TargetPlatform.windows: const _CoverSlideTransitionsBuilder(),
          TargetPlatform.macOS: const _CoverSlideTransitionsBuilder(),
          TargetPlatform.linux: const _CoverSlideTransitionsBuilder(),
        },
      ),
    );
  }
}

/// 统一间距常量（基础 4dp 栅格，见《界面UI改版设计方案》4.4 节）
///
/// 供各页面与共享组件复用，避免间距视觉细节漂移。
/// 命名示例：`space4` = 16dp（页面左右边距），`space6` = 24dp（大间距）。
abstract final class AppSpacing {
  /// 4dp
  static const double space1 = 4;

  /// 8dp
  static const double space2 = 8;

  /// 12dp
  static const double space3 = 12;

  /// 16dp（页面左右边距）
  static const double space4 = 16;

  /// 20dp
  static const double space5 = 20;

  /// 24dp
  static const double space6 = 24;

  /// 32dp
  static const double space8 = 32;

  /// 40dp
  static const double space10 = 40;
}

/// 统一圆角常量（见《界面UI改版设计方案》4.5 节）
///
/// 页面内圆角种类控制在三种以内，保持视觉一致。
abstract final class AppRadius {
  /// 页面主卡片：16dp
  static const double card = 16;

  /// 小标签 / 图标容器：8dp
  static const double small = 8;

  /// 输入框 / 按钮：12dp
  static const double input = 12;
}

final themeControllerProvider =
    AsyncNotifierProvider<ThemeController, AppThemeConfig>(ThemeController.new);

class ThemeController extends AsyncNotifier<AppThemeConfig> {
  @override
  Future<AppThemeConfig> build() async {
    final repo = await ref.watch(quizRepositoryProvider);
    final raw = await repo.setting('theme_config');
    if (raw == null) return AppThemeConfig.defaults();
    try {
      return AppThemeConfig.fromJson(jsonDecode(raw) as Map<String, dynamic>);
    } catch (_) {
      return AppThemeConfig.defaults();
    }
  }

  /// 应用新主题：持久化 + 全局刷新
  Future<void> apply(AppThemeConfig config) async {
    final repo = await ref.read(quizRepositoryProvider);
    await repo.setSetting('theme_config', jsonEncode(config.toJson()));
    state = AsyncData(config);
  }
}


/// 覆盖式横滑转场（v1.1.3）：新页右滑入 + 下层淡出。
///
/// - 新页（incoming）：从右侧覆盖式滑入，下层不平移（区别于 iOS 下层平移 1/3）。
/// - 下层（被覆盖方）：用 secondaryAnimation 驱动淡出（1→0），避免横滑过程中
///   左侧清晰露出下层页面内容（"背景浮现别的界面"问题，v1.1.3 复检修复）。
/// - 反向返回时：下层随之淡入回来，自然过渡。
class _CoverSlideTransitionsBuilder extends PageTransitionsBuilder {
  const _CoverSlideTransitionsBuilder();

  @override
  Widget buildTransitions<T>(
    PageRoute<T> route,
    BuildContext context,
    Animation<double> animation,
    Animation<double> secondaryAnimation,
    Widget child,
  ) {
    final curved = CurvedAnimation(
      parent: animation,
      curve: Curves.easeOutCubic,
    );
    // 新页：覆盖式右滑入（下层静止不平移）
    final slide = SlideTransition(
      position: Tween<Offset>(
        begin: const Offset(1, 0),
        end: Offset.zero,
      ).animate(curved),
      child: child,
    );
    // 下层：转场中被覆盖时淡出（新页 secondaryAnimation=0 → opacity=1，不受影响）
    return FadeTransition(
      opacity: Tween<double>(begin: 1, end: 0).animate(
        CurvedAnimation(parent: secondaryAnimation, curve: Curves.easeOut),
      ),
      child: slide,
    );
  }
}
