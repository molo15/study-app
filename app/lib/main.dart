import 'dart:async';

import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'data/app_database.dart';
import 'services/db_factory.dart';
import 'ui/router.dart';
import 'ui/theme_controller.dart';
import 'ui/responsive.dart';
import 'ui/widgets/frost_background.dart';
import 'ui/app_background_image.dart';
import 'ui/theme/ios_theme.dart';

/// 中文字体就绪信号：FontLoader 在 runApp 之后（引擎初始化完成后）异步注册
/// NotoSansSC，注册完成后自增，驱动整棵 Widget 树重建一次。
///
/// 为什么需要整树重建：CanvasKit 首帧布局时本地中文字体尚未注册，会走在线
/// 字形回退（fontFallbackBaseUrl 已同源化为快速 404），回退失败后引擎缓存
/// “缺中文字形”的布局结果；仅 ensureVisualUpdate 请求一帧不足以让先绘制的
/// 文本（如 AppBar 标题）重新匹配字形，表现为持续豆腐块。字体就绪后用变化
/// 的 key 重建整树，所有 RenderParagraph 重新 layout，此时字体已注册，标题
/// 与全部文本正常。字体只加载一次，故只重建一次；routerConfig 为全局单例，
/// 重建不丢路由状态。
final ValueNotifier<int> appFontRevision = ValueNotifier<int>(0);

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // 平台数据库工厂：io 默认 sqflite；web 切 sqflite_common_ffi_web（sqlite3.wasm）
  await initPlatformDatabaseFactory();
  // 启动优化：提前并行打开数据库（web 首次打开会加载
  // sqlite3.wasm，与首帧渲染并行，减少首屏等待）。
  // 失败不阻塞首帧（HomePage 加载态会重试，AppDatabase.open 已有自愈逻辑）。
  unawaited(AppDatabase.instance.then((_) {}, onError: (_) {}));
  // 中文字体（启动加载优化）：不再放入 pubspec fonts 声明（web 端 Flutter 会
  // 预下载 FontManifest 声明的全部字体，17.7MB VF 首屏必下载），改用 FontLoader
  // 运行时按平台加载子集字体——web 用 woff2（3MB），io 用 ttf（7MB 本地文件）。
  //
  // web 端仅加载 Regular(w400)：主题中所有文本统一用 w400（AppBar/Dialog 标题
  // 靠字号与颜色维持层次），避免粗体字重回退到 fonts.gstatic.com 在线分片
  // （国内被阻断 → 豆腐块）。unawaited 并行加载，index.html 已 preload 该字体，
  // 下载与引擎编译并行；注册完成后 ensureVisualUpdate 触发重绘。
  unawaited(_loadAppFont());
  // 边缘绘制 edge-to-edge：内容绘制到状态栏/导航栏区域后方，
  // 系统栏透明叠加（需求：边缘绘制 edge 到 edge；上滑唤出/隐藏由系统手势导航接管）
  if (!kIsWeb) {
    SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);
    SystemChrome.setSystemUIOverlayStyle(
      const SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        systemNavigationBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.dark,
        systemNavigationBarIconBrightness: Brightness.dark,
      ),
    );
  }
  runApp(ProviderScope(
    child: ValueListenableBuilder<int>(
      valueListenable: appFontRevision,
      builder: (context, revision, _) =>
          QuizApp(key: ValueKey<int>(revision)),
    ),
  ));
}

/// 后台加载中文字体，不阻塞首帧。加载完成后请求一帧重绘，
/// 使已渲染文本切换到 NotoSansSC（避免 fallback 到 Google Fonts CDN）。
///
/// web 端仅加载 Regular(w400) 子集：主题统一用 w400，粗体靠字号与颜色区分，
/// 避免粗体字重回退到在线字体（国内被阻断 → 豆腐块）。
/// io 端使用单一 ttf（系统 Skia 就近匹配并合成粗体）。
Future<void> _loadAppFont() async {
  try {
    final fontAsset = kIsWeb
        ? 'assets/fonts/NotoSansSC-subset.woff2'
        : 'assets/fonts/NotoSansSC-subset.ttf';
    final fontData = await rootBundle.load(fontAsset);
    final loader = FontLoader('NotoSansSC')
      ..addFont(Future.value(fontData));
    await loader.load();
    // 字体注册完成：请求一帧，确保首帧/已渲染文本使用新字体重绘
    WidgetsBinding.instance.ensureVisualUpdate();
    // web 端再自增修订号驱动整树重建一次（见 appFontRevision 说明），
    // 清除 CanvasKit 缓存的“缺中文字形”首帧布局；io 端本地字体毫秒级就绪、
    // 无在线回退，不需要重建。
    if (kIsWeb) appFontRevision.value++;
  } catch (e) {
    debugPrint('中文字体加载失败: $e');
  }
}

