# -*- coding: utf-8 -*-
f = r'D:\study_app\app\lib\ui\theme_controller.dart'
s = open(f, encoding='utf-8').read()

old1 = """      pageTransitionsTheme: PageTransitionsTheme(
        builders: {
          TargetPlatform.android: const _FadeUpPageTransitionsBuilder(),
          TargetPlatform.iOS: const CupertinoPageTransitionsBuilder(),
          TargetPlatform.windows: const _FadeUpPageTransitionsBuilder(),
          TargetPlatform.macOS: const CupertinoPageTransitionsBuilder(),
          TargetPlatform.linux: const _FadeUpPageTransitionsBuilder(),
        },
      ),"""
new1 = """      pageTransitionsTheme: PageTransitionsTheme(
        builders: {
          // 全平台统一 iOS 式横向滑动（含下层平移响应；慢速由 app_routes.routeDuration 控制）
          TargetPlatform.android: const CupertinoPageTransitionsBuilder(),
          TargetPlatform.iOS: const CupertinoPageTransitionsBuilder(),
          TargetPlatform.windows: const CupertinoPageTransitionsBuilder(),
          TargetPlatform.macOS: const CupertinoPageTransitionsBuilder(),
          TargetPlatform.linux: const CupertinoPageTransitionsBuilder(),
        },
      ),"""
assert old1 in s, 'anchor1 not found'
s = s.replace(old1, new1)

# 删除旧的 _FadeUpPageTransitionsBuilder 类
old2 = """
/// 自定义转场：淡入 + 轻微上滑（去安卓 Zoom 转场的原生感）
class _FadeUpPageTransitionsBuilder extends PageTransitionsBuilder {
  const _FadeUpPageTransitionsBuilder();

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
      reverseCurve: Curves.easeInCubic,
    );
    return FadeTransition(
      opacity: curved,
      child: SlideTransition(
        position: Tween<Offset>(
          begin: const Offset(0, 0.03),
          end: Offset.zero,
        ).animate(curved),
        child: child,
      ),
    );
  }
}
"""
assert old2 in s, 'anchor2 not found'
s = s.replace(old2, '')

open(f, 'w', encoding='utf-8').write(s)
print('theme_controller: 全平台 Cupertino 转场 + 已删 _FadeUpPageTransitionsBuilder')
print('  残留 _FadeUp:', s.count('_FadeUp'), '| Cupertino builder:', s.count('CupertinoPageTransitionsBuilder'))
