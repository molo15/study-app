# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\study_app\app\lib\ui\practice_page.dart'
s = open(p, encoding='utf-8').read()

# 1. 加 import（在 glass_app_bar.dart 之前）
s = s.replace(
    "import 'glass_app_bar.dart';",
    "import 'widgets/animation_constants.dart';\n"
    "import 'widgets/pressable_card.dart';\n"
    "import 'theme_controller.dart';\n\n"
    "import 'glass_app_bar.dart';"
)

# 2. 在 _QuestionView 调用处加 reduceMotion 参数
# 先找到 body: _QuestionView( 那一段，在 question: _current, 之前加 reduceMotion
s = s.replace(
    "      body: _QuestionView(\n"
    "        question: _current,",
    "      body: _QuestionView(\n"
    "        reduceMotion: _reduceMotion,\n"
    "        question: _current,"
)

# 3. 在 build 方法里加 _reduceMotion 计算。
# 找到 Widget build(BuildContext context) { 之后，在 return Scaffold 之前加。
# 用一个独特的锚点：_PracticePageState 的 build 里有 _loading 判断
old_build_anchor = "  @override\n  Widget build(BuildContext context) {\n    final theme = Theme.of(context);"
if old_build_anchor in s:
    s = s.replace(
        old_build_anchor,
        "  @override\n  Widget build(BuildContext context) {\n"
        "    final theme = Theme.of(context);\n"
        "    // P0 手感优化：减少动效开关（主题配置持久化）\n"
        "    final _reduceMotion = ref.watch(themeControllerProvider).valueOrNull?.reduceMotion ?? false;"
    )
    print('build 锚点匹配成功')
else:
    print('WARNING: build 锚点未匹配，尝试查找...')
    # 找 build 方法
    import re
    m = re.search(r'Widget build\(BuildContext context\) \{', s)
    if m:
        print('找到 build 在位置', m.start())
        print('上下文:', repr(s[m.start():m.start()+120]))

open(p, 'w', encoding='utf-8', newline='').write(s)
print('import 含 animation_constants:', "widgets/animation_constants.dart" in s)
print('import 含 theme_controller:', "import 'theme_controller.dart';" in s)
print('_reduceMotion 计算:', '_reduceMotion = ref.watch' in s)
print('_QuestionView 传 reduceMotion:', 'reduceMotion: _reduceMotion,' in s)
