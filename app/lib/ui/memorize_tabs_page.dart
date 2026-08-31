/// 背题模式容器页（P2 · 知识点卡）
///
/// 顶部两个 Tab：`知识点卡`（提炼要点，默认） / `题目背诵`（逐题卡流）。
/// - 知识点卡：KnowledgeMemorizePage（每张卡一个知识点，要点高亮，会/不会推流）
/// - 题目背诵：MemorizePage（题干→答案→会/不会，不背单词式推流）
/// - 知识点卡底部「关联题可练」可跳转到对应知识点的题目背诵。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import '../models/models.dart';
import 'glass_app_bar.dart';
import 'knowledge_memorize_page.dart';
import 'memorize_page.dart';
import 'practice_page.dart';
import 'app_routes.dart';

class MemorizeTabsPage extends ConsumerStatefulWidget {
  const MemorizeTabsPage({
    super.key,
    required this.bankId,
    required this.chapter,
    required this.title,
    required this.questions,
    required this.knowledge,
    this.initialTab = 0,
  });

  final String bankId;
  final String chapter;
  final String title;

  /// 整章题目（题目背诵 Tab 用）
  final List<Question> questions;

  /// 本章知识点（知识点卡 Tab 用）
  final List<KnowledgePoint> knowledge;

  /// 0=知识点卡（默认），1=题目背诵
  final int initialTab;

  @override
  ConsumerState<MemorizeTabsPage> createState() => _MemorizeTabsPageState();
}

class _MemorizeTabsPageState extends ConsumerState<MemorizeTabsPage> {
  late int _tab;

  /// v11 整章知识点卡进度：已掌握数（null=未加载完）
  int? _kpMastered;

  @override
  void initState() {
    super.initState();
    _tab = widget.initialTab;
    _loadKpProgress();
  }

  /// 加载整章知识点卡已掌握数（用于顶部汇总进度条）
  Future<void> _loadKpProgress() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      final states = await repo.memorizeStates(
        bankId: widget.bankId,
        chapter: widget.chapter,
        cardType: 'knowledge',
      );
      var mastered = 0;
      for (final kp in widget.knowledge) {
        final st = states[QuizRepository.kpKey(kp.id)];
        if (st != null && st.mastered) mastered++;
      }
      if (!mounted) return;
      setState(() => _kpMastered = mastered);
    } catch (_) {}
  }

  /// 跳转某知识点题目背诵
  Future<void> _practiceKnowledge(KnowledgePoint kp) async {
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

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: GlassAppBar(
        title: Text(widget.title),
        centerTitle: true,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(46 + 30),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 6),
                child: Container(
                  height: 38,
                  padding: const EdgeInsets.all(3),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.surfaceContainerHighest.withValues(
                      alpha: 0.6,
                    ),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    children: [
                      _Segment(
                        label: '知识点卡',
                        icon: Icons.account_tree_outlined,
                        selected: _tab == 0,
                        onTap: () => setState(() => _tab = 0),
                      ),
                      _Segment(
                        label: '题目背诵',
                        icon: Icons.style_outlined,
                        selected: _tab == 1,
                        onTap: () => setState(() => _tab = 1),
                      ),
                    ],
                  ),
                ),
              ),
              // v11 整章知识点卡进度
              if (widget.knowledge.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
                  child: Row(
                    children: [
                      Expanded(
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(3),
                          child: LinearProgressIndicator(
                            value: widget.knowledge.isEmpty
                                ? 0
                                : ((_kpMastered ?? 0) / widget.knowledge.length)
                                    .clamp(0.0, 1.0),
                            minHeight: 4,
                            backgroundColor:
                                theme.colorScheme.surfaceContainerHighest,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '知识点已掌握 ${_kpMastered ?? 0}/${widget.knowledge.length}',
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: theme.colorScheme.outline,
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),
        ),
      ),
      body: _tab == 0
          ? KnowledgeMemorizePage(
              bankId: widget.bankId,
              chapter: widget.chapter,
              title: widget.title,
              knowledge: widget.knowledge,
              embedded: true,
              onPracticeQuestions: _practiceKnowledge,
            )
          : MemorizePage(
              bankId: widget.bankId,
              chapter: widget.chapter,
              title: widget.title,
              questions: widget.questions,
              embedded: true,
            ),
    );
  }
}

class _Segment extends StatelessWidget {
  const _Segment({
    required this.label,
    required this.icon,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final IconData icon;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Expanded(
      child: Material(
        color: selected
            ? theme.colorScheme.primaryContainer
            : Colors.transparent,
        borderRadius: BorderRadius.circular(17),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(17),
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 7),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  icon,
                  size: 16,
                  color: selected
                      ? theme.colorScheme.onPrimaryContainer
                      : theme.colorScheme.outline,
                ),
                const SizedBox(width: 6),
                Text(
                  label,
                  style: theme.textTheme.labelMedium?.copyWith(
                    color: selected
                        ? theme.colorScheme.onPrimaryContainer
                        : theme.colorScheme.outline,
                    fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
