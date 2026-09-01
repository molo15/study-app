/// 题库详情页（二级界面）：按「上编/中编/下编 → 章节」树形展示
///
/// 需求：首页是题库列表，点进题库后这里按思源笔记的编/章架构展开，
/// 点击具体章节进入该章刷题（三级）。
///
/// 改版（阶段 B，设计方案 §3.3）：
/// - 概览卡精简：总题数为主要信息，版本信息弱化为 bodySmall；
/// - 三个入口视觉分层：重点章节合集（主卡片/星标）> 整本随机刷（次级）>
///   论述题专题（独立专题样式，左侧色条 + 浅色主题背景），点击行为与
///   PracticePage 传参均不变；
/// - 章节树保留 ExpansionTile 结构与「论述题专题不重复出现」过滤逻辑，
///   统一行内间距与题量弱化展示；
/// - 加载失败给出重试按钮，无章节时给出轻量空态。
library;

import 'package:flutter/material.dart';
import 'widgets/app_card.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../data/quiz_repository.dart';
import '../models/models.dart';
import 'glass_app_bar.dart';
import 'practice_page.dart';
import 'app_routes.dart';
import 'widgets/staggered_item.dart';

class BankPage extends ConsumerStatefulWidget {
  const BankPage({super.key, required this.bankId});

  final String bankId;

  @override
  ConsumerState<BankPage> createState() => _BankPageState();
}

