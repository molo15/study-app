# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'D:\study_app\app\lib\data\quiz_repository_mock.dart'
s = open(p, encoding='utf-8').read()

anchor = """  /// 历史成绩单（按卷）
  Future<List<MockSession>> mockSessions({String? paperId}) async {
    final where = paperId == null ? null : 'paper_id = ?';
    final rows = await _db.query(
      'mock_sessions',
      where: where,
      whereArgs: paperId == null ? null : [paperId],
      orderBy: 'submitted_at DESC',
      limit: 50,
    );
    return rows.map(MockSession.fromMap).toList();
  }
"""
addition = """  /// 历史成绩单（按卷）
  Future<List<MockSession>> mockSessions({String? paperId}) async {
    final where = paperId == null ? null : 'paper_id = ?';
    final rows = await _db.query(
      'mock_sessions',
      where: where,
      whereArgs: paperId == null ? null : [paperId],
      orderBy: 'submitted_at DESC',
      limit: 50,
    );
    return rows.map(MockSession.fromMap).toList();
  }

  /// 恢复某次模考会话的逐题回顾数据（历史成绩二次回看）：
  /// 从 answer_logs 按 session 读 user_answer 快照，还原 answers map。
  Future<({List<Question> questions, Map<String, Set<String>> answers})>
  mockSessionReview(int sessionId) async {
    final logs = await _db.query(
      'answer_logs',
      where: 'session_id = ?',
      whereArgs: [sessionId],
      orderBy: 'id',
    );
    final ids = <String>[
      for (final r in logs) r['question_id'] as String,
    ];
    final questions = await questionsByIds(ids);
    final typeById = {for (final q in questions) q.id: q.type};
    final answers = <String, Set<String>>{};
    for (final r in logs) {
      final qid = r['question_id'] as String;
      final ua = r['user_answer'] as String?;
      final type = typeById[qid];
      if (type == null) continue;
      if (ua == null || ua.isEmpty) {
        answers[qid] = <String>{};
        continue;
      }
      final isChoice =
          type == QuestionType.singleChoice ||
          type == QuestionType.multiChoice ||
          type == QuestionType.trueFalse;
      answers[qid] = isChoice ? ua.split('、').toSet() : <String>{ua};
    }
    return (questions: questions, answers: answers);
  }
"""
assert anchor in s, 'mockSessions anchor'
s = s.replace(anchor, addition, 1)
open(p, 'w', encoding='utf-8').write(s)
print('[1] mockSessionReview ok')
