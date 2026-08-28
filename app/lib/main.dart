import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'ui/root_page.dart';
import 'ui/theme_controller.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  // 边缘绘制 edge-to-edge：内容绘制到状态栏/导航栏区域后方，
  // 系统栏透明叠加（需求：边缘绘制 edge 到 edge；上滑唤出/隐藏由系统手势导航接管）
  SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      systemNavigationBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
      systemNavigationBarIconBrightness: Brightness.dark,
    ),
  );
  runApp(const ProviderScope(child: QuizApp()));
}

class QuizApp extends ConsumerWidget {
  const QuizApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final config =
        ref.watch(themeControllerProvider).value ?? AppThemeConfig.defaults();
    // 隐藏状态栏开关（主题设置）：开启 → 沉浸模式（状态栏+导航栏隐藏，下滑临时唤出）
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
        statusBarIconBrightness: config.darkMode ? Brightness.light : Brightness.dark,
        systemNavigationBarIconBrightness: config.darkMode ? Brightness.light : Brightness.dark,
      ));
    });
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

/// 全局背景层：支持背景图（本地文件）+ 透明度可调 + 渐变遮罩（需求：全局背景）
class _BackgroundStack extends StatelessWidget {
  const _BackgroundStack({required this.config, required this.child});

  final AppThemeConfig config;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final hasImage = config.backgroundImagePath.isNotEmpty;
    if (!hasImage) {
      // 无背景图：垫一层不透明底色，保证转场淡出/透明处底色统一（不闪白/黑）
      return Stack(
        fit: StackFit.expand,
        children: [
          ColoredBox(color: config.background),
          child,
        ],
      );
    }
    // 渐变遮罩颜色：深色模式下使用深色遮罩（如 #0F1214）且 alpha 更高，
    // 避免用户配置的浅色背景把背景图冲淡（需求：深色模式背景图遮罩）
    final overlayColor = config.darkMode
        ? const Color(0xFF0F1214)
        : config.background;
    final overlayTopAlpha = config.darkMode ? 0.96 : 0.92;
    final overlayBottomAlpha = config.darkMode ? 0.92 : 0.85;
    return Stack(
      fit: StackFit.expand,
      children: [
        // 本地文件背景图（全局应用），透明度由配置控制
        Image.file(
          File(config.backgroundImagePath),
          fit: BoxFit.cover,
          opacity: AlwaysStoppedAnimation(config.backgroundOpacity),
          // 文件不存在/不可读时优雅回退，不白屏
          errorBuilder: (_, _, _) => const SizedBox.shrink(),
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
}
