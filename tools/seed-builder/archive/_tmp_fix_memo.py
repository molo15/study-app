# -*- coding: utf-8 -*-
"""背题存档：修复 analyze 问题"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ===== 1. quiz_repository.dart: QuizRepository 类加 kpKey/qKey static =====
p = r'D:\study_app\app\lib\data\quiz_repository.dart'
s = open(p, encoding='utf-8').read()
old = """  QuizRepository(super._db);

  // 与 UI 约定的静态常量/键（定义在 QuizRepository 上，供上层静态访问）"""
new = """  QuizRepository(super._db);

  // ---------- 背题存档 key（v11）----------

  /// 知识点卡 key
  static String kpKey(String knowledgeId) => 'kp:$knowledgeId';

  /// 题目卡 key
  static String qKey(String questionId) => 'q:$questionId';

  // 与 UI 约定的静态常量/键（定义在 QuizRepository 上，供上层静态访问）"""
assert old in s, 'repo anchor missing'
s = s.replace(old, new)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('quiz_repository.dart kpKey/qKey 已加')

# ===== 2. quiz_repository_memorize.dart: 移除 mixin 里的 static key + 修 firstIntValue =====
p2 = r'D:\study_app\app\lib\data\quiz_repository_memorize.dart'
s2 = open(p2, encoding='utf-8').read()

# 2a. 移除 mixin 内的 static kpKey/qKey
old_key = """  static const _table = 'memorize_progress';

  /// 知识点卡 key
  static String kpKey(String knowledgeId) => 'kp:$knowledgeId';

  /// 题目卡 key
  static String qKey(String questionId) => 'q:$questionId';
"""
new_key = """  static const _table = 'memorize_progress';
"""
assert old_key in s2, 'key anchor missing'
s2 = s2.replace(old_key, new_key)

# 2b. 修 firstIntValue 用法
old_fi = """    for (final r in rows) {
      final c = Sqflite.firstIntValue([r['c']]) ?? 0;
      if (r['state'] == 'mastered') {
        mastered = c;
      } else {
        learning += c;
      }
    }"""
new_fi = """    for (final r in rows) {
      final c = (r['c'] as num?)?.toInt() ?? 0;
      if (r['state'] == 'mastered') {
        mastered = c;
      } else {
        learning += c;
      }
    }"""
assert old_fi in s2, 'fi anchor missing'
s2 = s2.replace(old_fi, new_fi)

open(p2, 'w', encoding='utf-8', newline='').write(s2)
print('quiz_repository_memorize.dart 修复完成')
