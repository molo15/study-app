part of 'quiz_repository.dart';

/// 作答日志（append-only）、间隔重复队列、错题本
mixin _SrsMixin on RepositoryMixinBase {
  /// 写 answer_logs；答错时移出排除记录（审查 P1-8：恢复「答错自动归集」）
  Future<void> logAnswer(AnswerLog log) async {
    await _db.insert('answer_logs', log.toMap());
    if (log.result == 'wrong') {
      await _db.delete(
        'wrong_book_exclusions',
        where: 'question_id = ?',
        whereArgs: [log.questionId],
      );
    }
  }

  /// 作答日志 + FSRS 调度状态单事务原子写入（审查 P2-8）：
  /// 任一失败整体回滚，避免「有日志无调度」或「日志双计」。
  Future<void> logAnswerAndSchedule(
    AnswerLog log,
    Card card, {
    DateTime? now,
  }) async {
    await _db.transaction((txn) async {
      await txn.insert('answer_logs', log.toMap());
      await txn.insert('card_scheduling', {
        'question_id': log.questionId,
        'state': card.state.name,
        'step': card.step,
        'stability': card.stability,
        'difficulty': card.difficulty,
        'due': card.due.toUtc().millisecondsSinceEpoch,
        'last_review': card.lastReview?.toUtc().millisecondsSinceEpoch,
        'updated_at': (now ?? DateTime.now()).millisecondsSinceEpoch,
      }, conflictAlgorithm: ConflictAlgorithm.replace);
      if (log.result == 'wrong') {
        await txn.delete(
          'wrong_book_exclusions',
          where: 'question_id = ?',
          whereArgs: [log.questionId],
        );
      }
    });
  }

  /// 某题是否有错题记录（错题本判定，设计方案 §3.5）
  Future<bool> hasWrongRecord(String questionId) async {
    final rows = await _db.rawQuery(
      "SELECT 1 FROM answer_logs WHERE question_id = ? AND result = 'wrong' LIMIT 1",
      [questionId],
    );
    return rows.isNotEmpty;
  }

  /// 错题本：有错题记录的题目 id 集（一期按「存在答错记录」归集）
  Future<Set<String>> wrongQuestionIds() async {
    final rows = await _db.rawQuery(
      "SELECT DISTINCT question_id FROM answer_logs WHERE result = 'wrong'",
    );
    return rows.map((r) => r['question_id'] as String).toSet();
  }

  /// 今日到期题目（new/learning/review 中 due ≤ now 的 active 题）
  Future<List<Question>> dueQuestions({DateTime? now}) async {
    final due = (now ?? DateTime.now()).millisecondsSinceEpoch;
    final rows = await _db.rawQuery(
      '''
      SELECT q.* FROM questions q
      JOIN card_scheduling c ON c.question_id = q.id
      WHERE q.status = 'active' AND c.due <= ?
      ORDER BY c.due
    ''',
      [due],
    );
    return rows.map(Question.fromMap).toList();
  }

  /// 新题：尚未建立调度记录的 active 题（按章节顺序，最多 [limit] 道）
  Future<List<Question>> newQuestions({
    String? bankId,
    String? chapter,
    int limit = 20,
  }) async {
    final where = <String>["q.status = 'active'", 'c.question_id IS NULL'];
    final args = <Object?>[];
    if (bankId != null) {
      where.add('q.bank_id = ?');
      args.add(bankId);
    }
    if (chapter != null) {
      where.add('q.chapter = ?');
      args.add(chapter);
    }
    final rows = await _db.rawQuery(
      '''
      SELECT q.* FROM questions q
      LEFT JOIN card_scheduling c ON c.question_id = q.id
      WHERE ${where.join(' AND ')}
      ORDER BY q.chapter, q.id
      LIMIT ?
    ''',
      [...args, limit],
    );
    return rows.map(Question.fromMap).toList();
  }

  /// 复习队列 = 今日到期（学习+复习），不含新题（bankId=null 全局合并）
  Future<List<Question>> reviewQueue({DateTime? now, String? bankId}) async {
    final due = (now ?? DateTime.now()).millisecondsSinceEpoch;
    final where = <String>[
      "q.status = 'active'",
      "c.state IN ('learning','review','relearning')",
      'c.due <= ?',
    ];
    final args = <Object?>[due];
    if (bankId != null) {
      where.add('q.bank_id = ?');
      args.add(bankId);
    }
    final rows = await _db.rawQuery('''
      SELECT q.* FROM questions q
      JOIN card_scheduling c ON c.question_id = q.id
      WHERE ${where.join(' AND ')}
      ORDER BY c.due
    ''', args);
    return rows.map(Question.fromMap).toList();
  }

  /// 今日到期题数（首页概览；bankId=null 全局）
  @override
  Future<int> dueCount({DateTime? now, String? bankId}) async {
    final due = (now ?? DateTime.now()).millisecondsSinceEpoch;
    final where = <String>["q.status = 'active'", 'c.due <= ?'];
    final args = <Object?>[due];
    if (bankId != null) {
      where.add('q.bank_id = ?');
      args.add(bankId);
    }
    final rows = await _db.rawQuery('''
      SELECT COUNT(*) AS c FROM questions q
      JOIN card_scheduling c ON c.question_id = q.id
      WHERE ${where.join(' AND ')}
    ''', args);
    return Sqflite.firstIntValue(rows) ?? 0;
  }

  /// 新题数（尚未建立调度记录；bankId=null 全局）
  Future<int> newCount({String? bankId}) async {
    final where = <String>["q.status = 'active'", 'c.question_id IS NULL'];
    final args = <Object?>[];
    if (bankId != null) {
      where.add('q.bank_id = ?');
      args.add(bankId);
    }
    final rows = await _db.rawQuery('''
      SELECT COUNT(*) AS c FROM questions q
      LEFT JOIN card_scheduling c ON c.question_id = q.id
      WHERE ${where.join(' AND ')}
    ''', args);
    return Sqflite.firstIntValue(rows) ?? 0;
  }

  /// 错题本题目列表：答错过且未手动移出（按最近答错时间倒序；bankId=null 全局）
  /// （审查 P2-2：改 EXISTS 写法，避免依赖 SQLite 裸列 GROUP BY 扩展）
  Future<List<Question>> wrongBookQuestions({String? bankId}) async {
    final where = <String>[
      "q.status = 'active'",
      '''EXISTS (
          SELECT 1 FROM answer_logs al
          WHERE al.question_id = q.id AND al.result = 'wrong'
        )''',
      '''NOT EXISTS (
          SELECT 1 FROM wrong_book_exclusions wbe
          WHERE wbe.question_id = q.id
        )''',
    ];
    final args = <Object?>[];
    if (bankId != null) {
      where.add('q.bank_id = ?');
      args.add(bankId);
    }
    final rows = await _db.rawQuery('''
      SELECT q.* FROM questions q
      WHERE ${where.join(' AND ')}
      ORDER BY (
        SELECT MAX(al.answered_at) FROM answer_logs al
        WHERE al.question_id = q.id AND al.result = 'wrong'
      ) DESC
    ''', args);
    return rows.map(Question.fromMap).toList();
  }

  /// 错题数量（审查 P2-C：首页计数专用，避免全量加载错题行；bankId=null 全局）
  Future<int> wrongBookCount({String? bankId}) async {
    final where = <String>[
      "q.status = 'active'",
      '''EXISTS (
          SELECT 1 FROM answer_logs al
          WHERE al.question_id = q.id AND al.result = 'wrong'
        )''',
      '''NOT EXISTS (
          SELECT 1 FROM wrong_book_exclusions wbe
          WHERE wbe.question_id = q.id
        )''',
    ];
    final args = <Object?>[];
    if (bankId != null) {
      where.add('q.bank_id = ?');
      args.add(bankId);
    }
    final rows = await _db.rawQuery('''
      SELECT COUNT(*) AS c FROM questions q
      WHERE ${where.join(' AND ')}
    ''', args);
    return Sqflite.firstIntValue(rows) ?? 0;
  }

  /// 某题是否在错题本中
  Future<bool> inWrongBook(String questionId) async {
    final rows = await _db.rawQuery(
      '''
      SELECT 1 FROM answer_logs al
      LEFT JOIN wrong_book_exclusions wbe ON wbe.question_id = al.question_id
      WHERE al.question_id = ? AND al.result = 'wrong' AND wbe.question_id IS NULL
      LIMIT 1
    ''',
      [questionId],
    );
    return rows.isNotEmpty;
  }

  /// 手动移出错题本（写排除记录；answer_logs 保持 append-only 不移除历史）
  Future<void> removeFromWrongBook(String questionId) async {
    await _db.insert('wrong_book_exclusions', {
      'question_id': questionId,
      'created_at': DateTime.now().millisecondsSinceEpoch,
    }, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  /// 该题最近连续正确次数（错题重刷自动移出判定，设计方案 §3.5）。
  /// 审查 P2-11：加 mode 过滤，错题移出只数 wrong_rework 模式，
  /// 避免 learn/mock 的正确/错误污染连续计数。
  /// 错题重刷的连续答对次数（自动移出判定，设计方案 §3.5）。
  ///
  /// 审查 B2：以「最近一次任意模式的答错」为界——重新归集（再次答错）
  /// 后链条重置，只统计其后的 wrong_rework 答对，杜绝
  /// 「重归后 1 次答对就达旧阈值移出」。
  Future<int> consecutiveCorrectCount(String questionId) async {
    // 最近一次答错时间（任何模式；无则从头数）
    final lastWrong =
        Sqflite.firstIntValue(
          await _db.rawQuery(
            "SELECT MAX(answered_at) FROM answer_logs WHERE question_id = ? AND result = 'wrong'",
            [questionId],
          ),
        ) ??
        0;
    final rows = await _db.query(
      'answer_logs',
      where: "question_id = ? AND mode = 'wrong_rework' AND answered_at > ?",
      whereArgs: [questionId, lastWrong],
      orderBy: 'answered_at DESC',
      columns: ['result'],
    );
    var count = 0;
    for (final r in rows) {
      if (r['result'] == 'correct') {
        count++;
      } else {
        break;
      }
    }
    return count;
  }
}
