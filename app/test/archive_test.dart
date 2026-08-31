import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

import 'package:quiz_app/data/app_database.dart';
import 'package:quiz_app/data/quiz_repository.dart';
import 'package:quiz_app/data/seed_loader.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  sqfliteFfiInit();

  Future<String> demoBankJson() async =>
      await File('test/fixtures/demo_bank.json').readAsString();

  late Database db;
  late QuizRepository repo;
  final qid = 'bank-demo-kaoyan:q_0001';

  /// 构造一份覆盖全部用户状态表的假数据
  Future<void> seedUserState(Database d) async {
    final now = DateTime.now().millisecondsSinceEpoch;
    await d.insert('answer_logs', {
      'question_id': qid,
      'mode': 'practice',
      'result': 'correct',
      'rating': 4,
      'time_ms': 3200,
      'answered_at': now,
      'user_answer': 'A',
    });
    await d.insert('card_scheduling', {
      'question_id': qid,
      'state': 'review',
      'stability': 3.5,
      'difficulty': 5.0,
      'due': now,
      'last_review': now,
      'updated_at': now,
    });
    await d.insert('memorize_progress', {
      'card_key': 'xdhy:c1:kp1',
      'bank_id': 'bank-demo-kaoyan',
      'chapter': '第一章',
      'card_type': 'knowledge',
      'knowledge_id': 'kp1',
      'state': 'mastered',
      'correct_streak': 5,
      'reviewed_count': 6,
      'last_reviewed_at': now,
      'updated_at': now,
    });
    await d.insert('review_flags', {
      'question_id': qid,
      'bank_id': 'bank-demo-kaoyan',
      'comment': '答案有误',
      'created_at': now,
    });
    await d.insert('wrong_book_exclusions', {
      'question_id': qid,
      'created_at': now,
    });
    await d.insert('mock_papers', {
      'id': 'paper1',
      'bank_id': 'bank-demo-kaoyan',
      'name': '综合模拟',
      'duration_min': 60,
      'question_ids': '[1]',
      'created_at': now,
    });
    await d.insert('mock_sessions', {
      'paper_id': 'paper1',
      'started_at': now,
      'duration_min': 60,
      'total': 10,
      'correct': 8,
      'partial': 1,
      'wrong': 1,
      'skipped': 0,
      'score': 85,
      'submitted_at': now,
    });
    await d.insert('settings', {'key': 'theme', 'value': 'frost'});
  }

  setUp(() async {
    db = await databaseFactoryFfi.openDatabase(inMemoryDatabasePath,
        options: OpenDatabaseOptions(
          version: 11, // 最新 schema（含 memorize_progress / review_flags）
          onConfigure: AppDatabase.configure,
          onCreate: (db, v) => AppDatabase.createSchema(db, v),
        ));
    repo = QuizRepository(db);
    await repo.importBank(SeedLoader.parse(await demoBankJson()));
    await seedUserState(db);
  });

  tearDown(() => db.close());

  group('存档 v3（多端方案 §2）', () {
    test('导出为 zip（PK 魔数），预览格式 v3', () async {
      final bytes = await repo.exportArchive();
      expect(bytes, isNotEmpty);
      // zip 魔数 PK\x03\x04
      expect(bytes[0], 0x50);
      expect(bytes[1], 0x4B);
      expect(bytes[2], 0x03);
      expect(bytes[3], 0x04);

      final preview = await repo.parseArchive(bytes);
      expect(preview.formatVersion, 3);
      expect(preview.exportedAt, isNotNull);
      expect(preview.kind, ArchiveKind.manual);
      expect(preview.bankVersions,
          contains('bank-demo-kaoyan')); // 题库版本清单已带上
    });

    test('导出→清库→导入：用户状态一致，题库不被覆盖', () async {
      final questionsBefore = await db.query('questions');
      expect(questionsBefore, isNotEmpty); // 种子题库存在

      final bytes = await repo.exportArchive();

      // 模拟另一端全新状态：清空全部用户状态表
      await db.delete('answer_logs');
      await db.delete('card_scheduling');
      await db.delete('memorize_progress');
      await db.delete('review_flags');
      await db.delete('wrong_book_exclusions');
      await db.delete('mock_sessions');
      await db.delete('mock_papers');
      await db.delete('settings');
      expect(await db.query('answer_logs'), isEmpty);

      final result = await repo.restoreArchive(bytes);
      expect(result.restoredLogs, 1);
      expect(result.restoredCards, 1);

      // 用户状态完整恢复
      expect(await db.query('answer_logs'), hasLength(1));
      expect(await db.query('card_scheduling'), hasLength(1));
      expect(await db.query('memorize_progress'), hasLength(1));
      expect(await db.query('review_flags'), hasLength(1));
      expect(await db.query('wrong_book_exclusions'), hasLength(1));
      // mock_papers：demo 包自带示例卷 + seedUserState 的 paper1
      expect((await db.query('mock_papers')).any((p) => p['id'] == 'paper1'),
          isTrue);
      expect(await db.query('mock_sessions'), hasLength(1));
      // settings：importBank 会写题库版本等若干条，至少含 theme（seedUserState 写入）
      final settings = await db.query('settings');
      expect(settings, isNotEmpty);
      expect(settings.any((s) => s['key'] == 'theme' && s['value'] == 'frost'),
          isTrue);

      // 题库不被存档覆盖（保持本地种子）
      final questionsAfter = await db.query('questions');
      expect(questionsAfter.length, questionsBefore.length);
      expect(questionsAfter.first['id'], questionsBefore.first['id']);
      expect(questionsAfter.first['stem'], questionsBefore.first['stem']);
    });

    test('v2 旧备份兼容：restoreArchive 自动识别 JSON，忽略题目字段', () async {
      final questionsBefore = await db.query('questions');
      final v2 = const JsonEncoder().convert({
        'formatVersion': 2,
        'exportedAt': '2026-01-01T00:00:00',
        'questions': [
          {'id': 'FAKE', 'stem': '假题', 'bank_id': 'fake'},
        ],
        'answerLogs': [
          {
            'question_id': qid,
            'mode': 'practice',
            'result': 'wrong',
            'rating': 1,
            'time_ms': 2000,
            'answered_at': 1700000000000,
          },
        ],
        'cardScheduling': [],
        'wrongBookExclusions': [],
        'mockPapers': [],
        'mockSessions': [],
        'settings': [],
      });
      final bytes = Uint8List.fromList(utf8.encode(v2));

      final preview = await repo.parseArchive(bytes);
      expect(preview.formatVersion, 2);

      await repo.restoreArchive(bytes);
      // 用户状态恢复（v2 answerLogs 生效）
      final logs = await db.query('answer_logs');
      expect(logs, hasLength(1));
      expect(logs.first['result'], 'wrong');
      // 题库不被 v2 的假题覆盖
      final questionsAfter = await db.query('questions');
      expect(questionsAfter.length, questionsBefore.length);
      expect(questionsAfter.any((q) => q['id'] == 'FAKE'), isFalse);
    });

    test('损坏文件：校验失败抛 FormatException，库保持原状', () async {
      final logsBefore = await db.query('answer_logs');
      final bad = Uint8List.fromList(utf8.encode('{not valid json'));
      expect(() => repo.restoreArchive(bad), throwsFormatException);
      expect(await db.query('answer_logs'), hasLength(logsBefore.length));
    });

    test('非法版本：抛 FormatException', () async {
      final bad = Uint8List.fromList(utf8.encode(
          '{"formatVersion": 99, "answerLogs": [], "cardScheduling": [], "settings": []}'));
      expect(() => repo.restoreArchive(bad), throwsFormatException);
    });
  });
}
