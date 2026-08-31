# -*- coding: utf-8 -*-
"""背题存档：chapter_overview_page 进度胶囊 + memorize_tabs 整章进度条"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============ 1. chapter_overview_page.dart ============
p = r'D:\study_app\app\lib\ui\chapter_overview_page.dart'
s = open(p, encoding='utf-8').read()

# 1a. 状态加 _memoStates
old_state = """  ChapterOverview? _overview;
  List<KnowledgePoint> _knowledge = const [];
  Map<String, ({int total, int answered, int correct})> _progress = const {};"""
new_state = """  ChapterOverview? _overview;
  List<KnowledgePoint> _knowledge = const [];
  Map<String, ({int total, int answered, int correct})> _progress = const {};
  // v11 背题存档：{knowledgeId: MemorizeProgress}
  Map<String, MemorizeProgress> _memoStates = const {};"""
assert old_state in s, 'state anchor missing'
s = s.replace(old_state, new_state)

# 1b. _load 中加载背题存档
old_load = """      final progress = <String, ({int total, int answered, int correct})>{};
      for (final kp in knowledge) {
        progress[kp.id] = await repo.knowledgeProgress(
          widget.bankId,
          kp.id,
        );
      }
      if (!mounted) return;
      setState(() {
        _overview = ov;
        _knowledge = knowledge;
        _progress = progress;
        _loading = false;
      });"""
new_load = """      final progress = <String, ({int total, int answered, int correct})>{};
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
      });"""
assert old_load in s, 'load anchor missing'
s = s.replace(old_load, new_load)

# 1c. _KnowledgeCard 调用处传 memorize
old_card_call = """            _KnowledgeCard(
              kp: kp,
              progress: _progress[kp.id],
              onPractice: () => _startKnowledge(kp),
              onMemorize: () => _startMemorize(knowledgeId: kp.id),
            ),"""
new_card_call = """            _KnowledgeCard(
              kp: kp,
              progress: _progress[kp.id],
              memorize: _memoStates[kp.id],
              onPractice: () => _startKnowledge(kp),
              onMemorize: () => _startMemorize(knowledgeId: kp.id),
            ),"""
assert old_card_call in s, 'card call anchor missing'
s = s.replace(old_card_call, new_card_call)

# 1d. _KnowledgeCard 类定义加 memorize 参数
old_widget = """class _KnowledgeCard extends StatefulWidget {
  const _KnowledgeCard({
    required this.kp,
    required this.progress,
    required this.onPractice,
    required this.onMemorize,
  });

  final KnowledgePoint kp;
  final ({int total, int answered, int correct})? progress;
  final VoidCallback onPractice;
  final VoidCallback onMemorize;"""
new_widget = """class _KnowledgeCard extends StatefulWidget {
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
  final VoidCallback onMemorize;"""
assert old_widget in s, 'widget anchor missing'
s = s.replace(old_widget, new_widget)

# 1e. _KnowledgeCard build 中题数旁加背诵状态胶囊
old_count = """                Text(
                  '${kp.questionCount} 题',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.outline,
                  ),
                ),
              ],
            ),"""
new_count = """                Text(
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
            ),"""
assert old_count in s, 'count anchor missing'
s = s.replace(old_count, new_count)

# 1f. 文件末尾追加 _MemorizeBadge 组件
append = '''

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
'''
s = s.rstrip() + '\n' + append
open(p, 'w', encoding='utf-8', newline='').write(s)
print('chapter_overview_page 完成')
print('  _memoStates:', '_memoStates' in s)
print('  _MemorizeBadge:', '_MemorizeBadge' in s)

# ============ 2. memorize_tabs_page.dart 整章进度条 ============
p2 = r'D:\study_app\app\lib\ui\memorize_tabs_page.dart'
s2 = open(p2, encoding='utf-8').read()

# 2a. 状态加 _kpMastered
old2_state = """class _MemorizeTabsPageState extends ConsumerState<MemorizeTabsPage> {
  late int _tab;

  @override
  void initState() {
    super.initState();
    _tab = widget.initialTab;
  }"""
new2_state = """class _MemorizeTabsPageState extends ConsumerState<MemorizeTabsPage> {
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
  }"""
assert old2_state in s2, 'tabs state anchor missing'
s2 = s2.replace(old2_state, new2_state)

# 2b. AppBar bottom 加进度条（Tab 栏下方）
old2_bottom = """        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(46),
          child: Padding(
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
        ),"""
new2_bottom = """        bottom: PreferredSize(
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
        ),"""
assert old2_bottom in s2, 'tabs bottom anchor missing'
s2 = s2.replace(old2_bottom, new2_bottom)

open(p2, 'w', encoding='utf-8', newline='').write(s2)
print('memorize_tabs_page 完成')
print('  _kpMastered:', '_kpMastered' in s2)
print('  顶部进度条:', '知识点已掌握' in s2)
