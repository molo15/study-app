part of 'quiz_repository.dart';

/// 数据维护（题库清单/清理归档）、备份导出与恢复、审题标记
mixin _ExportMixin on RepositoryMixinBase {
  /// 已导入题库包（含已归档题）的清单
  /// [includeHidden] = true 时包含被用户卸载/隐藏的库（设置页管理用）；
  /// 首页默认过滤隐藏库。
  Future<List<BankInfo>> banks({bool includeHidden = false}) async {
    final rows = await _db.rawQuery('''
      SELECT bank_id,
             COUNT(*) AS total,
             SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active,
             SUM(CASE WHEN user_edited = 1 THEN 1 ELSE 0 END) AS edited
      FROM questions GROUP BY bank_id ORDER BY bank_id
    ''');
    final result = <BankInfo>[];
    for (final r in rows) {
      final bankId = r['bank_id'] as String;
      final hidden = await setting('bank_${bankId}_hidden') == 'true';
      if (hidden && !includeHidden) continue;
      result.add(
        BankInfo(
          bankId: bankId,
          name: await setting('bank_${bankId}_name') ?? bankId,
          version: await importedVersion(bankId) ?? '',
          total: r['total'] as int,
          active: (r['active'] as int?) ?? 0,
          archived: (r['total'] as int) - ((r['active'] as int?) ?? 0),
          userEdited: (r['edited'] as int?) ?? 0,
          hidden: hidden,
        ),
      );
    }
    return result;
  }

  /// 彻底清理某题库包的已归档题（删除题与其作答历史；设计方案 §3.4）
  Future<int> purgeArchived(String bankId) async {
    final rows = await _db.rawQuery(
      "SELECT id FROM questions WHERE bank_id = ? AND status = 'archived'",
      [bankId],
    );
    final ids = rows.map((r) => r['id'] as String).toList();
    await _db.transaction((txn) async {
      for (final id in ids) {
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
        await txn.delete('questions', where: 'id = ?', whereArgs: [id]);
      }
    });
    return ids.length;
  }

  /// 导出全部数据为 JSON 文本（备份，设计方案 §7 本地优先可移植）
  ///
  /// 导出净化：剥离思源块溯源字段（所有题型），并移除简答题的解析字段，
  /// 避免导出文件携带出题来源的块信息（设置页"导出备份"需求）。
  Future<String> exportJson() async {
    final rawQuestions = await _db.query('questions', orderBy: 'id');
    final questions = [
      for (final r in rawQuestions)
        _sanitizedExportQuestion(Map<String, dynamic>.from(r)),
    ];
    final logs = await _db.query('answer_logs', orderBy: 'id');
    final cards = await _db.query('card_scheduling', orderBy: 'question_id');
    final exclusions = await _db.query(
      'wrong_book_exclusions',
      orderBy: 'question_id',
    );
    final papers = await _db.query('mock_papers', orderBy: 'id'); // 审查 P2-3
    final sessions = await _db.query('mock_sessions', orderBy: 'id');
    final settings = await _db.query('settings');
    return const JsonEncoder.withIndent('  ').convert({
      'formatVersion': 2,
      'exportedAt': DateTime.now().toIso8601String(),
      'questions': questions,
      'answerLogs': logs,
      'cardScheduling': cards,
      'wrongBookExclusions': exclusions,
      'mockPapers': papers,
      'mockSessions': sessions,
      'settings': settings,
    });
  }

  /// 导出时剥离敏感/冗余字段：
  /// - 所有题型移除思源块溯源（source_block_id / source_doc_path）；
  /// - 简答题（short_answer）额外移除解析（explanation）。
  Map<String, dynamic> _sanitizedExportQuestion(Map<String, dynamic> row) {
    row.remove('source_block_id');
    row.remove('source_doc_path');
    if (row['type'] == 'short_answer') {
      row.remove('explanation');
    }
    return row;
  }

  /// 从备份 JSON 恢复（清空后全量写入；审查 P1-2：补齐 wrong_book_exclusions）
  ///
  /// 审查 P2-2：入口校验 formatVersion 与核心字段，非法抛 [FormatException]
  /// 整体回滚，杜绝「误传损坏文件静默清空数据」。v2 备份含 mock 表（审查 P2-3）。
  Future<void> restoreJson(String jsonText) async {
    final data = const JsonDecoder().convert(jsonText) as Map<String, dynamic>;
    final version = data['formatVersion'];
    if (version is! int || version < 1 || version > 2) {
      throw FormatException('备份格式版本不受支持: $version');
    }
    for (final key in [
      'questions',
      'answerLogs',
      'cardScheduling',
      'settings',
    ]) {
      if (data[key] is! List) {
        throw FormatException('备份缺少字段: $key');
      }
    }
    await _db.transaction((txn) async {
      await txn.delete('answer_logs');
      await txn.delete('card_scheduling');
      await txn.delete('wrong_book_exclusions');
      await txn.delete('mock_sessions');
      await txn.delete('mock_papers');
      await txn.delete('questions');
      await txn.delete('settings');
      final questions = (data['questions'] as List<dynamic>? ?? const [])
          .cast<Map<String, dynamic>>();
      for (final q in questions) {
        await txn.insert(
          'questions',
          q,
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }
      final logs = (data['answerLogs'] as List<dynamic>? ?? const [])
          .cast<Map<String, dynamic>>();
      for (final l in logs) {
        await txn.insert('answer_logs', l);
      }
      final cards = (data['cardScheduling'] as List<dynamic>? ?? const [])
          .cast<Map<String, dynamic>>();
      for (final c in cards) {
        await txn.insert(
          'card_scheduling',
          c,
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }
      final exclusions =
          (data['wrongBookExclusions'] as List<dynamic>? ?? const [])
              .cast<Map<String, dynamic>>();
      for (final e in exclusions) {
        await txn.insert(
          'wrong_book_exclusions',
          e,
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }
      final papers = (data['mockPapers'] as List<dynamic>? ?? const [])
          .cast<Map<String, dynamic>>();
      for (final p in papers) {
        await txn.insert(
          'mock_papers',
          p,
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }
      final sessions = (data['mockSessions'] as List<dynamic>? ?? const [])
          .cast<Map<String, dynamic>>();
      for (final s in sessions) {
        await txn.insert('mock_sessions', s);
      }
      final settings = (data['settings'] as List<dynamic>? ?? const [])
          .cast<Map<String, dynamic>>();
      for (final s in settings) {
        await txn.insert(
          'settings',
          s,
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }
    });
  }

  /// 标记一道题为"待审/需修改"，返回是否为新标记（true=新增，false=已存在）
  Future<bool> flagQuestion(
    String questionId,
    String bankId, {
    String? comment,
  }) async {
    final count = await _db.insert(
      'review_flags',
      {
        'question_id': questionId,
        'bank_id': bankId,
        'comment': comment,
        'created_at': DateTime.now().millisecondsSinceEpoch,
      },
      // ignore：已标记的题跳过（保留原 comment/created_at），0=已存在
      conflictAlgorithm: ConflictAlgorithm.ignore,
    );
    return count > 0;
  }

  /// 取消一道题的标记
  Future<void> unflagQuestion(String questionId) async {
    await _db.delete(
      'review_flags',
      where: 'question_id = ?',
      whereArgs: [questionId],
    );
  }

  /// 判断某题是否已标记
  Future<bool> isFlagged(String questionId) async {
    final rows = await _db.query(
      'review_flags',
      columns: ['question_id'],
      where: 'question_id = ?',
      whereArgs: [questionId],
      limit: 1,
    );
    return rows.isNotEmpty;
  }

  /// 全部标记清单（含题干快照，便于导出）
  Future<List<Map<String, dynamic>>> reviewFlags() async {
    final rows = await _db.rawQuery(
      "SELECT r.question_id, r.bank_id, r.comment, r.created_at, "
      "q.stem, q.chapter, q.type FROM review_flags r "
      "LEFT JOIN questions q ON q.id = r.question_id "
      "ORDER BY r.created_at DESC",
    );
    return rows;
  }

  /// 导出审题标记为 JSON 文本（含题干快照，供回传修改）
  Future<String> exportReviewFlags() async {
    final rows = await reviewFlags();
    return const JsonEncoder.withIndent('  ').convert({
      'exportedAt': DateTime.now().toIso8601String(),
      'count': rows.length,
      'flags': rows,
    });
  }

  /// 清空全部标记
  Future<void> clearReviewFlags() async {
    await _db.delete('review_flags');
  }
}
