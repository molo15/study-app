/// 模拟卷 · 历史成绩页（V3 iOS 风格）
///
/// 展示某卷历次成绩（次数/最高/平均），点击某次进入该次逐题解析
/// （从 answer_logs 恢复题目与作答，支持历史成绩二次回看）。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import '../models/models.dart';
import 'mock_review_page.dart';
import 'app_routes.dart';
import 'responsive.dart';
import 'theme/ios_tokens.dart';
import 'widgets/ios_animated_item.dart';
import 'widgets/ios_card.dart';

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
    final colors = IOSColors.of(context);
    return Scaffold(
      backgroundColor: colors.bg,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        title: Text('${widget.paper.name} · 历史成绩',
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
              : _sessions.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.history,
                            size: 56,
                            color: colors.text3,
                          ),
                          const SizedBox(height: IOSSpacing.s12),
                          Text(
                            '暂无成绩记录',
                            style: IOSTypography.body(color: colors.text2),
                          ),
                          const SizedBox(height: IOSSpacing.s8),
                          Text(
                            '完成一次模拟考后会显示在这里',
                            style: IOSTypography.caption1(color: colors.text3),
                          ),
                        ],
                      ),
                    )
                  : Center(
                      child: ConstrainedBox(
                        constraints: BoxConstraints(
                            maxWidth: effectiveContentWidth(context)),
                        child: ListView(
                          padding: const EdgeInsets.fromLTRB(
                              IOSSpacing.s16, IOSSpacing.s8, IOSSpacing.s16,
                              IOSFloatingBar.kTContentBottomInset),
                          children: [
                            _StatsCard(sessions: _sessions, full: _full),
                            const SizedBox(height: IOSSpacing.s16),
                            for (final entry in _sessions.asMap().entries)
                              IOSAnimatedItem(
                                index: entry.key,
                                child: _SessionCard(
                                  session: entry.value,
                                  full: _full,
                                  timeText:
                                      '${_fmtTime(entry.value.submittedAt)} · 用时 ${entry.value.durationMin} 分钟',
                                  onTap: () => _openReview(entry.value),
                                ),
                              ),
                          ],
                        ),
                      ),
                    ),
    );
  }
}

/// 历次成绩行卡（V3）：分数容器 52dp + 明细弱化
class _SessionCard extends StatelessWidget {
  const _SessionCard({
    required this.session,
    required this.full,
    required this.timeText,
    required this.onTap,
  });

  final MockSession session;
  final int full;
  final String timeText;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    return IOSCard(
      padding: EdgeInsets.zero,
      margin: const EdgeInsets.only(bottom: IOSSpacing.s8),
      onTap: onTap,
      child: ListTile(
        leading: Container(
          width: 52,
          height: 52,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: colors.primaryBg,
            borderRadius: BorderRadius.circular(IOSRadius.md),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                '${session.score}',
                style: IOSTypography.title3(color: colors.primary)
                    .copyWith(fontWeight: FontWeight.w800),
              ),
              Text(
                '/ $full',
                style: IOSTypography.caption2(color: colors.text3),
              ),
            ],
          ),
        ),
        title: Text(
          '正确 ${session.correct} · 部分 ${session.partial} · 错误 ${session.wrong} · 未答 ${session.skipped}',
          style: IOSTypography.body(color: colors.text),
        ),
        subtitle: Text(
          timeText,
          style: IOSTypography.caption1(color: colors.text2),
        ),
        trailing: Icon(Icons.chevron_right, color: colors.text3),
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
    final colors = IOSColors.of(context);
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
                style: IOSTypography.title2(color: colors.primary)
                    .copyWith(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: IOSSpacing.s4),
              Text(
                label,
                style: IOSTypography.caption1(color: colors.text2),
              ),
            ],
          ),
        );
    return IOSCard(
      padding: const EdgeInsets.symmetric(vertical: IOSSpacing.s16),
      child: Row(
        children: [
          cell('次数', '${sessions.length}'),
          cell('最高分', '$best'),
          cell('平均分', '$avg / $full'),
        ],
      ),
    );
  }
}
