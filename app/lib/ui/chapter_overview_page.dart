/// 章节知识概览页（P2，formatVersion=4）
///
/// 进入章节刷题前先看知识概览：章节 summary + 知识点树（每点关联题数、
/// 高频标记、摘要、作答进度），并可从概览直达「刷题」或「背题模式」。
/// 旧包（无知识点树）时概览页提供降级入口：直接整章刷题。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import '../models/models.dart';
import 'glass_app_bar.dart';
import 'memorize_page.dart';
import 'memorize_tabs_page.dart';
import 'practice_page.dart';
import 'widgets/app_section_header.dart';
import 'widgets/app_state_view.dart';
import 'app_routes.dart';

class ChapterOverviewPage extends ConsumerStatefulWidget {
  const ChapterOverviewPage({
    super.key,
    required this.bankId,
    required this.chapter,
    this.bankName = '',
  });

  final String bankId;
  final String chapter;
  final String bankName;

  @override
  ConsumerState<ChapterOverviewPage> createState() =>
      _ChapterOverviewPageState();
}

class _ChapterOverviewPageState extends ConsumerState<ChapterOverviewPage> {
  bool _loading = true;
  String? _error;
  ChapterOverview? _overview;
  List<KnowledgePoint> _knowledge = const [];
  Map<String, ({int total, int answered, int correct})> _progress = const {};
  // v11 背题存档：{knowledgeId: MemorizeProgress}
  Map<String, MemorizeProgress> _memoStates = const {};

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      final overviews = await repo.chapterOverviews(widget.bankId);
      ChapterOverview? ov;
      for (final o in overviews) {
        if (o.chapter == widget.chapter) {
          ov = o;
          break;
        }
      }
      final knowledge = await repo.knowledgeByChapter(
        widget.bankId,
        widget.chapter,
      );
      final progress = <String, ({int total, int answered, int correct})>{};
      for (final kp in knowledge) {
        progress[kp.id] = await repo.knowledgeProgress(
          widget.bankId,
          kp.id,
        );
      }
      // v11 背题存档：加载本章知识点卡记忆状态（概览页显示进度胶囊）
      final memoStates = await repo.memorizeStates(
        bankId: widget.bankId,
        chapter: widget.chapter,
        cardType: 'knowledge',
      );
      if (!mounted) return;
      setState(() {
        _overview = ov;
        _knowledge = knowledge;
        _progress = progress;
        _memoStates = memoStates;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = '加载失败：$e';
      });
    }
  }

  /// 整章刷题
  void _startChapter() {
    Navigator.of(context).push(
      AppPageRoute(
        builder: (_) => PracticePage(
          bankId: widget.bankId,
          chapter: widget.chapter,
          progressKey: 'chapter:${widget.bankId}:${widget.chapter}',
        ),
      ),
    );
  }

  /// 某个知识点刷题
  Future<void> _startKnowledge(KnowledgePoint kp) async {
    final repo = await ref.read(quizRepositoryProvider);
    final questions = await repo.questionsByKnowledge(widget.bankId, kp.id);
    if (!mounted) return;
    Navigator.of(context).push(
      AppPageRoute(
        builder: (_) => PracticePage(
          bankId: widget.bankId,
          questions: questions,
          progressKey: 'knowledge:${widget.bankId}:${kp.id}',
        ),
      ),
    );
  }

  /// 背题模式：整章进入「知识点卡/题目背诵」双 Tab；单知识点保持逐题背诵
  Future<void> _startMemorize({String? knowledgeId}) async {
    final repo = await ref.read(quizRepositoryProvider);
    final List<Question> questions;
    if (knowledgeId != null) {
      questions = await repo.questionsByKnowledge(widget.bankId, knowledgeId);
    } else {
      questions = await repo.questions(
        bankId: widget.bankId,
        chapter: widget.chapter,
      );
    }
    if (!mounted) return;
    final kpName = _kpName(knowledgeId);
    if (knowledgeId == null) {
      // 整章：双 Tab 背题（知识点卡默认）
      Navigator.of(context).push(
        AppPageRoute(
          builder: (_) => MemorizeTabsPage(
            bankId: widget.bankId,
            chapter: widget.chapter,
            title: '${widget.chapter} · 背题',
            questions: questions,
            knowledge: _knowledge,
          ),
        ),
      );
    } else {
      // 单知识点：逐题背诵
      Navigator.of(context).push(
        AppPageRoute(
          builder: (_) => MemorizePage(
            bankId: widget.bankId,
            chapter: widget.chapter,
            title: kpName.isEmpty ? '${widget.chapter} · 背题' : '$kpName · 背题',
            questions: questions,
          ),
        ),
      );
    }
  }

  /// 知识点名称兜底查找（knowledgeId 失效时返回空串，避免 firstWhere 抛异常）
  String _kpName(String? id) {
    if (id == null) return '';
    for (final k in _knowledge) {
      if (k.id == id) return k.name;
    }
    return '';
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: GlassAppBar(
        title: Hero(
          tag: 'chapter-title:${widget.bankId}:${widget.chapter}',
          child: Text(widget.chapter),
        ),
        centerTitle: true,
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? AppStateView.error(
                  message: _error!,
                  onRetry: () {
                    setState(() {
                      _loading = true;
                      _error = null;
                    });
                    _load();
                  },
                )
              : _buildBody(theme),
    );
  }

  Widget _buildBody(ThemeData theme) {
    final hasKnowledge = _knowledge.isNotEmpty;
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
      children: [
        _buildOverviewCard(theme),
        const SizedBox(height: 12),
        _buildActionRow(theme),
        const SizedBox(height: 20),
        AppSectionHeader(
          title: hasKnowledge ? '知识点 · ${_knowledge.length}' : '本章题目',
          trailing: Text(
            hasKnowledge
                ? '${_overview?.questionCount ?? 0} 道基础题'
                : '${_overview?.questionCount ?? 0} 题',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.outline,
            ),
          ),
        ),
        const SizedBox(height: 8),
        if (!hasKnowledge)
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: theme.colorScheme.surfaceContainerHighest.withValues(
                alpha: 0.5,
              ),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              children: [
                Icon(
                  Icons.account_tree_outlined,
                  size: 40,
                  color: theme.colorScheme.outline,
                ),
                const SizedBox(height: 12),
                Text(
                  '此题库包未含知识点结构',
                  style: theme.textTheme.titleMedium,
                ),
                const SizedBox(height: 4),
                Text(
                  '可直接整章刷题，或升级题库包获得知识点概览',
                  textAlign: TextAlign.center,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.outline,
                  ),
                ),
              ],
            ),
          )
        else
          for (final kp in _knowledge) ...[
            _KnowledgeCard(
              kp: kp,
              progress: _progress[kp.id],
              memorize: _memoStates[kp.id],
              onPractice: () => _startKnowledge(kp),
              onMemorize: () => _startMemorize(knowledgeId: kp.id),
            ),
            const SizedBox(height: 8),
          ],
      ],
    );
  }

  Widget _buildOverviewCard(ThemeData theme) {
    final ov = _overview;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.colorScheme.primaryContainer.withValues(alpha: 0.4),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.auto_stories_outlined,
                color: theme.colorScheme.primary,
              ),
              const SizedBox(width: 8),
              Text(
                '本章知识概览',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            ov?.summary.isNotEmpty == true
                ? ov!.summary
                : '${widget.chapter} · ${ov?.questionCount ?? 0} 道题待练习。',
            style: theme.textTheme.bodySmall?.copyWith(height: 1.5),
          ),
        ],
      ),
    );
  }

  Widget _buildActionRow(ThemeData theme) {
    return Row(
      children: [
        Expanded(
          child: FilledButton.icon(
            onPressed: _startChapter,
            icon: const Icon(Icons.edit_note),
            label: const Text('开始刷题'),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: FilledButton.tonalIcon(
            onPressed: _startMemorize,
            icon: const Icon(Icons.style_outlined),
            label: const Text('背题模式'),
          ),
        ),
      ],
    );
  }
}

