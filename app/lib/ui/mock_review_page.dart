/// 模拟卷 · 逐题解析回顾页
///
/// 交卷后进入：逐题列出题干、我的作答、正确要点与对错，用于复盘
/// （尤其简答/填空）。判分与交卷一致（grading.gradeQuestion），
/// 支持综合卷（150 分制）与单科固定卷。
/// 顶部可在「全部 / 只看错题」间切换，聚焦本次错题专项复习。
library;

import 'package:flutter/material.dart';

import '../data/grading.dart';
import '../models/models.dart';
import 'practice_page.dart' show typeColor, typeLabel;
import 'glass_app_bar.dart';

/// 题库 id → 学科名（综合卷跨科标签用）
String mockBankLabel(String bankId) {
  switch (bankId) {
    case 'bank-xiandai-hanyu':
      return '现代汉语';
    case 'bank-gudai-hanyu':
      return '古代汉语';
    case 'bank-zhongguo-xiandai-wenxue':
      return '现代文学史';
    case 'bank-zhongguo-dangdai-wenxue':
      return '当代文学史';
    case 'bank-zhongguo-gudai-wenxue':
      return '古代文学史';
    default:
      return '';
  }
}

class MockReviewPage extends StatefulWidget {
  const MockReviewPage({
    super.key,
    required this.questions,
    required this.answers,
    this.onlyWrong = false,
  });

  final List<Question> questions;
  final Map<String, Set<String>> answers;

  /// 初始是否只看错题（历史成绩入口可传入）
  final bool onlyWrong;

  @override
  State<MockReviewPage> createState() => _MockReviewPageState();
}

class _MockReviewPageState extends State<MockReviewPage> {
  late bool _onlyWrong = widget.onlyWrong;

  Grade _gradeOf(Question q) =>
      gradeQuestion(q, widget.answers[q.id] ?? const <String>{});

  /// 我的作答文本（选择题转选项文本；填空/简答为原文）
  String _myAnswer(Question q) {
    final set = widget.answers[q.id] ?? const <String>{};
    if (set.isEmpty) return '（未作答）';
    final isChoice =
        q.type == QuestionType.singleChoice ||
        q.type == QuestionType.multiChoice ||
        q.type == QuestionType.trueFalse;
    if (!isChoice) return set.first;
    return set.map((k) {
      final opt = q.options.where((o) => o.key == k).toList();
      return opt.isNotEmpty ? '${opt.first.key}. ${opt.first.text}' : k;
    }).join('、');
  }

  /// 正确答案文本（选择题转选项文本；填空/简答为参考要点）
  String _correctAnswer(Question q) {
    final isChoice =
        q.type == QuestionType.singleChoice ||
        q.type == QuestionType.multiChoice ||
        q.type == QuestionType.trueFalse;
    if (isChoice) {
      return q.answer
          .map((k) {
            final opt = q.options.where((o) => o.key == k).toList();
            return opt.isNotEmpty ? '${opt.first.key}. ${opt.first.text}' : k;
          })
          .join('、');
    }
    return q.answer.join('；');
  }

