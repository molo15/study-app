/// 背题模式（P2）
///
/// 「不背单词式」卡片流：题干 → 点「显示答案」→ 看答案+解析 → 标「会/不会」→ 下一张。
/// - 标「不会」的卡进入待背队列，每隔 N 张再推回一次，直到标「会」（会话内循环推送）；
/// - 不判分、不写 answer_logs、不进错题本、不建立 FSRS 调度（用户拍板：不占用复习队列）；
/// - 会话结束：已背会数量统计；未背会的仅会话内保留（可继续本次会话）。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/models.dart';
import 'glass_app_bar.dart';

class MemorizePage extends ConsumerStatefulWidget {
  const MemorizePage({
    super.key,
    required this.bankId,
    required this.chapter,
    required this.title,
    required this.questions,
  });

  final String bankId;
  final String chapter;
  final String title;
  final List<Question> questions;

  @override
  ConsumerState<MemorizePage> createState() => _MemorizePageState();
}

class _MemorizePageState extends ConsumerState<MemorizePage> {
  /// 每隔多少张把「不会」的卡推回队列（不背单词式）
  static const _pushBackInterval = 5;

  late final List<Question> _queue;
  final List<Question> _pending = []; // 本轮待再次推送
  final List<Question> _mastered = []; // 已背会
  final List<Question> _notYet = []; // 会话结束仍未背会
  int _processed = 0; // 已处理的卡数（含推送）
  bool _revealed = false; // 是否已显示答案
  bool _finished = false;

  @override
  void initState() {
    super.initState();
    _queue = List.of(widget.questions);
  }

  Question? get _current => _queue.isEmpty ? null : _queue.first;

  void _reveal() {
    setState(() => _revealed = true);
  }

  void _know() {
    final q = _queue.removeAt(0);
    _mastered.add(q);
    _processed++;
    _revealed = false;
    _advance();
  }

  void _again() {
    final q = _queue.removeAt(0);
    _pending.add(q);
    _notYet.add(q);
    _processed++;
    _revealed = false;
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

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: GlassAppBar(
        title: Text(widget.title),
        centerTitle: true,
      ),
      body: _finished ? _buildSummary(theme) : _buildCard(theme),
    );
  }

  Widget _buildCard(ThemeData theme) {
    final q = _current!;
    final total = widget.questions.length;
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
      children: [
        // 进度
        Row(
          children: [
            Expanded(
              child: ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: total == 0 ? 0 : _mastered.length / total,
                  minHeight: 6,
                  backgroundColor: theme.colorScheme.surfaceContainerHighest,
                ),
              ),
            ),
            const SizedBox(width: 10),
            Text(
              '已会 ${_mastered.length} / $total',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.outline,
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        if (_pending.isNotEmpty)
          Text(
            '待回背 ${_pending.length} 张（不背单词式，稍后再推）',
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
    final total = widget.questions.length;
    final mastered = _mastered.length;
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
                  Icons.emoji_events_outlined,
                  size: 48,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(height: 12),
                Text(
                  '本轮背题完成',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '背会 $mastered / $total 张 · ${(ratio * 100).toStringAsFixed(0)}%',
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
              ],
            ),
          ),
        ),
        if (_notYet.isNotEmpty) ...[
          const SizedBox(height: 16),
          Text(
            '本次尚未背会（下次进入可继续）',
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
            for (final o in q.options)
              if (q.answer.contains(o.key))
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
