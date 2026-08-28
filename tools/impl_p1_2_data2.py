# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============ app_database.dart：v10 迁移 ============
p = r'D:\study_app\app\lib\data\app_database.dart'
s = open(p, encoding='utf-8').read()
old = """      await db.execute(
          'CREATE INDEX IF NOT EXISTS idx_questions_knowledge ON questions(knowledge_id)');
    }
  }

  /// v7：审题标记表（用户逐题审查时标记"需修改/待复核"）"""
new = """      await db.execute(
          'CREATE INDEX IF NOT EXISTS idx_questions_knowledge ON questions(knowledge_id)');
    }
    if (oldVersion < 10) {
      // v10: 模拟卷逐题回顾 —— answer_logs 加 user_answer（存用户作答快照）
      final acols = await db.rawQuery('PRAGMA table_info(answer_logs)');
      if (!acols.any((c) => c['name'] == 'user_answer')) {
        await db.execute('ALTER TABLE answer_logs ADD COLUMN user_answer TEXT');
      }
    }
  }

  /// v7：审题标记表（用户逐题审查时标记"需修改/待复核"）"""
assert old in s, 'v10 migration anchor'
s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(s)
print('[3] v10 migration ok')

# ============ quiz_repository_mock.dart：写 user_answer ============
p = r'D:\study_app\app\lib\data\quiz_repository_mock.dart'
s = open(p, encoding='utf-8').read()
old = """      for (final q in questions) {
        final grade = gradeQuestion(q, answers[q.id] ?? const <String>{});
        switch (grade) {
          case Grade.correct:
            correct++;
          case Grade.partial:
            partial++;
          case Grade.wrong:
            wrong++;
          case Grade.skip:
            skipped++;
        }
        await txn.insert(
          'answer_logs',
          AnswerLog(
            questionId: q.id,
            mode: 'mock',
            result: grade.name,
            timeMs: 0,
            answeredAt: submittedAt,
            sessionId: sessionId,
          ).toMap(),
        );"""
new = """      for (final q in questions) {
        final userSet = answers[q.id] ?? const <String>{};
        final grade = gradeQuestion(q, userSet);
        switch (grade) {
          case Grade.correct:
            correct++;
          case Grade.partial:
            partial++;
          case Grade.wrong:
            wrong++;
          case Grade.skip:
            skipped++;
        }
        await txn.insert(
          'answer_logs',
          AnswerLog(
            questionId: q.id,
            mode: 'mock',
            result: grade.name,
            timeMs: 0,
            answeredAt: submittedAt,
            sessionId: sessionId,
            userAnswer: _userAnswerText(q, userSet),
          ).toMap(),
        );"""
assert old in s, 'submit user_answer anchor'
s = s.replace(old, new, 1)

# 在 generateCompositePaper 前加 _userAnswerText 辅助
anchor = """  // ---------- 综合模拟卷（随机组卷，150 分制） ----------"""
addition = """  /// 用户作答快照文本：选择题为选项 key（如"A、B"），填空/简答为文本
  static String _userAnswerText(Question q, Set<String> user) {
    if (user.isEmpty) return '';
    final isChoice =
        q.type == QuestionType.singleChoice ||
        q.type == QuestionType.multiChoice ||
        q.type == QuestionType.trueFalse;
    if (!isChoice) return user.first;
    final keys = user.toList()..sort();
    return keys.join('、');
  }

  // ---------- 综合模拟卷（随机组卷，150 分制） ----------"""
assert anchor in s, 'helper anchor'
s = s.replace(anchor, addition, 1)
open(p, 'w', encoding='utf-8').write(s)
print('[4] submit user_answer ok')
