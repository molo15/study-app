/// 模拟卷 · 历史成绩页
///
/// 展示某卷历次成绩（次数/最高/平均），点击某次进入该次逐题解析
/// （从 answer_logs 恢复题目与作答，支持历史成绩二次回看）。
library;

import 'package:flutter/material.dart';
import 'widgets/app_card.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import '../models/models.dart';
import 'mock_review_page.dart';
import 'glass_app_bar.dart';
import 'app_routes.dart';

class MockHistoryPage extends ConsumerStatefulWidget {
  const MockHistoryPage({super.key, required this.paper});

  final MockPaper paper;

  @override
  ConsumerState<MockHistoryPage> createState() => _MockHistoryPageState();
}

class _MockHistoryPageState extends ConsumerState<MockHistoryPage> {
  bool _loading = true;
  String? _error;
  List<MockSession> _sessions = const [];

  /// 满分：综合卷 150，单科卷 100
  bool get _isComposite => widget.paper.id == 'composite';
  int get _full => _isComposite ? 150 : 100;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      final sessions = await repo.mockSessions(paperId: widget.paper.id);
      if (!mounted) return;
      setState(() {
        _sessions = sessions;
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

  String _fmtTime(int ms) {
    final t = DateTime.fromMillisecondsSinceEpoch(ms);
    final hh = t.hour.toString().padLeft(2, '0');
    final mm = t.minute.toString().padLeft(2, '0');
    return '${t.month}-${t.day} $hh:$mm';
  }

  Future<void> _openReview(MockSession session) async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      final data = await repo.mockSessionReview(session.id!);
      if (!mounted) return;
      Navigator.of(context).push(
        AppPageRoute(
          builder: (_) => MockReviewPage(
            questions: data.questions,
            answers: data.answers,
          ),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('加载该次解析失败：$e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: GlassAppBar(title: Text('${widget.paper.name} · 历史成绩')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
          ? Center(child: Text(_error!))
          : _sessions.isEmpty
          ? Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.history,
                    size: 56,
                    color: theme.colorScheme.outline,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    '暂无成绩记录',
                    style: theme.textTheme.bodyLarge?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '完成一次模拟考后会显示在这里',
                    style: theme.textTheme.bodySmall,
                  ),
                ],
              ),
            )
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                _StatsCard(sessions: _sessions, full: _full),
                const SizedBox(height: 16),
                for (final s in _sessions)
                  AppCard(padding: EdgeInsets.zero, margin: const EdgeInsets.only(bottom: 8),
                    child: ListTile(
                      leading: Container(
                        width: 52,
                        height: 52,
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                          color: theme.colorScheme.primary.withValues(
                            alpha: 0.10,
                          ),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              '${s.score}',
                              style: theme.textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.w800,
                                color: theme.colorScheme.primary,
                              ),
                            ),
                            Text(
                              '/ $_full',
                              style: theme.textTheme.labelSmall?.copyWith(
                                color: theme.colorScheme.outline,
                              ),
                            ),
                          ],
                        ),
                      ),
                      title: Text(
                        '正确 ${s.correct} · 部分 ${s.partial} · 错误 ${s.wrong} · 未答 ${s.skipped}',
                        style: theme.textTheme.bodyMedium,
                      ),
                      subtitle: Text(
                        '${_fmtTime(s.submittedAt)} · 用时 ${s.durationMin} 分钟',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.outline,
                        ),
                      ),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () => _openReview(s),
                    ),
                  ),
              ],
            ),
    );
  }
}

/// 顶部统计卡：次数 / 最高 / 平均（按满分显示）
class _StatsCard extends StatelessWidget {
  const _StatsCard({required this.sessions, required this.full});

  final List<MockSession> sessions;
  final int full;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scores = sessions.map((s) => s.score).toList()..sort();
    final best = scores.isEmpty ? 0 : scores.last;
    final avg = scores.isEmpty
        ? 0
        : (scores.reduce((a, b) => a + b) / scores.length).round();
    Widget cell(String label, String value) => Expanded(
          child: Column(
            children: [
              Text(
                value,
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w800,
                  color: theme.colorScheme.primary,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                label,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
        );
    return AppCard(padding: EdgeInsets.zero, margin: const EdgeInsets.symmetric(vertical: 6), 
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 16),
        child: Row(
          children: [
            cell('次数', '${sessions.length}'),
            cell('最高分', '$best'),
            cell('平均分', '$avg / $full'),
          ],
        ),
      ),
    );
  }
}