class _BankPageState extends ConsumerState<BankPage> {
  bool _loading = true;
  String? _error;
  String _bankName = '';
  String _bankVersion = '';
  List<ChapterGroup> _groups = const [];
  Map<String, int> _chapterCounts = const {};
  Map<(String, String), int> _purposeCounts = const {}; // (chapter, purpose) -> count
  int _totalCount = 0;
  int _keyQuestionCount = 0; // 重点题目合集题数（按考点热门抽取，大章不再整章进入）
  List<Question> _keyQuestions = const []; // 重点题目合集缓存（点击即刷）
  bool _hasKnowledge = false; // 是否 v4 包（含知识点树）→ 章节入口先进知识概览页

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      final name =
          await repo.setting('bank_${widget.bankId}_name') ?? widget.bankId;
      final version = await repo.importedVersion(widget.bankId) ?? '';
      final groups = await repo.chapterGroups(widget.bankId);
      // 分组兜底：无分组元数据时用实际章节
      // 论述题专题使用章节末尾的独立入口展示，避免同时出现在分组树中造成重复。
      var effectiveGroups = groups
          .where((group) => group.group != '论述题专题')
          .toList();
      if (effectiveGroups.isEmpty) {
        final chapters = (await repo.chapters(
          widget.bankId,
        )).where((chapter) => chapter != '论述题专题').toList();
        effectiveGroups = chapters.isEmpty
            ? const []
            : [ChapterGroup(group: '全部', chapters: chapters)];
      }
      final counts = await repo.chapterCounts(widget.bankId);
      final purposeCounts = await repo.chapterPurposeCounts(widget.bankId);
      final hasKnowledge = await repo.hasKnowledge(widget.bankId);
      var total = 0;
      for (final c in counts.values) {
        total += c;
      }
      // 重点题目：按考点热门（章节题量厚优先）抽取合集 50~150 题（用户要求），
      // 大章不再整章进合集——古汉/现汉也能稳定得到重点合集。
      final keyQuestions = await repo.keyQuestions(
        widget.bankId,
        minTotal: 50,
        maxTotal: 150,
      );
      if (!mounted) return;
      setState(() {
        _bankName = name;
        _bankVersion = version;
        _groups = effectiveGroups;
        _chapterCounts = counts;
        _purposeCounts = purposeCounts;
        _hasKnowledge = hasKnowledge;
        _totalCount = total;
        _keyQuestions = keyQuestions;
        _keyQuestionCount = keyQuestions.length;
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

  /// 整本随机刷：弹层选 50/100/150 → 随机取题按题型顺序排列（用户要求）
  Future<void> _pickRandomCount() async {
    final count = await showModalBottomSheet<int>(
      context: context,
      builder: (ctx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                '选择随机刷题量',
                style: Theme.of(ctx).textTheme.titleMedium,
              ),
            ),
            for (final n in [50, 100, 150])
              ListTile(
                leading: const Icon(Icons.shuffle),
                title: Text('$n 题'),
                subtitle: Text(
                  n <= _totalCount ? '整本随机 · 按题型顺序' : '题库共 $_totalCount 题，取全部',
                ),
                onTap: () => Navigator.pop(ctx, n),
              ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
    if (count == null || !mounted) return;
    Navigator.of(context).push(
      AppPageRoute(
        builder: (_) => PracticePage(bankId: widget.bankId, randomLimit: count),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: GlassAppBar(title: Text(_bankName), centerTitle: true),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
          ? _ErrorView(
              message: _error!,
              onRetry: () {
                setState(() {
                  _loading = true;
                  _error = null;
                });
                _load();
              },
            )
          : ListView(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
              children: [
                _buildOverview(theme),
                if (_keyQuestions.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  _buildKeyQuestions(theme),
                ],
                const SizedBox(height: 12),
                _buildRandom(theme),
                if (_hasKnowledge) ...[
                  const SizedBox(height: 12),
                  _buildOverviewEntry(theme),
                ],
                if ((_chapterCounts['论述题专题'] ?? 0) > 0) ...[
                  const SizedBox(height: 12),
                  _buildEssayTopic(theme),
                ],
                if (_groups.isEmpty)
                  _buildEmptyGroups(theme)
                else ...[
                  const SizedBox(height: 12),
                  // 章节树：编（ExpansionTile）→ 章（ListTile → 刷题）
                  for (var i = 0; i < _groups.length; i++) ...[
                    StaggeredItem(
                      index: i,
                      child: _buildGroupCard(theme, _groups[i]),
                    ),
                    const SizedBox(height: 12),
                  ],
                ],
              ],
            ),
    );
  }

  /// 题库概览卡：总题数为主要信息，版本弱化为 bodySmall（设计方案 §3.3）
  Widget _buildOverview(ThemeData theme) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.colorScheme.primaryContainer.withValues(alpha: 0.4),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: theme.colorScheme.primary.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              Icons.menu_book_outlined,
              color: theme.colorScheme.primary,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '共 $_totalCount 题',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  '题库包 v$_bankVersion',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.outline,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 重点题目：主推荐卡（星标强调，设计定位高优先级学习路径）
  /// 按考点热门（章节题量厚优先）抽取合集，大章不再整章进入（古汉/现汉也稳定可用）。
  Widget _buildKeyQuestions(ThemeData theme) {
    return Container(
      decoration: BoxDecoration(
        color: theme.colorScheme.primaryContainer.withValues(alpha: 0.45),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: theme.colorScheme.primary.withValues(alpha: 0.25),
        ),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: theme.colorScheme.primary,
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(Icons.star, color: theme.colorScheme.onPrimary, size: 22),
        ),
        title: const Text(
          '重点题目',
          style: TextStyle(fontWeight: FontWeight.w700),
        ),
        subtitle: Text('$_keyQuestionCount 题 · 按考点热门章节抽取'),
        trailing: const Icon(Icons.chevron_right),
        onTap: () => Navigator.of(context).push(
          AppPageRoute(
            builder: (_) => PracticePage(
              bankId: widget.bankId,
              questions: _keyQuestions,
              progressKey: 'key-questions:${widget.bankId}',
            ),
          ),
        ),
      ),
    );
  }

  /// 整本随机刷：次级入口（用户要求：选 50/100/150 题，按题型顺序排列）
  Widget _buildRandom(ThemeData theme) {
    return AppCard(padding: EdgeInsets.zero, margin: EdgeInsets.zero,
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: theme.colorScheme.tertiary.withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(
            Icons.shuffle,
            color: theme.colorScheme.tertiary,
            size: 22,
          ),
        ),
        title: const Text(
          '整本随机刷',
          style: TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: const Text('选 50 / 100 / 150 题 · 按题型顺序'),
        trailing: const Icon(Icons.chevron_right),
        onTap: _pickRandomCount,
      ),
    );
  }

  /// 章节知识概览入口（P2，v4 库独立成部分）：点击进入全库章节概览列表
  Widget _buildOverviewEntry(ThemeData theme) {
    return AppCard(padding: EdgeInsets.zero, margin: EdgeInsets.zero,
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: theme.colorScheme.primary.withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(
            Icons.account_tree_outlined,
            color: theme.colorScheme.primary,
            size: 22,
          ),
        ),
        title: const Text(
          '章节知识概览',
          style: TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: const Text('按章节浏览知识点 · 直达刷题/背题'),
        trailing: const Icon(Icons.chevron_right),
        onTap: () => context.go('/bank/${widget.bankId}/chapters'),
      ),
    );
  }

