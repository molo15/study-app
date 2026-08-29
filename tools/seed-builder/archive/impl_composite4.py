# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============ 1. quiz_repository_mock.dart：score 作用域 + 常量引用改类名 ============
p = r'D:\study_app\app\lib\data\quiz_repository_mock.dart'
s = open(p, encoding='utf-8').read()

# (1a) score 声明移到事务闭包外
old = """  }) async {
    var correct = 0, partial = 0, wrong = 0, skipped = 0;
    late int sessionId;
    await _db.transaction((txn) async {"""
new = """  }) async {
    var correct = 0, partial = 0, wrong = 0, skipped = 0;
    late int sessionId;
    late int score; // 闭包外声明，供返回 MockSession 复用
    await _db.transaction((txn) async {"""
assert old in s, 'score decl anchor'
s = s.replace(old, new, 1)

old = """      late final int score;
      if (pointsByType == null || pointsByType.isEmpty) {"""
new = """      if (pointsByType == null || pointsByType.isEmpty) {"""
assert old in s, 'score inner decl anchor'
s = s.replace(old, new, 1)

# (1b) generateCompositePaper 里常量引用改为 QuizRepository 类名（常量将移入 QuizRepository）
old = """  /// 综合卷学科抽题模板：{bankId: {type: 题量}}
  /// 无写作、无论述（论述并入简答）。分值：单选1×30、多选2×10、填空1×20、简答10×8=150。
  static const Map<String, Map<String, int>> compositeTemplate = {
    'bank-xiandai-hanyu': {
      'single_choice': 11,
      'multi_choice': 4,
      'blank': 8,
      'short_answer': 3,
    },
    'bank-gudai-hanyu': {
      'single_choice': 11,
      'multi_choice': 3,
      'blank': 8,
      'short_answer': 3,
    },
    'bank-zhongguo-xiandai-wenxue': {
      'single_choice': 3,
      'multi_choice': 1,
      'blank': 2,
      'short_answer': 1,
    },
    'bank-zhongguo-dangdai-wenxue': {
      'single_choice': 3,
      'multi_choice': 1,
      'blank': 1,
      'short_answer': 1,
    },
    'bank-zhongguo-gudai-wenxue': {
      'single_choice': 2,
      'multi_choice': 1,
      'blank': 1,
      'short_answer': 0,
    },
  };

  /// 综合卷题型分值（150 分制）
  static const Map<QuestionType, int> compositePoints = {
    QuestionType.singleChoice: 1,
    QuestionType.multiChoice: 2,
    QuestionType.blank: 1,
    QuestionType.shortAnswer: 10,
  };

  /// 综合卷：按模板从 5 科随机抽题（卷内不重复）。
  /// 某科某题型题量不足时按实际可得题量抽（不报错），保证可作答。
  Future<List<Question>> generateCompositePaper() async {
    final questions = <Question>[];
    final seen = <String>{};
    for (final entry in compositeTemplate.entries) {"""
new = """  /// 综合卷：按模板从 5 科随机抽题（卷内不重复）。
  /// 某科某题型题量不足时按实际可得题量抽（不报错），保证可作答。
  /// 模板与分值常量定义在 [QuizRepository.compositeTemplate] / [QuizRepository.compositePoints]。
  Future<List<Question>> generateCompositePaper() async {
    final questions = <Question>[];
    final seen = <String>{};
    for (final entry in QuizRepository.compositeTemplate.entries) {"""
assert old in s, 'template anchor'
s = s.replace(old, new, 1)

open(p, 'w', encoding='utf-8').write(s)
print('[1] mock mixin ok')

# ============ 2. quiz_repository.dart：常量移入 QuizRepository 类 ============
p = r'D:\study_app\app\lib\data\quiz_repository.dart'
s = open(p, encoding='utf-8').read()

old = """  static const practiceTimerVisibleKey = 'show_practice_timer';
  static const reviewModeEnabledKey = 'review_mode_enabled';
  static String practiceProgressKey(String key) => 'practice_progress:$key';
  static String practiceResultsKey(String key) => 'practice_results:$key';
  static const wrongBookRetireThreshold = 2;"""
new = """  static const practiceTimerVisibleKey = 'show_practice_timer';
  static const reviewModeEnabledKey = 'review_mode_enabled';
  static String practiceProgressKey(String key) => 'practice_progress:$key';
  static String practiceResultsKey(String key) => 'practice_results:$key';
  static const wrongBookRetireThreshold = 2;

  // ---------- 综合模拟卷（随机组卷，150 分制） ----------

  /// 综合卷学科抽题模板：{bankId: {type: 题量}}
  /// 无写作、无论述（论述并入简答）。分值：单选1×30、多选2×10、填空1×20、简答10×8=150。
  static const Map<String, Map<String, int>> compositeTemplate = {
    'bank-xiandai-hanyu': {
      'single_choice': 11,
      'multi_choice': 4,
      'blank': 8,
      'short_answer': 3,
    },
    'bank-gudai-hanyu': {
      'single_choice': 11,
      'multi_choice': 3,
      'blank': 8,
      'short_answer': 3,
    },
    'bank-zhongguo-xiandai-wenxue': {
      'single_choice': 3,
      'multi_choice': 1,
      'blank': 2,
      'short_answer': 1,
    },
    'bank-zhongguo-dangdai-wenxue': {
      'single_choice': 3,
      'multi_choice': 1,
      'blank': 1,
      'short_answer': 1,
    },
    'bank-zhongguo-gudai-wenxue': {
      'single_choice': 2,
      'multi_choice': 1,
      'blank': 1,
      'short_answer': 0,
    },
  };

  /// 综合卷题型分值（150 分制）
  static const Map<QuestionType, int> compositePoints = {
    QuestionType.singleChoice: 1,
    QuestionType.multiChoice: 2,
    QuestionType.blank: 1,
    QuestionType.shortAnswer: 10,
  };"""
assert old in s, 'quiz_repository anchor'
s = s.replace(old, new, 1)

open(p, 'w', encoding='utf-8').write(s)
print('[2] quiz_repository ok')
