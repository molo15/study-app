import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

import 'package:quiz_app/data/app_database.dart';
import 'package:quiz_app/data/seed_loader.dart';
import 'package:quiz_app/models/models.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  sqfliteFfiInit();

  // 读取 assets 里的示例题库包（测试 cwd 为包根目录）
  Future<String> demoBankJson() async =>
      await File('test/fixtures/demo_bank.json').readAsString();

  late Database db;

  setUp(() async {
    db = await databaseFactoryFfi.openDatabase(inMemoryDatabasePath,
        options: OpenDatabaseOptions(
          version: 3,
          onConfigure: AppDatabase.configure,
          onCreate: (db, v) => AppDatabase.createSchema(db, v),
        ));
  });

  tearDown(() => db.close());

  group('题库包解析（设计方案 §2.4）', () {
    test('示例题库包解析：10 题覆盖 5 种题型', () async {
      final pack = SeedLoader.parse(await demoBankJson());
      expect(pack.manifest.bankId, 'bank-demo-kaoyan');
      expect(pack.manifest.formatVersion, 2);
      expect(pack.questions, hasLength(10));
      final types = pack.questions.map((q) => q.type).toSet();
      expect(types, {
        QuestionType.singleChoice,
        QuestionType.multiChoice,
        QuestionType.blank,
        QuestionType.shortAnswer,
        QuestionType.trueFalse,
      });
    });

    test('题目 id 为全局唯一格式 {bank_id}:{序号}', () async {
      final pack = SeedLoader.parse(await demoBankJson());
      final ids = pack.questions.map((q) => q.id).toSet();
      expect(ids.length, 10);
      for (final q in pack.questions) {
        expect(q.id, startsWith('${pack.manifest.bankId}:'));
      }
    });

    test('answer 统一编码为字符串集合', () async {
      final pack = SeedLoader.parse(await demoBankJson());
      final single = pack.questions.firstWhere((q) => q.type == QuestionType.singleChoice);
      expect(single.answer, {'A'});
      final multi = pack.questions.firstWhere((q) => q.type == QuestionType.multiChoice);
      expect(multi.answer, {'A', 'B', 'D'});
    });

    test('formatVersion 过新拒绝导入', () {
      expect(
        () => SeedLoader.parse(
            '{"formatVersion": 99, "bankId": "x", "name": "x", "version": "1", "questions": []}'),
        throwsFormatException,
      );
    });

    test('判断题自动补齐「正确/错误」选项（审查 P0-1）', () async {
      final demo = jsonDecode(await demoBankJson()) as Map<String, dynamic>;
      final pack = SeedLoader.parse(jsonEncode(demo));
      final tf = pack.questions.where((q) => q.type == QuestionType.trueFalse).toList();
      expect(tf, isNotEmpty);
      for (final q in tf) {
        expect(q.options, hasLength(2));
        expect(q.options.map((o) => o.key), containsAll(['正确', '错误']));
      }
    });
  });

  group('题库包导入（设计方案 §3.4）', () {
    test('幂等导入：重复导入不产生重复题', () async {
      final pack = SeedLoader.parse(await demoBankJson());
      await SeedLoader.import(db, pack);
      await SeedLoader.import(db, pack);
      final rows = await db.query('questions');
      expect(rows, hasLength(10));
    });

    test('软归档：新包删除的题标记 archived 而非物理删除', () async {
      final pack = SeedLoader.parse(await demoBankJson());
      await SeedLoader.import(db, pack);

      // 构造仅含 5 题的"新版本"包（模拟题包更新删除了后 5 题）
      final subset = {
        ...jsonDecode(await demoBankJson()) as Map<String, dynamic>,
        'version': '2.0.0',
        'questions': (jsonDecode(await demoBankJson())
                as Map<String, dynamic>)['questions']
            .take(5)
            .toList(),
      };
      await SeedLoader.import(db, SeedLoader.parse(jsonEncode(subset)));

      final active =
          await db.query('questions', where: "status = 'active'");
      final archived =
          await db.query('questions', where: "status = 'archived'");
      expect(active, hasLength(5));
      expect(archived, hasLength(5));
      // 版本记录更新
      final version = await db.query('settings',
          where: "key = 'bank_bank-demo-kaoyan_version'");
      expect(version.single['value'], '2.0.0');
    });

    test('作答日志 append-only 写入', () async {
      final now = DateTime.now().millisecondsSinceEpoch;
      await db.insert('answer_logs', AnswerLog(
        questionId: 'bank-test:q1',
        mode: 'learn',
        result: 'correct',
        timeMs: 1500,
        answeredAt: now,
      ).toMap());
      await db.insert('answer_logs', AnswerLog(
        questionId: 'bank-test:q1',
        mode: 'wrong_rework',
        result: 'wrong',
        timeMs: 800,
        answeredAt: now + 1,
      ).toMap());
      final rows = await db.query('answer_logs');
      expect(rows, hasLength(2));
    });

    test('空题包导入不归档现有题库（审查 P1-1）', () async {
      final pack = SeedLoader.parse(await demoBankJson());
      await SeedLoader.import(db, pack);
      // 导入空包（同 bank_id，无题）
      await SeedLoader.import(db, SeedLoader.parse(
          '{"formatVersion": 1, "bankId": "bank-demo-kaoyan", "name": "x", "version": "2.0.0", "questions": []}'));
      final active = await db.query('questions', where: "status = 'active'");
      expect(active, hasLength(10)); // 不被归档
    });
  });
}
