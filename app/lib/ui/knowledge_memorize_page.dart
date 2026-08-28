/// 知识点卡背题模式（P2 · 知识点卡）
///
/// 「不背单词式」知识点卡片流：每张卡 = 一个知识点（名称 + 提炼要点 summary，
/// 关键术语高亮），点「背会了/还不会」推进。
/// - 标「还不会」的知识点进入待背队列，每隔 N 张再推回一次，直到标「会」（会话内循环推送）；
/// - 不判分、不写 answer_logs、不进错题本、不建立 FSRS 调度（与逐题背题一致，不占复习队列）；
/// - 不跨会话：每次进入都是全新一轮，无持久状态（用户拍板）；
/// - 卡片底部展示该知识点关联的基础题数，可一键跳到「题目背诵」。
library;

import 'package:flutter/material.dart';

import '../models/models.dart';
import 'glass_app_bar.dart';

class KnowledgeMemorizePage extends StatefulWidget {
  const KnowledgeMemorizePage({
    super.key,
    required this.bankId,
    required this.chapter,
    required this.title,
    required this.knowledge,
    this.embedded = false,
    this.onPracticeQuestions,
  });

  final String bankId;
  final String chapter;
  final String title;

  /// 本章/本组知识点
  final List<KnowledgePoint> knowledge;

  /// 嵌在 TabBar 容器内时不再自带 AppBar/Scaffold
  final bool embedded;

  /// 点击卡片底部「关联题」时回调（由外层负责跳转题目背诵）
  final void Function(KnowledgePoint kp)? onPracticeQuestions;

  @override
  State<KnowledgeMemorizePage> createState() => _KnowledgeMemorizePageState();
}

class _KnowledgeMemorizePageState extends State<KnowledgeMemorizePage> {
  /// 每隔多少张把「不会」的卡推回队列（不背单词式）
  static const _pushBackInterval = 5;

  late final List<KnowledgePoint> _queue;
  final List<KnowledgePoint> _pending = []; // 本轮待再次推送
  final List<KnowledgePoint> _mastered = []; // 已背会
  final List<KnowledgePoint> _notYet = []; // 会话结束仍未背会
  int _processed = 0; // 已处理的卡数（含推送）
  bool _revealed = false; // 是否已展开要点（显示完整）
  bool _finished = false;

  @override
  void initState() {
    super.initState();
    _queue = List.of(widget.knowledge);
  }

  KnowledgePoint? get _current => _queue.isEmpty ? null : _queue.first;

  void _reveal() => setState(() => _revealed = true);

  void _know() {
    final kp = _queue.removeAt(0);
    _mastered.add(kp);
    _processed++;
    _revealed = false;
    _advance();
  }

  void _again() {
    final kp = _queue.removeAt(0);
    _pending.add(kp);
    _notYet.add(kp);
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
  void _finishEarly() => setState(() => _finished = true);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final body = _finished ? _buildSummary(theme) : _buildCard(theme);
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
    final kp = _current;
    // 队列为空（极端边界）时回到总结视图，避免强解包崩溃
    if (kp == null) return _buildSummary(theme);
    final total = widget.knowledge.length;
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
            '还有 ${_pending.length} 个知识点没记住，稍后会再推给你',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.tertiary,
            ),
          ),
        const SizedBox(height: 12),
        // 知识点卡
        Card(
          margin: EdgeInsets.zero,
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    if (kp.hot) ...[
                      Icon(
                        Icons.local_fire_department,
                        size: 18,
                        color: theme.colorScheme.tertiary,
                      ),
                      const SizedBox(width: 4),
                    ],
                    Expanded(
                      child: Text(
                        kp.name,
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                          height: 1.3,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  '${widget.chapter} · 知识点',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.outline,
                  ),
                ),
                if (kp.summary.isNotEmpty) ...[
                  const SizedBox(height: 14),
                  _HighlightSummary(
                    text: kp.summary,
                    term: kp.name,
                    maxLines: _revealed ? null : 8,
                  ),
                ] else ...[
                  const SizedBox(height: 14),
                  Text(
                    '（本章节暂未提炼要点，可直接练习关联题目）',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.outline,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
                const SizedBox(height: 16),
                // 关联题入口
                if (kp.questionCount > 0)
                  InkWell(
                    onTap: () => widget.onPracticeQuestions?.call(kp),
                    borderRadius: BorderRadius.circular(8),
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      child: Row(
                        children: [
                          Icon(
                            Icons.edit_note,
                            size: 16,
                            color: theme.colorScheme.primary,
                          ),
                          const SizedBox(width: 6),
                          Text(
                            '本章 ${kp.questionCount} 题可练 →',
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: theme.colorScheme.primary,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        // 操作
        if (!_revealed)
          SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              onPressed: _reveal,
              icon: const Icon(Icons.visibility_outlined),
              label: const Text('展开要点'),
            ),
          )
        else ...[
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
    final total = widget.knowledge.length;
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
                  '本轮知识点背题完成',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '背会 $mastered / $total 个 · ${(ratio * 100).toStringAsFixed(0)}%',
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
          for (final kp in _notYet.take(50))
            Card(
              margin: EdgeInsets.zero,
              child: ListTile(
                dense: true,
                leading: kp.hot
                    ? Icon(
                        Icons.local_fire_department,
                        size: 18,
                        color: theme.colorScheme.tertiary,
                      )
                    : null,
                title: Text(
                  kp.name,
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

/// summary 关键术语高亮：书名号/引号内容与知识点名加粗着色，便于扫读记忆。
class _HighlightSummary extends StatelessWidget {
  const _HighlightSummary({
    required this.text,
    required this.term,
    this.maxLines,
  });

  final String text;
  final String term;
  final int? maxLines;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final base = theme.textTheme.bodyMedium?.copyWith(height: 1.55);
    final hl = TextStyle(
      color: theme.colorScheme.primary,
      fontWeight: FontWeight.w700,
      height: 1.55,
    );
    final termStyle = theme.textTheme.bodyMedium?.copyWith(
      color: theme.colorScheme.tertiary,
      fontWeight: FontWeight.w700,
      height: 1.55,
    );
    return Text.rich(
      TextSpan(style: base, children: _buildSpans(hl, termStyle)),
      maxLines: maxLines,
      overflow: maxLines == null ? null : TextOverflow.ellipsis,
    );
  }

  List<TextSpan> _buildSpans(TextStyle hl, TextStyle? termStyle) {
    // 优先切分标号内容（书名号/引号）
    final re = RegExp(r'《[^》]*》|「[^」]*」|“[^”]*”');
    final spans = <TextSpan>[];
    int last = 0;
    for (final m in re.allMatches(text)) {
      if (m.start > last) {
        _pushPlain(text.substring(last, m.start), spans, termStyle);
      }
      spans.add(TextSpan(text: m.group(0), style: hl));
      last = m.end;
    }
    if (last < text.length) {
      _pushPlain(text.substring(last), spans, termStyle);
    }
    return spans;
  }

  void _pushPlain(
    String s,
    List<TextSpan> spans,
    TextStyle? termStyle,
  ) {
    final t = term.trim();
    if (t.isNotEmpty && t.length >= 2 && s.contains(t)) {
      // 知识点名出现处高亮（tertiary）
      final idx = s.indexOf(t);
      if (idx > 0) {
        spans.add(TextSpan(text: s.substring(0, idx)));
      }
      spans.add(TextSpan(text: s.substring(idx, idx + t.length), style: termStyle));
      if (idx + t.length < s.length) {
        spans.add(TextSpan(text: s.substring(idx + t.length)));
      }
    } else {
      spans.add(TextSpan(text: s));
    }
  }
}
