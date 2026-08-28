# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============ 1. quiz_repository_mock.dart：加权计分 + 随机组卷 ============
p = r'D:\study_app\app\lib\data\quiz_repository_mock.dart'
s = open(p, encoding='utf-8').read()

# (1a) submitMockSession 加 pointsByType 加权计分
old = """  /// 模拟卷交卷：单事务原子写入（审查 P1-4）
  /// 插成绩单占位 → 逐题日志（mode=mock, session_id）→ 回填汇总，返回完整会话
  Future<MockSession> submitMockSession({
    required String paperId,
    required int startedAt,
    required int durationMin,
    required List<Question> questions,
    required Map<String, Set<String>> answers,
    required int submittedAt,
  }) async {
    var correct = 0, partial = 0, wrong = 0, skipped = 0;"""
new = """  /// 模拟卷交卷：单事务原子写入（审查 P1-4）
  /// 插成绩单占位 → 逐题日志（mode=mock, session_id）→ 回填汇总，返回完整会话
  /// [pointsByType] 提供时按题型加权计分（综合卷 150 分制）：正确满分、部分正确半分；
  /// 为空时保持百分制（正确数/总题数×100），兼容单科固定卷。
  Future<MockSession> submitMockSession({
    required String paperId,
    required int startedAt,
    required int durationMin,
    required List<Question> questions,
    required Map<String, Set<String>> answers,
    required int submittedAt,
    Map<QuestionType, int>? pointsByType,
  }) async {
    var correct = 0, partial = 0, wrong = 0, skipped = 0;"""
assert old in s, 'submit anchor'
s = s.replace(old, new, 1)

# (1b) 交卷加权计分逻辑替换
old = """      final score = questions.isEmpty
          ? 0
          : (correct * 100 / questions.length).round();
      await txn.update("""
new = """      late final int score;
      if (pointsByType == null || pointsByType.isEmpty) {
        score = questions.isEmpty
            ? 0
            : (correct * 100 / questions.length).round();
      } else {
        // 150 分制加权：正确满分、部分正确半分
        var gained = 0;
        var total = 0;
        for (final q in questions) {
          final pts = pointsByType[q.type] ?? 1;
          total += pts;
          final g = gradeQuestion(q, answers[q.id] ?? const <String>{});
          if (g == Grade.correct) {
            gained += pts;
          } else if (g == Grade.partial) {
            gained += (pts / 2).round();
          }
        }
        score = total == 0 ? 0 : gained;
      }
      await txn.update("""
assert old in s, 'score anchor'
s = s.replace(old, new, 1)

# (1c) 返回的 MockSession score 也要用加权（保持与落库一致）
old = """      score: questions.isEmpty ? 0 : (correct * 100 / questions.length).round(),
      submittedAt: submittedAt,
    );
  }"""
new = """      score: pointsByType == null || pointsByType.isEmpty
          ? (questions.isEmpty ? 0 : (correct * 100 / questions.length).round())
          : score,
      submittedAt: submittedAt,
    );
  }"""
assert old in s, 'return score anchor'
s = s.replace(old, new, 1)

# (1d) 文件末尾追加随机组卷方法（在 mixin 结尾前）
anchor = """  /// 保存模拟卷成绩单，返回会话 id（调用方随后写 answer_logs 并回填汇总）"""
addition = """  // ---------- 综合模拟卷（随机组卷，150 分制） ----------

  /// 综合卷学科抽题模板：{bankId: {type: 题量}}
  /// 无写作、无论述（论述并入简答）。分值：单选1×30、多选2×10、填空1×20、简答10×8=150。
  static const Map<String, Map<String, int>> compositeTemplate = {
    'bank-xiandai-hanyu': {
      'single_choice': 11,
      'multi_choice': 4,
      'blank': 8,
      'short_answer': 3,
    },
    'bank-gudai-hanyu': {
      'single_choice': 11,
      'multi_choice': 3,
      'blank': 8,
      'short_answer': 3,
    },
    'bank-zhongguo-xiandai-wenxue': {
      'single_choice': 3,
      'multi_choice': 1,
      'blank': 2,
      'short_answer': 1,
    },
    'bank-zhongguo-dangdai-wenxue': {
      'single_choice': 3,
      'multi_choice': 1,
      'blank': 1,
      'short_answer': 1,
    },
    'bank-zhongguo-gudai-wenxue': {
      'single_choice': 2,
      'multi_choice': 1,
      'blank': 1,
      'short_answer': 0,
    },
  };

  /// 综合卷题型分值（150 分制）
  static const Map<QuestionType, int> compositePoints = {
    QuestionType.singleChoice: 1,
    QuestionType.multiChoice: 2,
    QuestionType.blank: 1,
    QuestionType.shortAnswer: 10,
  };

  /// 综合卷：按模板从 5 科随机抽题（卷内不重复）。
  /// 某科某题型题量不足时按实际可得题量抽（不报错），保证可作答。
  Future<List<Question>> generateCompositePaper() async {
    final questions = <Question>[];
    final seen = <String>{};
    for (final entry in compositeTemplate.entries) {
      final bankId = entry.key;
      for (final te in entry.value.entries) {
        final type = te.key;
        final want = te.value;
        if (want <= 0) continue;
        final rows = await _db.rawQuery(
          "SELECT * FROM questions WHERE bank_id = ? AND type = ? AND status = 'active' ORDER BY RANDOM() LIMIT ?",
          [bankId, type, want],
        );
        for (final r in rows) {
          final q = Question.fromMap(r);
          if (seen.add(q.id)) questions.add(q);
        }
      }
    }
    // 去重后若不足预期（题库缺题），不影响作答；排序保持学科顺序即可
    return questions;
  }

  /// 保存模拟卷成绩单，返回会话 id（调用方随后写 answer_logs 并回填汇总）"""
assert anchor in s, 'mixin end anchor'
s = s.replace(anchor, addition, 1)

open(p, 'w', encoding='utf-8').write(s)
print('[1] quiz_repository_mock ok')
