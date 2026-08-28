/// 综合模拟卷 · 排题中页面
///
/// 进入综合卷时先展示「正在排题中」过渡页，后台按学科权重×题型从 5 科
/// 随机抽题（综合卷 150 分制），完成后自动进入考试页。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import '../models/models.dart';
import 'mock_exam_page.dart';
import 'glass_app_bar.dart';
import 'app_routes.dart';

class CompositeLoadingPage extends ConsumerStatefulWidget {
  const CompositeLoadingPage({super.key});

  @override
  ConsumerState<CompositeLoadingPage> createState() =>
      _CompositeLoadingPageState();
}

class _CompositeLoadingPageState extends ConsumerState<CompositeLoadingPage>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 1200),
  )..repeat();

  String? _error;

  @override
  void initState() {
    super.initState();
    _compose();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _compose() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      // 并行：抽题 + 保证过渡页至少可见一小段（避免毫秒级跳闪）
      final results = await Future.wait<Object?>([
        repo.generateCompositePaper(),
        Future<void>.delayed(const Duration(milliseconds: 900)),
      ]);
      final questions = results.first as List<Question>;
      if (!mounted) return;
      final paper = MockPaper(
        id: 'composite',
        bankId: 'composite',
        name: '综合模拟卷',
        durationMin: 180,
        questionIds: const [],
      );
      Navigator.of(context).pushReplacement(
        AppPageRoute(
          builder: (_) => MockExamPage(
            paper: paper,
            presetQuestions: questions,
            pointsByType: QuizRepository.compositePoints,
          ),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = '排题失败：$e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: GlassAppBar(title: const Text('综合模拟卷')),
      body: _error != null
          ? Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.error_outline,
                      size: 48,
                      color: theme.colorScheme.error,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      _error!,
                      textAlign: TextAlign.center,
                      style: theme.textTheme.bodyMedium,
                    ),
                    const SizedBox(height: 24),
                    FilledButton.tonalIcon(
                      onPressed: () {
                        setState(() => _error = null);
                        _compose();
                      },
                      icon: const Icon(Icons.refresh),
                      label: const Text('重试'),
                    ),
                  ],
                ),
              ),
            )
          : Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // 旋转抽题动画
                  AnimatedBuilder(
                    animation: _controller,
                    builder: (_, child) => Transform.rotate(
                      angle: _controller.value * 2 * 3.1415927,
                      child: child,
                    ),
                    child: Icon(
                      Icons.auto_awesome,
                      size: 56,
                      color: theme.colorScheme.primary,
                    ),
                  ),
                  const SizedBox(height: 24),
                  Text(
                    '正在排题中…',
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '正在从现代汉语、古代汉语与文学史题库随机抽取',
                    textAlign: TextAlign.center,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(height: 32),
                  const SizedBox(
                    width: 220,
                    child: LinearProgressIndicator(),
                  ),
                  const SizedBox(height: 24),
                  Text(
                    '本次共 68 题 · 满分 150 分 · 限时 180 分钟',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.outline,
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
