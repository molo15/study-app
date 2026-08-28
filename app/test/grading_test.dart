import 'package:flutter_test/flutter_test.dart';
import 'package:quiz_app/data/grading.dart';
import 'package:quiz_app/models/models.dart';

Question _choice({required QuestionType type, required Set<String> answer}) =>
    Question(
      id: 't:1',
      bankId: 'b',
      type: type,
      stem: '题干',
      options: const [
        QuestionOption(key: 'A', text: '甲'),
        QuestionOption(key: 'B', text: '乙'),
        QuestionOption(key: 'C', text: '丙'),
        QuestionOption(key: 'D', text: '丁'),
      ],
      answer: answer,
    );

Question _free(QuestionType type, Set<String> answer,
        {List<List<String>> variants = const []}) =>
    Question(
      id: 't:2',
      bankId: 'b',
      type: type,
      stem: '题干',
      answer: answer,
      answerVariants: variants,
    );

void main() {
  group('单选/判断', () {
    test('答对 → correct', () {
      expect(
        gradeQuestion(_choice(type: QuestionType.singleChoice, answer: {'B'}), {
          'B',
        }),
        Grade.correct,
      );
    });
    test('答错 → wrong', () {
      expect(
        gradeQuestion(_choice(type: QuestionType.singleChoice, answer: {'B'}), {
          'A',
        }),
        Grade.wrong,
      );
    });
    test('未答 → skip', () {
      expect(
        gradeQuestion(_choice(type: QuestionType.singleChoice, answer: {'B'}), {}),
        Grade.skip,
      );
    });
    test('判断 正确/错误', () {
      expect(
        gradeQuestion(_choice(type: QuestionType.trueFalse, answer: {'正确'}), {
          '正确',
        }),
        Grade.correct,
      );
    });
  });

  group('多选', () {
    test('全对 → correct', () {
      expect(
        gradeQuestion(_choice(type: QuestionType.multiChoice, answer: {'A', 'C'}), {
          'A',
          'C',
        }),
        Grade.correct,
      );
    });
    test('部分命中 → partial', () {
      expect(
        gradeQuestion(_choice(type: QuestionType.multiChoice, answer: {'A', 'C'}), {
          'A',
        }),
        Grade.partial,
      );
    });
    test('多选漏选/多选 → partial', () {
      expect(
        gradeQuestion(
          _choice(type: QuestionType.multiChoice, answer: {'A', 'C'}),
          {'A', 'C', 'D'},
        ),
        Grade.partial,
      );
    });
    test('无交集 → wrong', () {
      expect(
        gradeQuestion(
          _choice(type: QuestionType.multiChoice, answer: {'A', 'C'}),
          {'B', 'D'},
        ),
        Grade.wrong,
      );
    });
  });

  group('填空', () {
    test('全对 → correct', () {
      expect(
        gradeQuestion(_free(QuestionType.blank, {'长江'}), {'长江'}),
        Grade.correct,
      );
    });
    test('多空部分命中 → partial', () {
      expect(
        gradeQuestion(_free(QuestionType.blank, {'长江', '黄河'}), {'长江'}),
        Grade.partial,
      );
    });
    test('全错 → wrong', () {
      expect(
        gradeQuestion(_free(QuestionType.blank, {'长江'}), {'珠江'}),
        Grade.wrong,
      );
    });
    test('等价答案分组内命中 → correct', () {
      expect(
        gradeQuestion(
          _free(QuestionType.blank, {'夸大'}, variants: [
            ['夸大', '夸饰'],
          ]),
          {'夸饰'},
        ),
        Grade.correct,
      );
    });
  });

  group('简答', () {
    test('要点全中 → correct', () {
      expect(
        gradeQuestion(_free(QuestionType.shortAnswer, {'要点一；要点二'}), {
          '要点一 要点二',
        }),
        Grade.correct,
      );
    });
    test('部分要点命中 → partial', () {
      expect(
        gradeQuestion(_free(QuestionType.shortAnswer, {'要点一；要点二'}), {
          '要点一',
        }),
        Grade.partial,
      );
    });
    test('完全无关 → wrong', () {
      expect(
        gradeQuestion(_free(QuestionType.shortAnswer, {'要点一；要点二'}), {
          '完全无关的内容',
        }),
        Grade.wrong,
      );
    });
    test('等价要点分组命中 → correct', () {
      expect(
        gradeQuestion(
          _free(QuestionType.shortAnswer, {'夸张；比喻'}, variants: [
            ['夸张', '夸饰'],
            ['比喻', '打比方'],
          ]),
          {'用了夸饰手法'},
        ),
        Grade.partial, // 只命中一组
      );
      expect(
        gradeQuestion(
          _free(QuestionType.shortAnswer, {'夸张；比喻'}, variants: [
            ['夸张', '夸饰'],
            ['比喻', '打比方'],
          ]),
          {'用了夸饰，也用了打比方'},
        ),
        Grade.correct,
      );
    });
    test('未答 → skip', () {
      expect(
        gradeQuestion(_free(QuestionType.shortAnswer, {'要点一'}), {}),
        Grade.skip,
      );
    });
  });
}
