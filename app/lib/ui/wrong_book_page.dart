/// 错题本：答错自动归集，支持整批重刷与手动移出（设计方案 §3.5）
///
/// 改版（阶段 B）：
/// - 统一空态/错误态（图标 + 说明 + 可选行动），错误态提供重试；
/// - 列表行视觉与首页/题库保持一致（图标容器 40dp、题量弱化）；
/// - 不改错题归集/移出逻辑、不改 PracticePage 打开方式。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import '../models/models.dart';
import 'practice_page.dart';
import 'glass_app_bar.dart';
import 'app_routes.dart';

class WrongBookPage extends ConsumerStatefulWidget {
  const WrongBookPage({super.key, this.bankId});

  /// 按题库过滤（null = 全部，多题库需求）
  final String? bankId;

  @override
  ConsumerState<WrongBookPage> createState() => _WrongBookPageState();
}

class _WrongBookPageState extends ConsumerState<WrongBookPage> {
  bool _loading = true;
  List<Question> _questions = const [];
  Map<String, String> _bankNames = const {};
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      final questions = await repo.wrongBookQuestions(bankId: widget.bankId);
      final bankNames = await repo.bankNameMap();
      if (!mounted) return;
      setState(() {
        _questions = questions;
        _bankNames = bankNames;
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

  Future<void> _remove(String id) async {
    final repo = await ref.read(quizRepositoryProvider);
    await repo.removeFromWrongBook(id);
    if (!mounted) return; // 审查 P1-2：页面可能已被 pop
    setState(() {
      _questions = _questions.where((q) => q.id != id).toList();
    });
  }

  Future<void> _openPractice() async {
    await Navigator.of(context).push(
      AppPageRoute(
        builder: (_) => PracticePage(
          mode: PracticeMode.wrongRework,
          bankId: widget.bankId, // 审查 P1-1：错题重刷按当前库过滤
        ),
      ),
    );
    _load();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: GlassAppBar(title: const Text('错题本')),
      body: _buildBody(theme),
    );
  }

  Widget _buildBody(ThemeData theme) {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_error != null) {
      return _ErrorView(
        message: _error!,
        onRetry: () {
          setState(() {
            _loading = true;
            _error = null;
          });
          _load();
        },
      );
    }
    if (_questions.isEmpty) {
      // 空态：图标 + 说明 + 可选行动
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 88,
                height: 88,
                decoration: BoxDecoration(
                  color: theme.colorScheme.primary.withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.task_alt,
                  size: 44,
                  color: theme.colorScheme.primary,
                ),
              ),
              const SizedBox(height: 16),
              Text('暂无错题', style: theme.textTheme.titleMedium),
              const SizedBox(height: 4),
              Text(
                '答错的题目会自动归集到这里，继续保持！',
                textAlign: TextAlign.center,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 20),
              OutlinedButton.icon(
                onPressed: () => Navigator.of(context).pop(),
                icon: const Icon(Icons.arrow_back),
                label: const Text('返回首页'),
              ),
            ],
          ),
        ),
      );
    }
    return Column(
      children: [
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: _questions.length,
            itemBuilder: (context, index) {
              final q = _questions[index];
              return Card(
                child: ListTile(
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 4,
                  ),
                  leading: Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: theme.colorScheme.error.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(
                      Icons.error_outline,
                      color: theme.colorScheme.error,
                      size: 22,
                    ),
                  ),
                  title: Text(
                    q.stem,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  subtitle: Text(
                    '${_bankNames[q.bankId] ?? q.bankId} · ${q.chapter} · ${typeLabel(q.type)}',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                  trailing: IconButton(
                    icon: const Icon(Icons.delete_outline),
                    tooltip: '移出错题本',
                    onPressed: () => _remove(q.id),
                  ),
                  onTap: _openPractice,
                ),
              );
            },
          ),
        ),
        SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                onPressed: _openPractice,
                icon: const Icon(Icons.replay),
                label: Text('错题重刷（${_questions.length}）'),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

/// 通用错误态：图标 + 说明 + 重试按钮（页面内私有组件）
class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.cloud_off_outlined,
              size: 44,
              color: theme.colorScheme.error,
            ),
            const SizedBox(height: 12),
            Text(
              message,
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
            FilledButton.tonalIcon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh),
              label: const Text('重试'),
            ),
          ],
        ),
      ),
    );
  }
}
