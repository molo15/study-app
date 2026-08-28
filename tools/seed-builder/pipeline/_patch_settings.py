# -*- coding: utf-8 -*-
f = r'D:\study_app\app\lib\ui\settings_page.dart'
s = open(f, encoding='utf-8').read()

old1 = "import 'widgets/app_state_view.dart';\n\npart 'settings_theme_panel.dart';"
new1 = "import 'widgets/app_state_view.dart';\nimport 'app_toast.dart';\n\npart 'settings_theme_panel.dart';"
assert old1 in s, 'anchor1 not found'
s = s.replace(old1, new1)

old2 = """  void _toast(String text) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(text)));
  }"""
new2 = """  void _toast(String text) {
    if (!mounted) return;
    showAppToast(context, text);
  }"""
assert old2 in s, 'toast anchor not found'
s = s.replace(old2, new2)

open(f, 'w', encoding='utf-8').write(s)
print('settings_page: import + _toast 已改，showAppToast 引用', s.count('showAppToast'))
