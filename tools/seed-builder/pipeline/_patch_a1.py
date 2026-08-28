# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path = r'D:\study_app\app\lib\ui\theme_controller.dart'
s = open(path, encoding='utf-8').read()

old = """      // 去安卓原生 Zoom 转场（UI 审查③）：统一淡入+上滑，200ms 曲线
      pageTransitionsTheme: PageTransitionsTheme(
        builders: {
          // 全平台统一 iOS 式横向滑动（含下层平移响应；慢速由 app_routes.routeDuration 控制）
          TargetPlatform.android: const CupertinoPageTransitionsBuilder(),
          TargetPlatform.iOS: const CupertinoPageTransitionsBuilder(),
          TargetPlatform.windows: const CupertinoPageTransitionsBuilder(),
          TargetPlatform.macOS: const CupertinoPageTransitionsBuilder(),
          TargetPlatform.linux: const CupertinoPageTransitionsBuilder(),
        },
      ),"""

new = """      // 覆盖式横滑（v1.1.3）：新页右滑入，下层完全静止，消除转场时背景浮现其他页面；
      // 慢速由 app_routes.routeDuration 控制（400ms 正向 / 350ms 返回）
      pageTransitionsTheme: PageTransitionsTheme(
        builders: {
          TargetPlatform.android: const _CoverSlideTransitionsBuilder(),
          TargetPlatform.iOS: const _CoverSlideTransitionsBuilder(),
          TargetPlatform.windows: const _CoverSlideTransitionsBuilder(),
          TargetPlatform.macOS: const _CoverSlideTransitionsBuilder(),
          TargetPlatform.linux: const _CoverSlideTransitionsBuilder(),
        },
      ),"""

if old not in s:
    print('ERROR: old block not found')
    sys.exit(1)
s = s.replace(old, new, 1)

# 添加自定义 builder：在文件末尾（AppThemeConfig 类后）追加
# 先定位：在最后一个类的结束处追加。简单方式：直接追加到文件末尾。
builder = '''

/// 覆盖式横滑转场（v1.1.3）：新页从右滑入，下层完全静止（不平移不淡出）。
///
/// 相比 CupertinoPageTransitionsBuilder（下层向左平移 1/3 并淡出，动画期间
/// 背景会透出上一页内容、显得卡顿），本 builder 只驱动新页（incoming）做
/// 横向滑动、不理会 secondaryAnimation，因此下层静止，背景不会浮现其他页面。
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
    return SlideTransition(
      position: Tween<Offset>(
        begin: const Offset(1, 0),
        end: Offset.zero,
      ).animate(curved),
      child: child,
    );
  }
}
'''

s += builder

open(path, 'w', encoding='utf-8').write(s)
print('OK: theme_controller.dart updated')

# 清理不再使用的 Cupertino import（若仅此处使用）
if s.count('CupertinoPageTransitionsBuilder') == 0:
    old_imp = "import 'package:flutter/cupertino.dart' show CupertinoPageTransitionsBuilder;\n"
    if old_imp in s:
        s2 = s.replace(old_imp, '', 1)
        open(path, 'w', encoding='utf-8').write(s2)
        print('OK: removed unused cupertino import')
