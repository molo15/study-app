/// 背题模式（P2，v11 背题存档）
///
/// 「不背单词式」卡片流：题干 → 点「显示答案」→ 看答案+解析 → 标「会/不会」→ 下一张。
/// - 标「不会」的卡进入待背队列，每隔 N 张再推回一次，直到标「会」（会话内循环推送）；
/// - 不判分、不写 answer_logs、不进错题本、不建立 FSRS 调度（用户拍板：不占用复习队列）；
/// - 跨会话存档（v11）：记忆状态持久化，自评即时落库；已掌握的不再进队列，
///   未掌握的进入时优先推送；全部掌握后提供「重新开始」。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import '../models/models.dart';
import 'glass_app_bar.dart';

class MemorizePage extends ConsumerStatefulWidget {
  const MemorizePage({
    super.key,
    required this.bankId,
    required this.chapter,
    required this.title,
    required this.questions,
    this.embedded = false,
  });

  final String bankId;
  final String chapter;
  final String title;
  final List<Question> questions;

  /// 嵌在 TabBar 容器内时不再自带 AppBar/Scaffold
  final bool embedded;

  @override
  ConsumerState<MemorizePage> createState() => _MemorizePageState();
}

class _MemorizePageState extends ConsumerState<MemorizePage> {
  /// 每隔多少张把「不会」的卡推回队列（不背单词式）
  static const _pushBackInterval = 5;

  late final List<Question> _all;
  List<Question> _queue = []; // 本轮待背（未掌握：学习中+未背）
  final List<Question> _pending = []; // 本轮待再次推送
  final List<Question> _mastered = []; // 本会话标过「背会」的
  final List<Question> _notYet = []; // 会话结束仍未背会
  int _processed = 0; // 已处理的卡数（含推送）
  bool _revealed = false; // 是否已显示答案
  bool _finished = false;
  bool _loading = true; // 加载存档中
  int _preMastered = 0; // 存档中已掌握的题数
  bool _allMastered = false; // 全部已掌握（无需再背）

  @override
  void initState() {
    super.initState();
    _all = List.of(widget.questions);
    _loadArchive();
  }

