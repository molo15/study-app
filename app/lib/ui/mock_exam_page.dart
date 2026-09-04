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
import 'theme/ios_tokens.dart';
import 'widgets/ios_button.dart';
import 'widgets/ios_action_sheet.dart';
import 'widgets/circular_ring.dart';
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
  final Set<String> _flagged = {}; // 存疑标记（答题卡待回看）
  int _index = 0;
  Timer? _timer;
  DateTime? _startedAt;
  Duration _remaining = Duration.zero;
  bool _submitting = false; // 防重入（审查 P0-2：同步置位）
  bool _finished = false; // 已交卷（结果弹窗被系统返回键关闭后仍阻止二次交卷）
  bool _doubtEnabled = true; // 存疑标记开关（设置页持久化，默认开启）

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
      final doubt = await repo.doubtEnabled();
      if (!mounted) return;
      setState(() {
        _questions = questions;
        _doubtEnabled = doubt;
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

  /// 存疑标记开关（UI v2 · 模拟考）：标记不确定的题，交卷前回看
  void _toggleFlag(String questionId) {
    setState(() {
      if (!_flagged.remove(questionId)) _flagged.add(questionId);
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
        backgroundColor: IOSColors.of(context).card,
        title: Text('考试完成',
            style: IOSTypography.title3(color: IOSColors.of(context).text)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 分数环（UI v2）：得分 / 满分 + 生长动画
            Center(
              child: CircularRing(
                progress: full == 0 ? 0 : (score / full).clamp(0.0, 1.0),
                size: 128,
                strokeWidth: 12,
                color: IOSColors.of(context).primary,
                center: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      '$score',
                      style: IOSTypography.title1(color: IOSColors.of(context).primary)
                          .copyWith(fontWeight: FontWeight.w800),
                    ),
                    Text(
                      '/ $full',
                      style: IOSTypography.caption1(color: IOSColors.of(context).text3),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),
            Center(
              child: Text(
                '得分：$score / $full',
                style: IOSTypography.body(color: IOSColors.of(context).text)
                    .copyWith(fontWeight: FontWeight.w800),
              ),
            ),
            const SizedBox(height: 8),
            Center(
              child: Text(
                '正确 $correct · 部分正确 $partial · 错误 $wrong · 未答 $skipped',
                textAlign: TextAlign.center,
                style: IOSTypography.caption1(color: IOSColors.of(context).text2),
              ),
            ),
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
                    flagged: _flagged,
                  ),
                ),
              );
            },
            child: Text('查看逐题解析',
                style: IOSTypography.callout(color: IOSColors.of(context).primary)),
          ),
          IOSButton(
            label: '完成',
            onPressed: () {
              Navigator.of(context).pop();
              Navigator.of(context).pop(); // 返回列表页
            },
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    if (_loading) {
      return Scaffold(
        backgroundColor: colors.bg,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          centerTitle: true,
          title: Text(widget.paper.name,
              style: IOSTypography.title2(color: colors.text)),
          leading: const BackButton(color: IOSSystemColors.blue),
        ),
        body: const Center(child: CircularProgressIndicator(strokeWidth: 2.5)),
      );
    }
    if (_error != null) {
      return Scaffold(
        backgroundColor: colors.bg,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          centerTitle: true,
          title: Text(widget.paper.name,
              style: IOSTypography.title2(color: colors.text)),
          leading: const BackButton(color: IOSSystemColors.blue),
        ),
        body: Center(
            child: Text(_error!,
                style: IOSTypography.callout(color: colors.danger))),
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
      backgroundColor: colors.bg,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        title: Text('${_index + 1}/${_questions.length}',
            style: IOSTypography.title2(color: colors.text)),
        leading: const BackButton(color: IOSSystemColors.blue),
        actions: [
          Center(
            child: Padding(
              padding: const EdgeInsets.only(right: 16),
              child: Text(
                '$mm:$ss',
                style: IOSTypography.title3(
                        color: _remaining.inMinutes < 5 ? colors.danger : colors.text)
                    .copyWith(fontWeight: FontWeight.w700),
              ),
            ),
          ),
          IconButton(
            icon: Icon(Icons.grid_view_outlined, color: colors.primary),
            tooltip: '答题卡',
            onPressed: _showAnswerCard,
          ),
        ],
      ),
      body: Center(
        child: ConstrainedBox(
          // 桌面答题内容限宽 760 居中（P4 对齐原型 d-desktop 答题限宽）
          constraints: const BoxConstraints(maxWidth: 760),
          child: ListView(
        padding: const EdgeInsets.fromLTRB(
            IOSSpacing.s16, IOSSpacing.s8, IOSSpacing.s16, IOSSpacing.s16),
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: IOSSpacing.s8,
                  vertical: IOSSpacing.s4,
                ),
                decoration: BoxDecoration(
                  color: typeColor(context, q.type).withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(IOSRadius.tag),
                ),
                child: Text(
                  typeLabel(q.type),
                  style: IOSTypography.caption2(color: typeColor(context, q.type))
                      .copyWith(fontWeight: FontWeight.w700),
                ),
              ),
              const SizedBox(width: IOSSpacing.s8),
              Expanded(
                child: Text(
                  // 综合卷跨科标注：学科名 · 章节（P2-3）
                  widget.pointsByType == null
                      ? q.chapter
                      : [mockBankLabel(q.bankId), q.chapter]
                            .where((s) => s.isNotEmpty)
                            .join(' · '),
                  style: IOSTypography.caption1(color: colors.text3),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              // 存疑标记（◆ 菱形，答题卡虚线待回看；设置页开关控制）
              if (_doubtEnabled)
                GestureDetector(
                  behavior: HitTestBehavior.opaque,
                  onTap: () => _toggleFlag(q.id),
                  child: Padding(
                    padding: const EdgeInsets.all(4),
                    child: Icon(
                      _flagged.contains(q.id)
                          ? Icons.diamond
                          : Icons.diamond_outlined,
                      size: 18,
                      color: _flagged.contains(q.id)
                          ? IOSSystemColors.yellow
                          : colors.text3,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: IOSSpacing.s16),
          Text(
            q.stem,
            style: IOSTypography.title2(color: colors.text)
                .copyWith(height: 1.6, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: IOSSpacing.s16),
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
          const SizedBox(height: IOSSpacing.s24),
          Row(
            children: [
              Expanded(
                child: IOSButton(
                  type: IOSButtonType.text,
                  label: '上一题',
                  onPressed: _index == 0
                      ? null
                      : () => setState(() => _index--),
                ),
              ),
              const SizedBox(width: IOSSpacing.s12),
              Expanded(
                child: IOSButton(
                  label: '下一题',
                  onPressed: _index >= _questions.length - 1
                      ? null
                      : () => setState(() => _index++),
                ),
              ),
            ],
          ),
          const SizedBox(height: IOSSpacing.s8),
          Text(
            '已答 $answeredCount / ${_questions.length}',
            textAlign: TextAlign.center,
            style: IOSTypography.caption1(color: colors.text2),
          ),
        ],
      ),
        ),
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(IOSSpacing.s16),
          child: SizedBox(
            width: double.infinity,
            child: IOSButton(
              label: '交卷',
              icon: Icons.flag_outlined,
              onPressed: _submitAll,
            ),
          ),
        ),
      ),
    );
  }

  void _showAnswerCard() {
    final colors = IOSColors.of(context);
    showIOSModalSheet(
      context: context,
      // P2-2：去掉内层 DraggableScrollableSheet（与 showIOSModalSheet 双层容器
      // 导致顶部大片空白）；直接 Column + 可滚动 GridView，与刷题答题卡统一。
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(IOSSpacing.s16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              '答题卡（已答 ${_answers.length}/${_questions.length}）',
              style: IOSTypography.title3(color: colors.text)
                  .copyWith(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: IOSSpacing.s12),
            // 响应式列数：每格最小约 48pt，4-10 列（与刷题答题卡一致）
            LayoutBuilder(
              builder: (ctx, constraints) {
                final cols =
                    (constraints.maxWidth / 48).floor().clamp(4, 10);
                return GridView.builder(
                  shrinkWrap: true,
                  // 内容多时允许内部滚动，避免溢出弹窗高度（R4 复查新增）
                  physics: const ClampingScrollPhysics(),
                  padding: const EdgeInsets.only(bottom: 8),
                  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: cols,
                    crossAxisSpacing: 8,
                    mainAxisSpacing: 8,
                  ),
                  itemCount: _questions.length,
                  itemBuilder: (_, i) => GestureDetector(
                    // P2-2：InkWell 水波纹 -> GestureDetector（深色无涟漪，iOS 风格）
                    onTap: () {
                      Navigator.pop(ctx);
                      setState(() => _index = i);
                    },
                    child: Center(
                      child: Container(
                        width: 36,
                        height: 36,
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                          color: _answers.containsKey(_questions[i].id)
                              ? colors.primary
                              : colors.fill2,
                          shape: BoxShape.circle,
                          border: _flagged.contains(_questions[i].id)
                              ? Border.all(
                                  color: IOSSystemColors.yellow,
                                  width: 1.6,
                                  style: BorderStyle.solid,
                                )
                              : null,
                        ),
                        child: Text(
                          '${i + 1}',
                          style: IOSTypography.caption1(
                                  color:
                                      _answers.containsKey(_questions[i].id)
                                          ? Colors.white
                                          : colors.text)
                              .copyWith(fontWeight: FontWeight.w600),
                        ),
                      ),
                    ),
                  ),
                );
              },
            ),
            const SizedBox(height: IOSSpacing.s16),
            SizedBox(
              width: double.infinity,
              child: IOSButton(
                label: '交卷',
                icon: Icons.flag_outlined,
                onPressed: () {
                  Navigator.pop(ctx);
                  _submitAll();
                },
              ),
            ),
          ],
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
    final colors = IOSColors.of(context);
    return Container(
      margin: const EdgeInsets.symmetric(vertical: IOSSpacing.s4),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(IOSRadius.md),
        border: Border.all(
          color: selected ? colors.primary : colors.separator,
          width: selected ? 1.8 : 1,
        ),
      ),
      child: Material(
        color: selected ? colors.primaryBg : Colors.transparent,
        borderRadius: BorderRadius.circular(IOSRadius.md),
        child: ListTile(
          leading: Icon(
            selected ? Icons.check_circle_outlined : Icons.circle_outlined,
            color: selected ? colors.primary : colors.text3,
          ),
          // 判断题显示「正确/错误」不带 key 前缀（修复：避免"正确. 正确"）
          title: Text(
            question.type == QuestionType.trueFalse
                ? option.text
                : '${option.key}. ${option.text}',
            style: IOSTypography.body(color: colors.text),
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
    final colors = IOSColors.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextField(
          controller: _controller,
          minLines: widget.isShortAnswer ? 3 : 1,
          maxLines: widget.isShortAnswer ? 5 : 1,
          decoration: InputDecoration(
            hintText: widget.isShortAnswer ? '简答作答' : '填写答案',
            hintStyle: IOSTypography.caption1(color: colors.text3),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(IOSRadius.md),
              borderSide: BorderSide(color: colors.separator),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(IOSRadius.md),
              borderSide: BorderSide(color: colors.separator),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(IOSRadius.md),
              borderSide: BorderSide(color: colors.primary, width: 1.5),
            ),
            filled: true,
            fillColor: colors.fill,
            contentPadding: const EdgeInsets.symmetric(
                horizontal: IOSSpacing.s12, vertical: IOSSpacing.s12),
          ),
          style: IOSTypography.body(color: colors.text),
          onChanged: (v) => widget.onSubmit(v.trim()),
        ),
      ],
    );
  }
}
