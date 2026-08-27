part of 'quiz_repository.dart';

/// 知识点树与章节概览（v4）：章节知识概览页 / 背题模式按知识点筛选用
mixin _KnowledgeMixin on RepositoryMixinBase {
  /// 某库知识点树（按包内清单顺序）
  Future<List<KnowledgePoint>> knowledgePoints(String bankId) async {
    final rows = await _db.query(
      'knowledge_points',
      where: 'bank_id = ?',
      whereArgs: [bankId],
      orderBy: 'rowid',
    );
    return rows.map(_kpFromRow).toList();
  }

  /// 某库章节知识概览
  Future<List<ChapterOverview>> chapterOverviews(String bankId) async {
    final rows = await _db.query(
      'chapter_overviews',
      where: 'bank_id = ?',
      whereArgs: [bankId],
      orderBy: 'rowid',
    );
    return rows
        .map((r) => ChapterOverview(
              chapter: r['chapter'] as String,
              knowledgeCount: r['knowledge_count'] as int? ?? 0,
              questionCount: r['question_count'] as int? ?? 0,
              summary: r['summary'] as String? ?? '',
            ))
        .toList();
  }

  /// 某章节的知识点列表（概览页）
  Future<List<KnowledgePoint>> knowledgeByChapter(
      String bankId, String chapter) async {
    final rows = await _db.query(
      'knowledge_points',
      where: 'bank_id = ? AND chapter = ?',
      whereArgs: [bankId, chapter],
      orderBy: 'rowid',
    );
    return rows.map(_kpFromRow).toList();
  }

  /// 某库是否含知识点树（v4 包；旧包无则概览页降级）
  Future<bool> hasKnowledge(String bankId) async {
    final rows = await _db.rawQuery(
      'SELECT COUNT(*) AS c FROM knowledge_points WHERE bank_id = ?',
      [bankId],
    );
    return (Sqflite.firstIntValue(rows) ?? 0) > 0;
  }

  /// 按知识点取题（知识点刷题 / 背题模式）
  Future<List<Question>> questionsByKnowledge(
      String bankId, String knowledgeId) async {
    final rows = await _db.query(
      'questions',
      where: "bank_id = ? AND status = 'active' AND knowledge_id = ?",
      whereArgs: [bankId, knowledgeId],
      orderBy:
          "CASE type WHEN 'single_choice' THEN 0 WHEN 'multi_choice' THEN 1 "
          "WHEN 'true_false' THEN 2 WHEN 'blank' THEN 3 WHEN 'short_answer' THEN 4 "
          "ELSE 99 END, id",
    );
    return rows.map(Question.fromMap).toList();
  }

  /// 某知识点在各题型的作答进度（概览页"已答 x/N"）：返回 {questionId: 已正确? }
  /// 取该知识点所有题 + answer_logs 中 result=correct 的题集合。
  Future<({int total, int answered, int correct})> knowledgeProgress(
      String bankId, String knowledgeId) async {
    final qRows = await _db.rawQuery(
      'SELECT COUNT(*) AS c FROM questions '
      "WHERE bank_id = ? AND status = 'active' AND knowledge_id = ?",
      [bankId, knowledgeId],
    );
    final total = Sqflite.firstIntValue(qRows) ?? 0;
    if (total == 0) return (total: 0, answered: 0, correct: 0);
    final aRows = await _db.rawQuery(
      'SELECT COUNT(DISTINCT al.question_id) AS c '
      'FROM answer_logs al JOIN questions q ON q.id = al.question_id '
      "WHERE q.bank_id = ? AND q.knowledge_id = ? AND q.status = 'active'",
      [bankId, knowledgeId],
    );
    final answered = Sqflite.firstIntValue(aRows) ?? 0;
    final cRows = await _db.rawQuery(
      'SELECT COUNT(DISTINCT al.question_id) AS c '
      'FROM answer_logs al JOIN questions q ON q.id = al.question_id '
      "WHERE q.bank_id = ? AND q.knowledge_id = ? AND q.status = 'active' "
      "AND al.result = 'correct'",
      [bankId, knowledgeId],
    );
    final correct = Sqflite.firstIntValue(cRows) ?? 0;
    return (total: total, answered: answered, correct: correct);
  }

  static KnowledgePoint _kpFromRow(Map<String, dynamic> r) => KnowledgePoint(
        id: r['id'] as String,
        name: r['name'] as String,
        chapter: r['chapter'] as String? ?? '',
        parent: r['parent'] as String?,
        summary: r['summary'] as String? ?? '',
        hot: (r['hot'] as int? ?? 0) == 1,
        examRef: r['exam_ref'] as String? ?? '',
        questionCount: r['question_count'] as int? ?? 0,
      );
}
