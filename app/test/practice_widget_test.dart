/// 刷题页 widget 测试（审查 P2-B：UI 层修复补齐测试覆盖）
///
/// 覆盖：判断题选项渲染（P0-1/P1-A 双渲染回归）、点选后提交可用。
/// 注意：sqflite 是真实异步 I/O，在 FakeAsync 的 testWidgets 里会挂起，
/// 因此 DB 初始化与页面加载都在 tester.runAsync 中执行。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

import 'package:quiz_app/data/app_database.dart';
import 'package:quiz_app/data/quiz_repository.dart';
import 'package:quiz_app/data/seed_loader.dart';
import 'package:quiz_app/models/models.dart';
import 'package:quiz_app/ui/practice_page.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  sqfliteFfiInit();

  Future<Database> openDb() async => databaseFactoryFfi.openDatabase(
        inMemoryDatabasePath,
        options: OpenDatabaseOptions(
          version: 3,
          onConfigure: AppDatabase.configure,
          onCreate: (db, v) => AppDatabase.createSchema(db, v),
        ),
      );

  testWidgets('判断题渲染恰好两个选项且可点选提交（审查 P0-1/P1-A/P1-B）',
      (tester) async {
    await tester.runAsync(() async {
      final db = await openDb();
      final repo = QuizRepository(db);
      // 手动构造无 options 的判断题（最坏数据，模拟未补齐入库路径）
      await repo.importBank(BankPack(
        manifest: const BankManifest(
            formatVersion: 1, bankId: 'bank-tf', name: 't', version: '1'),
        questions: [
          Question(
            id: 'bank-tf:q1',
            bankId: 'bank-tf',
            type: QuestionType.trueFalse,
            stem: '地球是圆的。',
            answer: {'正确'},
          ),
        ],
      ));

      await tester.pumpWidget(ProviderScope(
        overrides: [
          databaseProvider.overrideWithValue(Future.value(db)),
          quizRepositoryProvider.overrideWithValue(Future.value(repo)),
        ],
        child: const MaterialApp(home: PracticePage(bankId: 'bank-tf')),
      ));
      // 让 _load 的真实异步完成
      await Future<void>.delayed(const Duration(milliseconds: 200));
      await tester.pump();

      // 恰好两个「正确/错误」选项，无双渲染（审查 P1-A）
      // 恰好两个「正确/错误」选项，无双渲染（审查 P1-A）；无 key 前缀（修复：避免"正确. 正确"）
      expect(find.text('正确'), findsOneWidget);
      expect(find.text('错误'), findsOneWidget);
      expect(find.text('正确. 正确'), findsNothing);

      // 单选/判断「选完即判分」（需求）：点选后直接进入判分态，
      // 出现「回答正确」+ 评分按钮，且无「提交」按钮
      await tester.tap(find.text('正确'));
      await tester.pump();
      expect(find.text('回答正确'), findsOneWidget);
      expect(find.text('提交'), findsNothing);
      expect(find.text('良好'), findsOneWidget); // 评分条出现
      // 解析卡展示正确答案
      expect(find.textContaining('正确答案'), findsOneWidget);

      await db.close();
    });
  });

  testWidgets('自由作答题按题目重建输入框，切换题不串题（审查 P1-5）',
      (tester) async {
    await tester.runAsync(() async {
      final db = await openDb();
      final repo = QuizRepository(db);
      await repo.importBank(BankPack(
        manifest: const BankManifest(
            formatVersion: 1, bankId: 'bank-b', name: 'b', version: '1'),
        questions: [
          Question(
            id: 'bank-b:q1',
            bankId: 'bank-b',
            type: QuestionType.blank,
            stem: '普通话有____个声母。',
            answer: {'21'},
          ),
          Question(
            id: 'bank-b:q2',
            bankId: 'bank-b',
            type: QuestionType.blank,
            stem: '六书中日属于____字。',
            answer: {'象形'},
          ),
        ],
      ));

      await tester.pumpWidget(ProviderScope(
        overrides: [
          databaseProvider.overrideWithValue(Future.value(db)),
          quizRepositoryProvider.overrideWithValue(Future.value(repo)),
        ],
        child: const MaterialApp(home: PracticePage(bankId: 'bank-b')),
      ));
      await Future<void>.delayed(const Duration(milliseconds: 200));
      await tester.pump();

      // 第一题输入答案 → 填入 → 提交 → 评分
      await tester.enterText(find.byType(TextField), '21');
      await tester.pump();
      await tester.tap(find.text('填入答案'));
      await tester.pump();
      await tester.tap(find.text('提交'));
      await tester.pump();
      await tester.tap(find.text('良好'));
      await Future<void>.delayed(const Duration(milliseconds: 200));
      await tester.pump();

      // 第二题：输入框应已清空（按题目 id 重建，审查 P1-5）
      expect(find.text('六书中日属于____字。'), findsOneWidget);
      final field = tester.widget<TextField>(find.byType(TextField));
      expect(field.controller!.text, isEmpty);

      await db.close();
    });
  });

  testWidgets('简答题显示 answerFormat 作答格式提示（v3）', (tester) async {
    await tester.runAsync(() async {
      final db = await databaseFactoryFfi.openDatabase(
        inMemoryDatabasePath,
        options: OpenDatabaseOptions(
          version: 4,
          onConfigure: AppDatabase.configure,
          onCreate: (db, v) => AppDatabase.createSchema(db, v),
        ),
      );
      final repo = QuizRepository(db);
      await repo.importBank(BankPack(
        manifest: const BankManifest(
            formatVersion: 3, bankId: 'bank-af', name: 'af', version: '1'),
        questions: [
          Question(
            id: 'bank-af:q1',
            bankId: 'bank-af',
            type: QuestionType.shortAnswer,
            stem: '名词解释：六书',
            answer: {'六书指象形、指事、会意、形声、转注、假借六种造字法。'},
            answerFormat: '作答格式：①定义 ②核心特征 ③代表例证',
          ),
        ],
      ));

      await tester.pumpWidget(ProviderScope(
        overrides: [
          databaseProvider.overrideWithValue(Future.value(db)),
          quizRepositoryProvider.overrideWithValue(Future.value(repo)),
        ],
        child: const MaterialApp(home: PracticePage(bankId: 'bank-af')),
      ));
      await Future<void>.delayed(const Duration(milliseconds: 200));
      await tester.pump();

      // 作答格式提示应显示
      expect(find.text('作答格式：①定义 ②核心特征 ③代表例证'), findsOneWidget);
      // 简答输入框存在
      expect(find.byType(TextField), findsOneWidget);

      await db.close();
    });
  });

  testWidgets('空题库进入不崩溃（v7 _loadFlagState 越界回归）', (tester) async {
    await tester.runAsync(() async {
      final db = await openDb();
      final repo = QuizRepository(db);
      await repo.importBank(BankPack(
        manifest: const BankManifest(
            formatVersion: 1, bankId: 'bank-empty', name: 'e', version: '1'),
        questions: const [],
      ));
      await tester.pumpWidget(ProviderScope(
        overrides: [
          databaseProvider.overrideWithValue(Future.value(db)),
          quizRepositoryProvider.overrideWithValue(Future.value(repo)),
        ],
        child: const MaterialApp(home: PracticePage(bankId: 'bank-empty')),
      ));
      // 让 _load 完成；不应抛 RangeError（_loadFlagState 越界守卫）
      await Future<void>.delayed(const Duration(milliseconds: 200));
      await tester.pump();
      expect(find.textContaining('暂无题目'), findsOneWidget);
      await db.close();
    });
  });
}
