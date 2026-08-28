# -*- coding: utf-8 -*-
p = r'D:\study_app\app\lib\ui\memorize_page.dart'
s = open(p, encoding='utf-8').read()

old = """          if (isChoice)
            for (final o in q.options)
              // 优先按选项 key 匹配；若 answer 存的是正确项文本（脏数据/旧包），按文本兜底匹配
              if (q.answer.contains(o.key) || q.answer.contains(o.text))
                Padding("""
new = """          if (isChoice)
            for (final o in _matchedOptions(q))
              Padding("""
assert old in s, 'old block not found'
s = s.replace(old, new)

# 在 _AnswerCard class 内加 helper：在 build 方法前插入
helper = """
  /// 正确项选项（防脏数据）：单选最多返回 1 项（优先 key 精确匹配，无则按文本取第一个）；
  /// 多选按选项顺序取 answer 命中的 key（去重），key 全不命中时按文本兜底。
  static List<QuestionOption> _matchedOptions(Question q) {
    if (q.type == QuestionType.singleChoice) {
      for (final o in q.options) {
        if (q.answer.contains(o.key)) return [o];
      }
      for (final o in q.options) {
        if (q.answer.contains(o.text)) return [o];
      }
      return const [];
    }
    final byKey = <QuestionOption>[];
    final seen = <String>{};
    for (final o in q.options) {
      if (q.answer.contains(o.key) && seen.add(o.key)) byKey.add(o);
    }
    if (byKey.isNotEmpty) return byKey;
    return q.options.where((o) => q.answer.contains(o.text)).toList();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final q = question;
    final isChoice = q.type == QuestionType.singleChoice ||
        q.type == QuestionType.multiChoice;
"""
old_build = """  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final q = question;
    final isChoice = q.type == QuestionType.singleChoice ||
        q.type == QuestionType.multiChoice;
"""
assert old_build in s, 'build block not found'
s = s.replace(old_build, helper, 1)

open(p, 'w', encoding='utf-8').write(s)
print('memorize_page _AnswerCard hardened')