  /// 论述题专题：独立专题样式（左侧色条 + 浅色主题背景，避免与普通章节混淆）
  Widget _buildEssayTopic(ThemeData theme) {    return Container(
      decoration: BoxDecoration(
        color: theme.colorScheme.secondaryContainer.withValues(alpha: 0.4),
        borderRadius: BorderRadius.circular(16),
        border: Border(
          left: BorderSide(color: theme.colorScheme.secondary, width: 4),
        ),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.fromLTRB(20, 8, 16, 8),
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: theme.colorScheme.secondary.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(
            Icons.forum_outlined,
            color: theme.colorScheme.secondary,
            size: 22,
          ),
        ),
        title: const Text(
          '论述题专题',
          style: TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: Text('${_chapterCounts['论述题专题'] ?? 0} 题 · 历年真题论述题'),
        trailing: const Icon(Icons.chevron_right),
        onTap: () => Navigator.of(context).push(
          AppPageRoute(
            builder: (_) => PracticePage(
              bankId: widget.bankId,
              chapter: '论述题专题',
              progressKey: 'essay:${widget.bankId}',
            ),
          ),
        ),
      ),
    );
  }

  /// 编/章组卡：ExpansionTile 结构不变，统一行内间距、题量弱化展示
  Widget _buildGroupCard(ThemeData theme, ChapterGroup group) {
    return AppCard(padding: EdgeInsets.zero, margin: EdgeInsets.zero,
      child: ExpansionTile(
        tilePadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
        childrenPadding: const EdgeInsets.only(left: 16, right: 16, bottom: 8),
        leading: Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: theme.colorScheme.primary.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(
            Icons.folder_outlined,
            color: theme.colorScheme.primary,
            size: 20,
          ),
        ),
        title: Text(
          group.group,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: Text(
          '${group.chapters.length} 章 · '
          '${group.chapters.fold(0, (s, c) => s + (_chapterCounts[c] ?? 0))} 题',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        children: [
          for (final chapter in group.chapters)
            _ChapterTile(
              bankId: widget.bankId,
              chapter: chapter,
              hasKnowledge: _hasKnowledge,
              basicCount: _purposeCounts[(chapter, 'basic')] ?? 0,
              testCount: _purposeCounts[(chapter, 'test')] ?? 0,
              otherCount: (_chapterCounts[chapter] ?? 0) -
                  ((_purposeCounts[(chapter, 'basic')] ?? 0) +
                      (_purposeCounts[(chapter, 'test')] ?? 0)),
            ),
        ],
      ),
    );
  }

  /// 无章节空态：给出下一步行动（整本随机刷已在入口区展示）
  Widget _buildEmptyGroups(ThemeData theme) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: [
          Icon(
            Icons.folder_off_outlined,
            size: 40,
            color: theme.colorScheme.outline,
          ),
          const SizedBox(height: 12),
          Text('该题库暂无章节', style: theme.textTheme.titleMedium),
          const SizedBox(height: 4),
          Text(
            '可先使用「整本随机刷」开始练习',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.outline,
            ),
          ),
        ],
      ),
    );
  }
}

/// 通用错误态：图标 + 说明 + 重试按钮（页面内私有组件）
class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.cloud_off_outlined,
              size: 44,
              color: theme.colorScheme.error,
            ),
            const SizedBox(height: 12),
            Text(
              message,
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
            FilledButton.tonalIcon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh),
              label: const Text('重试'),
            ),
          ],
        ),
      ),
    );
  }
}

/// 章节行：点击整章刷全部；行内可展开"基础题 / 测试题"两个子分类（v0.9.0 双轨）。
/// v4 库（hasKnowledge=true）：整章入口先进「章节知识概览页」（P2）。
class _ChapterTile extends StatelessWidget {
  const _ChapterTile({
    required this.bankId,
    required this.chapter,
    required this.hasKnowledge,
    required this.basicCount,
    required this.testCount,
    required this.otherCount,
  });

