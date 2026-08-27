part of 'quiz_repository.dart';

/// 题目查询：列表/章节/重点合集/随机/按章节统计
mixin _QuestionsMixin on RepositoryMixinBase {
  /// 题目列表（默认仅 active；可按章节、purpose 过滤）
  Future<List<Question>> questions({
    String? bankId,
    String? chapter,
    String? purpose,
  }) async {
    final where = <String>["status = 'active'"];
    final args = <Object?>[];
    if (bankId != null) {
      where.add('bank_id = ?');
      args.add(bankId);
    }
    if (chapter != null) {
      where.add('chapter = ?');
      args.add(chapter);
    }
    if (purpose != null && purpose.isNotEmpty) {
      where.add('purpose = ?');
      args.add(purpose);
    }
    final rows = await _db.query(
      'questions',
      where: where.join(' AND '),
      whereArgs: args,
      // 出题顺序：选择(单选/多选/判断) → 填空 → 简答/论述（发布规范）
      orderBy:
          "chapter, "
          "CASE type WHEN 'single_choice' THEN 0 WHEN 'multi_choice' THEN 1 "
          "WHEN 'true_false' THEN 2 WHEN 'blank' THEN 3 WHEN 'short_answer' THEN 4 "
          "ELSE 99 END, id",
    );
    return rows.map(Question.fromMap).toList();
  }

  /// 多章节取题（重点章节合集刷题用）
  Future<List<Question>> questionsInChapters(
    String bankId,
    List<String> chapters,
  ) async {
    if (chapters.isEmpty) return const [];
    final placeholders = List.filled(chapters.length, '?').join(',');
    final rows = await _db.rawQuery(
      "SELECT * FROM questions WHERE bank_id = ? AND status = 'active' "
      'AND chapter IN ($placeholders) '
      "ORDER BY chapter, "
      "CASE type WHEN 'single_choice' THEN 0 WHEN 'multi_choice' THEN 1 "
      "WHEN 'true_false' THEN 2 WHEN 'blank' THEN 3 WHEN 'short_answer' THEN 4 "
      "ELSE 99 END, id",
      [bankId, ...chapters],
    );
    return rows.map(Question.fromMap).toList();
  }

  /// 重点题目：按「考点热门=章节题量厚优先」抽取合集，共 [maxTotal] 道
  /// （大章不再整章进合集，改为从重点章节逐章截取题目，保证每个题库都有重点合集）。
  /// 排除「论述题专题」；全库不足 [minTotal] 时返回全部。按章节内题目顺序（chapter, id）取。
  Future<List<Question>> keyQuestions(
    String bankId, {
    int minTotal = 50,
    int maxTotal = 150,
  }) async {
    final rows = await _db.rawQuery(
      "SELECT * FROM questions WHERE bank_id = ? AND status = 'active' "
      "AND chapter != '论述题专题' ORDER BY chapter, id",
      [bankId],
    );
    final all = rows.map(Question.fromMap).toList();
    if (all.length <= maxTotal) return all;

    // 按章节题量降序，章节内保持原有顺序
    final byChapter = <String, List<Question>>{};
    for (final q in all) {
      byChapter.putIfAbsent(q.chapter, () => []).add(q);
    }
    final chapters = byChapter.keys.toList()
      ..sort((a, b) => byChapter[b]!.length.compareTo(byChapter[a]!.length));

    final result = <Question>[];
    for (final ch in chapters) {
      if (result.length >= maxTotal) break;
      final take = byChapter[ch]!.take(maxTotal - result.length);
      result.addAll(take);
    }
    return result.length >= minTotal ? result : all.take(minTotal).toList();
  }

  /// 各题库已作答题数（distinct 题目，按 bank 分组；首页题库卡「已答进度」用）
  Future<Map<String, int>> answeredCountByBank() async {
    final rows = await _db.rawQuery(
      'SELECT q.bank_id, COUNT(DISTINCT al.question_id) AS cnt '
      'FROM answer_logs al JOIN questions q ON q.id = al.question_id '
      "WHERE q.status = 'active' GROUP BY q.bank_id",
    );
    return {
      for (final r in rows) (r['bank_id'] as String): ((r['cnt'] as int?) ?? 0),
    };
  }

  /// 整本随机刷：随机取 [limit] 题，按题型顺序排列
  /// （单选 → 多选 → 判断 → 填空 → 简答，用户要求）
  Future<List<Question>> randomByType(
    String bankId, {
    int limit = 50,
    String? chapter,
  }) async {
    final where = <String>["bank_id = ?", "status = 'active'"];
    final args = <Object?>[bankId];
    if (chapter != null) {
      where.add('chapter = ?');
      args.add(chapter);
    }
    final rows = await _db.rawQuery(
      'SELECT * FROM questions WHERE ${where.join(' AND ')} ORDER BY RANDOM() LIMIT $limit',
      args,
    );
    final questions = rows.map(Question.fromMap).toList();
    // 按题型顺序排列（type 权重：单选0 多选1 判断2 填空3 简答4）
    int typeOrder(QuestionType t) => switch (t) {
      QuestionType.singleChoice => 0,
      QuestionType.multiChoice => 1,
      QuestionType.trueFalse => 2,
      QuestionType.blank => 3,
      QuestionType.shortAnswer => 4,
    };
    questions.sort((a, b) => typeOrder(a.type).compareTo(typeOrder(b.type)));
    return questions;
  }

  /// 已导入的题库包 id 列表
  Future<List<String>> bankIds() async {
    final rows = await _db.rawQuery(
      "SELECT DISTINCT bank_id FROM questions WHERE status = 'active'",
    );
    return rows.map((r) => r['bank_id'] as String).toList();
  }

  /// 某题库包内的章节（动态生成，设计方案 §2.4：实际章节以题目上的 chapter 为准）
  Future<List<String>> chapters(String bankId) async {
    final rows = await _db.rawQuery(
      "SELECT DISTINCT chapter FROM questions WHERE bank_id = ? AND status = 'active' ORDER BY chapter",
      [bankId],
    );
    return rows
        .map((r) => (r['chapter'] as String?) ?? '')
        .where((c) => c.isNotEmpty)
        .toList();
  }

  /// 章节内题目数
  Future<int> chapterCount(String bankId, String chapter) async {
    final rows = await _db.rawQuery(
      "SELECT COUNT(*) AS c FROM questions WHERE bank_id = ? AND chapter = ? AND status = 'active'",
      [bankId, chapter],
    );
    return Sqflite.firstIntValue(rows) ?? 0;
  }

  /// 批量章节题数（审查 P2-1：替代逐章查询的 N+1；P2-5：NULL chapter 防御）
  Future<Map<String, int>> chapterCounts(String bankId) async {
    final rows = await _db.rawQuery(
      "SELECT chapter, COUNT(*) AS c FROM questions "
      "WHERE bank_id = ? AND status = 'active' GROUP BY chapter",
      [bankId],
    );
    return {
      for (final r in rows)
        (r['chapter'] as String?) ?? '': (r['c'] as int?) ?? 0,
    };
  }

  /// 按章节 + purpose 统计题数（基础/测试双轨用）：
  /// 返回 { (chapter, purpose): count }，purpose 为空串表示未分区的普通题。
  Future<Map<(String, String), int>> chapterPurposeCounts(String bankId) async {
    final rows = await _db.rawQuery(
      "SELECT chapter, purpose, COUNT(*) AS c FROM questions "
      "WHERE bank_id = ? AND status = 'active' GROUP BY chapter, purpose",
      [bankId],
    );
    return {
      for (final r in rows)
        ((r['chapter'] as String?) ?? '', (r['purpose'] as String?) ?? ''):
            (r['c'] as int?) ?? 0,
    };
  }

  /// 随机抽题（范围内随机，设计方案 §3.5 随机刷）
  Future<List<Question>> randomQuestions({
    int limit = 20,
    String? bankId,
    String? chapter,
  }) async {
    final where = <String>["status = 'active'"];
    final args = <Object?>[];
    if (bankId != null) {
      where.add('bank_id = ?');
      args.add(bankId);
    }
    if (chapter != null) {
      where.add('chapter = ?');
      args.add(chapter);
    }
    final rows = await _db.query(
      'questions',
      where: where.join(' AND '),
      whereArgs: args,
      orderBy: 'RANDOM()',
      limit: limit,
    );
    return rows.map(Question.fromMap).toList();
  }

  // ---------- 题库包管理（删除/编辑/还原，设计：bank_management） ----------

  /// 单题查询（题目编辑页用）
  Future<Question?> questionById(String id) async {
    final rows = await _db.query(
      'questions',
      where: 'id = ?',
      whereArgs: [id],
      limit: 1,
    );
    return rows.isEmpty ? null : Question.fromMap(rows.first);
  }

  /// 题目管理查询：按题库包 + 可选章节/题型/关键词过滤（active 题）
  Future<List<Question>> questionsForManage(
    String bankId, {
    String? chapter,
    QuestionType? type,
    String? keyword,
    int limit = 300,
  }) async {
    final where = <String>["bank_id = ? AND status = 'active'"];
    final args = <Object?>[bankId];
    if (chapter != null && chapter.isNotEmpty) {
      where.add('chapter = ?');
      args.add(chapter);
    }
    if (type != null) {
      where.add('type = ?');
      args.add(type.json);
    }
    if (keyword != null && keyword.isNotEmpty) {
      where.add('(stem LIKE ? OR answer LIKE ? OR explanation LIKE ?)');
      final like = '%$keyword%';
      args.addAll([like, like, like]);
    }
    final rows = await _db.query(
      'questions',
      where: where.join(' AND '),
      whereArgs: args,
      orderBy:
          "CASE type WHEN 'single_choice' THEN 0 WHEN 'multi_choice' THEN 1 "
          "WHEN 'true_false' THEN 2 WHEN 'blank' THEN 3 WHEN 'short_answer' THEN 4 "
          "ELSE 99 END, chapter, id",
      limit: limit,
    );
    return rows.map(Question.fromMap).toList();
  }

  /// 章节分组列表（题目浏览器分组用；仅含 active 题的章节）
  Future<List<String>> chaptersForManage(String bankId) async {
    final rows = await _db.rawQuery(
      "SELECT DISTINCT chapter FROM questions "
      "WHERE bank_id = ? AND status = 'active' AND chapter != '' "
      "ORDER BY chapter",
      [bankId],
    );
    return rows.map((r) => r['chapter'] as String).toList();
  }

  /// 更新题目（题目编辑保存）。置 user_edited=1，内置式更新时保留本地版本。
  Future<void> updateQuestion(Question q) async {
    final now = DateTime.now().millisecondsSinceEpoch;
    final map = q.toMap()
      ..['user_edited'] = 1
      ..['updated_at'] = now;
    await _db.update('questions', map, where: 'id = ?', whereArgs: [q.id]);
  }

  /// 还原为官方版：清除本地修改标记（user_edited=0）。
  /// 下次内置式题库更新导入时，该题恢复为官方内容。
  Future<void> restoreQuestionToOfficial(String id) async {
    await _db.update(
      'questions',
      {'user_edited': 0, 'updated_at': DateTime.now().millisecondsSinceEpoch},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  /// 卸载/隐藏题库包：该库全部 active 题软归档 + 模拟卷软归档 + 写 hidden 标记。
  /// 作答记录/FSRS/错题本/审题标记全部保留；重新导入同库包可恢复。
  Future<void> uninstallBank(String bankId) async {
    final now = DateTime.now().millisecondsSinceEpoch;
    await _db.transaction((txn) async {
      await txn.update(
        'questions',
        {'status': 'archived', 'updated_at': now},
        where: "bank_id = ? AND status = 'active'",
        whereArgs: [bankId],
      );
      // 模拟卷一并归档，避免卸载库的卷仍在首页展示（审查修复）
      await txn.update(
        'mock_papers',
        {'status': 'archived', 'updated_at': now},
        where: "bank_id = ? AND status = 'active'",
        whereArgs: [bankId],
      );
      await txn.insert(
        'settings',
        {'key': 'bank_${bankId}_hidden', 'value': 'true'},
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    });
  }

  /// 恢复显示被卸载的库（移除 hidden 标记；题目待重新导入恢复 active）
  Future<void> restoreBank(String bankId) async {
    await _db.delete(
      'settings',
      where: 'key = ?',
      whereArgs: ['bank_${bankId}_hidden'],
    );
  }

  /// 彻底删除题库包：卸载基础上，连同该库全部作答数据/模拟卷/元数据物理删除。
  /// 不可恢复（需用户输入库名二次确认后调用）。
  Future<void> deleteBankCompletely(String bankId) async {
    await _db.transaction((txn) async {
      final qRows = await txn.query(
        'questions',
        columns: ['id'],
        where: 'bank_id = ?',
        whereArgs: [bankId],
      );
      final qIds = qRows.map((r) => r['id'] as String).toList();
      for (final id in qIds) {
        await txn.delete(
          'answer_logs',
          where: 'question_id = ?',
          whereArgs: [id],
        );
        await txn.delete(
          'card_scheduling',
          where: 'question_id = ?',
          whereArgs: [id],
        );
        await txn.delete(
          'wrong_book_exclusions',
          where: 'question_id = ?',
          whereArgs: [id],
        );
        await txn.delete(
          'review_flags',
          where: 'question_id = ?',
          whereArgs: [id],
        );
      }
      await txn.delete('questions', where: 'bank_id = ?', whereArgs: [bankId]);
      final paperRows = await txn.query(
        'mock_papers',
        columns: ['id'],
        where: 'bank_id = ?',
        whereArgs: [bankId],
      );
      for (final r in paperRows) {
        await txn.delete(
          'mock_sessions',
          where: 'paper_id = ?',
          whereArgs: [r['id']],
        );
      }
      await txn.delete(
        'mock_papers',
        where: 'bank_id = ?',
        whereArgs: [bankId],
      );
      for (final key in [
        'bank_${bankId}_version',
        'bank_${bankId}_name',
        'bank_${bankId}_groups',
        'bank_${bankId}_hidden',
      ]) {
        await txn.delete('settings', where: 'key = ?', whereArgs: [key]);
      }
    });
  }
}
