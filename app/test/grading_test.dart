import 'package:flutter_test/flutter_test.dart';
import 'package:quiz_app/data/grading.dart';
import 'package:quiz_app/models/models.dart';

Question _question({
  required String id,
  required QuestionType type,
  List<QuestionOption> options = const [],
  Set<String>? answer,
  List<List<String>> answerVariants = const [],
}) =>
    Question(
      id: id,
      bankId: 'bank-test',
      type: type,
      stem: '题干 $id',
      options: options,
      answer: answer ?? const {},
      answerVariants: answerVariants,
    );

void main() {
  group('判分逻辑（设计方案 §3.5）', () {
    test('单选：选中正确答案判 correct', () {
      final q = _question(
        id: 'q1',
        type: QuestionType.singleChoice,
        options: const [
          QuestionOption(key: 'A', text: '甲'),
          QuestionOption(key: 'B', text: '乙'),
        ],
        answer: {'B'},
      );
      expect(gradeQuestion(q, {'B'}), Grade.correct);
      expect(gradeQuestion(q, {'A'}), Grade.wrong);
    });

    test('单选：未作答判 skip', () {
      final q = _question(
          id: 'q2', type: QuestionType.singleChoice, answer: {'A'});
      expect(gradeQuestion(q, {}), Grade.skip);
    });

    test('多选：全中 correct、部分 partial、零命中 wrong', () {
      final q = _question(
        id: 'q3',
        type: QuestionType.multiChoice,
        options: const [
          QuestionOption(key: 'A', text: '一'),
          QuestionOption(key: 'B', text: '二'),
          QuestionOption(key: 'C', text: '三'),
        ],
        answer: {'A', 'C'},
      );
      expect(gradeQuestion(q, {'A', 'C'}), Grade.correct);
      expect(gradeQuestion(q, {'A', 'B'}), Grade.partial);
      expect(gradeQuestion(q, {'B'}), Grade.wrong);
      // 多答（含正确项）也算部分正确
      expect(gradeQuestion(q, {'A', 'B', 'C'}), Grade.partial);
    });

    test('判断：正确答案「错误」判对', () {
      final q = _question(
        id: 'q4',
        type: QuestionType.trueFalse,
        answer: {'错误'},
      );
      expect(gradeQuestion(q, {'错误'}), Grade.correct);
      expect(gradeQuestion(q, {'正确'}), Grade.wrong);
    });

    test('填空：关键词命中判对，忽略空白', () {
      final q = _question(
        id: 'q5',
        type: QuestionType.blank,
        answer: {'21'},
      );
      expect(gradeQuestion(q, {'21'}), Grade.correct);
      expect(gradeQuestion(q, {' 21 '}), Grade.correct); // 去空白
      expect(gradeQuestion(q, {'22'}), Grade.wrong);
    });

    test('简答：多个标准答案项都需命中', () {
      final q = _question(
        id: 'q6',
        type: QuestionType.shortAnswer,
        answer: {'主谓一致', '就近原则'},
      );
      expect(gradeQuestion(q, {'就近原则', '主谓一致'}), Grade.correct);
      // P2 部分得分：只命中一项 → partial（原 wrong）
      expect(gradeQuestion(q, {'就近原则'}), Grade.partial);
    });

    test('英文答案不区分大小写', () {
      final q = _question(
        id: 'q7',
        type: QuestionType.blank,
        answer: {'opening'},
      );
      expect(gradeQuestion(q, {'OPENING'}), Grade.correct);
    });

    test('填空收紧：答参考答的子串不再判对（审查 P1-7）', () {
      final q = _question(
        id: 'q8',
        type: QuestionType.blank,
        answer: {'21'},
      );
      expect(gradeQuestion(q, {'2'}), Grade.wrong);
      expect(gradeQuestion(q, {'21'}), Grade.correct);
    });

    test('填空近义：由 answerVariants 显式声明覆盖（美酒=酒），不做事后子串放宽', () {
      // 无 variants：标准"酒"，用户填"白酒"含"酒"——不能误判为对
      final qPlain = _question(
        id: 'q8b',
        type: QuestionType.blank,
        answer: {'酒'},
      );
      expect(gradeQuestion(qPlain, {'酒'}), Grade.correct);
      expect(gradeQuestion(qPlain, {'白酒'}), Grade.wrong); // 子串不放行
      // 有 variants：声明 [美酒,酒] 为等价组，用户填"美酒"或"酒"均判对
      final qVar = _question(
        id: 'q8c',
        type: QuestionType.blank,
        answer: {'美酒'},
        answerVariants: const [
          ['美酒', '酒'],
        ],
      );
      expect(gradeQuestion(qVar, {'酒'}), Grade.correct);
      expect(gradeQuestion(qVar, {'美酒'}), Grade.correct);
      expect(gradeQuestion(qVar, {'白酒'}), Grade.wrong); // 非等价
      // P1-7 不破坏：标准"21"、用户"2"仍判错
      expect(gradeQuestion(qVar, {'2'}), Grade.wrong);
    });

    test('简答收紧：长参考答的短子串不判对，覆盖要点判对（审查 P1-7）', () {
      final q = _question(
        id: 'q9',
        type: QuestionType.shortAnswer,
        answer: {'主谓一致就近原则谓语与最近主语保持一致'},
      );
      // 只答一个短子串（长度 < 参考 50%）→ wrong
      expect(gradeQuestion(q, {'就近原则'}), Grade.wrong);
      // 覆盖参考要点（正向包含）→ correct
      expect(gradeQuestion(q, {'主谓一致就近原则谓语与最近主语保持一致'}), Grade.correct);
    });

    test('简答要点覆盖：段落级参考答按标点拆要点，命中即判对（审查 P1-C）', () {
      final q = _question(
        id: 'q11',
        type: QuestionType.shortAnswer,
        answer: {'就近原则指谓语动词的人称和数与最近的主语保持一致。常见于there be句型及并列结构。'},
      );
      // P2 按要点积分：覆盖完整参考答（两句要点）→ correct
      expect(
        gradeQuestion(q, {'就近原则指谓语动词的人称和数与最近的主语保持一致。常见于there be句型及并列结构。'}),
        Grade.correct,
      );
      // 只覆盖第一个要点句 → partial（P2 部分得分）
      expect(gradeQuestion(q, {'就近原则指谓语动词的人称和数与最近的主语保持一致'}), Grade.partial);
      // 4 字核心概念子串命中首个要点句 → partial（未覆盖全部要点）
      expect(gradeQuestion(q, {'就近原则'}), Grade.partial);
      // 极短子串（1 字）→ wrong
      expect(gradeQuestion(q, {'的'}), Grade.wrong);
    });

    test('判断题作答（审查 P0-1）', () {
      final q = _question(
        id: 'q10',
        type: QuestionType.trueFalse,
        answer: {'正确'},
      );
      expect(gradeQuestion(q, {'正确'}), Grade.correct);
      expect(gradeQuestion(q, {'错误'}), Grade.wrong);
    });

    group('等价答案判分（v0.9.0 answerVariants）', () {
      test('填空单空：命中任一等价表述即判对', () {
        final q = _question(
          id: 'v1',
          type: QuestionType.blank,
          answer: {'夸大'},
          answerVariants: const [
            ['夸大', '夸饰'],
          ],
        );
        expect(gradeQuestion(q, {'夸大'}), Grade.correct);
        expect(gradeQuestion(q, {'夸饰'}), Grade.correct); // 等价表述
        expect(gradeQuestion(q, {'夸张'}), Grade.wrong); // 非等价
        expect(gradeQuestion(q, {}), Grade.skip);
      });

      test('填空双空：按空分组，组内任一命中、两空全中才判对', () {
        final q = _question(
          id: 'v2',
          type: QuestionType.blank,
          answer: {'象形', '形声'},
          answerVariants: const [
            ['象形', '象形字'],
            ['形声', '形声字'],
          ],
        );
        expect(gradeQuestion(q, {'象形', '形声'}), Grade.correct);
        expect(gradeQuestion(q, {'象形字', '形声字'}), Grade.correct); // 两空都用等价词
        expect(gradeQuestion(q, {'象形', '形声字'}), Grade.correct); // 混用
        // P2 部分得分：只中一空 → partial（原 wrong）
        expect(gradeQuestion(q, {'象形'}), Grade.partial);
      });

      test('简答：按要点分组，命中任一等价要点表述即该要点对', () {
        final q = _question(
          id: 'v3',
          type: QuestionType.shortAnswer,
          answer: {'谦辞', '敬辞'},
          answerVariants: const [
            ['谦辞', '谦敬词'],
            ['敬辞'],
          ],
        );
        expect(gradeQuestion(q, {'谦辞', '敬辞'}), Grade.correct);
        expect(gradeQuestion(q, {'谦敬词', '敬辞'}), Grade.correct); // 等价词
        expect(gradeQuestion(q, {'谦辞'}), Grade.partial); // P2：只中一点 → 部分得分
      });

      test('无 variants 的题回退原判分逻辑（兼容旧包）', () {
        final q = _question(
          id: 'v4',
          type: QuestionType.blank,
          answer: {'21'},
        );
        expect(gradeQuestion(q, {'21'}), Grade.correct);
        expect(gradeQuestion(q, {'2'}), Grade.wrong); // 子串不判对
        final sa = _question(
          id: 'v5',
          type: QuestionType.shortAnswer,
          answer: {'主谓一致', '就近原则'},
        );
        expect(gradeQuestion(sa, {'就近原则', '主谓一致'}), Grade.correct);
        expect(gradeQuestion(sa, {'就近原则'}), Grade.partial); // P2 部分得分
      });
    });
  });
}
