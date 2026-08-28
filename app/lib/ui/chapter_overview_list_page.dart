/// 章节知识概览列表页（P2）
///
/// 题库 → 独立「章节知识概览」入口：列出全库各章的知识概览卡片
/// （章名 + 知识点数 + 题数 + 章节摘要），点击进入单章 ChapterOverviewPage
/// （知识点树 + 直达刷题/背题）。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import '../models/models.dart';
import 'chapter_overview_page.dart';
import 'glass_app_bar.dart';
import 'app_routes.dart';

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
    Navigator.of(context).push(
      AppPageRoute(
        builder: (_) => ChapterOverviewPage(
          bankId: widget.bankId,
          chapter: ov.chapter,
          bankName: widget.bankName,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: GlassAppBar(title: const Text('章节知识概览'), centerTitle: true),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : _overviews.isEmpty
                  ? const Center(
                      child: Padding(
                        padding: EdgeInsets.all(32),
                        child: Text('暂无章节概览（需要 v4 题库包）'),
                      ),
                    )
                  : ListView(
                      padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
                      children: [
                        for (final ov in _overviews) ...[
                          _ChapterOverviewCard(overview: ov, onTap: () => _openChapter(ov)),
                          const SizedBox(height: 10),
                        ],
                      ],
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
    final theme = Theme.of(context);
    return Card(
      margin: EdgeInsets.zero,
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: theme.colorScheme.primaryContainer.withValues(alpha: 0.5),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(
                  Icons.account_tree_outlined,
                  color: theme.colorScheme.primary,
                  size: 22,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      overview.chapter,
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${overview.knowledgeCount} 个知识点 · ${overview.questionCount} 题',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.primary,
                      ),
                    ),
                    if (overview.summary.isNotEmpty) ...[
                      const SizedBox(height: 6),
                      Text(
                        overview.summary,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.outline,
                          height: 1.4,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(width: 8),
              Icon(
                Icons.chevron_right,
                color: theme.colorScheme.outline,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
