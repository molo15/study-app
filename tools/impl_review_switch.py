# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. QuizRepository 加 reviewModeEnabledKey 常量
p = r'D:\study_app\app\lib\data\quiz_repository.dart'
s = open(p, encoding='utf-8').read()
old = "  static const practiceTimerVisibleKey = 'show_practice_timer';"
new = ("  static const practiceTimerVisibleKey = 'show_practice_timer';\n"
       "  static const reviewModeEnabledKey = 'review_mode_enabled';")
assert old in s, 'key anchor'
s = s.replace(old, new)
open(p, 'w', encoding='utf-8').write(s)
print('[1] key ok')

# 2. export_helper.dart 移除硬编码 const
p = r'D:\study_app\app\lib\services\export_helper.dart'
s = open(p, encoding='utf-8').read()
old = """/// 审题标记功能（刷题页旗子 + 设置页导出入口）。
/// 常驻功能（用户决策 2026-08-24）：不再按构建隐藏，正式版同样可见。
const bool reviewModeEnabled = true;

"""
assert old in s, 'export_helper anchor'
s = s.replace(old, '')
open(p, 'w', encoding='utf-8').write(s)
print('[2] export_helper ok')

# 3. practice_page.dart：移除 show import，加 _reviewEnabled
p = r'D:\study_app\app\lib\ui\practice_page.dart'
s = open(p, encoding='utf-8').read()
old = "import '../services/export_helper.dart' show reviewModeEnabled;"
assert old in s, 'practice_page import anchor'
s = s.replace(old, '')
old = "  bool _showPracticeTimer = false;"
new = ("  bool _showPracticeTimer = false;\n"
       "  bool _reviewEnabled = false; // 审题标记开关（默认关，主题定制中开启）")
assert old in s, 'practice_page field anchor'
s = s.replace(old, new, 1)
old = """      final repo = await ref.read(quizRepositoryProvider);
      final showPracticeTimer = await repo.practiceTimerVisible();"""
new = """      final repo = await ref.read(quizRepositoryProvider);
      final showPracticeTimer = await repo.practiceTimerVisible();
      final reviewEnabled = await repo.reviewModeEnabled();"""
assert old in s, 'practice_page load anchor'
s = s.replace(old, new, 1)
# setState 里加 _reviewEnabled（找到 load 里的 setState）
old = """      if (!mounted) return;
      setState(() {
        _showPracticeTimer = showPracticeTimer;"""
new = """      if (!mounted) return;
      setState(() {
        _showPracticeTimer = showPracticeTimer;
        _reviewEnabled = reviewEnabled;"""
assert old in s, 'practice_page setState anchor'
s = s.replace(old, new, 1)
# _QuestionView 调用处传 showFlag
old = """        flagged: _flagged,
        onToggleFlag: _toggleFlag,
        showRating: _submitted,"""
new = """        flagged: _flagged,
        showFlag: _reviewEnabled,
        onToggleFlag: _toggleFlag,
        showRating: _submitted,"""
assert old in s, 'practice_page view call anchor'
s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(s)
print('[3] practice_page ok')

# 4. practice_question_view.dart：_QuestionView 加 showFlag，替换 reviewModeEnabled
p = r'D:\study_app\app\lib\ui\practice_question_view.dart'
s = open(p, encoding='utf-8').read()
old = """    required this.flagged,
    required this.onToggleFlag,"""
new = """    required this.flagged,
    required this.showFlag,
    required this.onToggleFlag,"""
assert old in s, 'pqv ctor anchor'
s = s.replace(old, new, 1)
old = """  final bool flagged;
  final Future<void> Function() onToggleFlag;"""
new = """  final bool flagged;

  /// 审题标记开关（关闭时隐藏旗子，默认关）
  final bool showFlag;
  final Future<void> Function() onToggleFlag;"""
assert old in s, 'pqv field anchor'
s = s.replace(old, new, 1)
old = "            if (reviewModeEnabled) ...["
new = "            if (showFlag) ...["
assert old in s, 'pqv usage anchor'
s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(s)
print('[4] practice_question_view ok')
