/// 间隔重复调度适配层（设计方案 §3.6）
///
/// 直接用 dart-fsrs 包（FSRS-4/5 官方纯 Dart 实现），这里只做薄适配：
/// - 自持 card_scheduling 表结构（主键 question_id，字段对齐 fsrs Card）
/// - [review] 把一次评分交给 fsrs Scheduler 计算，结果写回表
/// - 到期/新题队列的 SQL 查询在 quiz_repository 里做（需要 join questions）
///
/// 考研场景参数（M3 设置页可调，届时从 settings 读取）：
/// - desiredRetention 默认 0.9；冲刺期可调低至 0.8（间隔更短、密度更高）
/// - learningSteps 默认 10min → 1d；冲刺期可缩短
library;

import 'package:fsrs/fsrs.dart';
import 'package:sqflite/sqflite.dart';

class SrsService {
  SrsService(this._db, {this.enableFuzzing = true});

  final Database _db;

  /// 间隔随机抖动（产品默认开；测试关掉以保证确定性）
  final bool enableFuzzing;

  /// FSRS 调度器：参数从 settings 表读取（M3 设置页可调），
  /// desired_retention 默认 0.9；调低（如冲刺期 0.8）会拉长复习间隔、
  /// 降低复习密度——把时间留给刷新题（FSRS: interval ∝ retention^(1/decay)−1，decay<0）。
  Future<Scheduler> _scheduler() async {
    final rows = await _db.query('settings',
        where: "key = 'desired_retention'", limit: 1);
    final desiredRetention = rows.isEmpty
        ? 0.9
        : double.tryParse(rows.first['value'] as String? ?? '') ?? 0.9;
    return Scheduler(
      desiredRetention: desiredRetention,
      learningSteps: const [Duration(minutes: 10), Duration(days: 1)],
      relearningSteps: const [Duration(minutes: 10)],
      enableFuzzing: enableFuzzing,
    );
  }

  /// 读取某题的调度状态；无记录返回 null（= 新卡）。
  /// 审查 P2-4：对脏数据防御——未知状态回退 learning，relearning 缺 step 补 0。
  Future<Card?> load(String questionId) async {
    final rows = await _db.query('card_scheduling',
        where: 'question_id = ?', whereArgs: [questionId], limit: 1);
    if (rows.isEmpty) return null;
    final r = rows.first;
    final rawState = r['state'] as String? ?? 'learning';
    var state = State.learning;
    for (final s in State.values) {
      if (s.name == rawState) {
        state = s;
        break;
      }
    }
    var step = r['step'] as int?;
    if ((state == State.learning || state == State.relearning) && step == null) {
      step = 0;
    }
    return Card(
      // fsrs 的 cardId 仅作内部标识，我们用 question_id 哈希即可（不参与持久化）
      cardId: questionId.hashCode,
      state: state,
      step: step,
      stability: (r['stability'] as num?)?.toDouble(),
      difficulty: (r['difficulty'] as num?)?.toDouble(),
      due: DateTime.fromMillisecondsSinceEpoch(r['due'] as int? ?? 0, isUtc: true),
      lastReview: r['last_review'] == null
          ? null
          : DateTime.fromMillisecondsSinceEpoch(r['last_review'] as int, isUtc: true),
    );
  }

  /// 写回调度状态（upsert）
  Future<void> save(String questionId, Card card, {DateTime? now}) async {
    await _db.insert('card_scheduling', {
      'question_id': questionId,
      'state': card.state.name,
      'step': card.step,
      'stability': card.stability,
      'difficulty': card.difficulty,
      'due': card.due.toUtc().millisecondsSinceEpoch,
      'last_review': card.lastReview?.toUtc().millisecondsSinceEpoch,
      'updated_at': (now ?? DateTime.now()).millisecondsSinceEpoch,
    }, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  /// 一次评分（Again/Hard/Good/Easy）→ fsrs 计算 → 写回调度状态
  Future<Card> review(
    String questionId,
    Rating rating, {
    int? durationMs,
    DateTime? now,
  }) async {
    final card = await compute(questionId, rating, durationMs: durationMs, now: now);
    await save(questionId, card, now: now);
    return card;
  }

  /// 只计算不落库（审查 P2-8：与 answer_logs 一起在 repository 事务里原子写入）
  Future<Card> compute(
    String questionId,
    Rating rating, {
    int? durationMs,
    DateTime? now,
  }) async {
    final current = (now ?? DateTime.now()).toUtc();
    final card = await load(questionId) ?? Card(cardId: questionId.hashCode, due: current);
    final result = (await _scheduler())
        .reviewCard(card, rating, reviewDateTime: current, reviewDuration: durationMs);
    return result.card;
  }
}
