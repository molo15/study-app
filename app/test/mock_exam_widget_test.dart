/// 模拟卷答题流程 widget 测试（定位模拟器闪退）
///
/// 用真实 DB + 真实 demo 题库包（含 mockPapers），完整走：
/// 进入答题页 → 渲染题干/倒计时/选项 → 作答 → 交卷 → 成绩单弹窗。
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

import 'package:quiz_app/data/app_database.dart';
import 'package:quiz_app/data/quiz_repository.dart';
import 'package:quiz_app/data/seed_loader.dart';
import 'package:quiz_app/models/models.dart';
import 'package:quiz_app/ui/mock_exam_page.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  sqfliteFfiInit();

  Future<String> demoBankJson() async =>
      await File('test/fixtures/demo_bank.json').readAsString();

  testWidgets('模拟卷完整答题流程不崩溃', (tester) async {
    await tester.runAsync(() async {
      final db = await databaseFactoryFfi.openDatabase(
        inMemoryDatabasePath,
        options: OpenDatabaseOptions(
          version: 3,
          onConfigure: AppDatabase.configure,
          onCreate: (db, v) => AppDatabase.createSchema(db, v),
        ),
      );
      final repo = QuizRepository(db);
      final pack = SeedLoader.parse(await demoBankJson());
      await repo.importBank(pack);
      expect(pack.mockPapers, isNotEmpty, reason: 'demo 包应含模拟卷');
      final paper = pack.mockPapers.first;

      await tester.pumpWidget(ProviderScope(
        overrides: [
          databaseProvider.overrideWithValue(Future.value(db)),
          quizRepositoryProvider.overrideWithValue(Future.value(repo)),
        ],
        child: MaterialApp(home: MockExamPage(paper: paper)),
      ));
      // 等真实异步加载完成
      await Future<void>.delayed(const Duration(milliseconds: 400));
      await tester.pump();

      // 答题页渲染：倒计时（10:00）+ 题干
      final qs = pack.questions.where((q) => paper.questionIds.contains(q.id)).toList();
      expect(qs, isNotEmpty);
      expect(find.text('10:00'), findsOneWidget, reason: '初始倒计时 10 分钟');
      final q0 = qs.first;
      expect(find.text(q0.stem), findsOneWidget, reason: '应显示第一题题干');

      // 逐题作答并切下一题（走完整答题循环）
      for (final q in qs) {
        if (q.type == QuestionType.singleChoice ||
            q.type == QuestionType.trueFalse) {
          final firstOption = q.options.isNotEmpty ? q.options.first : null;
          if (firstOption != null) {
            // 判断题显示纯文本（无 key 前缀，修复后）；选择题带 key 前缀
            await tester.tap(find.text(q.type == QuestionType.trueFalse
                ? firstOption.text
                : '${firstOption.key}. ${firstOption.text}'));
            await tester.pump();
          }
        }
        // 切下一题
        final next = find.text('下一题');
        if (next.evaluate().isNotEmpty) {
          await tester.tap(next);
          await tester.pump();
        }
      }
      await tester.pump(const Duration(milliseconds: 100));

      // 交卷（底部按钮）→ 成绩单弹窗
      await tester.tap(find.text('交卷').first);
      await Future<void>.delayed(const Duration(milliseconds: 400));
      await tester.pump();
      expect(find.text('考试完成'), findsOneWidget, reason: '交卷后应弹出成绩单');
      expect(find.textContaining('得分'), findsOneWidget);

      // 完成 → 返回
      await tester.tap(find.text('完成'));
      await tester.pump();

      // 会话已落库
      final sessions = await repo.mockSessions(paperId: paper.id);
      expect(sessions, hasLength(1));
      expect(sessions.first.score, greaterThanOrEqualTo(0));

      await db.close();
    });
  });
}