class QuizApp extends ConsumerWidget {
  const QuizApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final config =
        ref.watch(themeControllerProvider).value ?? AppThemeConfig.defaults();
    // V3 §3.6：有效深色 = 三段切换（system 跟随系统 / light 强制浅 / dark 强制深）
    final isDark = switch (config.themePreference) {
      ThemePreference.system =>
        MediaQuery.platformBrightnessOf(context) == Brightness.dark,
      ThemePreference.light => false,
      ThemePreference.dark => true,
    };
    // 隐藏状态栏开关（主题设置）：开启 → 沉浸模式（状态栏+导航栏隐藏，下滑临时唤出）
    if (!kIsWeb) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        SystemChrome.setEnabledSystemUIMode(
          config.hideStatusBar
              ? SystemUiMode.immersiveSticky
              : SystemUiMode.edgeToEdge,
        );
        // 系统栏图标跟随有效深色切换，避免深色主题下深色图标不可见（审查修复）
        SystemChrome.setSystemUIOverlayStyle(SystemUiOverlayStyle(
          statusBarColor: Colors.transparent,
          systemNavigationBarColor: Colors.transparent,
          statusBarIconBrightness: isDark ? Brightness.light : Brightness.dark,
          systemNavigationBarIconBrightness:
              isDark ? Brightness.light : Brightness.dark,
        ));
      });
    }
    return MaterialApp.router(
      title: '考研刷题',
      debugShowCheckedModeBanner: false,
      // V3 iOS 主题：light/dark 双主题，NoSplash 全局去水波纹
      // V2 主题（config.buildThemeData）保留在 theme_controller.dart 中，可随时回退
      theme: buildIOSLightTheme(),
      darkTheme: buildIOSDarkTheme(),
      // V3 §3.6：三段切换（system 跟随系统 / light 强制浅 / dark 强制深）
      themeMode: config.themeModeValue,
      builder: (context, child) =>
          _BackgroundStack(config: config, isDark: isDark, child: child!),
      routerConfig: appRouter,
    );
  }
}

/// 全局背景层（UI v2 沉浸原则）：放在 Navigator 最底层，
/// 所有 Tab 页与二级页（push 路由）共享同一背景，切换不跳背景。
///
/// 优先级：冷磨砂（渐变+光斑） > 背景图（+遮罩） > 纯色垫底。
///
/// Web 适配（Phase 2.2）：内容居中，最大宽度 560（手机布局不拉伸）；
/// 桌面/平板两侧露出共享背景；web 无本地背景图（`AppBackgroundImage` web 版为空）。
class _BackgroundStack extends StatelessWidget {
  const _BackgroundStack({
    required this.config,
    required this.isDark,
    required this.child,
  });

  final AppThemeConfig config;
  final bool isDark;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    // web 没有本地文件背景图概念，背景图仅 io 平台可用
    final hasImage = !kIsWeb && config.backgroundImagePath.isNotEmpty;
    Widget body;
    if (config.frost && !hasImage) {
      // 冷磨砂：渐变 + 漂浮光斑（全局共享，Tab 页与二级页统一）
      body = FrostBackground(config: config, child: child);
    } else if (!hasImage) {
      // 无背景图：垫一层不透明底色，保证转场淡出/透明处底色统一（不闪白/黑）
      body = Stack(
        fit: StackFit.expand,
        children: [
          ColoredBox(color: config.background),
          child,
        ],
      );
    } else {
      // 渐变遮罩颜色：深色模式下使用深色遮罩（如 #0F1214）且 alpha 更高，
      // 避免用户配置的浅色背景把背景图冲淡（需求：深色模式背景图遮罩）
      final overlayColor = isDark
          ? const Color(0xFF0F1214)
          : config.background;
      final overlayTopAlpha = isDark ? 0.96 : 0.92;
      final overlayBottomAlpha = isDark ? 0.92 : 0.85;
      body = Stack(
        fit: StackFit.expand,
        children: [
          // 本地文件背景图（全局应用），透明度由配置控制
          AppBackgroundImage(
            path: config.backgroundImagePath,
            opacity: config.backgroundOpacity,
          ),
          // 渐变遮罩保证前景可读性
          DecoratedBox(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  overlayColor.withValues(alpha: overlayTopAlpha),
                  overlayColor.withValues(alpha: overlayBottomAlpha),
                ],
              ),
            ),
          ),
          child,
        ],
      );
    }
    // Web/平板宽屏适配：内容顶部对齐 + 最大宽度（手机布局不拉伸）。
    // 修复 v2（Phase 2.2 审查 P3 二次修复）：上一版用
    // ConstrainedBox(maxWidth:560, maxHeight:viewportH) + SizedBox.expand，
    // 但 SizedBox.expand 内部是 tightFor(width:∞, height:∞)，与 maxHeight 求交后
    // 产生矛盾约束（minHeight:∞ > maxHeight:883）。web 无界根约束下 Scaffold
    // 布局错乱、底部导航浮在视口中部（浏览器实测确认）；widget 测试通过是因为
    // 测试环境根约束是 tight 有限，矛盾约束在 release 下不 assert、行为未定义。
    // 解法：改用显式 tight 尺寸（宽度取 min(560, 视口宽)，高度取视口高），
    // 消除矛盾约束，在 tight（测试/窄屏）与无界（web）两种约束下行为一致。
    final viewportSize = MediaQuery.sizeOf(context);
    final viewport = viewportSize.width;
    // 内容限宽需容纳侧边栏（平板 66 / 桌面 232），否则侧边栏挤占后内容区过窄，
    // 宽屏双列布局放不下会退回单列（P5 浏览器实测：题库双列退回单列）。
    // 手机（compact）无侧边栏，维持原 560/视口 限宽。
    final sidebarW = switch (appLayoutFromWidth(viewport)) {
      AppLayout.compact => 0.0,
      AppLayout.medium => 66.0,
      AppLayout.expanded => 232.0,
    };
    final baseW = contentWidthFromWidth(viewport) + sidebarW;
    final contentWidth = viewport < baseW ? viewport : baseW;
    return Align(
      alignment: Alignment.topCenter,
      child: SizedBox(
        width: contentWidth,
        height: viewportSize.height,
        child: body,
      ),
    );
  }
}
