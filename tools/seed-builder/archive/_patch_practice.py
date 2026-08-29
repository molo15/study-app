# -*- coding: utf-8 -*-
f = r'D:\study_app\app\lib\ui\practice_page.dart'
s = open(f, encoding='utf-8').read()

# 1) import app_toast
old1 = "import 'glass_app_bar.dart';\n\npart 'practice_question_view.dart';"
new1 = "import 'glass_app_bar.dart';\nimport 'app_toast.dart';\n\npart 'practice_question_view.dart';"
assert old1 in s, 'import anchor not found'
s = s.replace(old1, new1)

# 2) 自动移出错题本（连续答对）：静默移除，不再弹横幅（用户诉求：减少频繁横幅）
old2 = """        await repo.removeFromWrongBook(question.id);
        if (mounted) {
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(const SnackBar(content: Text('已移出错题本（连续答对）')));
        }"""
new2 = """        // 连续答对自动移出：静默执行，不弹横幅打断练习节奏（UI 审查 P2-4）
        await repo.removeFromWrongBook(question.id);"""
assert old2 in s, 'auto-remove anchor not found'
s = s.replace(old2, new2)

# 3) 手动移出错题本：统一走 showAppToast
old3 = """    await repo.removeFromWrongBook(_current.id);
    if (mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('已移出错题本')));
    }"""
new3 = """    await repo.removeFromWrongBook(_current.id);
    if (mounted) {
      showAppToast(context, '已移出错题本');
    }"""
assert old3 in s, 'manual-remove anchor not found'
s = s.replace(old3, new3)

open(f, 'w', encoding='utf-8').write(s)
print('practice_page: 自动移除静默化 + 手动移除统一 toast 已改')
print('  showAppToast:', s.count('showAppToast'), '| 剩余 SnackBar 直接使用:', s.count('showSnackBar'))
