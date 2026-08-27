part of 'practice_page.dart';

class _SummaryView extends StatelessWidget {
  const _SummaryView({
    required this.total,
    required this.correct,
    required this.partial,
    required this.onFinish,
    required this.onReview,
  });

  final int total;
  final int correct;
  final int partial;
  final VoidCallback onFinish;

  /// 打开答题卡做整轮回顾（设计：完成页复用同一组件）
  final VoidCallback onReview;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final rate = total == 0 ? 0.0 : correct / total * 100;
    return Scaffold(
      appBar: GlassAppBar(title: const Text('刷题完成')),
      body: Center(
        // SingleChildScrollView：防止小屏/横屏/大字体溢出（设计方案 §8）
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // 环形正确率
              SizedBox(
                width: 140,
                height: 140,
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    CircularProgressIndicator(
                      value: rate / 100,
                      strokeWidth: 12,
                      backgroundColor:
                          theme.colorScheme.surfaceContainerHighest,
                    ),
                    Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            '${rate.toStringAsFixed(0)}%',
                            style: theme.textTheme.headlineMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: theme.colorScheme.primary,
                            ),
                          ),
                          Text('正确率', style: theme.textTheme.bodySmall),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),
              Text(
                '共 $total 题 · 正确 $correct · 部分正确 $partial',
                style: theme.textTheme.bodyLarge,
              ),
              const SizedBox(height: 32),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  OutlinedButton.icon(
                    onPressed: onReview,
                    icon: const Icon(Icons.grid_view_outlined, size: 18),
                    label: const Text('查看答题卡'),
                  ),
                  const SizedBox(width: 12),
                  FilledButton(onPressed: onFinish, child: const Text('完成')),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// 刷题页统一空/错误状态视图（页面内私有组件，设计方案 §3.4 状态机）
class _PracticeStateView extends StatelessWidget {
  const _PracticeStateView({
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

/// 审题标记备注对话框（v7）：用户标记"待修改"时可附一句说明