/// 知识点卡片：名称 + 高频标记 + 题数/进度 + 摘要（可展开）+ 刷题/背题
class _KnowledgeCard extends StatefulWidget {
  const _KnowledgeCard({
    required this.kp,
    required this.progress,
    this.memorize,
    required this.onPractice,
    required this.onMemorize,
  });

  final KnowledgePoint kp;
  final ({int total, int answered, int correct})? progress;

  /// v11 背题存档状态（null=未背）
  final MemorizeProgress? memorize;
  final VoidCallback onPractice;
  final VoidCallback onMemorize;

  @override
  State<_KnowledgeCard> createState() => _KnowledgeCardState();
}

class _KnowledgeCardState extends State<_KnowledgeCard> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final kp = widget.kp;
    final p = widget.progress;
    final ratio = (p == null || p.total == 0)
        ? 0.0
        : (p.answered / p.total).clamp(0.0, 1.0);
    return Card(
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 12, 12, 12),
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
                ],                Expanded(
                  child: Text(
                    kp.name,
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                Text(
                  '${kp.questionCount} 题',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.outline,
                  ),
                ),
                if (widget.memorize != null) ...[
                  const SizedBox(width: 6),
                  _MemorizeBadge(progress: widget.memorize!),
                ],
              ],
            ),
            if (kp.summary.isNotEmpty) ...[
              const SizedBox(height: 6),
              Text(
                kp.summary,
                maxLines: _expanded ? null : 2,
                overflow: _expanded ? null : TextOverflow.ellipsis,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                  height: 1.45,
                ),
              ),
              if (kp.summary.length > 40)
                GestureDetector(
                  onTap: () => setState(() => _expanded = !_expanded),
                  child: Text(
                    _expanded ? '收起' : '展开',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.primary,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
            ],
            if (p != null && p.total > 0) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(3),
                      child: LinearProgressIndicator(
                        value: ratio,
                        minHeight: 4,
                        backgroundColor: theme.colorScheme.surfaceContainerHighest,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '已答 ${p.answered}/${p.total}',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.outline,
                    ),
                  ),
                ],
              ),
            ],
            const SizedBox(height: 4),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton.icon(
                  onPressed: widget.onMemorize,
                  icon: const Icon(Icons.style_outlined, size: 18),
                  label: const Text('背题'),
                ),
                const SizedBox(width: 4),
                TextButton.icon(
                  onPressed: widget.onPractice,
                  icon: const Icon(Icons.play_arrow, size: 18),
                  label: const Text('刷题'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}


/// v11 背题存档状态胶囊：已掌握（绿）/ 学习中（橙）
class _MemorizeBadge extends StatelessWidget {
  const _MemorizeBadge({required this.progress});

  final MemorizeProgress progress;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final mastered = progress.mastered;
    final color = mastered ? const Color(0xFF2E7D32) : Colors.orange.shade800;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Text(
        mastered ? '已掌握' : '学习中',
        style: theme.textTheme.labelSmall?.copyWith(
          color: color,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }
}
