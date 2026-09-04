/// 模拟卷列表页（需求：题库含模拟卷可刷 · V3 iOS 风格）
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import '../models/models.dart';
import 'mock_exam_page.dart';
import 'mock_history_page.dart';
import 'composite_loading_page.dart';
import 'app_routes.dart';
import 'responsive.dart';
import 'theme/ios_tokens.dart';
import 'widgets/ios_button.dart';
import 'widgets/ios_card.dart';

class MockExamListPage extends ConsumerStatefulWidget {
  const MockExamListPage({super.key, this.bankId});

  final String? bankId;

  @override
  ConsumerState<MockExamListPage> createState() => _MockExamListPageState();
}

class _MockExamListPageState extends ConsumerState<MockExamListPage> {
  bool _loading = true;
  String? _error;
  List<MockPaper> _papers = const [];
  Map<String, List<MockSession>> _history = const {};

  /// 综合模拟卷（随机组卷，150 分制；不落 mock_papers 表，列表页恒置顶）
  static const _composite = MockPaper(
    id: 'composite',
    bankId: 'composite',
    name: '综合模拟卷',
    durationMin: 180,
    questionIds: [],
  );

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      final papers = await repo.mockPapers(bankId: widget.bankId);
      final history = <String, List<MockSession>>{};
      history['composite'] = await repo.mockSessions(paperId: 'composite');
      for (final p in papers) {
        history[p.id] = await repo.mockSessions(paperId: p.id);
      }
      if (!mounted) return;
      setState(() {
        _papers = papers;
        _history = history;
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
        title: Text('模拟考试',
            style: IOSTypography.title2(color: colors.text)),
        leading: const BackButton(color: IOSSystemColors.blue),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(strokeWidth: 2.5))
          : _error != null
              ? _MockExamStateView(
                  icon: Icons.error_outline,
                  title: '加载失败',
                  message: _error!,
                  actionLabel: '重试',
                  actionIcon: Icons.refresh,
                  onAction: _load,
                )
              : Center(
                  child: ConstrainedBox(
                    constraints:
                        BoxConstraints(maxWidth: effectiveContentWidth(context)),
                    child: ListView.builder(
                      padding: const EdgeInsets.fromLTRB(IOSSpacing.s16,
                          IOSSpacing.s8, IOSSpacing.s16, IOSFloatingBar.kTContentBottomInset),
                      itemCount: _papers.length + 1,
                      itemBuilder: (context, index) {
                        if (index == 0) {
                          // 综合模拟卷：随机组卷入口（恒置顶）
                          final sessions =
                              _history['composite'] ?? const <MockSession>[];
                          return _PaperCard(
                            name: _composite.name,
                            subtitle:
                                '150 分 · 5 科随机组卷 · 限时 180 分钟'
                                '${sessions.isNotEmpty ? ' · 最近 ${sessions.first.score} / 150' : ''}',
                            icon: Icons.auto_awesome,
                            iconColor: colors.primary,
                            onHistory: () =>
                                Navigator.of(context).push(
                                  AppPageRoute(
                                    builder: (_) =>
                                        MockHistoryPage(paper: _composite),
                                  ),
                                ),
                            onTap: () async {
                              await Navigator.of(context).push(
                                AppPageRoute(
                                    builder: (_) =>
                                        const CompositeLoadingPage()),
                              );
                              _load(); // 从考试页返回后刷新历史成绩（缺陷 #1）
                            },
                          );
                        }
                        final p = _papers[index - 1];
                        final sessions =
                            _history[p.id] ?? const <MockSession>[];
                        return _PaperCard(
                          name: p.name,
                          subtitle:
                              '${p.questionIds.length} 题 · 限时 ${p.durationMin} 分钟'
                              '${sessions.isNotEmpty ? ' · 最近 ${sessions.first.score} 分' : ''}',
                          icon: Icons.assignment_outlined,
                          iconColor: IOSSystemColors.purple,
                          onHistory: () => Navigator.of(context).push(
                            AppPageRoute(
                              builder: (_) => MockHistoryPage(paper: p),
                            ),
                          ),
                          onTap: () async {
                            await Navigator.of(context).push(
                              AppPageRoute(builder: (_) => MockExamPage(paper: p)),
                            );
                            _load(); // 从考试页返回后刷新历史成绩（缺陷 #1）
                          },
                        );
                      },
                    ),
                  ),
                ),
    );
  }
}

/// 模拟卷行卡（V3）：统一图标容器 40dp + 题量弱化 + 历史入口
class _PaperCard extends StatelessWidget {
  const _PaperCard({
    required this.name,
    required this.subtitle,
    required this.icon,
    required this.iconColor,
    required this.onHistory,
    required this.onTap,
  });

  final String name;
  final String subtitle;
  final IconData icon;
  final Color iconColor;
  final VoidCallback onHistory;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    return IOSCard(
      padding: EdgeInsets.zero,
      margin: const EdgeInsets.symmetric(vertical: IOSSpacing.s8),
      onTap: onTap,
      child: ListTile(
        contentPadding:
            const EdgeInsets.symmetric(horizontal: IOSSpacing.s16, vertical: IOSSpacing.s4),
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: iconColor.withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(IOSRadius.xs),
          ),
          child: Icon(icon, color: iconColor),
        ),
        title: Text(
          name,
          style: IOSTypography.body(color: colors.text)
              .copyWith(fontWeight: FontWeight.w700),
        ),
        subtitle: Text(
          subtitle,
          style: IOSTypography.caption1(color: colors.text2),
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              icon: Icon(Icons.history, color: colors.text2),
              tooltip: '历史成绩',
              onPressed: onHistory,
            ),
            Icon(Icons.chevron_right, color: colors.text3),
          ],
        ),
      ),
    );
  }
}

/// 模拟卷列表页统一空/错误状态视图（页面内私有组件，V3 风格）
class _MockExamStateView extends StatelessWidget {
  const _MockExamStateView({
    required this.icon,
    required this.title,
    required this.message,
    required this.actionLabel,
    required this.actionIcon,
    required this.onAction,
  });

  final IconData icon;
  final String title;
  final String message;
  final String actionLabel;
  final IconData actionIcon;
  final VoidCallback onAction;

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                color: colors.primaryBg,
                shape: BoxShape.circle,
              ),
              child: Icon(icon, size: 36, color: colors.primary),
            ),
            const SizedBox(height: IOSSpacing.s16),
            Text(
              title,
              textAlign: TextAlign.center,
              style: IOSTypography.title3(color: colors.text)
                  .copyWith(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: IOSSpacing.s8),
            Text(
              message,
              textAlign: TextAlign.center,
              style: IOSTypography.callout(color: colors.text2),
            ),
            const SizedBox(height: IOSSpacing.s24),
            IOSButton(
              label: actionLabel,
              icon: actionIcon,
              onPressed: onAction,
            ),
          ],
        ),
      ),
    );
  }
}
