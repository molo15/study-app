import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'services/db_factory.dart';
import 'ui/root_page.dart';
import 'ui/theme_controller.dart';
import 'ui/widgets/frost_background.dart';
import 'ui/app_background_image.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // 平台数据库工厂：io 默认 sqflite；web 切 sqflite_common_ffi_web（sqlite3.wasm）
  await initPlatformDatabaseFactory();
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
  runApp(const ProviderScope(child: QuizApp()));
}

class QuizApp extends ConsumerWidget {
  const QuizApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final config =
        ref.watch(themeControllerProvider).value ?? AppThemeConfig.defaults();
    // 隐藏状态栏开关（主题设置）：开启 → 沉浸模式（状态栏+导航栏隐藏，下滑临时唤出）
    if (!kIsWeb) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        SystemChrome.setEnabledSystemUIMode(
          config.hideStatusBar
              ? SystemUiMode.immersiveSticky
              : SystemUiMode.edgeToEdge,
        );
        // 系统栏图标跟随深色模式切换，避免深色主题下深色图标不可见（审查修复）
        SystemChrome.setSystemUIOverlayStyle(SystemUiOverlayStyle(
          statusBarColor: Colors.transparent,
          systemNavigationBarColor: Colors.transparent,
          statusBarIconBrightness:
              config.darkMode ? Brightness.light : Brightness.dark,
          systemNavigationBarIconBrightness:
              config.darkMode ? Brightness.light : Brightness.dark,
        ));
      });
    }
    return MaterialApp(
      title: '考研刷题',
      debugShowCheckedModeBanner: false,
      theme: config.buildThemeData(),
      darkTheme: config.buildThemeData(),
      themeMode: config.darkMode ? ThemeMode.dark : ThemeMode.light,
      builder: (context, child) =>
          _BackgroundStack(config: config, child: child!),
      home: const RootPage(),
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
  const _BackgroundStack({required this.config, required this.child});

  final AppThemeConfig config;
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
      final overlayColor = config.darkMode
          ? const Color(0xFF0F1214)
          : config.background;
      final overlayTopAlpha = config.darkMode ? 0.96 : 0.92;
      final overlayBottomAlpha = config.darkMode ? 0.92 : 0.85;
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
    // Web/平板宽屏适配：内容居中 + 最大宽度（手机布局不拉伸）
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 560),
        child: body,
      ),
    );
  }
}