  /// 加载背题存档：排除已掌握的，构建本轮队列（v11）
  Future<void> _loadArchive() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      final states = await repo.memorizeStates(
        bankId: widget.bankId,
        chapter: widget.chapter,
        cardType: 'question',
      );
      final notMastered = <Question>[];
      var preMastered = 0;
      for (final q in _all) {
        final st = states[QuizRepository.qKey(q.id)];
        if (st != null && st.mastered) {
          preMastered++;
        } else {
          notMastered.add(q);
        }
      }
      if (!mounted) return;
      setState(() {
        _preMastered = preMastered;
        if (notMastered.isEmpty) {
          _allMastered = true;
          _finished = true;
        } else {
          _queue = notMastered;
        }
        _loading = false;
      });
    } catch (_) {
      // 存档读取失败降级为全量队列（原行为）
      if (!mounted) return;
      setState(() {
        _queue = List.of(_all);
        _loading = false;
      });
    }
  }

  Question? get _current => _queue.isEmpty ? null : _queue.first;

  void _reveal() {
    setState(() => _revealed = true);
  }

  /// 背题存档：自评即时落库（失败不阻断背诵）
  Future<void> _persist(Question q, {required bool know}) async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      await repo.recordMemorize(
        cardKey: QuizRepository.qKey(q.id),
        bankId: widget.bankId,
        chapter: widget.chapter,
        cardType: 'question',
        questionId: q.id,
        knowledgeId: q.knowledgeId,
        know: know,
      );
    } catch (_) {
      // 忽略：存档失败仅丢失本次自评，不影响会话
    }
  }

  Future<void> _know() async {
    final q = _queue.removeAt(0);
    _mastered.add(q);
    _processed++;
    _revealed = false;
    await _persist(q, know: true);
    _advance();
  }

  Future<void> _again() async {
    final q = _queue.removeAt(0);
    _pending.add(q);
    _notYet.add(q);
    _processed++;
    _revealed = false;
    await _persist(q, know: false);
    _advance();
  }

  /// 推送逻辑：每 _pushBackInterval 张把 pending 按序插到队尾（不背单词式循环）
  void _advance() {
    if (_queue.isEmpty && _pending.isNotEmpty) {
      // 一轮结束仍有不会的 → 全部重新入队，再来一轮
      _queue.addAll(_pending);
      _pending.clear();
      setState(() {});
      return;
    }
    if (_processed > 0 && _processed % _pushBackInterval == 0) {
      if (_pending.isNotEmpty) {
        _queue.addAll(_pending);
        _pending.clear();
      }
    }
    if (_queue.isEmpty) {
      _finished = true;
    }
    if (mounted) setState(() {});
  }

  /// 提前结束（未背会的保留在 _notYet，供提示继续）
  void _finishEarly() {
    setState(() => _finished = true);
  }

  /// 重新开始：重置本章题目卡全部存档，从头再背一轮
  Future<void> _restartAll() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      await repo.resetMemorize(
        bankId: widget.bankId,
        cardType: 'question',
        chapter: widget.chapter,
      );
    } catch (_) {}
    if (!mounted) return;
    setState(() {
      _queue = List.of(_all);
      _pending.clear();
      _mastered.clear();
      _notYet.clear();
      _processed = 0;
      _preMastered = 0;
      _allMastered = false;
      _finished = false;
      _revealed = false;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final Widget body;
    if (_loading) {
      body = const Center(child: CircularProgressIndicator());
    } else {
      body = _finished ? _buildSummary(theme) : _buildCard(theme);
    }
    if (widget.embedded) return body;
    return Scaffold(
      appBar: GlassAppBar(
        title: Text(widget.title),
        centerTitle: true,
      ),
      body: body,
    );
  }

  Widget _buildCard(ThemeData theme) {
    final q = _current;
    // 队列为空（极端边界）时回到总结视图，避免强解包崩溃（UI 审查 P2-6）
    if (q == null) return _buildSummary(theme);
    final total = _all.length;
    final masteredNow = _mastered.length + _preMastered;
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
      children: [
        // 进度（含存档已掌握 + 本会话新背会）
        Row(
          children: [
            Expanded(
              child: ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: total == 0 ? 0 : masteredNow / total,
                  minHeight: 6,
                  backgroundColor: theme.colorScheme.surfaceContainerHighest,
                ),
              ),
            ),
            const SizedBox(width: 10),
            Text(
              '已会 $masteredNow / $total',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.outline,
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        if (_pending.isNotEmpty)
          Text(
            '还有 ${_pending.length} 张没记住，稍后会再推给你',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.tertiary,
            ),
          ),
        const SizedBox(height: 12),
        // 题干卡
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    _TypeChip(type: q.type),
                    const SizedBox(width: 8),
                    if (q.purpose == 'basic')
                      Text(
                        '基础题',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.primary,
                        ),
                      ),
                    const Spacer(),
                    Text(
                      q.chapter,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.outline,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  q.stem,
                  style: theme.textTheme.titleSmall?.copyWith(height: 1.5),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        // 答案与解析
        if (!_revealed)
          SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              onPressed: _reveal,
              icon: const Icon(Icons.visibility_outlined),
              label: const Text('显示答案'),
            ),
          )
        else ...[
          _AnswerCard(question: q),
          const SizedBox(height: 12),
          if (q.explanation.isNotEmpty)
            _ExplanationCard(explanation: q.explanation),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _again,
                  style: OutlinedButton.styleFrom(
                    minimumSize: const Size(0, 52),
                    foregroundColor: theme.colorScheme.error,
                  ),
                  icon: const Icon(Icons.replay),
                  label: const Text('还不会'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: FilledButton.icon(
                  onPressed: _know,
                  style: FilledButton.styleFrom(minimumSize: const Size(0, 52)),
                  icon: const Icon(Icons.check),
                  label: const Text('背会了'),
                ),
              ),
            ],
          ),
        ],
        const SizedBox(height: 12),
        // 提前结束
        TextButton(
          onPressed: _finishEarly,
          child: const Text('结束本次背题'),
        ),
      ],
    );
  }

  Widget _buildSummary(ThemeData theme) {
    final total = _all.length;
    final mastered = _mastered.length + _preMastered;
    final ratio = total == 0 ? 0.0 : mastered / total;
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 24, 16, 96),
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              children: [
                Icon(
                  _allMastered
                      ? Icons.workspace_premium_outlined
                      : Icons.emoji_events_outlined,
                  size: 48,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(height: 12),
                Text(
                  _allMastered ? '本章题目已全部背会' : '本轮背题完成',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '已掌握 $mastered / $total · ${(ratio * 100).toStringAsFixed(0)}%',
                  style: theme.textTheme.bodyMedium,
                ),
                const SizedBox(height: 8),
                ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: ratio,
                    minHeight: 8,
                    backgroundColor: theme.colorScheme.surfaceContainerHighest,
                  ),
                ),
                if (_allMastered) ...[
                  const SizedBox(height: 12),
                  Text(
                    '进度已存档，之后进入无需重背',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.outline,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
        if (_notYet.isNotEmpty) ...[
          const SizedBox(height: 16),
          Text(
            '本次尚未背会（已存档，下次进入继续）',
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 8),
          for (final q in _notYet.take(50))
            Card(
              margin: EdgeInsets.zero,
              child: ListTile(
                dense: true,
                leading: _TypeChip(type: q.type),
                title: Text(
                  q.stem,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: theme.textTheme.bodySmall,
                ),
              ),
            ),
        ],
        const SizedBox(height: 20),
        if (_allMastered) ...[
          // 全部掌握：提供重新开始（重置存档）
          OutlinedButton.icon(
            onPressed: _restartAll,
            icon: const Icon(Icons.replay),
            label: const Text('重新背一遍（重置存档）'),
          ),
          const SizedBox(height: 8),
        ],
        FilledButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('完成'),
        ),
      ],
    );
  }
}

