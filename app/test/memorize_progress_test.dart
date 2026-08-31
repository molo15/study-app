import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

import 'package:quiz_app/data/app_database.dart';
import 'package:quiz_app/data/quiz_repository.dart';
import 'package:quiz_app/models/models.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  sqfliteFfiInit();

  late Database db;
  late QuizRepository repo;

  setUp(() async {
    db = await databaseFactoryFfi.openDatabase(inMemoryDatabasePath,
        options: OpenDatabaseOptions(
          version: 11,
          onConfigure: AppDatabase.configure,
          onCreate: (db, v) => AppDatabase.createSchema(db, v),
        ));
    repo = QuizRepository(db);
  });

  tearDown(() => db.close());

  group('背题存档（v11）', () {
    test('初始无记录时 memorizeStates 为空', () async {
      final states = await repo.memorizeStates(
        bankId: 'b1',
        chapter: '第一章',
        cardType: 'knowledge',
      );
      expect(states, isEmpty);
    });

    test('记录一次背会后仍为学习中（streak=1），两次后为已掌握', () async {
      const bankId = 'b1';
      const chapter = '第一章';
      final t0 = DateTime(2026, 1, 1);
      await repo.recordMemorize(
        cardKey: QuizRepository.kpKey('kp1'),
        bankId: bankId,
        chapter: chapter,
        cardType: 'knowledge',
        knowledgeId: 'kp1',
        know: true,
        now: t0,
      );
      var states = await repo.memorizeStates(
        bankId: bankId,
        chapter: chapter,
        cardType: 'knowledge',
      );
      var st = states[QuizRepository.kpKey('kp1')]!;
      expect(st.state, MemorizeCardState.learning);
      expect(st.correctStreak, 1);
      expect(st.reviewedCount, 1);
      expect(st.lastReviewedAt, t0);

      await repo.recordMemorize(
        cardKey: QuizRepository.kpKey('kp1'),
        bankId: bankId,
        chapter: chapter,
        cardType: 'knowledge',
        knowledgeId: 'kp1',
        know: true,
        now: t0.add(const Duration(days: 1)),
      );
      states = await repo.memorizeStates(
        bankId: bankId,
        chapter: chapter,
        cardType: 'knowledge',
      );
      st = states[QuizRepository.kpKey('kp1')]!;
      expect(st.state, MemorizeCardState.mastered);
      expect(st.correctStreak, 2);
      expect(st.reviewedCount, 2);
    });

    test('标"还不会"会清零连续背会次数', () async {
      await repo.recordMemorize(
        cardKey: QuizRepository.qKey('q1'),
        bankId: 'b1',
        chapter: '第一章',
        cardType: 'question',
        questionId: 'q1',
        know: true,
      );
      // 第一次背会 → streak=1
      await repo.recordMemorize(
        cardKey: QuizRepository.qKey('q1'),
        bankId: 'b1',
        chapter: '第一章',
        cardType: 'question',
        questionId: 'q1',
        know: false,
      );
      // 还不会 → streak=0
      final states = await repo.memorizeStates(
        bankId: 'b1',
        chapter: '第一章',
        cardType: 'question',
      );
      final st = states[QuizRepository.qKey('q1')]!;
      expect(st.state, MemorizeCardState.learning);
      expect(st.correctStreak, 0);
      expect(st.reviewedCount, 2);
    });

    test('memorizeSummary 正确统计 学习中/已掌握', () async {
      // kp1 背会两次 → mastered
      await repo.recordMemorize(
        cardKey: QuizRepository.kpKey('kp1'),
        bankId: 'b1',
        chapter: '第一章',
        cardType: 'knowledge',
        knowledgeId: 'kp1',
        know: true,
      );
      await repo.recordMemorize(
        cardKey: QuizRepository.kpKey('kp1'),
        bankId: 'b1',
        chapter: '第一章',
        cardType: 'knowledge',
        knowledgeId: 'kp1',
        know: true,
      );
      // kp2 背会一次 → learning
      await repo.recordMemorize(
        cardKey: QuizRepository.kpKey('kp2'),
        bankId: 'b1',
        chapter: '第一章',
        cardType: 'knowledge',
        knowledgeId: 'kp2',
        know: true,
      );
      final summary = await repo.memorizeSummary(
        bankId: 'b1',
        chapter: '第一章',
        cardType: 'knowledge',
      );
      expect(summary.total, 2);
      expect(summary.learning, 1);
      expect(summary.mastered, 1);
    });

    test('resetMemorize 按知识点/整章重置', () async {
      await repo.recordMemorize(
        cardKey: QuizRepository.kpKey('kp1'),
        bankId: 'b1',
        chapter: '第一章',
        cardType: 'knowledge',
        knowledgeId: 'kp1',
        know: true,
      );
      await repo.recordMemorize(
        cardKey: QuizRepository.kpKey('kp2'),
        bankId: 'b1',
        chapter: '第一章',
        cardType: 'knowledge',
        knowledgeId: 'kp2',
        know: true,
      );
      // 重置单知识点
      await repo.resetMemorize(
        bankId: 'b1',
        cardType: 'knowledge',
        knowledgeId: 'kp1',
      );
      var states = await repo.memorizeStates(
        bankId: 'b1',
        chapter: '第一章',
        cardType: 'knowledge',
      );
      expect(states.containsKey(QuizRepository.kpKey('kp1')), isFalse);
      expect(states.containsKey(QuizRepository.kpKey('kp2')), isTrue);

      // 重置整章
      await repo.resetMemorize(
        bankId: 'b1',
        cardType: 'knowledge',
        chapter: '第一章',
      );
      states = await repo.memorizeStates(
        bankId: 'b1',
        chapter: '第一章',
        cardType: 'knowledge',
      );
      expect(states, isEmpty);
    });

    test('memorizeStatesByKnowledge 只返回该知识点题目卡', () async {
      await repo.recordMemorize(
        cardKey: QuizRepository.qKey('q1'),
        bankId: 'b1',
        chapter: '第一章',
        cardType: 'question',
        questionId: 'q1',
        knowledgeId: 'kpA',
        know: true,
      );
      await repo.recordMemorize(
        cardKey: QuizRepository.qKey('q2'),
        bankId: 'b1',
        chapter: '第一章',
        cardType: 'question',
        questionId: 'q2',
        knowledgeId: 'kpB',
        know: true,
      );
      final states = await repo.memorizeStatesByKnowledge(
        bankId: 'b1',
        knowledgeId: 'kpA',
      );
      expect(states.length, 1);
      expect(states.containsKey(QuizRepository.qKey('q1')), isTrue);
    });
  });
}
