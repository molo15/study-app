/// 模拟卷列表页（需求：题库含模拟卷可刷）
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import '../models/models.dart';
import 'mock_exam_page.dart';
import 'glass_app_bar.dart';

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
    final theme = Theme.of(context);
    return Scaffold(
      appBar: GlassAppBar(title: const Text('模拟考试')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
          ? _MockExamStateView(
              icon: Icons.error_outline,
              title: '加载失败',
              message: _error!,
              actionLabel: '重试',
              actionIcon: Icons.refresh,
              onAction: _load,
            )
          : _papers.isEmpty
          ? _MockExamStateView(
              icon: Icons.assignment_outlined,
              title: '当前题库暂无模拟卷',
              message: '题库包可包含 mockPapers 字段，暂无可用试卷',
              actionLabel: '重试',
              actionIcon: Icons.refresh,
              onAction: _load,
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _papers.length,
              itemBuilder: (context, index) {
                final p = _papers[index];
                final sessions = _history[p.id] ?? const <MockSession>[];
                return Card(
                  child: ListTile(
                    leading: Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: theme.colorScheme.tertiary.withValues(
                          alpha: 0.12,
                        ),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Icon(
                        Icons.assignment_outlined,
                        color: theme.colorScheme.tertiary,
                      ),
                    ),
                    title: Text(p.name),
                    subtitle: Text(
                      '${p.questionIds.length} 题 · 限时 ${p.durationMin} 分钟'
                      '${sessions.isNotEmpty ? ' · 最近 ${sessions.first.score} 分' : ''}',
                    ),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => MockExamPage(paper: p)),
                    ),
                  ),
                );
              },
            ),
    );
  }
}

/// 模拟卷列表页统一空/错误状态视图（页面内私有组件，设计方案 §3.4 状态机）
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
    final theme = Theme.of(context);
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
                color: theme.colorScheme.primary.withValues(alpha: 0.08),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, size: 36, color: theme.colorScheme.primary),
            ),
            const SizedBox(height: 16),
            Text(
              title,
              textAlign: TextAlign.center,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              message,
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 24),
            FilledButton.tonalIcon(
              style: FilledButton.styleFrom(minimumSize: const Size(0, 48)),
              onPressed: onAction,
              icon: Icon(actionIcon, size: 18),
              label: Text(actionLabel),
            ),
          ],
        ),
      ),
    );
  }
}
