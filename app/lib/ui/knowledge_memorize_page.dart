/// 知识点卡背题模式（P2 · 知识点卡，v11 背题存档）
///
/// 「不背单词式」知识点卡片流：每张卡 = 一个知识点（名称 + 提炼要点 summary，
/// 关键术语高亮），点「背会了/还不会」推进。
/// - 标「还不会」的知识点进入待背队列，每隔 N 张再推回一次，直到标「会」（会话内循环推送）；
/// - 不判分、不写 answer_logs、不进错题本、不建立 FSRS 调度（与逐题背题一致，不占复习队列）；
/// - 跨会话存档（v11）：记忆状态持久化，自评即时落库；已掌握的不再进队列，
///   未掌握的进入时优先推送；全部掌握后提供「重新开始」；
/// - 卡片底部展示该知识点关联的基础题数，可一键跳到「题目背诵」。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import '../models/models.dart';
import 'theme_controller.dart';
import 'glass_app_bar.dart';
import 'widgets/flippable_card.dart';

class KnowledgeMemorizePage extends ConsumerStatefulWidget {
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
  ConsumerState<KnowledgeMemorizePage> createState() =>
      _KnowledgeMemorizePageState();
}

class _KnowledgeMemorizePageState
    extends ConsumerState<KnowledgeMemorizePage> {
  /// 每隔多少张把「不会」的卡推回队列（不背单词式）
  static const _pushBackInterval = 5;

  late final List<KnowledgePoint> _all;
  List<KnowledgePoint> _queue = []; // 本轮待背（未掌握：学习中+未背）
  final List<KnowledgePoint> _pending = []; // 本轮待再次推送
  final List<KnowledgePoint> _mastered = []; // 本会话标过「背会」的
  final List<KnowledgePoint> _notYet = []; // 会话结束仍未背会
  int _processed = 0; // 已处理的卡数（含推送）
  bool _revealed = false; // 是否已展开要点（显示完整）
  bool _finished = false;
  bool _loading = true; // 加载存档中
  int _preMastered = 0; // 存档中已掌握的知识点数
  bool _allMastered = false; // 全部已掌握（无需再背）

  @override
  void initState() {
    super.initState();
    _all = List.of(widget.knowledge);
    _loadArchive();
  }

  /// 加载背题存档：排除已掌握的，构建本轮队列（v11）
  Future<void> _loadArchive() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      final states = await repo.memorizeStates(
        bankId: widget.bankId,
        chapter: widget.chapter,
        cardType: 'knowledge',
      );
      final notMastered = <KnowledgePoint>[];
      var preMastered = 0;
      for (final kp in _all) {
        final st = states[QuizRepository.kpKey(kp.id)];
        if (st != null && st.mastered) {
          preMastered++;
        } else {
          notMastered.add(kp);
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

  KnowledgePoint? get _current => _queue.isEmpty ? null : _queue.first;

  void _reveal() => setState(() => _revealed = true);

  /// 背题存档：自评即时落库（失败不阻断背诵）
  Future<void> _persist(KnowledgePoint kp, {required bool know}) async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      await repo.recordMemorize(
        cardKey: QuizRepository.kpKey(kp.id),
        bankId: widget.bankId,
        chapter: widget.chapter,
        cardType: 'knowledge',
        knowledgeId: kp.id,
        know: know,
      );
    } catch (_) {
      // 忽略：存档失败仅丢失本次自评，不影响会话
    }
  }

  Future<void> _know() async {
    final kp = _queue.removeAt(0);
    _mastered.add(kp);
    _processed++;
    _revealed = false;
    await _persist(kp, know: true);
    _advance();
  }

  Future<void> _again() async {
    final kp = _queue.removeAt(0);
    _pending.add(kp);
    _notYet.add(kp);
    _processed++;
    _revealed = false;
    await _persist(kp, know: false);
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

  /// 重新开始：重置本章知识点卡全部存档，从头再背一轮
  Future<void> _restartAll() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      await repo.resetMemorize(
        bankId: widget.bankId,
        cardType: 'knowledge',
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
    final kp = _current;
    // 队列为空（极端边界）时回到总结视图，避免强解包崩溃
    if (kp == null) return _buildSummary(theme);
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
            '还有 ${_pending.length} 个知识点没记住，稍后会再推给你',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.tertiary,
            ),
          ),
        const SizedBox(height: 12),
        // 知识点卡（3D 翻转：正面知识点名 → 背面要点）
        FlippableCard(
          flipped: _revealed,
          onTap: _reveal,
          height: 330,
          borderRadius: 24,
          front: _frontCard(theme, kp),
          back: _backCard(theme, kp),
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

  /// 卡正面：知识点名 + 章节 + 轻点提示
  Widget _frontCard(ThemeData theme, KnowledgePoint kp) {
    final config = ref.watch(themeControllerProvider).asData?.value;
    final accent = config?.accent ?? const Color(0xFF4F7CD4);
    final dark = config?.darkMode ?? false;
    final base = dark ? const Color(0xFF2B3646) : Colors.white;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            base.withValues(alpha: dark ? 0.9 : 0.78),
            base.withValues(alpha: dark ? 0.7 : 0.40),
          ],
        ),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: Colors.white.withValues(alpha: dark ? 0.2 : 0.7),
        ),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          if (kp.hot) ...[
            Icon(Icons.local_fire_department, size: 20, color: theme.colorScheme.tertiary),
            const SizedBox(height: 8),
          ],
          // 长知识点名保护：最多 4 行，超出省略
          Flexible(
            child: SingleChildScrollView(
              child: Text(
                kp.name,
                textAlign: TextAlign.center,
                maxLines: 6,
                overflow: TextOverflow.ellipsis,
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w800,
                  height: 1.35,
                  color: theme.colorScheme.onSurface,
                ),
              ),
            ),
          ),
          const SizedBox(height: 10),
          Text(
            '${widget.chapter} · 知识点',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.outline,
            ),
          ),
          const SizedBox(height: 28),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(18),
              color: accent.withValues(alpha: 0.12),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.touch_app, size: 14, color: accent),
                const SizedBox(width: 6),
                Text(
                  '轻点卡片查看要点',
                  style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: accent),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 卡背面：要点完整展开 + 关联题入口
  Widget _backCard(ThemeData theme, KnowledgePoint kp) {
    final config = ref.watch(themeControllerProvider).asData?.value;
    final dark = config?.darkMode ?? false;
    final base = dark ? const Color(0xFF2B3646) : Colors.white;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            base.withValues(alpha: dark ? 0.92 : 0.80),
            base.withValues(alpha: dark ? 0.72 : 0.42),
          ],
        ),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: Colors.white.withValues(alpha: dark ? 0.2 : 0.7),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '要点',
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w800,
              color: theme.colorScheme.primary,
            ),
          ),
          const SizedBox(height: 10),
          Expanded(
            child: SingleChildScrollView(
              child: kp.summary.isNotEmpty
                  ? _HighlightSummary(text: kp.summary, term: kp.name)
                  : Text(
                      '（本章节暂未提炼要点，可直接练习关联题目）',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.outline,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
            ),
          ),
          const SizedBox(height: 10),
          // 关联题入口
          if (kp.questionCount > 0)
            InkWell(
              onTap: () => widget.onPracticeQuestions?.call(kp),
              borderRadius: BorderRadius.circular(10),
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(12),
                  color: theme.colorScheme.primary.withValues(alpha: 0.10),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.edit_note, size: 16, color: theme.colorScheme.primary),
                    const SizedBox(width: 6),
                    Text(
                      '本章 ${kp.questionCount} 题可练 →',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.primary,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ],
                ),
              ),
            )
          else
            Text(
              '轻点卡片返回',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.outline,
              ),
            ),
        ],
      ),
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
                  _allMastered ? '本章知识点已全部背会' : '本轮知识点背题完成',
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

/// summary 关键术语高亮：书名号/引号内容与知识点名加粗着色，便于扫读记忆。
class _HighlightSummary extends StatelessWidget {
  const _HighlightSummary({
    required this.text,
    required this.term,
  });

  final String text;
  final String term;

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
