/// 判分逻辑（纯函数，设计方案 §3.5）
///
/// 基础机制：作答与标准答案都归一化为 `Set<String>` 做集合比较——
/// 单选天然单元素，单选/多选共用同一套集合判分；填空/简答按关键词命中。
/// 审查收紧（P1-7）：填空不允许"只答参考答的短子串"即判对（"答 2 判 21 对"）；
/// 简答只允许「用户答覆盖参考要点」，禁止「用户只答参考答的任意子串」即判对。
/// v0.9.0 新增：题带 `answerVariants`（等价答案分组）时，填空按"空"、
/// 简答按"要点"分组判分——组内用户命中任一等价表述即该组判对（如"夸大"="夸饰"）。
/// 近义/缩写（如"美酒"="酒"）由数据层 answerVariants 显式声明覆盖，判分层不做
/// 事后子串放宽，避免"白酒"含"酒"被误判。
library;

import '../models/models.dart';

/// 判分结果
enum Grade { correct, wrong, partial, skip }

/// 对作答判分。[userAnswer] 为用户作答（选项 key 集合 / 填空词集合 / 简答文本集合）。
Grade gradeQuestion(Question question, Set<String> userAnswer) {
  if (userAnswer.isEmpty) return Grade.skip;

  final correct = question.answer;
  switch (question.type) {
    case QuestionType.singleChoice:
    case QuestionType.trueFalse:
      return _sameSet(userAnswer, correct) ? Grade.correct : Grade.wrong;

    case QuestionType.multiChoice:
      if (_sameSet(userAnswer, correct)) return Grade.correct;
      return userAnswer.intersection(correct).isEmpty ? Grade.wrong : Grade.partial;

    case QuestionType.blank:
      return _blankGrade(userAnswer, correct, question.answerVariants);

    case QuestionType.shortAnswer:
      return _shortGrade(userAnswer, correct, question.answerVariants);
  }
}

/// 填空：按「空」逐组判定——有等价答案分组时按组（组内任一等价表述命中即该空对），
/// 无分组按参考答案逐项；全部命中 correct，部分命中 partial，全不中 wrong。
Grade _blankGrade(
    Set<String> user, Set<String> correct, List<List<String>> variants) {
  if (user.isEmpty) return Grade.skip;
  final normalizedUser = user.map(_normalize).toSet();
  if (variants.isNotEmpty) {
    final groups = variants
        .map((group) => group.map(_normalize).where((v) => v.isNotEmpty).toSet())
        .where((s) => s.isNotEmpty)
        .toList();
    if (groups.isEmpty) return Grade.wrong;
    final hit = groups.where((g) => g.any(normalizedUser.contains)).length;
    if (hit == groups.length) return Grade.correct;
    return hit > 0 ? Grade.partial : Grade.wrong;
  }
  final items =
      correct.map(_normalize).where((v) => v.isNotEmpty).toList();
  if (items.isEmpty) return Grade.wrong;
  final hit = items.where(normalizedUser.contains).length;
  if (hit == items.length) return Grade.correct;
  return hit > 0 ? Grade.partial : Grade.wrong;
}

/// 简答：按「要点」逐组判定（有等价答案分组时）；部分要点命中 partial。
/// 用户作答覆盖参考要点才判该要点对，禁止"只答参考答的任意短子串"即判对。
Grade _shortGrade(
    Set<String> user, Set<String> correct, List<List<String>> variants) {
  if (user.isEmpty) return Grade.skip;
  final normalizedUser = user.map(_normalize).toSet();
  if (variants.isNotEmpty) {
    final groups = variants.where((g) => g.isNotEmpty).toList();
    if (groups.isEmpty) return Grade.wrong;
    final hit = groups
        .where((group) => group.any((v) {
              final normalized = _normalize(v);
              return normalized.isNotEmpty &&
                  normalizedUser.any((u) => _hitPoint(u, normalized));
            }))
        .length;
    if (hit == groups.length) return Grade.correct;
    return hit > 0 ? Grade.partial : Grade.wrong;
  }
  // 无分组：按要点句切分（复用作答文本与参考要点命中计数）
  final items = <String>[];
  for (final item in correct) {
    final normalized = _normalize(item);
    if (normalized.isEmpty) continue;
    final points = normalized
        .split(RegExp(r'[，。；、！？,.;!?：]'))
        .map((p) => p.trim())
        .where((p) => p.isNotEmpty)
        .toList();
    items.addAll(points);
  }
  if (items.isEmpty) return Grade.wrong;
  final minLen = items.length > 1 ? 4 : (items.first.length * 0.5).ceil();
  final hit = items
      .where((p) => normalizedUser.any((u) => u.contains(p) ||
          (p.contains(u) && u.length >= minLen)))
      .length;
  if (hit >= items.length) return Grade.correct;
  return hit > 0 ? Grade.partial : Grade.wrong;
}

/// 要点命中：用户作答 u 覆盖要点 p（或反向子串命中需够长，复用原阈值逻辑）
bool _hitPoint(String user, String point) {
  if (user.contains(point)) return true;
  return point.contains(user) && user.length >= 4;
}

bool _sameSet(Set<String> a, Set<String> b) =>
    a.length == b.length && a.containsAll(b);

/// 去所有空白字符并转小写（英文答案不区分大小写，中文不受影响）
String _normalize(String value) => value.replaceAll(RegExp(r'\s+'), '').toLowerCase();
