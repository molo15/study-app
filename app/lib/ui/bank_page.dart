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

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../data/quiz_repository.dart';
import '../models/models.dart';
import 'practice_page.dart';
import 'app_routes.dart';
import 'responsive.dart';
import 'theme/ios_tokens.dart';
import 'widgets/ios_button.dart';
import 'widgets/ios_card.dart';
import 'widgets/ios_action_sheet.dart';
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
    final count = await showIOSActionSheet<int>(
      context: context,
      title: '选择随机刷题量',
      items: [
        for (final n in [50, 100, 150])
          IOSActionItem(
            value: n,
            title: '$n 题',
            subtitle: n <= _totalCount
                ? '整本随机 · 按题型顺序'
                : '题库共 $_totalCount 题，取全部',
            icon: Icons.shuffle,
          ),
      ],
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
    final colors = IOSColors.of(context);
    return Scaffold(
      backgroundColor: colors.bg,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        title: Text(_bankName,
            style: IOSTypography.title2(color: colors.text)),
        leading: const BackButton(color: IOSSystemColors.blue),
      ),
      body: _loading
          ? const Center(child: CupertinoActivityIndicator(radius: 14))
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
          : Center(
              child: ConstrainedBox(
                constraints: BoxConstraints(
                    maxWidth: effectiveContentWidth(context)),
                child: ListView(
              padding: const EdgeInsets.fromLTRB(16, 4, 16, 96),
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
              ),
            ),
    );
  }

  /// 题库概览卡：总题数为主要信息，版本弱化为 bodySmall（设计方案 §3.3）
  Widget _buildOverview(ThemeData theme) {
    final colors = IOSColors.of(context);
    return IOSCard(
      padding: const EdgeInsets.all(IOSSpacing.s16),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: colors.primaryBg,
              borderRadius: BorderRadius.circular(IOSRadius.md),
            ),
            child: Icon(
              Icons.menu_book_outlined,
              color: colors.primary,
              size: 22,
            ),
          ),
          const SizedBox(width: IOSSpacing.s12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '共 $_totalCount 题',
                  style: IOSTypography.body(color: colors.text)
                      .copyWith(fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: IOSSpacing.s4),
                Text(
                  '题库包 v$_bankVersion',
                  style: IOSTypography.caption1(color: colors.text3),
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
    final colors = IOSColors.of(context);
    return IOSCard(
      padding: EdgeInsets.zero,
      showBorder: true,
      onTap: () => Navigator.of(context).push(
        AppPageRoute(
          builder: (_) => PracticePage(
            bankId: widget.bankId,
            questions: _keyQuestions,
            progressKey: 'key-questions:${widget.bankId}',
          ),
        ),
      ),
      child: _BankEntryRow(
        icon: Icons.star,
        iconBg: colors.primary,
        iconColor: Colors.white,
        title: '重点题目',
        titleWeight: FontWeight.w700,
        subtitle: '$_keyQuestionCount 题 · 按考点热门章节抽取',
      ),
    );
  }

  /// 整本随机刷：次级入口（用户要求：选 50/100/150 题，按题型顺序排列）
  Widget _buildRandom(ThemeData theme) {
    final colors = IOSColors.of(context);
    return IOSCard(
      padding: EdgeInsets.zero,
      onTap: _pickRandomCount,
      child: _BankEntryRow(
        icon: Icons.shuffle,
        iconBg: colors.primaryBg,
        iconColor: colors.primary,
        title: '整本随机刷',
        subtitle: '选 50 / 100 / 150 题 · 按题型顺序',
      ),
    );
  }

  /// 章节知识概览入口（P2，v4 库独立成部分）：点击进入全库章节概览列表
  Widget _buildOverviewEntry(ThemeData theme) {
    final colors = IOSColors.of(context);
    return IOSCard(
      padding: EdgeInsets.zero,
      onTap: () => context.go('/bank/${widget.bankId}/chapters'),
      child: _BankEntryRow(
        icon: Icons.account_tree_outlined,
        iconBg: colors.primaryBg,
        iconColor: colors.primary,
        title: '章节知识概览',
        subtitle: '按章节浏览知识点 · 直达刷题/背题',
      ),
    );
  }

  /// 论述题专题：独立专题样式（左侧色条 + 浅色主题背景，避免与普通章节混淆）
  Widget _buildEssayTopic(ThemeData theme) {
    final colors = IOSColors.of(context);
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(IOSRadius.lg),
        border: Border(
          left: BorderSide(color: colors.primary, width: 4),
        ),
      ),
      child: IOSCard(
        padding: EdgeInsets.zero,
        onTap: () => Navigator.of(context).push(
          AppPageRoute(
            builder: (_) => PracticePage(
              bankId: widget.bankId,
              chapter: '论述题专题',
              progressKey: 'essay:${widget.bankId}',
            ),
          ),
        ),
        child: _BankEntryRow(
          icon: Icons.forum_outlined,
          iconBg: colors.primaryBg,
          iconColor: colors.primary,
          title: '论述题专题',
          subtitle: '${_chapterCounts['论述题专题'] ?? 0} 题 · 历年真题论述题',
          padding: const EdgeInsets.fromLTRB(IOSSpacing.s20, IOSSpacing.s8, IOSSpacing.s16, IOSSpacing.s8),
        ),
      ),
    );
  }

  /// 编/章组卡：ExpansionTile 结构不变，统一行内间距、题量弱化展示
  Widget _buildGroupCard(ThemeData theme, ChapterGroup group) {
    final colors = IOSColors.of(context);
    return IOSCard(
      padding: EdgeInsets.zero,
      child: ExpansionTile(
        tilePadding:
            const EdgeInsets.symmetric(horizontal: IOSSpacing.s16, vertical: 4),
        childrenPadding:
            const EdgeInsets.only(left: IOSSpacing.s16, right: IOSSpacing.s16, bottom: IOSSpacing.s8),
        leading: Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: colors.primaryBg,
            borderRadius: BorderRadius.circular(IOSRadius.xs),
          ),
          child: Icon(
            Icons.folder_outlined,
            color: colors.primary,
            size: 20,
          ),
        ),
        title: Text(
          group.group,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: IOSTypography.body(color: colors.text)
              .copyWith(fontWeight: FontWeight.w600),
        ),
        subtitle: Text(
          '${group.chapters.length} 章 · '
          '${group.chapters.fold(0, (s, c) => s + (_chapterCounts[c] ?? 0))} 题',
          style: IOSTypography.caption1(color: colors.text2),
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
    final colors = IOSColors.of(context);
    return IOSCard(
      padding: const EdgeInsets.all(IOSSpacing.s24),
      child: Column(
        children: [
          Icon(
            Icons.folder_off_outlined,
            size: 40,
            color: colors.text3,
          ),
          const SizedBox(height: IOSSpacing.s12),
          Text('该题库暂无章节', style: IOSTypography.title3(color: colors.text)),
          const SizedBox(height: IOSSpacing.s4),
          Text(
            '可先使用「整本随机刷」开始练习',
            style: IOSTypography.caption1(color: colors.text3),
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
    final colors = IOSColors.of(context);
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.cloud_off_outlined,
              size: 44,
              color: colors.danger,
            ),
            const SizedBox(height: IOSSpacing.s12),
            Text(
              message,
              textAlign: TextAlign.center,
              style: IOSTypography.body(color: colors.text2),
            ),
            const SizedBox(height: IOSSpacing.s16),
            IOSButton(
              label: '重试',
              icon: Icons.refresh,
              onPressed: onRetry,
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
    final colors = IOSColors.of(context);
    final total = basicCount + testCount + otherCount;
    final hasSplit = basicCount > 0 || testCount > 0;

    // 无分类数据的章节（旧包）：整行可点，尾显总题数
    if (!hasSplit) {
      return GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () => _go(context),
        child: Padding(
          padding: const EdgeInsets.symmetric(
              horizontal: IOSSpacing.s16, vertical: IOSSpacing.s12),
          child: Row(
            children: [
              Icon(Icons.description_outlined, size: 20, color: colors.text2),
              const SizedBox(width: IOSSpacing.s12),
              Expanded(
                child: Hero(
                  tag: 'chapter-title:$bankId:$chapter',
                  child: Text(
                    chapter,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: IOSTypography.body(color: colors.text),
                  ),
                ),
              ),
              Text('$total 题',
                  style: IOSTypography.caption1(color: colors.text3)),
            ],
          ),
        ),
      );
    }

    return ExpansionTile(
      tilePadding: const EdgeInsets.symmetric(horizontal: IOSSpacing.s16, vertical: 0),
      childrenPadding: const EdgeInsets.only(left: IOSSpacing.s24),
      leading: Icon(Icons.description_outlined, size: 20, color: colors.text2),
      title: Hero(
        tag: 'chapter-title:$bankId:$chapter',
        child: Text(
          chapter,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: IOSTypography.body(color: colors.text),
        ),
      ),
      subtitle: Text(
        '共 $total 题 · 展开按基础/测试分类刷',
        style: IOSTypography.caption1(color: colors.text3),
      ),
      children: [
        if (hasKnowledge)
          _ChapterActionRow(
            icon: Icons.account_tree_outlined,
            iconColor: colors.primary,
            title: '本章知识概览',
            subtitle: '知识点树 · 直达刷题/背题',
            onTap: () => _goOverview(context),
          ),
        if (basicCount > 0)
          _ChapterActionRow(
            icon: Icons.lightbulb_outline,
            iconColor: colors.warning,
            title: '基础题',
            subtitle: basicCount > 1
                ? '$basicCount 题 · 单选题/填空题为主'
                : '$basicCount 题',
            onTap: () => _go(context, purpose: 'basic'),
          ),
        if (testCount > 0)
          _ChapterActionRow(
            icon: Icons.rate_review_outlined,
            iconColor: IOSSystemColors.purple,
            title: '测试题',
            subtitle: testCount > 1
                ? '$testCount 题 · 简答/名解/论述为主'
                : '$testCount 题',
            onTap: () => _go(context, purpose: 'test'),
          ),
        // 整章刷全部入口：始终提供（基础+测试+未分区一并刷，统一 3 级导航行为）
        _ChapterActionRow(
          icon: Icons.all_inclusive,
          iconColor: colors.success,
          title: '全部',
          subtitle: otherCount > 0
              ? '$total 题 · 基础+测试+未分区'
              : '$total 题 · 基础+测试整章刷',
          onTap: () => _go(context),
        ),
      ],
    );
  }
}


/// V3 风格章节子项行：替代 ExpansionTile 内的 Material ListTile（dense），无 InkWell。
class _ChapterActionRow extends StatelessWidget {
  const _ChapterActionRow({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final Color iconColor;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(
            horizontal: IOSSpacing.s16, vertical: IOSSpacing.s8),
        child: Row(
          children: [
            Icon(icon, size: 18, color: iconColor),
            const SizedBox(width: IOSSpacing.s12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: IOSTypography.body(color: colors.text)),
                  const SizedBox(height: 2),
                  Text(subtitle,
                      style: IOSTypography.caption1(color: colors.text2)),
                ],
              ),
            ),
            Icon(Icons.chevron_right, size: 18, color: colors.text3),
          ],
        ),
      ),
    );
  }
}

/// V3 风格题库入口行：替代 Material ListTile，无 InkWell 水波纹。
class _BankEntryRow extends StatelessWidget {
  const _BankEntryRow({
    required this.icon,
    required this.iconBg,
    required this.iconColor,
    required this.title,
    required this.subtitle,
    this.titleWeight = FontWeight.w600,
    this.padding = const EdgeInsets.symmetric(
        horizontal: IOSSpacing.s16, vertical: IOSSpacing.s8),
  });

  final IconData icon;
  final Color iconBg;
  final Color iconColor;
  final String title;
  final String subtitle;
  final FontWeight titleWeight;
  final EdgeInsets padding;

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    return Padding(
      padding: padding,
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: iconBg,
              borderRadius: BorderRadius.circular(IOSRadius.xs),
            ),
            child: Icon(icon, color: iconColor, size: 22),
          ),
          const SizedBox(width: IOSSpacing.s12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: IOSTypography.body(color: colors.text)
                        .copyWith(fontWeight: titleWeight)),
                const SizedBox(height: 2),
                Text(subtitle,
                    style: IOSTypography.caption1(color: colors.text2)),
              ],
            ),
          ),
          Icon(Icons.chevron_right, color: colors.text3),
        ],
      ),
    );
  }
}
