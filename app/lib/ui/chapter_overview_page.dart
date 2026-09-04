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
import 'memorize_page.dart';
import 'memorize_tabs_page.dart';
import 'practice_page.dart';
import 'responsive.dart';
import 'app_routes.dart';
import 'theme/ios_tokens.dart';
import 'widgets/ios_button.dart';
import 'widgets/ios_card.dart';

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
    final colors = IOSColors.of(context);
    return Scaffold(
      backgroundColor: colors.bg,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        title: Hero(
          tag: 'chapter-title:${widget.bankId}:${widget.chapter}',
          child: Text(widget.chapter,
              style: IOSTypography.title2(color: colors.text)),
        ),
        leading: const BackButton(color: IOSSystemColors.blue),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(strokeWidth: 2.5))
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
              : _buildBody(),
    );
  }

  Widget _buildBody() {
    final colors = IOSColors.of(context);
    final hasKnowledge = _knowledge.isNotEmpty;
    return Center(
      child: ConstrainedBox(
        constraints:
            BoxConstraints(maxWidth: effectiveContentWidth(context)),
        child: ListView(
          padding: const EdgeInsets.fromLTRB(
              IOSSpacing.s16, IOSSpacing.s8, IOSSpacing.s16,
              IOSFloatingBar.kTContentBottomInset),
          children: [
            _buildOverviewCard(),
            const SizedBox(height: IOSSpacing.s12),
            _buildActionRow(),
            const SizedBox(height: IOSSpacing.s40),
            _buildSectionHeader(
              title: hasKnowledge ? '知识点 · ${_knowledge.length}' : '本章题目',
              trailing: hasKnowledge
                  ? '${_overview?.questionCount ?? 0} 道基础题'
                  : '${_overview?.questionCount ?? 0} 题',
            ),
            const SizedBox(height: IOSSpacing.s8),
            if (!hasKnowledge)
              IOSCard(
                padding: const EdgeInsets.all(IOSSpacing.s24),
                child: Column(
                  children: [
                    Icon(
                      Icons.account_tree_outlined,
                      size: 40,
                      color: colors.text3,
                    ),
                    const SizedBox(height: IOSSpacing.s12),
                    Text('此题库包未含知识点结构',
                        style: IOSTypography.title3(color: colors.text)),
                    const SizedBox(height: IOSSpacing.s4),
                    Text(
                      '可直接整章刷题，或升级题库包获得知识点概览',
                      textAlign: TextAlign.center,
                      style: IOSTypography.caption1(color: colors.text3),
                    ),
                  ],
                ),
              )
            else if (isWideScreen(context))
              // 宽屏（平板/桌面）知识点两列（P3 对齐原型 chaps）
              Wrap(
                spacing: 12,
                runSpacing: 12,
                children: [
                  for (final kp in _knowledge)
                    SizedBox(
                      width: (effectiveContentWidth(context) - 32 - 12) / 2,
                      child: _KnowledgeCard(
                        kp: kp,
                        progress: _progress[kp.id],
                        memorize: _memoStates[kp.id],
                        onPractice: () => _startKnowledge(kp),
                        onMemorize: () => _startMemorize(knowledgeId: kp.id),
                      ),
                    ),
                ],
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
                const SizedBox(height: IOSSpacing.s8),
              ],
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader({required String title, required String trailing}) {
    final colors = IOSColors.of(context);
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Text(title,
            style: IOSTypography.title3(color: colors.text)
                .copyWith(fontWeight: FontWeight.w700)),
        Text(trailing, style: IOSTypography.caption1(color: colors.text3)),
      ],
    );
  }

  Widget _buildOverviewCard() {
    final colors = IOSColors.of(context);
    final ov = _overview;
    return IOSCard(
      padding: const EdgeInsets.all(IOSSpacing.s16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.auto_stories_outlined,
                color: colors.primary,
              ),
              const SizedBox(width: IOSSpacing.s8),
              Text(
                '本章知识概览',
                style: IOSTypography.title3(color: colors.text)
                    .copyWith(fontWeight: FontWeight.w700),
              ),
            ],
          ),
          const SizedBox(height: IOSSpacing.s8),
          Text(
            ov?.summary.isNotEmpty == true
                ? ov!.summary
                : '${widget.chapter} · ${ov?.questionCount ?? 0} 道题待练习。',
            style: IOSTypography.caption1(color: colors.text2)
                .copyWith(height: 1.5),
          ),
        ],
      ),
    );
  }

  Widget _buildActionRow() {
    return Row(
      children: [
        Expanded(
          child: IOSButton(
            type: IOSButtonType.primary,
            label: '开始刷题',
            icon: Icons.edit_note,
            onPressed: _startChapter,
          ),
        ),
        const SizedBox(width: IOSSpacing.s12),
        Expanded(
          child: IOSButton(
            type: IOSButtonType.text,
            label: '背题模式',
            icon: Icons.style_outlined,
            onPressed: _startMemorize,
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
    final colors = IOSColors.of(context);
    final kp = widget.kp;
    final p = widget.progress;
    final ratio = (p == null || p.total == 0)
        ? 0.0
        : (p.answered / p.total).clamp(0.0, 1.0);
    return IOSCard(
      padding: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(
            IOSSpacing.s16, IOSSpacing.s12, IOSSpacing.s12, IOSSpacing.s12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                if (kp.hot) ...[
                  Icon(
                    Icons.local_fire_department,
                    size: 18,
                    color: IOSSystemColors.orange,
                  ),
                  const SizedBox(width: IOSSpacing.s4),
                ],
                Expanded(
                  child: Text(
                    kp.name,
                    style: IOSTypography.body(color: colors.text)
                        .copyWith(fontWeight: FontWeight.w600),
                  ),
                ),
                Text(
                  '${kp.questionCount} 题',
                  style: IOSTypography.caption1(color: colors.text3),
                ),
                if (widget.memorize != null) ...[
                  const SizedBox(width: IOSSpacing.s8),
                  _MemorizeBadge(progress: widget.memorize!),
                ],
              ],
            ),
            if (kp.summary.isNotEmpty) ...[
              const SizedBox(height: IOSSpacing.s8),
              Text(
                kp.summary,
                maxLines: _expanded ? null : 2,
                overflow: _expanded ? null : TextOverflow.ellipsis,
                style: IOSTypography.caption1(color: colors.text2)
                    .copyWith(height: 1.45),
              ),
              if (kp.summary.length > 40)
                GestureDetector(
                  onTap: () => setState(() => _expanded = !_expanded),
                  child: Text(
                    _expanded ? '收起' : '展开',
                    style: IOSTypography.caption1(color: colors.primary)
                        .copyWith(fontWeight: FontWeight.w600),
                  ),
                ),
            ],
            if (p != null && p.total > 0) ...[
              const SizedBox(height: IOSSpacing.s8),
              Row(
                children: [
                  Expanded(
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(3),
                      child: LinearProgressIndicator(
                        value: ratio,
                        minHeight: 4,
                        color: colors.primary,
                        backgroundColor: colors.fill2,
                      ),
                    ),
                  ),
                  const SizedBox(width: IOSSpacing.s8),
                  Text(
                    '已答 ${p.answered}/${p.total}',
                    style: IOSTypography.caption1(color: colors.text3),
                  ),
                ],
              ),
            ],
            const SizedBox(height: IOSSpacing.s4),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton.icon(
                  onPressed: widget.onMemorize,
                  icon: Icon(Icons.style_outlined,
                      size: 18, color: colors.primary),
                  label: Text('背题', style: IOSTypography.callout(color: colors.primary)),
                ),
                const SizedBox(width: IOSSpacing.s4),
                TextButton.icon(
                  onPressed: widget.onPractice,
                  icon: Icon(Icons.play_arrow, size: 18, color: colors.primary),
                  label: Text('刷题', style: IOSTypography.callout(color: colors.primary)),
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
    final colors = IOSColors.of(context);
    final mastered = progress.mastered;
    final color = mastered ? colors.success : IOSSystemColors.orange;
    return Container(
      padding:
          const EdgeInsets.symmetric(horizontal: IOSSpacing.s8, vertical: IOSSpacing.s4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(IOSRadius.tag),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Text(
        mastered ? '已掌握' : '学习中',
        style: IOSTypography.caption2(color: color)
            .copyWith(fontWeight: FontWeight.w700),
      ),
    );
  }
}

/// 通用错误态：图标 + 说明 + 重试按钮（V3 风格）
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
            Icon(Icons.cloud_off_outlined, size: 44, color: colors.danger),
            const SizedBox(height: IOSSpacing.s12),
            Text(
              message,
              textAlign: TextAlign.center,
              style: IOSTypography.body(color: colors.text2),
            ),
            const SizedBox(height: IOSSpacing.s16),
            IOSButton(label: '重试', icon: Icons.refresh, onPressed: onRetry),
          ],
        ),
      ),
    );
  }
}
