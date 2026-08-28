# -*- coding: utf-8 -*-
f = r'D:\study_app\app\lib\ui\memorize_page.dart'
s = open(f, encoding='utf-8').read()

# 1) 强解包判空
old1 = """  Widget _buildCard(ThemeData theme) {
    final q = _current!;
    final total = widget.questions.length;"""
new1 = """  Widget _buildCard(ThemeData theme) {
    final q = _current;
    // 队列为空（极端边界）时回到总结视图，避免强解包崩溃（UI 审查 P2-6）
    if (q == null) return _buildSummary(theme);
    final total = widget.questions.length;"""
assert old1 in s, 'anchor1 not found'
s = s.replace(old1, new1)

# 2) 文案用户化
old2 = "'待回背 ${_pending.length} 张（不背单词式，稍后再推）'"
new2 = "'还有 ${_pending.length} 张没记住，稍后会再推给你'"
assert old2 in s, 'anchor2 not found'
s = s.replace(old2, new2)

open(f, 'w', encoding='utf-8').write(s)
print('memorize_page: 判空 + 文案 已改')
print('  _current! 残留:', s.count('_current!'))
