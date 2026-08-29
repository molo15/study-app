# -*- coding: utf-8 -*-
f = r'D:\study_app\app\lib\ui\question_manage_page.dart'
s = open(f, encoding='utf-8').read()

# 1) import app_toast
old1 = "import 'glass_app_bar.dart';\nimport 'practice_page.dart' show typeColor, typeLabel;"
new1 = "import 'glass_app_bar.dart';\nimport 'app_toast.dart';\nimport 'practice_page.dart' show typeColor, typeLabel;"
assert old1 in s, 'import anchor not found'
s = s.replace(old1, new1)

# 2) _toast -> showAppToast
old2 = """  void _toast(String msg) {
    if (!mounted) return;
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(msg), duration: const Duration(seconds: 2)));
  }"""
new2 = """  void _toast(String msg) {
    if (!mounted) return;
    showAppToast(context, msg);
  }"""
assert old2 in s, 'toast anchor not found'
s = s.replace(old2, new2)

# 3) 裸 TextStyle fontSize:11 -> labelSmall
old3 = "        style: TextStyle(fontSize: 11, color: typeColor(context, type)),"
new3 = "        style: Theme.of(context).textTheme.labelSmall?.copyWith(color: typeColor(context, type)),"
assert old3 in s, 'style anchor not found'
s = s.replace(old3, new3)

open(f, 'w', encoding='utf-8').write(s)
print('question_manage_page: import + _toast + 裸样式 已改')
print('  showAppToast:', s.count('showAppToast'), '| 残留裸TextStyle(fontSize:', s.count('TextStyle(fontSize: 11'))
