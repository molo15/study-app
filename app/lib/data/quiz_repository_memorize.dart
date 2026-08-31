part of 'quiz_repository.dart';

/// 背题存档（v11）：知识点卡/题目卡的跨会话记忆状态
///
/// 状态机：无记录=未背 → 标"还不会"→ learning(streak=0)；
/// 标"背会"→ streak+1，streak>=2 → mastered（已掌握，不再主动进队列）。
/// 自评即时落库（防闪退丢进度），不进入 SRS 复习队列。
mixin _MemorizeMixin on RepositoryMixinBase {
  static const _table = 'memorize_progress';

  /// 记录一次自评：know=true 背会，know=false 还不会
  Future<void> recordMemorize({
    required String cardKey,
    required String bankId,
    required String chapter,
    required String cardType,
    String? knowledgeId,
    String? questionId,
    required bool know,
    DateTime? now,
  }) async {
    final t = now ?? DateTime.now();
    final rows = await _db.query(
      _table,
      where: 'card_key = ?',
      whereArgs: [cardKey],
      limit: 1,
    );
    final prev = rows.isEmpty ? null : rows.first;
    final prevStreak = prev?['correct_streak'] as int? ?? 0;
    final streak = know ? prevStreak + 1 : 0;
    final state = streak >= 2 ? 'mastered' : 'learning';
    await _db.insert(
      _table,
      {
        'card_key': cardKey,
        'bank_id': bankId,
        'chapter': chapter,
        'card_type': cardType,
        'knowledge_id': knowledgeId,
        'question_id': questionId,
        'state': state,
        'correct_streak': streak,
        'reviewed_count': (prev?['reviewed_count'] as int? ?? 0) + 1,
        'last_reviewed_at': t.millisecondsSinceEpoch,
        'updated_at': t.millisecondsSinceEpoch,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  /// 批量查某章某类卡的记忆状态：{cardKey: MemorizeProgress}
  Future<Map<String, MemorizeProgress>> memorizeStates({
    required String bankId,
    required String chapter,
    required String cardType,
  }) async {
    final rows = await _db.query(
      _table,
      where: 'bank_id = ? AND chapter = ? AND card_type = ?',
      whereArgs: [bankId, chapter, cardType],
    );
    return {
      for (final r in rows) (r['card_key'] as String): _mpFromRow(r),
    };
  }

  /// 某知识点下题目卡的记忆状态（单知识点背题用）
  Future<Map<String, MemorizeProgress>> memorizeStatesByKnowledge({
    required String bankId,
    required String knowledgeId,
  }) async {
    final rows = await _db.query(
      _table,
      where: 'bank_id = ? AND card_type = ? AND knowledge_id = ?',
      whereArgs: [bankId, 'question', knowledgeId],
    );
    return {
      for (final r in rows) (r['card_key'] as String): _mpFromRow(r),
    };
  }

  /// 某章某类卡汇总：{total, learning, mastered}
  Future<({int total, int learning, int mastered})> memorizeSummary({
    required String bankId,
    required String chapter,
    required String cardType,
  }) async {
    final rows = await _db.rawQuery(
      'SELECT state, COUNT(*) AS c FROM memorize_progress '
      'WHERE bank_id = ? AND chapter = ? AND card_type = ? GROUP BY state',
      [bankId, chapter, cardType],
    );
    var learning = 0;
    var mastered = 0;
    for (final r in rows) {
      final c = (r['c'] as num?)?.toInt() ?? 0;
      if (r['state'] == 'mastered') {
        mastered = c;
      } else {
        learning += c;
      }
    }
    return (total: learning + mastered, learning: learning, mastered: mastered);
  }

  /// 重置背诵进度：knowledgeId 非空=单知识点；否则按 chapter 整章重置
  Future<void> resetMemorize({
    required String bankId,
    required String cardType,
    String? chapter,
    String? knowledgeId,
  }) async {
    if (knowledgeId != null) {
      await _db.delete(
        _table,
        where: 'bank_id = ? AND card_type = ? AND knowledge_id = ?',
        whereArgs: [bankId, cardType, knowledgeId],
      );
    } else if (chapter != null) {
      await _db.delete(
        _table,
        where: 'bank_id = ? AND card_type = ? AND chapter = ?',
        whereArgs: [bankId, cardType, chapter],
      );
    }
  }

  static MemorizeProgress _mpFromRow(Map<String, dynamic> r) => MemorizeProgress(
        cardKey: r['card_key'] as String,
        bankId: r['bank_id'] as String,
        chapter: r['chapter'] as String,
        cardType: r['card_type'] as String,
        knowledgeId: r['knowledge_id'] as String?,
        questionId: r['question_id'] as String?,
        state: (r['state'] as String? ?? 'learning') == 'mastered'
            ? MemorizeCardState.mastered
            : MemorizeCardState.learning,
        correctStreak: r['correct_streak'] as int? ?? 0,
        reviewedCount: r['reviewed_count'] as int? ?? 0,
        lastReviewedAt: r['last_reviewed_at'] != null
            ? DateTime.fromMillisecondsSinceEpoch(
                r['last_reviewed_at'] as int,
              )
            : null,
      );
}