  final String bankId;
  final String chapter;
  final bool hasKnowledge;
  final int basicCount;
  final int testCount;

  /// 未分区（purpose 为空）的普通题数
  final int otherCount;

  void _go(BuildContext context, {String? purpose}) {
    // 概览页已独立为题库页「章节知识概览」入口；章节行保持直达刷题（快速通道）
    Navigator.of(context).push(
      AppPageRoute(
        builder: (_) => PracticePage(
          bankId: bankId,
          chapter: chapter,
          purpose: purpose,
          progressKey: purpose == null
              ? 'chapter:$bankId:$chapter'
              : 'chapter:$bankId:$chapter:$purpose',
        ),
      ),
    );
  }

  /// 章节知识概览（单章）——章节行独立入口，与「全部」刷题分离
  void _goOverview(BuildContext context) {
    context.go('/bank/$bankId/chapter/${Uri.encodeComponent(chapter)}');
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final total = basicCount + testCount + otherCount;
    final hasSplit = basicCount > 0 || testCount > 0;

    // 无分类数据的章节（旧包）：整行可点，尾显总题数
    if (!hasSplit) {
      return ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16),
        leading: const Icon(Icons.description_outlined, size: 20),
        title: Hero(
          tag: 'chapter-title:$bankId:$chapter',
          child: Text(
            chapter,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: theme.textTheme.bodyMedium,
          ),
        ),
        trailing: Text(
          '$total 题',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.outline,
          ),
        ),
        onTap: () => _go(context),
      );
    }

    return ExpansionTile(
      tilePadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 0),
      childrenPadding: const EdgeInsets.only(left: 24),
      leading: const Icon(Icons.description_outlined, size: 20),
      title: Hero(
        tag: 'chapter-title:$bankId:$chapter',
        child: Text(
          chapter,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: theme.textTheme.bodyMedium,
        ),
      ),
      subtitle: Text(
        '共 $total 题 · 展开按基础/测试分类刷',
        style: theme.textTheme.bodySmall?.copyWith(
          color: theme.colorScheme.outline,
        ),
      ),
      children: [
        if (hasKnowledge)
          ListTile(
            dense: true,
            leading: const Icon(Icons.account_tree_outlined, size: 18),
            title: const Text('本章知识概览'),
            subtitle: Text(
              '知识点树 · 直达刷题/背题',
              style: theme.textTheme.bodySmall,
            ),
            trailing: const Icon(Icons.chevron_right, size: 18),
            onTap: () => _goOverview(context),
          ),
        if (basicCount > 0)
          ListTile(
            dense: true,
            leading: const Icon(Icons.lightbulb_outline, size: 18),
            title: const Text('基础题'),
            subtitle: Text(
              basicCount > 1 ? '$basicCount 题 · 单选题/填空题为主' : '$basicCount 题',
              style: theme.textTheme.bodySmall,
            ),
            trailing: const Icon(Icons.chevron_right, size: 18),
            onTap: () => _go(context, purpose: 'basic'),
          ),
        if (testCount > 0)
          ListTile(
            dense: true,
            leading: const Icon(Icons.rate_review_outlined, size: 18),
            title: const Text('测试题'),
            subtitle: Text(
              testCount > 1 ? '$testCount 题 · 简答/名解/论述为主' : '$testCount 题',
              style: theme.textTheme.bodySmall,
            ),
            trailing: const Icon(Icons.chevron_right, size: 18),
            onTap: () => _go(context, purpose: 'test'),
          ),
        // 整章刷全部入口：始终提供（基础+测试+未分区一并刷，统一 3 级导航行为）
        ListTile(
          dense: true,
          leading: const Icon(Icons.all_inclusive, size: 18),
          title: const Text('全部'),
          subtitle: Text(
            otherCount > 0
                ? '$total 题 · 基础+测试+未分区'
                : '$total 题 · 基础+测试整章刷',
            style: theme.textTheme.bodySmall,
          ),
          trailing: const Icon(Icons.chevron_right, size: 18),
          onTap: () => _go(context),
        ),
      ],
    );
  }
}
