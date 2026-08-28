/// 模拟卷页面（需求：允许用户刷模拟卷）
///
/// 流程：入场确认 → 限时答题（暂存不判分）→ 答题卡跳题 → 交卷统一判分
/// → 成绩单存档（mock_sessions）+ 逐题日志（answer_logs mode=mock, session_id）。
/// 模考不进 FSRS 调度；答错自动归集错题本（全局 wrong 语义）。
library;

import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import '../models/models.dart';
import '../services/app_log.dart';
import 'app_routes.dart';
import 'glass_app_bar.dart';
import 'mock_review_page.dart';
import 'practice_page.dart' show typeColor, typeLabel;

class MockExamPage extends ConsumerStatefulWidget {
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
}

class _MockExamPageState extends ConsumerState<MockExamPage> {
  bool _loading = true;
  String? _error;
  List<Question> _questions = const [];
  final Map<String, Set<String>> _answers = {};
  int _index = 0;
  Timer? _timer;
  DateTime? _startedAt;
  Duration _remaining = Duration.zero;
  bool _submitting = false; // 防重入（审查 P0-2：同步置位）
  bool _finished = false; // 已交卷（结果弹窗被系统返回键关闭后仍阻止二次交卷）

  @override
  void initState() {
    super.initState();
    _load(); // 计时器在加载成功后启动（审查 P0-1：避免抢跑交空卷）
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      AppLog.quiz(
        '进入模拟卷: ${widget.paper.name} (${widget.paper.questionIds.length}题)',
      );
      final repo = await ref.read(quizRepositoryProvider);
      final questions = widget.presetQuestions != null
          ? widget.presetQuestions!
          : await repo.questionsByIds(widget.paper.questionIds);
      if (!mounted) return;
      setState(() {
        _questions = questions;
        _startedAt = DateTime.now();
        _remaining = Duration(minutes: widget.paper.durationMin);
        _loading = false;
        if (questions.isEmpty) {
          _error = '该卷没有可作答的题目';
        } else {
          AppLog.quiz(
            '模拟卷加载成功: ${questions.length} 题, 倒计时 ${widget.paper.durationMin} 分钟',
          );
        }
      });
      if (questions.isNotEmpty) _startTimer(); // 加载成功后才开始倒计时
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = '加载失败：$e';
      });
    }
  }

  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (_remaining <= Duration.zero) {
        _timer?.cancel();
        _submitAll(); // 到时自动交卷
        return;
      }
      setState(() => _remaining -= const Duration(seconds: 1));
    });
  }

  void _onSelect(String value) {
    final q = _questions[_index];
    setState(() {
      AppLog.quiz(
        '模拟卷作答: 题${_index + 1}/${_questions.length} (${q.type.name}) value=${value.isNotEmpty ? value.substring(0, value.length > 8 ? 8 : value.length) : '(清空)'}',
      );
      if (q.type == QuestionType.singleChoice ||
          q.type == QuestionType.trueFalse) {
        _answers[q.id] = {value};
      } else if (q.type == QuestionType.multiChoice) {
        // 审查修复：多选必须写回 map（putIfAbsent 持久化），
        // 否则每次点击新建临时 Set、添加即丢失（用户反馈「第 3 题选不了」）
        final current = _answers.putIfAbsent(q.id, () => <String>{});
        if (current.contains(value)) {
          current.remove(value);
          if (current.isEmpty) _answers.remove(q.id); // 全取消恢复「未答」
        } else {
          current.add(value);
        }
      } else {
        // blank / shortAnswer：每次替换为当前完整文本（避免击键累积）
        if (value.isEmpty) {
          _answers.remove(q.id);
        } else {
          _answers[q.id] = {value};
        }
      }
    });
  }

  /// 交卷：判分汇总 → 写日志（mode=mock, session_id）→ 成绩单存档
  /// （审查 P0-2：_submitting 同步置位防并发双交卷；P1-4：单事务原子写入）
  Future<void> _submitAll() async {
    if (_submitting || _finished) return;
    if (_loading || _questions.isEmpty) return; // 防御：加载未完成不交卷（P0-1）
    _submitting = true;
    try {
      final repo = await ref.read(quizRepositoryProvider);
      final now = DateTime.now().millisecondsSinceEpoch;

      final session = await repo.submitMockSession(
        paperId: widget.paper.id,
        startedAt: _startedAt?.millisecondsSinceEpoch ?? now,
        durationMin: widget.paper.durationMin,
        questions: _questions,
        answers: _answers,
        submittedAt: now,
        pointsByType: widget.pointsByType,
      );
      // 会话已落库即置位：即使成绩弹窗被系统返回键关闭，也不允许再次交卷
      // 重复写 mock_sessions/answer_logs（审查修复）
      _finished = true;

      _timer?.cancel(); // 审查 P2-10：交卷后停止倒计时
      if (!mounted) return;
      _showResult(
        session.correct,
        session.partial,
        session.wrong,
        session.skipped,
        session.score,
      );
    } finally {
      _submitting = false;
    }
  }

  void _showResult(
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
            ),
            const SizedBox(height: 8),
            Text('正确 $correct · 部分正确 $partial · 错误 $wrong · 未答 $skipped'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop(); // 关结果弹窗
              Navigator.of(context).push(
                AppPageRoute(
                  builder: (_) => MockReviewPage(
                    questions: _questions,
                    answers: _answers,
                  ),
                ),
              );
            },
            child: const Text('查看逐题解析'),
          ),
          FilledButton(
            onPressed: () {
              Navigator.of(context).pop();
              Navigator.of(context).pop(); // 返回列表页
            },
            child: const Text('完成'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return Scaffold(
        appBar: GlassAppBar(title: Text(widget.paper.name)),
        body: const Center(child: CircularProgressIndicator()),
      );
    }
    if (_error != null) {
      return Scaffold(
        appBar: GlassAppBar(title: Text(widget.paper.name)),
        body: Center(child: Text(_error!)),
      );
    }
    final q = _questions[_index];
    final mm = _remaining.inMinutes.remainder(60).toString().padLeft(2, '0');
    final ss = (_remaining.inSeconds % 60).toString().padLeft(2, '0');
    final isChoice =
        q.type == QuestionType.singleChoice ||
        q.type == QuestionType.multiChoice ||
        q.type == QuestionType.trueFalse;
    final answers = _answers[q.id] ?? const <String>{};
    final answeredCount = _answers.length;

    return Scaffold(
      appBar: GlassAppBar(
        title: Text('${_index + 1}/${_questions.length}'),
        actions: [
          Center(
            child: Padding(
              padding: const EdgeInsets.only(right: 16),
              child: Text(
                '$mm:$ss',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: _remaining.inMinutes < 5
                      ? Theme.of(context).colorScheme.error
                      : null,
                ),
              ),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.grid_view_outlined),
            tooltip: '答题卡',
            onPressed: _showAnswerCard,
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: typeColor(context, q.type).withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  typeLabel(q.type),
                  style: TextStyle(
                    color: typeColor(context, q.type),
                    fontWeight: FontWeight.w700,
                    fontSize: 12,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  // 综合卷跨科标注：学科名 · 章节（P2-3）
                  widget.pointsByType == null
                      ? q.chapter
                      : [mockBankLabel(q.bankId), q.chapter]
                            .where((s) => s.isNotEmpty)
                            .join(' · '),
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.outline,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            q.stem,
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              height: 1.6,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 16),
          if (isChoice)
            for (final option in q.options)
              _MockOptionTile(
                option: option,
                question: q,
                selected: answers.contains(option.key),
                onTap: () => _onSelect(option.key),
              ),
          // 填空/简答作答入口（审查 P1-3：避免恒判未答）
          if (q.type == QuestionType.blank ||
              q.type == QuestionType.shortAnswer)
            _MockFreeAnswer(
              // 审查修复：按题目重建输入框，防相邻自由作答题串题（对齐 practice P1-5）
              key: ValueKey('answer-${q.id}'),
              questionId: q.id,
              initial: answers.isEmpty ? '' : answers.first,
              isShortAnswer: q.type == QuestionType.shortAnswer,
              onSubmit: (text) => _onSelect(text),
            ),
          const SizedBox(height: 24),
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: _index == 0
                      ? null
                      : () => setState(() => _index--),
                  child: const Text('上一题'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: FilledButton(
                  onPressed: _index >= _questions.length - 1
                      ? null
                      : () => setState(() => _index++),
                  child: const Text('下一题'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            '已答 $answeredCount / ${_questions.length}',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: SizedBox(
            width: double.infinity,
            child: FilledButton.tonalIcon(
              onPressed: _submitAll,
              icon: const Icon(Icons.flag_outlined),
              label: const Text('交卷'),
            ),
          ),
        ),
      ),
    );
  }

  void _showAnswerCard() {
    showModalBottomSheet(
      context: context,
      // 弹窗内容含大量格子，需控制高度上限（审查修复：题多时溢出裁切）
      isScrollControlled: true,
      builder: (ctx) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        maxChildSize: 0.85,
        minChildSize: 0.3,
        expand: false,
        builder: (ctx, scrollController) => Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Text('答题卡（已答 ${_answers.length}/${_questions.length}）'),
              const SizedBox(height: 12),
              Expanded(
                child: GridView.builder(
                  controller: scrollController,
                  padding: const EdgeInsets.only(bottom: 8),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 6,
                    crossAxisSpacing: 8,
                    mainAxisSpacing: 8,
                  ),
                  itemCount: _questions.length,
                  itemBuilder: (_, i) => SizedBox(
                    height: 48,
                    child: InkWell(
                      onTap: () {
                        Navigator.pop(ctx);
                        setState(() => _index = i);
                      },
                      customBorder: const CircleBorder(),
                      child: Center(
                        child: Container(
                          width: 36,
                          height: 36,
                          alignment: Alignment.center,
                          decoration: BoxDecoration(
                            color: _answers.containsKey(_questions[i].id)
                                ? Theme.of(context).colorScheme.primary
                                : Theme.of(context)
                                    .colorScheme
                                    .surfaceContainerHighest,
                            shape: BoxShape.circle,
                          ),
                          child: Text(
                            '${i + 1}',
                            style: TextStyle(
                              color: _answers.containsKey(_questions[i].id)
                                  ? Colors.white
                                  : null,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: FilledButton.icon(
                  onPressed: () {
                    Navigator.pop(ctx);
                    _submitAll();
                  },
                  icon: const Icon(Icons.flag_outlined),
                  label: const Text('交卷'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _MockOptionTile extends StatelessWidget {
  const _MockOptionTile({
    required this.option,
    required this.question,
    required this.selected,
    required this.onTap,
  });

  final QuestionOption option;
  final Question question;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 5),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: selected
              ? theme.colorScheme.primary
              : theme.colorScheme.outlineVariant,
          width: selected ? 1.8 : 1,
        ),
      ),
      child: Material(
        color: selected
            ? theme.colorScheme.primary.withValues(alpha: 0.08)
            : Colors.transparent,
        borderRadius: BorderRadius.circular(13),
        child: ListTile(
          leading: Icon(
            selected ? Icons.check_circle_outlined : Icons.circle_outlined,
            color: selected
                ? theme.colorScheme.primary
                : theme.colorScheme.outline,
          ),
          // 判断题显示「正确/错误」不带 key 前缀（修复：避免"正确. 正确"）
          title: Text(
            question.type == QuestionType.trueFalse
                ? option.text
                : '${option.key}. ${option.text}',
          ),
          onTap: onTap,
        ),
      ),
    );
  }
}

/// 模拟卷填空/简答输入框（审查 P1-3）
class _MockFreeAnswer extends StatefulWidget {
  const _MockFreeAnswer({
    super.key,
    required this.questionId,
    required this.initial,
    required this.isShortAnswer,
    required this.onSubmit,
  });

  final String questionId;
  final String initial;
  final bool isShortAnswer;
  final void Function(String) onSubmit;

  @override
  State<_MockFreeAnswer> createState() => _MockFreeAnswerState();
}

class _MockFreeAnswerState extends State<_MockFreeAnswer> {
  late final TextEditingController _controller = TextEditingController(
    text: widget.initial,
  );

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextField(
          controller: _controller,
          minLines: widget.isShortAnswer ? 3 : 1,
          maxLines: widget.isShortAnswer ? 5 : 1,
          decoration: InputDecoration(
            hintText: widget.isShortAnswer ? '简答作答' : '填写答案',
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
            filled: true,
            fillColor: theme.colorScheme.surfaceContainerHighest,
          ),
          onChanged: (v) => widget.onSubmit(v.trim()),
        ),
      ],
    );
  }
}
