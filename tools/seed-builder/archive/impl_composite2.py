# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'D:\study_app\app\lib\ui\mock_exam_page.dart'
s = open(p, encoding='utf-8').read()

# (1) 构造加可选参数
old = """class MockExamPage extends ConsumerStatefulWidget {
  const MockExamPage({super.key, required this.paper});

  final MockPaper paper;

  @override
  ConsumerState<MockExamPage> createState() => _MockExamPageState();
}"""
new = """class MockExamPage extends ConsumerStatefulWidget {
  const MockExamPage({
    super.key,
    required this.paper,
    this.presetQuestions,
    this.pointsByType,
  });

  final MockPaper paper;

  /// 综合卷：排题页已抽好的题目（非空时优先于 paper.questionIds）
  final List<Question>? presetQuestions;

  /// 综合卷：题型分值（150 分制加权计分；为空时保持百分制）
  final Map<QuestionType, int>? pointsByType;

  @override
  ConsumerState<MockExamPage> createState() => _MockExamPageState();
}"""
assert old in s, 'ctor anchor'
s = s.replace(old, new, 1)

# (2) _load 优先用 presetQuestions
old = """      final repo = await ref.read(quizRepositoryProvider);
      final questions = await repo.questionsByIds(widget.paper.questionIds);
      if (!mounted) return;"""
new = """      final repo = await ref.read(quizRepositoryProvider);
      final questions = widget.presetQuestions != null
          ? widget.presetQuestions!
          : await repo.questionsByIds(widget.paper.questionIds);
      if (!mounted) return;"""
assert old in s, 'load anchor'
s = s.replace(old, new, 1)

# (3) _submitAll 传 pointsByType
old = """      final session = await repo.submitMockSession(
        paperId: widget.paper.id,
        startedAt: _startedAt?.millisecondsSinceEpoch ?? now,
        durationMin: widget.paper.durationMin,
        questions: _questions,
        answers: _answers,
        submittedAt: now,
      );"""
new = """      final session = await repo.submitMockSession(
        paperId: widget.paper.id,
        startedAt: _startedAt?.millisecondsSinceEpoch ?? now,
        durationMin: widget.paper.durationMin,
        questions: _questions,
        answers: _answers,
        submittedAt: now,
        pointsByType: widget.pointsByType,
      );"""
assert old in s, 'submit anchor'
s = s.replace(old, new, 1)

# (4) 结果弹窗显示满分
old = """  void _showResult(
    int correct,
    int partial,
    int wrong,
    int skipped,
    int score,
  ) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => AlertDialog(
        title: const Text('考试完成'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '得分：$score 分',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: Theme.of(context).colorScheme.primary,
              ),
            ),"""
new = """  void _showResult(
    int correct,
    int partial,
    int wrong,
    int skipped,
    int score,
  ) {
    // 满分：加权模式按题型分值求和（综合卷=150）；否则百分制（100）
    final full =
        widget.pointsByType == null || widget.pointsByType!.isEmpty
        ? 100
        : _questions.fold<int>(
            0,
            (acc, q) =>
                acc + (widget.pointsByType![q.type] ?? 1),
          );
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => AlertDialog(
        title: const Text('考试完成'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '得分：$score / $full',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: Theme.of(context).colorScheme.primary,
              ),
            ),"""
assert old in s, 'result anchor'
s = s.replace(old, new, 1)

open(p, 'w', encoding='utf-8').write(s)
print('[2] mock_exam_page ok')
