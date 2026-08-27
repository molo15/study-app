part of 'quiz_repository.dart';

/// 模拟卷、今日概览、学习统计
mixin _MockMixin on RepositoryMixinBase {
  /// 某题库的模拟卷列表（status=active）
  Future<List<MockPaper>> mockPapers({String? bankId}) async {
    final where = <String>["status = 'active'"];
    final args = <Object?>[];
    if (bankId != null) {
      where.add('bank_id = ?');
      args.add(bankId);
    }
    final rows = await _db.query(
      'mock_papers',
      where: where.join(' AND '),
      whereArgs: args,
      orderBy: 'id',
    );
    return rows.map(MockPaper.fromMap).toList();
  }

  /// 按 id 批量取题目（保持传入顺序；只取 active）
  Future<List<Question>> questionsByIds(List<String> ids) async {
    if (ids.isEmpty) return const [];
    final rows = await _db.rawQuery('''
      SELECT * FROM questions
      WHERE status = 'active' AND id IN (${List.filled(ids.length, '?').join(',')})
    ''', ids);
    final byId = {for (final r in rows) r['id'] as String: Question.fromMap(r)};
    return [
      for (final id in ids)
        if (byId.containsKey(id)) byId[id]!,
    ];
  }

  /// 模拟卷交卷：单事务原子写入（审查 P1-4）
  /// 插成绩单占位 → 逐题日志（mode=mock, session_id）→ 回填汇总，返回完整会话
  Future<MockSession> submitMockSession({
    required String paperId,
    required int startedAt,
    required int durationMin,
    required List<Question> questions,
    required Map<String, Set<String>> answers,
    required int submittedAt,
  }) async {
    var correct = 0, partial = 0, wrong = 0, skipped = 0;
    late int sessionId;
    await _db.transaction((txn) async {
      sessionId = await txn.insert(
        'mock_sessions',
        MockSession(
          paperId: paperId,
          startedAt: startedAt,
          durationMin: durationMin,
          total: questions.length,
          correct: 0,
          partial: 0,
          wrong: 0,
          skipped: 0,
          score: 0,
          submittedAt: submittedAt,
        ).toMap(),
      );
      for (final q in questions) {
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
        );
        if (grade == Grade.wrong) {
          // 模考答错自动归集错题本（全局 wrong 语义）
          await txn.delete(
            'wrong_book_exclusions',
            where: 'question_id = ?',
            whereArgs: [q.id],
          );
        }
      }
      final score = questions.isEmpty
          ? 0
          : (correct * 100 / questions.length).round();
      await txn.update(
        'mock_sessions',
        {
          'correct': correct,
          'partial': partial,
          'wrong': wrong,
          'skipped': skipped,
          'score': score,
        },
        where: 'id = ?',
        whereArgs: [sessionId],
      );
    });
    return MockSession(
      id: sessionId,
      paperId: paperId,
      startedAt: startedAt,
      durationMin: durationMin,
      total: questions.length,
      correct: correct,
      partial: partial,
      wrong: wrong,
      skipped: skipped,
      score: questions.isEmpty ? 0 : (correct * 100 / questions.length).round(),
      submittedAt: submittedAt,
    );
  }

  /// 保存模拟卷成绩单，返回会话 id（调用方随后写 answer_logs 并回填汇总）
  Future<int> insertMockSession(MockSession session) async {
    final id = await _db.insert('mock_sessions', session.toMap());
    return id;
  }

  /// 更新成绩单汇总（交卷后回填）
  Future<void> updateMockSession(MockSession session) async {
    await _db.update(
      'mock_sessions',
      session.toMap(),
      where: 'id = ?',
      whereArgs: [session.id],
    );
  }

  /// 历史成绩单（按卷）
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

  /// 今日已答数 / 今日正确率 / 连续学习天数（按 answered_at 去重日期倒推）
  Future<({int todayAnswered, double todayAccuracy, int streak})>
  todayOverview() async {
    final now = DateTime.now();
    final todayStart = DateTime(
      now.year,
      now.month,
      now.day,
    ).millisecondsSinceEpoch;
    final tomorrowStart = todayStart + Duration.millisecondsPerDay;

    final todayRows = await _db.rawQuery(
      'SELECT result FROM answer_logs WHERE answered_at >= ? AND answered_at < ?',
      [todayStart, tomorrowStart],
    );
    final todayAnswered = todayRows.length;
    final todayCorrect = todayRows
        .where((r) => r['result'] == 'correct')
        .length;

    // 连续学习天数：从今天往前，有作答记录的天连续计数
    var streak = 0;
    final dayMs = Duration.millisecondsPerDay;
    for (var i = 0; i < 365; i++) {
      final start = todayStart - i * dayMs;
      final end = start + dayMs;
      final c =
          Sqflite.firstIntValue(
            await _db.rawQuery(
              'SELECT COUNT(*) FROM answer_logs WHERE answered_at >= ? AND answered_at < ?',
              [start, end],
            ),
          ) ??
          0;
      if (c > 0) {
        streak++;
      } else if (i > 0) {
        break; // 今天还没做题但昨天有 → 不中断；否则中断
      }
      // i == 0 且今天为空：跳过今天继续往前数，昨天有记录则不中断连续天数
    }
    return (
      todayAnswered: todayAnswered,
      todayAccuracy: todayAnswered == 0
          ? 0.0
          : todayCorrect / todayAnswered * 100,
      streak: streak,
    );
  }

  /// 汇总统计：作答量/正确率/用时/章节分布/近 7 日做题数/到期未复习数
  /// （bankId=null 全局；byChapter 按 (bank_id, chapter) 分组，跨库同名章节不混淆）
  Future<StudyStats> studyStats({String? bankId}) async {
    final whereLog = bankId == null
        ? '1=1'
        : "al.question_id IN (SELECT id FROM questions WHERE bank_id = ? AND status = 'active')";
    final logArgs = bankId == null ? <Object?>[] : <Object?>[bankId];
    final total =
        Sqflite.firstIntValue(
          await _db.rawQuery(
            'SELECT COUNT(*) FROM answer_logs al WHERE $whereLog',
            logArgs,
          ),
        ) ??
        0;
    final correct =
        Sqflite.firstIntValue(
          await _db.rawQuery(
            "SELECT COUNT(*) FROM answer_logs al WHERE $whereLog AND al.result = 'correct'",
            logArgs,
          ),
        ) ??
        0;
    final partial =
        Sqflite.firstIntValue(
          await _db.rawQuery(
            "SELECT COUNT(*) FROM answer_logs al WHERE $whereLog AND al.result = 'partial'",
            logArgs,
          ),
        ) ??
        0;
    final wrong =
        Sqflite.firstIntValue(
          await _db.rawQuery(
            "SELECT COUNT(*) FROM answer_logs al WHERE $whereLog AND al.result = 'wrong'",
            logArgs,
          ),
        ) ??
        0;
    final totalTime =
        Sqflite.firstIntValue(
          await _db.rawQuery(
            'SELECT COALESCE(SUM(al.time_ms), 0) FROM answer_logs al WHERE $whereLog',
            logArgs,
          ),
        ) ??
        0;
    final dueTotal = await dueCount(bankId: bankId);

    // 题型分布（饼图）：按 questions.type 统计已作答的题（join answer_logs）
    // 与总览计数一致，仅统计 active 题，避免归档题历史拉高饼图（审查修复）
    final typeRows = await _db.rawQuery('''
      SELECT q.type, COUNT(*) AS cnt
      FROM answer_logs al
      JOIN questions q ON q.id = al.question_id
      WHERE 1=1 AND q.status = 'active'
        ${bankId == null ? '' : "AND q.bank_id = ?"}
      GROUP BY q.type
      ORDER BY cnt DESC
    ''', bankId == null ? <Object?>[] : <Object?>[bankId]);
    final typeDistribution = {
      for (final r in typeRows) (r['type'] as String): (r['cnt'] as int?) ?? 0,
    };

    // 作答结果分布（饼图）：correct/wrong/partial/skip
    final resultRows = await _db.rawQuery('''
      SELECT result, COUNT(*) AS cnt
      FROM answer_logs al
      WHERE 1=1
        ${bankId == null ? '' : "AND al.question_id IN (SELECT id FROM questions WHERE bank_id = ? AND status = 'active')"}
      GROUP BY result
    ''', bankId == null ? <Object?>[] : <Object?>[bankId]);
    final resultDistribution = {
      for (final r in resultRows)
        (r['result'] as String): (r['cnt'] as int?) ?? 0,
    };

    // 各章节分布：按 (bank_id, chapter) 分组
    final chapterRows = await _db.rawQuery('''
      SELECT q.bank_id, q.chapter,
             COUNT(*) AS total,
             SUM(CASE WHEN al.result = 'correct' THEN 1 ELSE 0 END) AS correct,
             SUM(CASE WHEN al.result = 'wrong' THEN 1 ELSE 0 END) AS wrong
      FROM answer_logs al
      JOIN questions q ON q.id = al.question_id
      WHERE q.status = 'active' AND q.chapter IS NOT NULL AND q.chapter != ''
        ${bankId == null ? '' : "AND q.bank_id = ?"}
      GROUP BY q.bank_id, q.chapter
      ORDER BY q.bank_id, q.chapter
    ''', bankId == null ? <Object?>[] : <Object?>[bankId]);
    final byChapter = chapterRows
        .map(
          (r) => ChapterStats(
            bankId: r['bank_id'] as String,
            chapter: (r['chapter'] as String?) ?? '',
            total: r['total'] as int,
            correct: (r['correct'] as int?) ?? 0,
            wrong: (r['wrong'] as int?) ?? 0,
          ),
        )
        .toList();

    // 近 7 日每日做题数（index 0 = 今天）
    final daily = <DailyData>[];
    final today = DateTime.now();
    final startOfToday = DateTime(
      today.year,
      today.month,
      today.day,
    ).millisecondsSinceEpoch;
    for (var i = 6; i >= 0; i--) {
      final dayStart = startOfToday - i * Duration.millisecondsPerDay;
      final dayEnd = dayStart + Duration.millisecondsPerDay;
      final count =
          Sqflite.firstIntValue(
            await _db.rawQuery(
              'SELECT COUNT(*) FROM answer_logs al WHERE al.answered_at >= ? AND al.answered_at < ? AND $whereLog',
              [dayStart, dayEnd, ...logArgs],
            ),
          ) ??
          0;
      final date = DateTime.fromMillisecondsSinceEpoch(dayStart);
      daily.add(DailyData(day: '${date.month}-${date.day}', count: count));
    }

    return StudyStats(
      totalAnswered: total,
      correctCount: correct,
      partialCount: partial,
      wrongCount: wrong,
      totalTimeMs: totalTime,
      dueCount: dueTotal,
      byChapter: byChapter,
      daily: daily,
      typeDistribution: typeDistribution,
      resultDistribution: resultDistribution,
    );
  }
}
