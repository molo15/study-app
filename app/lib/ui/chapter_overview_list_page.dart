/// 章节知识概览列表页（P2 · V3 iOS 风格）
///
/// 题库 → 独立「章节知识概览」入口：列出全库各章的知识概览卡片
/// （章名 + 知识点数 + 题数 + 章节摘要），点击进入单章 ChapterOverviewPage
/// （知识点树 + 直达刷题/背题）。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../data/quiz_repository.dart';
import '../models/models.dart';
import 'responsive.dart';
import 'theme/ios_tokens.dart';
import 'widgets/ios_animated_item.dart';
import 'widgets/ios_card.dart';

class ChapterOverviewListPage extends ConsumerStatefulWidget {
  const ChapterOverviewListPage({
    super.key,
    required this.bankId,
    this.bankName = '',
  });

  final String bankId;
  final String bankName;

  @override
  ConsumerState<ChapterOverviewListPage> createState() =>
      _ChapterOverviewListPageState();
}

class _ChapterOverviewListPageState
    extends ConsumerState<ChapterOverviewListPage> {
  bool _loading = true;
  String? _error;
  List<ChapterOverview> _overviews = const [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      final overviews = await repo.chapterOverviews(widget.bankId);
      if (!mounted) return;
      setState(() {
        _overviews = overviews;
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

  void _openChapter(ChapterOverview ov) {
    context.go('/bank/${widget.bankId}/chapter/${Uri.encodeComponent(ov.chapter)}');
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
        title: Text('章节知识概览',
            style: IOSTypography.title2(color: colors.text)),
        leading: const BackButton(color: IOSSystemColors.blue),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(strokeWidth: 2.5))
          : _error != null
              ? Center(
                  child: Text(_error!,
                      style: IOSTypography.callout(color: colors.danger)),
                )
              : _overviews.isEmpty
                  ? const Center(
                      child: Padding(
                        padding: EdgeInsets.all(32),
                        child: Text('暂无章节概览（需要 v4 题库包）'),
                      ),
                    )
                  : Center(
                      child: ConstrainedBox(
                        constraints: BoxConstraints(
                            maxWidth: effectiveContentWidth(context)),
                        child: ListView(
                          padding: const EdgeInsets.fromLTRB(
                              IOSSpacing.s16,
                              IOSSpacing.s8,
                              IOSSpacing.s16,
                              IOSFloatingBar.kTContentBottomInset),
                          children: [
                            if (isWideScreen(context))
                              // 宽屏（平板/桌面）章节两列（P3 对齐原型 chaps）
                              Wrap(
                                spacing: 12,
                                runSpacing: 12,
                                children: [
                                  for (final entry in _overviews.asMap().entries)
                                    IOSAnimatedItem(
                                      index: entry.key,
                                      child: SizedBox(
                                        width:
                                            (effectiveContentWidth(context) - 32 - 12) / 2,
                                        child: _ChapterOverviewCard(
                                          overview: entry.value,
                                          onTap: () => _openChapter(entry.value),
                                        ),
                                      ),
                                    ),
                                ],
                              )
                            else
                              for (final entry in _overviews.asMap().entries) ...[
                                IOSAnimatedItem(
                                  index: entry.key,
                                  child: _ChapterOverviewCard(
                                      overview: entry.value, onTap: () => _openChapter(entry.value)),
                                ),
                                const SizedBox(height: IOSSpacing.s12),
                              ],
                          ],
                        ),
                      ),
                    ),
    );
  }
}

/// 单章概览卡片：章名 + 知识点数/题数 + 摘要
class _ChapterOverviewCard extends StatelessWidget {
  const _ChapterOverviewCard({required this.overview, required this.onTap});

  final ChapterOverview overview;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    return IOSCard(
      padding: const EdgeInsets.all(IOSSpacing.s16),
      onTap: onTap,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(IOSSpacing.s8),
            decoration: BoxDecoration(
              color: colors.primaryBg,
              borderRadius: BorderRadius.circular(IOSRadius.xs),
            ),
            child: Icon(
              Icons.account_tree_outlined,
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
                  overview.chapter,
                  style: IOSTypography.body(color: colors.text)
                      .copyWith(fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: IOSSpacing.s4),
                Text(
                  '${overview.knowledgeCount} 个知识点 · ${overview.questionCount} 题',
                  style: IOSTypography.caption1(color: colors.primary),
                ),
                if (overview.summary.isNotEmpty) ...[
                  const SizedBox(height: IOSSpacing.s4),
                  Text(
                    overview.summary,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: IOSTypography.caption1(color: colors.text3)
                        .copyWith(height: 1.4),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(width: IOSSpacing.s8),
          Icon(Icons.chevron_right, color: colors.text3),
        ],
      ),
    );
  }
}