  List<Question> get _shown =>
      _onlyWrong
          ? widget.questions.where((q) => _gradeOf(q) == Grade.wrong).toList()
          : widget.questions;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final shown = _shown;
    // 统计
    var correct = 0, partial = 0, wrong = 0, skip = 0;
    for (final q in widget.questions) {
      switch (_gradeOf(q)) {
        case Grade.correct:
          correct++;
        case Grade.partial:
          partial++;
        case Grade.wrong:
          wrong++;
        case Grade.skip:
          skip++;
      }
    }
    return Scaffold(
      appBar: GlassAppBar(title: const Text('逐题解析')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    '正确 $correct · 部分 $partial · 错误 $wrong · 未答 $skip',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
                // 全部 / 只看错题 切换（步骤3：本次错题专项复习）
                TextButton(
                  onPressed: () => setState(() => _onlyWrong = !_onlyWrong),
                  child: Text(_onlyWrong ? '全部' : '只看错题'),
                ),
              ],
            ),
          ),
          const Divider(height: 1),
          if (shown.isEmpty)
            Expanded(
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.check_circle_outline,
                      size: 56,
                      color: Colors.green.shade400,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      _onlyWrong ? '本次没有错题' : '暂无题目',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _onlyWrong ? '继续保持！' : '',
                      style: theme.textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
            )
          else
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: shown.length,
                itemBuilder: (context, index) {
                  final q = shown[index];
                  final grade = _gradeOf(q);
                  final (label, color) = switch (grade) {
                    Grade.correct => ('对', Colors.green),
                    Grade.partial => ('部分', Colors.orange),
                    Grade.wrong => ('错', Colors.red),
                    Grade.skip => ('未答', theme.colorScheme.outline),
                  };
                  final bank = mockBankLabel(q.bankId);
                  return Card(
                    margin: const EdgeInsets.only(bottom: 8),
                    child: ListTile(
                      leading: Container(
                        width: 40,
                        height: 40,
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                          color: color.withValues(alpha: 0.12),
                          shape: BoxShape.circle,
                        ),
                        child: Text(
                          label,
                          style: TextStyle(
                            color: color,
                            fontWeight: FontWeight.w700,
                            fontSize: 13,
                          ),
                        ),
                      ),
                      title: Text(
                        '${index + 1}. ${q.stem}',
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.bodyMedium,
                      ),
                      subtitle: Text(
                        '${typeLabel(q.type)}'
                        '${bank.isNotEmpty ? ' · $bank' : ''}'
                        '${q.chapter.isNotEmpty ? ' · ${q.chapter}' : ''}',
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.outline,
                        ),
                      ),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () => _showDetail(context, index),
                    ),
                  );
                },
              ),
            ),
        ],
      ),
    );
  }

  void _showDetail(BuildContext context, int index) {
    final q = _shown[index];
    final theme = Theme.of(context);
    final grade = _gradeOf(q);
    final (label, color) = switch (grade) {
      Grade.correct => ('正确', Colors.green),
      Grade.partial => ('部分正确', Colors.orange),
      Grade.wrong => ('错误', Colors.red),
      Grade.skip => ('未作答', theme.colorScheme.outline),
    };
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (ctx) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        maxChildSize: 0.92,
        minChildSize: 0.4,
        expand: false,
        builder: (ctx, scrollController) => SingleChildScrollView(
          controller: scrollController,
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: color.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      '第 ${index + 1} 题 · $label',
                      style: TextStyle(
                        color: color,
                        fontWeight: FontWeight.w700,
                        fontSize: 13,
                      ),
                    ),
                  ),
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: typeColor(context, q.type).withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      typeLabel(q.type),
                      style: TextStyle(
                        color: typeColor(context, q.type),
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Text(
                q.stem,
                style: theme.textTheme.titleMedium?.copyWith(height: 1.6),
              ),
              const SizedBox(height: 20),
              _DetailBlock(
                title: '我的答案',
                content: _myAnswer(q),
                color: theme.colorScheme.primary,
              ),
              const SizedBox(height: 12),
              _DetailBlock(
                title: '参考要点',
                content: _correctAnswer(q),
                color: Colors.green.shade700,
              ),
              if (q.explanation.isNotEmpty) ...[
                const SizedBox(height: 12),
                _DetailBlock(
                  title: '解析',
                  content: q.explanation,
                  color: theme.colorScheme.tertiary,
                ),
              ],
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: FilledButton.tonal(
                  onPressed: () => Navigator.pop(ctx),
                  child: const Text('关闭'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _DetailBlock extends StatelessWidget {
  const _DetailBlock({
    required this.title,
    required this.content,
    required this.color,
  });

  final String title;
  final String content;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.07),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.25)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: theme.textTheme.labelLarge?.copyWith(
              color: color,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 8),
          Text(content, style: theme.textTheme.bodyMedium?.copyWith(height: 1.5)),
        ],
      ),
    );
  }
}
