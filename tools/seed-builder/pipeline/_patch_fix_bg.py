# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ---------- 1) theme_controller.dart: 覆盖式横滑 + 下层淡出 ----------
p1 = r'D:\study_app\app\lib\ui\theme_controller.dart'
s1 = open(p1, encoding='utf-8').read()

old = """/// 覆盖式横滑转场（v1.1.3）：新页从右滑入，下层完全静止（不平移不淡出）。
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
}"""

new = """/// 覆盖式横滑转场（v1.1.3）：新页右滑入 + 下层淡出。
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
}"""

if old not in s1:
    print('ERROR: builder block not found in theme_controller')
    sys.exit(1)
s1 = s1.replace(old, new, 1)
open(p1, 'w', encoding='utf-8').write(s1)
print('OK: theme_controller builder -> cover slide + fade-out')

# ---------- 2) main.dart: 无背景图时垫不透明底色 ----------
p2 = r'D:\study_app\app\lib\main.dart'
s2 = open(p2, encoding='utf-8').read()

old2 = """    final hasImage = config.backgroundImagePath.isNotEmpty;
    if (!hasImage) return child;"""

new2 = """    final hasImage = config.backgroundImagePath.isNotEmpty;
    if (!hasImage) {
      // 无背景图：垫一层不透明底色，保证转场淡出/透明处底色统一（不闪白/黑）
      return Stack(
        fit: StackFit.expand,
        children: [
          ColoredBox(color: config.background),
          child,
        ],
      );
    }"""

if old2 not in s2:
    print('ERROR: background stack block not found in main.dart')
    sys.exit(1)
s2 = s2.replace(old2, new2, 1)
open(p2, 'w', encoding='utf-8').write(s2)
print('OK: main.dart background stack -> opaque base color')
