import 'dart:convert';
import 'dart:io';

import 'package:archive/archive.dart';
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
    // 关掉 fuzz 抖动，保证 retention 对比测试确定性
    srs = SrsService(db, enableFuzzing: false);
    await repo.importBank(SeedLoader.parse(await demoBankJson()));
  });

  tearDown(() => db.close());

  final qid = 'bank-demo-kaoyan:q_0001';

  group('zip 题库包导入（设计方案 §2.4）', () {
    test('解析 manifest.json + questions.json 并导入', () async {
      final manifest = {
        'formatVersion': 1,
        'bankId': 'bank-zip-test',
        'name': 'zip 测试题库',
        'version': '1.0.0',
        'chapters': ['章节A'],
      };
      final questions = [
        {
          'id': 'bank-zip-test:q1',
          'type': 'single_choice',
          'stem': 'zip 测试题',
          'options': [
            {'key': 'A', 'text': '甲'},
            {'key': 'B', 'text': '乙'},
          ],
          'answer': 'A',
          'explanation': '解析',
          'tags': ['测试'],
          'chapter': '章节A',
          'difficulty': 'easy',
        }
      ];
      final zipBytes = ZipEncoder().encode(Archive()
        ..add(ArchiveFile.string('manifest.json', jsonEncode(manifest)))
        ..add(ArchiveFile.string('questions.json', jsonEncode(questions))));
      final pack = SeedLoader.parseZipBytes(zipBytes);
      expect(pack.manifest.bankId, 'bank-zip-test');
      expect(pack.questions.single.id, 'bank-zip-test:q1');
      await repo.importBank(pack);
      expect(await repo.bankIds(), contains('bank-zip-test'));
    });

    test('zip 缺 manifest.json 抛 FormatException', () {
      final zipBytes = ZipEncoder().encode(Archive()
        ..add(ArchiveFile.string('questions.json', '[]')));
      expect(() => SeedLoader.parseZipBytes(zipBytes), throwsFormatException);
    });
  });

  group('模拟卷系统（需求）', () {
    test('题库包解析 mockPapers 并导入', () async {
      final demo = jsonDecode(await demoBankJson()) as Map<String, dynamic>;
      final pack = SeedLoader.parse(jsonEncode(demo));
      expect(pack.mockPapers, isNotEmpty);
      expect(pack.mockPapers.first.id, 'bank-demo-kaoyan:mp_001');
      expect(pack.mockPapers.first.questionIds, hasLength(5));
      await repo.importBank(pack);
      final papers = await repo.mockPapers(bankId: 'bank-demo-kaoyan');
      expect(papers, hasLength(1));
      expect(papers.first.durationMin, 10);
    });

    test('模拟卷成绩单与 session 关联日志', () async {
      final now = DateTime.now().millisecondsSinceEpoch;
      final sessionId = await repo.insertMockSession(MockSession(
        paperId: 'bank-demo-kaoyan:mp_001',
        startedAt: now,
        durationMin: 10,
        total: 2,
        correct: 0, partial: 0, wrong: 0, skipped: 0,
        score: 0,
        submittedAt: now,
      ));
      await db.insert('answer_logs', AnswerLog(
        questionId: qid,
        mode: 'mock',
        result: 'correct',
        timeMs: 500,
        answeredAt: now,
        sessionId: sessionId,
      ).toMap());
      await repo.updateMockSession(MockSession(
        id: sessionId,
        paperId: 'bank-demo-kaoyan:mp_001',
        startedAt: now,
        durationMin: 10,
        total: 2,
        correct: 1, partial: 0, wrong: 0, skipped: 1,
        score: 50,
        submittedAt: now,
      ));
      final sessions = await repo.mockSessions(paperId: 'bank-demo-kaoyan:mp_001');
      expect(sessions, hasLength(1));
      expect(sessions.first.score, 50);
      final logs = await db.query('answer_logs', where: 'session_id = ?', whereArgs: [sessionId]);
      expect(logs, hasLength(1));
      expect(logs.first['mode'], 'mock');
    });
  });

  group('学习统计（设计方案 §3.8）', () {
    test('作答日志聚合为统计', () async {
      final now = DateTime.now().millisecondsSinceEpoch;
      await db.insert('answer_logs', AnswerLog(
        questionId: qid, mode: 'learn', result: 'correct', timeMs: 1000, answeredAt: now,
      ).toMap());
      await db.insert('answer_logs', AnswerLog(
        questionId: qid, mode: 'learn', result: 'wrong', timeMs: 2000, answeredAt: now,
      ).toMap());
      await db.insert('answer_logs', AnswerLog(
        questionId: 'bank-demo-kaoyan:q_0002', mode: 'learn',
        result: 'partial', timeMs: 500, answeredAt: now,
      ).toMap());
      final s = await repo.studyStats();
      expect(s.totalAnswered, 3);
      expect(s.correctCount, 1);
      expect(s.partialCount, 1);
      expect(s.wrongCount, 1);
      expect(s.totalTimeMs, 3500);
      expect(s.accuracy, closeTo(50.0, 0.01), reason: 'accuracy=(correct+0.5*partial)/total=(1+0.5)/3=50%');
      // 章节分布
      expect(s.byChapter, isNotEmpty);
      final english = s.byChapter.firstWhere((c) => c.chapter == '考研英语');
      expect(english.total, 2);
      // 近 7 日：今天有 3 次
      expect(s.daily.last.count, 3);
      expect(s.daily, hasLength(7));
    });
  });

  group('复习参数（设计方案 §3.6）', () {
    test('desired_retention 从 settings 读取且影响调度', () async {
      final now = DateTime.now().toUtc();
      // 评 3 次 good：10min → 1d → 进入 review（此时间隔由 desiredRetention 决定）
      for (var i = 0; i < 3; i++) {
        await srs.review(qid, Rating.good, now: now);
      }
      final due90 = (await srs.load(qid))!.due;

      // 调低到 0.8：目标保持率低 → 复习间隔更长（FSRS: interval ∝ retention^(1/decay)−1，decay<0）
      await repo.setSetting('desired_retention', '0.8');
      await db.delete('card_scheduling', where: 'question_id = ?', whereArgs: [qid]);
      for (var i = 0; i < 3; i++) {
        await srs.review(qid, Rating.good, now: now);
      }
      final due80 = (await srs.load(qid))!.due;
      expect(due80.isAfter(due90), isTrue);
    });
  });

  group('备份与维护（设计方案 §3.4/§7）', () {
    test('导出/恢复 JSON 数据一致', () async {
      final now = DateTime.now().millisecondsSinceEpoch;
      await db.insert('answer_logs', AnswerLog(
        questionId: qid, mode: 'learn', result: 'correct', timeMs: 1000, answeredAt: now,
      ).toMap());
      await srs.review(qid, Rating.good, now: DateTime.now().toUtc());
      await repo.removeFromWrongBook('bank-demo-kaoyan:q_0002');

      final json = await repo.exportJson();
      // 换一个全新库恢复
      final db2 = await databaseFactoryFfi.openDatabase(inMemoryDatabasePath,
          options: OpenDatabaseOptions(
            version: 3,
            onConfigure: AppDatabase.configure,
            onCreate: (db, v) => AppDatabase.createSchema(db, v),
          ));
      // 新设计：题库以本地内置包为准，先 seed 题库再恢复用户状态（多端方案 §2.5）
      await QuizRepository(db2).importBank(SeedLoader.parse(await demoBankJson()));
      await QuizRepository(db2).restoreJson(json);
      final stats2 = await QuizRepository(db2).studyStats();
      expect(stats2.totalAnswered, 1);
      expect((await QuizRepository(db2).questions()).length, 10);
      // 审查 P1-2：排除记录随备份恢复
      final exclusions = await db2.query('wrong_book_exclusions');
      expect(exclusions, hasLength(1));
      await db2.close();
    });

    test('答错后自动恢复错题归集（审查 P1-8）', () async {
      final now = DateTime.now().millisecondsSinceEpoch;
      // 答错 → 归集
      await db.insert('answer_logs', AnswerLog(
        questionId: qid, mode: 'learn', result: 'wrong', timeMs: 500, answeredAt: now,
      ).toMap());
      expect(await repo.inWrongBook(qid), isTrue);
      // 手动移出 → 不再归集
      await repo.removeFromWrongBook(qid);
      expect(await repo.inWrongBook(qid), isFalse);
      // 再答错 → 自动恢复归集
      await repo.logAnswer(AnswerLog(
        questionId: qid, mode: 'learn', result: 'wrong', timeMs: 500, answeredAt: now + 1,
      ));
      expect(await repo.inWrongBook(qid), isTrue);
    });

    test('归档清理删除归档题及其记录', () async {
      // 构造 5 题子集包模拟更新，归档后 5 题
      final demo = jsonDecode(await demoBankJson()) as Map<String, dynamic>;
      final subset = {
        ...demo,
        'version': '2.0.0',
        'questions': (demo['questions'] as List).take(5).toList(),
      };
      await repo.importBank(SeedLoader.parse(jsonEncode(subset)));

      // 给一道归档题制造作答记录
      final archivedId = 'bank-demo-kaoyan:q_0006';
      final now = DateTime.now().millisecondsSinceEpoch;
      await db.insert('answer_logs', AnswerLog(
        questionId: archivedId, mode: 'learn', result: 'wrong', timeMs: 500, answeredAt: now,
      ).toMap());

      final banks = await repo.banks();
      final bank = banks.firstWhere((b) => b.bankId == 'bank-demo-kaoyan');
      expect(bank.archived, 5);

      final removed = await repo.purgeArchived('bank-demo-kaoyan');
      expect(removed, 5);
      final rows = await db.query('answer_logs', where: 'question_id = ?', whereArgs: [archivedId]);
      expect(rows, isEmpty);
      final left = await db.query('questions', where: "status = 'archived'");
      expect(left, isEmpty);
    });
  });
}
