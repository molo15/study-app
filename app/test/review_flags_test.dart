import 'dart:io';

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

  setUp(() async {
    db = await databaseFactoryFfi.openDatabase(inMemoryDatabasePath,
        options: OpenDatabaseOptions(
          version: 7, // v7 含 review_flags 表
          onConfigure: AppDatabase.configure,
          onCreate: (db, v) => AppDatabase.createSchema(db, v),
        ));
    repo = QuizRepository(db);
    await repo.importBank(SeedLoader.parse(await demoBankJson()));
  });

  tearDown(() => db.close());

  final qid = 'bank-demo-kaoyan:q_0001';

  group('审题标记（v7 review_flags）', () {
    test('初始未标记', () async {
      expect(await repo.isFlagged(qid), isFalse);
    });

    test('标记后可查询、可导出、可取消', () async {
      // 标记带备注
      await repo.flagQuestion(qid, 'bank-demo-kaoyan', comment: '答案错误');
      expect(await repo.isFlagged(qid), isTrue);

      // 导出清单包含该题与题干快照
      final json = await repo.exportReviewFlags();
      expect(json.contains(qid), isTrue);
      final rows = await repo.reviewFlags();
      expect(rows, hasLength(1));
      expect(rows.first['comment'], '答案错误');
      expect(rows.first['stem'], isNotNull); // 题干快照已 join

      // 取消标记
      await repo.unflagQuestion(qid);
      expect(await repo.isFlagged(qid), isFalse);
      expect(await repo.reviewFlags(), isEmpty);
    });

    test('无标记时导出为空清单', () async {
      final json = await repo.exportReviewFlags();
      expect(json.contains('"count": 0'), isTrue);
    });
  });
}
