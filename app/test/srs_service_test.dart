import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:fsrs/fsrs.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

import 'package:quiz_app/data/app_database.dart';
import 'package:quiz_app/data/quiz_repository.dart';
import 'package:quiz_app/data/seed_loader.dart';
import 'package:quiz_app/data/srs_service.dart';
import 'package:quiz_app/models/models.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  sqfliteFfiInit();

  Future<String> demoBankJson() async =>
      await File('test/fixtures/demo_bank.json').readAsString();

  late Database db;
  late QuizRepository repo;
  late SrsService srs;

  setUp(() async {
    db = await databaseFactoryFfi.openDatabase(inMemoryDatabasePath,
        options: OpenDatabaseOptions(
          version: 3,
          onConfigure: AppDatabase.configure,
          onCreate: (db, v) => AppDatabase.createSchema(db, v),
        ));
    repo = QuizRepository(db);
    srs = SrsService(db);
    await repo.importBank(SeedLoader.parse(await demoBankJson()));
  });

  tearDown(() => db.close());

  final qid = 'bank-demo-kaoyan:q_0001';

  group('FSRS 调度（设计方案 §3.6）', () {
    test('新卡首次评分后建立调度记录，due 在未来', () async {
      final now = DateTime.now().toUtc();
      final card = await srs.review(qid, Rating.good, now: now);
      expect(card.due.isAfter(now), isTrue);
      final loaded = await srs.load(qid);
      expect(loaded, isNotNull);
      expect(loaded!.state, State.learning);
      expect(loaded.due.isAfter(now), isTrue);
    });

    test('多次 good 后进入 review 状态', () async {
      var card = await srs.review(qid, Rating.good, now: DateTime.now().toUtc());
      card = await srs.review(qid, Rating.good, now: DateTime.now().toUtc());
      card = await srs.review(qid, Rating.good, now: DateTime.now().toUtc());
      // 学习步进 10min → 1d → 后进入 review
      expect(card.state, State.review);
    });

    test('again 停留在学习态（due 在近期）', () async {
      final now = DateTime.now().toUtc();
      final card = await srs.review(qid, Rating.again, now: now);
      expect(card.state, State.learning);
      expect(card.due.isBefore(now.add(const Duration(hours: 1))), isTrue);
    });
  });

  group('到期队列', () {
    test('due 在未来的题不进今日队列', () async {
      await srs.review(qid, Rating.good, now: DateTime.now().toUtc());
      expect(await repo.reviewQueue(), isEmpty);
      expect(await repo.dueCount(), 0);
    });

    test('due 已过的题进入今日复习队列', () async {
      final now = DateTime.now().toUtc();
      await srs.review(qid, Rating.good, now: now);
      // 直接把 due 改成过去，模拟到期
      await db.update('card_scheduling', {'due': now.subtract(const Duration(days: 1)).millisecondsSinceEpoch},
          where: 'question_id = ?', whereArgs: [qid]);
      final queue = await repo.reviewQueue();
      expect(queue.map((q) => q.id), contains(qid));
      expect(await repo.dueCount(), 1);
    });

    test('新题计数：未建立调度的题', () async {
      final all = await repo.questions();
      expect(await repo.newCount(), all.length);
      await srs.review(qid, Rating.good, now: DateTime.now().toUtc());
      expect(await repo.newCount(), all.length - 1);
    });
  });

  group('错题本（设计方案 §3.5）', () {
    test('答错自动归集', () async {
      final now = DateTime.now().millisecondsSinceEpoch;
      await db.insert('answer_logs', AnswerLog(
        questionId: qid,
        mode: 'learn',
        result: 'wrong',
        timeMs: 1000,
        answeredAt: now,
      ).toMap());
      final wrong = await repo.wrongBookQuestions();
      expect(wrong.map((q) => q.id), contains(qid));
      expect(await repo.inWrongBook(qid), isTrue);
    });

    test('手动移出后不再归集', () async {
      final now = DateTime.now().millisecondsSinceEpoch;
      await db.insert('answer_logs', AnswerLog(
        questionId: qid,
        mode: 'learn',
        result: 'wrong',
        timeMs: 1000,
        answeredAt: now,
      ).toMap());
      await repo.removeFromWrongBook(qid);
      expect(await repo.inWrongBook(qid), isFalse);
      expect(await repo.wrongBookQuestions(), isEmpty);
    });

    test('连续答对计数', () async {
      final now = DateTime.now().millisecondsSinceEpoch;
      // 先错一次，再连续对两次 → 连续正确 = 2（从最新往前数）
      await db.insert('answer_logs', AnswerLog(
        questionId: qid,
        mode: 'learn', result: 'wrong', timeMs: 500, answeredAt: now,
      ).toMap());
      await db.insert('answer_logs', AnswerLog(
        questionId: qid,
        mode: 'wrong_rework', result: 'correct', timeMs: 500, answeredAt: now + 1,
      ).toMap());
      await db.insert('answer_logs', AnswerLog(
        questionId: qid,
        mode: 'wrong_rework', result: 'correct', timeMs: 500, answeredAt: now + 2,
      ).toMap());
      expect(await repo.consecutiveCorrectCount(qid), 2);
      // 达到阈值判定
      expect(await repo.consecutiveCorrectCount(qid) >= QuizRepository.wrongBookRetireThreshold, isTrue);
    });

    test('重新归集后连续答对链条重置（审查 B2）', () async {
      final now = DateTime.now().millisecondsSinceEpoch;
      // 第一次归集：错 + 重刷连对 2 次 → 链条 2
      await db.insert('answer_logs', AnswerLog(
        questionId: qid, mode: 'learn', result: 'wrong', timeMs: 500, answeredAt: now,
      ).toMap());
      await db.insert('answer_logs', AnswerLog(
        questionId: qid, mode: 'wrong_rework', result: 'correct', timeMs: 500, answeredAt: now + 1,
      ).toMap());
      await db.insert('answer_logs', AnswerLog(
        questionId: qid, mode: 'wrong_rework', result: 'correct', timeMs: 500, answeredAt: now + 2,
      ).toMap());
      expect(await repo.consecutiveCorrectCount(qid), 2);
      // 再次答错（learn）→ 重新归集，链条应重置为 0（只数最近答错之后）
      await db.insert('answer_logs', AnswerLog(
        questionId: qid, mode: 'learn', result: 'wrong', timeMs: 500, answeredAt: now + 3,
      ).toMap());
      expect(await repo.consecutiveCorrectCount(qid), 0);
      // 重刷答对 1 次 → 仍 1（需重新连对 2 次才移出）
      await db.insert('answer_logs', AnswerLog(
        questionId: qid, mode: 'wrong_rework', result: 'correct', timeMs: 500, answeredAt: now + 4,
      ).toMap());
      expect(await repo.consecutiveCorrectCount(qid), 1);
    });
  });
}
