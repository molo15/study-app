import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:quiz_app/data/app_database.dart';
import 'package:quiz_app/data/quiz_repository.dart';
import 'package:quiz_app/models/models.dart';

/// 综合模拟卷（随机组卷 + 150 分制计分）集成测试。
/// 内存 DB 按 createSchema(db, 10) 建最新 schema，插入 5 科种子题，
/// 覆盖：组卷题量/题型/去重/总分、交卷全对=150、全错=0、简答部分=半分。
void main() {
  sqfliteFfiInit();
  databaseFactory = databaseFactoryFfi;

  final banks = const [
    'bank-xiandai-hanyu',
    'bank-gudai-hanyu',
    'bank-zhongguo-xiandai-wenxue',
    'bank-zhongguo-dangdai-wenxue',
    'bank-zhongguo-gudai-wenxue',
  ];

  late Database db;
  late QuizRepository repo;

  Question makeQuestion(String id, String bank, QuestionType type) =>
      Question(
        id: id,
        bankId: bank,
        type: type,
        stem: '题干 $id',
        options: (type == QuestionType.singleChoice ||
                type == QuestionType.multiChoice)
            ? const [
                QuestionOption(key: 'A', text: '甲'),
                QuestionOption(key: 'B', text: '乙'),
                QuestionOption(key: 'C', text: '丙'),
                QuestionOption(key: 'D', text: '丁'),
              ]
            : const [],
        answer: switch (type) {
          QuestionType.singleChoice => {'A'},
          QuestionType.multiChoice => {'A', 'B'},
          QuestionType.blank => {'标准答案'},
          QuestionType.shortAnswer => {'要点一；要点二'},
          QuestionType.trueFalse => {'正确'},
        },
        explanation: '',
        chapter: '测试章',
      );

  setUp(() async {
    db = await databaseFactory.openDatabase(inMemoryDatabasePath);
    await AppDatabase.configure(db);
    await AppDatabase.createSchema(db, 10);
    for (final b in banks) {
      for (var i = 0; i < 12; i++) {
        await db.insert(
          'questions',
          makeQuestion('$b:sc$i', b, QuestionType.singleChoice).toMap(),
        );
      }
      for (var i = 0; i < 6; i++) {
        await db.insert(
          'questions',
          makeQuestion('$b:mc$i', b, QuestionType.multiChoice).toMap(),
        );
      }
      for (var i = 0; i < 9; i++) {
        await db.insert(
          'questions',
          makeQuestion('$b:bk$i', b, QuestionType.blank).toMap(),
        );
      }
      for (var i = 0; i < 4; i++) {
        await db.insert(
          'questions',
          makeQuestion('$b:sa$i', b, QuestionType.shortAnswer).toMap(),
        );
      }
    }
    repo = QuizRepository(db);
  });

  tearDown(() => db.close());

  Map<QuestionType, int> countByType(List<Question> qs) {
    final m = <QuestionType, int>{};
    for (final q in qs) {
      m[q.type] = (m[q.type] ?? 0) + 1;
    }
    return m;
  }

  group('generateCompositePaper 随机组卷', () {
    test('题量 68 且各题型达标', () async {
      final qs = await repo.generateCompositePaper();
      expect(qs.length, 68);
      final byType = countByType(qs);
      expect(byType[QuestionType.singleChoice], 30);
      expect(byType[QuestionType.multiChoice], 10);
      expect(byType[QuestionType.blank], 20);
      expect(byType[QuestionType.shortAnswer], 8);
    });

    test('卷内无重复题', () async {
      final qs = await repo.generateCompositePaper();
      expect(qs.map((q) => q.id).toSet().length, qs.length);
    });

    test('分值合计 = 150', () async {
      final qs = await repo.generateCompositePaper();
      final total = qs.fold<int>(
        0,
        (acc, q) => acc + (QuizRepository.compositePoints[q.type] ?? 1),
      );
      expect(total, 150);
    });

    test('现汉+古汉为主要来源（单选占比 ≥ 2/3）', () async {
      final qs = await repo.generateCompositePaper();
      final langBanks = {'bank-xiandai-hanyu', 'bank-gudai-hanyu'};
      final langSingle = qs
          .where((q) =>
              q.type == QuestionType.singleChoice && langBanks.contains(q.bankId))
          .length;
      expect(langSingle, greaterThanOrEqualTo(20)); // 模板 11+11=22
    });
  });

  group('submitMockSession 150 分制加权计分', () {
    test('全对 → 150 分', () async {
      final qs = await repo.generateCompositePaper();
      final answers = {for (final q in qs) q.id: q.answer};
      final session = await repo.submitMockSession(
        paperId: 'composite',
        startedAt: 0,
        durationMin: 180,
        questions: qs,
        answers: answers,
        submittedAt: 1,
        pointsByType: QuizRepository.compositePoints,
      );
      expect(session.score, 150);
      expect(session.correct, 68);
    });

    test('全错 → 0 分', () async {
      final qs = await repo.generateCompositePaper();
      final answers = <String, Set<String>>{};
      for (final q in qs) {
        answers[q.id] = switch (q.type) {
          QuestionType.singleChoice => {'B'}, // 正确答案 A
          QuestionType.multiChoice => {'C', 'D'}, // 正确答案 A,B
          QuestionType.blank => {'错误答案'},
          QuestionType.shortAnswer => {'完全不相关的内容'},
          QuestionType.trueFalse => {'错误'},
        };
      }
      final session = await repo.submitMockSession(
        paperId: 'composite',
        startedAt: 0,
        durationMin: 180,
        questions: qs,
        answers: answers,
        submittedAt: 1,
        pointsByType: QuizRepository.compositePoints,
      );
      expect(session.score, 0);
    });

    test('简答部分正确 → 半分支（其余全对 = 145）', () async {
      final qs = await repo.generateCompositePaper();
      // 全部答对
      final answers = {for (final q in qs) q.id: q.answer};
      // 挑一道简答题改为"只答对一个要点" → partial（10 分 → 5 分）
      final short = qs.firstWhere((q) => q.type == QuestionType.shortAnswer);
      answers[short.id] = {'要点一'};
      final session = await repo.submitMockSession(
        paperId: 'composite',
        startedAt: 0,
        durationMin: 180,
        questions: qs,
        answers: answers,
        submittedAt: 1,
        pointsByType: QuizRepository.compositePoints,
      );
      expect(session.score, 145);
    });

    test('未传 pointsByType → 保持百分制兼容', () async {
      final qs = await repo.generateCompositePaper();
      final answers = {for (final q in qs) q.id: q.answer};
      final session = await repo.submitMockSession(
        paperId: 'composite',
        startedAt: 0,
        durationMin: 180,
        questions: qs,
        answers: answers,
        submittedAt: 1,
      );
      expect(session.score, 100); // 全对 → 100
    });
  });
}