class _TypeChip extends StatelessWidget {
  const _TypeChip({required this.type});

  final QuestionType type;

  String get _label => switch (type) {
        QuestionType.singleChoice => '单选',
        QuestionType.multiChoice => '多选',
        QuestionType.trueFalse => '判断',
        QuestionType.blank => '填空',
        QuestionType.shortAnswer => '简答',
      };

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: theme.colorScheme.secondaryContainer,
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        _label,
        style: theme.textTheme.labelSmall?.copyWith(
          color: theme.colorScheme.onSecondaryContainer,
        ),
      ),
    );
  }
}

/// 背题模式答案卡：选择题高亮正确项，填空/简答显示参考答案
class _AnswerCard extends StatelessWidget {
  const _AnswerCard({required this.question});

  final Question question;

  /// 正确项选项（防脏数据）：单选最多返回 1 项（优先 key 精确匹配，无则按文本取第一个）；
  /// 多选按选项顺序取 answer 命中的 key（去重），key 全不命中时按文本兜底。
  static List<QuestionOption> _matchedOptions(Question q) {
    if (q.type == QuestionType.singleChoice) {
      for (final o in q.options) {
        if (q.answer.contains(o.key)) return [o];
      }
      for (final o in q.options) {
        if (q.answer.contains(o.text)) return [o];
      }
      return const [];
    }
    final byKey = <QuestionOption>[];
    final seen = <String>{};
    for (final o in q.options) {
      if (q.answer.contains(o.key) && seen.add(o.key)) byKey.add(o);
    }
    if (byKey.isNotEmpty) return byKey;
    return q.options.where((o) => q.answer.contains(o.text)).toList();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final q = question;
    final isChoice = q.type == QuestionType.singleChoice ||
        q.type == QuestionType.multiChoice;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.colorScheme.primaryContainer.withValues(alpha: 0.35),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: theme.colorScheme.primary.withValues(alpha: 0.3),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '参考答案',
            style: theme.textTheme.labelLarge?.copyWith(
              color: theme.colorScheme.primary,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 8),
          if (isChoice)
            for (final o in _matchedOptions(q))
              Padding(
                  padding: const EdgeInsets.symmetric(vertical: 2),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${o.key}. ',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      Expanded(
                        child: Text(
                          o.text,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            fontWeight: FontWeight.w600,
                            height: 1.4,
                          ),
                        ),
                      ),
                    ],
                  ),
                )
          else
            Text(
              q.answer.join('；'),
              style: theme.textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w600,
                height: 1.5,
              ),
            ),
        ],
      ),
    );
  }
}

/// 背题模式解析卡
class _ExplanationCard extends StatelessWidget {
  const _ExplanationCard({required this.explanation});

  final String explanation;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.lightbulb_outline, size: 16, color: theme.colorScheme.primary),
              const SizedBox(width: 6),
              Text(
                '解析',
                style: theme.textTheme.labelLarge?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            explanation,
            style: theme.textTheme.bodySmall?.copyWith(height: 1.5),
          ),
        ],
      ),
    );
  }
}
