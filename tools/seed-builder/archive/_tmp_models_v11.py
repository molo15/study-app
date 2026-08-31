# -*- coding: utf-8 -*-
"""背题存档：models.dart 增加 MemorizeProgress 模型"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\study_app\app\lib\models\models.dart'
s = open(p, encoding='utf-8').read()

# 在文件末尾追加模型
append = '''

/// 背题卡记忆状态（v11 背题存档）
enum MemorizeCardState {
  /// 学习中（背过但未掌握，或尚未连续背会）
  learning,

  /// 已掌握（连续 2 次自评"背会"）
  mastered,
}

/// 背题存档记录（v11）：一张记忆卡（知识点卡或题目卡）的跨会话记忆状态
class MemorizeProgress {
  const MemorizeProgress({
    required this.cardKey,
    required this.bankId,
    required this.chapter,
    required this.cardType,
    this.knowledgeId,
    this.questionId,
    this.state = MemorizeCardState.learning,
    this.correctStreak = 0,
    this.reviewedCount = 0,
    this.lastReviewedAt,
  });

  /// 卡唯一键：知识点卡 `kp:{knowledgeId}`，题目卡 `q:{questionId}`
  final String cardKey;
  final String bankId;
  final String chapter;

  /// 'knowledge' | 'question'
  final String cardType;

  /// 知识点卡关联的知识点 id（cardType=knowledge 时非空）
  final String? knowledgeId;

  /// 题目卡关联的题目 id（cardType=question 时非空）
  final String? questionId;

  final MemorizeCardState state;

  /// 连续"背会"次数（>=2 进入 mastered）
  final int correctStreak;

  /// 累计自评次数
  final int reviewedCount;

  /// 最近一次自评时间
  final DateTime? lastReviewedAt;

  bool get mastered => state == MemorizeCardState.mastered;

  MemorizeProgress copyWith({
    MemorizeCardState? state,
    int? correctStreak,
    int? reviewedCount,
    DateTime? lastReviewedAt,
  }) =>
      MemorizeProgress(
        cardKey: cardKey,
        bankId: bankId,
        chapter: chapter,
        cardType: cardType,
        knowledgeId: knowledgeId,
        questionId: questionId,
        state: state ?? this.state,
        correctStreak: correctStreak ?? this.correctStreak,
        reviewedCount: reviewedCount ?? this.reviewedCount,
        lastReviewedAt: lastReviewedAt ?? this.lastReviewedAt,
      );
}
'''

s = s.rstrip() + '\n' + append
open(p, 'w', encoding='utf-8', newline='').write(s)
print('models.dart 增加 MemorizeProgress 完成')
print('  enum MemorizeCardState:', 'enum MemorizeCardState' in s)
print('  class MemorizeProgress:', 'class MemorizeProgress' in s)
