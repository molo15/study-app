# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============ 1. models.dart：AnswerLog 加 userAnswer ============
p = r'D:\study_app\app\lib\models\models.dart'
s = open(p, encoding='utf-8').read()
old = """  const AnswerLog({
    required this.questionId,
    required this.mode,
    required this.result,
    this.rating,
    required this.timeMs,
    required this.answeredAt,
    this.sessionId,
  });"""
new = """  const AnswerLog({
    required this.questionId,
    required this.mode,
    required this.result,
    this.rating,
    required this.timeMs,
    required this.answeredAt,
    this.sessionId,
    this.userAnswer,
  });"""
assert old in s, 'answerlog ctor'
s = s.replace(old, new, 1)

old = """  /// 关联模拟卷会话（仅 mock 模式，v3）
  final int? sessionId;

  Map<String, dynamic> toMap() => {
        'question_id': questionId,
        'mode': mode,
        'result': result,
        'rating': rating,
        'time_ms': timeMs,
        'answered_at': answeredAt,
        'session_id': sessionId,
      };"""
new = """  /// 关联模拟卷会话（仅 mock 模式，v3）
  final int? sessionId;

  /// 用户作答快照（v10，模拟卷逐题回顾用；选择题为选项 key 如"A、B"，填空/简答为文本）
  final String? userAnswer;

  Map<String, dynamic> toMap() => {
        'question_id': questionId,
        'mode': mode,
        'result': result,
        'rating': rating,
        'time_ms': timeMs,
        'answered_at': answeredAt,
        'session_id': sessionId,
        'user_answer': userAnswer,
      };"""
assert old in s, 'answerlog field'
s = s.replace(old, new, 1)

old = """        timeMs: row['time_ms'] as int,
        answeredAt: row['answered_at'] as int,
        sessionId: row['session_id'] as int?,
      );
}"""
new = """        timeMs: row['time_ms'] as int,
        answeredAt: row['answered_at'] as int,
        sessionId: row['session_id'] as int?,
        userAnswer: row['user_answer'] as String?,
      );
}"""
assert old in s, 'answerlog frommap'
s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(s)
print('[1] models ok')

# ============ 2. app_database.dart：version 10 + user_answer 列 ============
p = r'D:\study_app\app\lib\data\app_database.dart'
s = open(p, encoding='utf-8').read()
old = "  static const _dbVersion = 9;"
new = "  static const _dbVersion = 10;"
assert old in s, 'db version'
s = s.replace(old, new, 1)

old = """      CREATE TABLE answer_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id TEXT NOT NULL,
        mode TEXT NOT NULL,
        result TEXT NOT NULL,
        rating INTEGER,
        time_ms INTEGER NOT NULL,
        answered_at INTEGER NOT NULL,
        session_id INTEGER
      )"""
new = """      CREATE TABLE answer_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id TEXT NOT NULL,
        mode TEXT NOT NULL,
        result TEXT NOT NULL,
        rating INTEGER,
        time_ms INTEGER NOT NULL,
        answered_at INTEGER NOT NULL,
        session_id INTEGER,
        user_answer TEXT
      )"""
assert old in s, 'create answer_logs'
s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(s)
print('[2] db version+create ok')
