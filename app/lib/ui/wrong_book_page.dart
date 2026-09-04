/// 错题本：答错自动归集，支持整批重刷与手动移出（设计方案 §3.5 · V3 iOS 风格）
///
/// 改版（阶段 B + V3）：
/// - 统一空态/错误态（图标 + 说明 + 可选行动），错误态提供重试；
/// - 列表行视觉与首页/题库保持一致（图标容器 40dp、题量弱化）；
/// - 不改错题归集/移出逻辑、不改 PracticePage 打开方式。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import '../models/models.dart';
import 'practice_page.dart';
import 'app_routes.dart';
import 'responsive.dart';
import 'theme/ios_tokens.dart';
import 'widgets/ios_animated_item.dart';
import 'widgets/ios_button.dart';
import 'widgets/ios_card.dart';

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
    final colors = IOSColors.of(context);
    return Scaffold(
      backgroundColor: colors.bg,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        title: Text('错题本', style: IOSTypography.title2(color: colors.text)),
        leading: const BackButton(color: IOSSystemColors.blue),
      ),
      body: _buildBody(colors),
    );
  }

  Widget _buildBody(IOSColorScheme colors) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator(strokeWidth: 2.5));
    }
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
                  color: colors.primaryBg,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.task_alt,
                  size: 44,
                  color: colors.primary,
                ),
              ),
              const SizedBox(height: IOSSpacing.s16),
              Text('暂无错题', style: IOSTypography.title3(color: colors.text)),
              const SizedBox(height: IOSSpacing.s4),
              Text(
                '答错的题目会自动归集到这里，继续保持！',
                textAlign: TextAlign.center,
                style: IOSTypography.callout(color: colors.text2),
              ),
              const SizedBox(height: IOSSpacing.s20),
              IOSButton(
                type: IOSButtonType.text,
                label: '返回首页',
                icon: Icons.arrow_back,
                onPressed: () => Navigator.of(context).pop(),
              ),
            ],
          ),
        ),
      );
    }
    return Column(
      children: [
        Expanded(
          child: Center(
            child: ConstrainedBox(
              constraints:
                  BoxConstraints(maxWidth: effectiveContentWidth(context)),
              child: ListView.builder(
                padding: const EdgeInsets.fromLTRB(
                    IOSSpacing.s16, IOSSpacing.s8, IOSSpacing.s16,
                    IOSSpacing.s8),
                itemCount: _questions.length,
                itemBuilder: (context, index) {
                  final q = _questions[index];
                  return IOSAnimatedItem(
                    index: index,
                    child: IOSCard(
                    padding: EdgeInsets.zero,
                    margin: const EdgeInsets.symmetric(vertical: IOSSpacing.s8),
                    child: ListTile(
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: IOSSpacing.s16,
                        vertical: IOSSpacing.s4,
                      ),
                      leading: Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          color: colors.dangerBg,
                          borderRadius: BorderRadius.circular(IOSRadius.xs),
                        ),
                        child: Icon(
                          Icons.error_outline,
                          color: colors.danger,
                          size: 22,
                        ),
                      ),
                      title: Text(
                        q.stem,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: IOSTypography.body(color: colors.text),
                      ),
                      subtitle: Text(
                        '${_bankNames[q.bankId] ?? q.bankId} · ${q.chapter} · ${typeLabel(q.type)}',
                        style: IOSTypography.caption1(color: colors.text2),
                      ),
                      trailing: IconButton(
                        icon: Icon(Icons.delete_outline, color: colors.text2),
                        tooltip: '移出错题本',
                        onPressed: () => _remove(q.id),
                      ),
                      onTap: _openPractice,
                    ),
                  ),
                );
                },
              ),
            ),
          ),
        ),
        SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(IOSSpacing.s16),
            child: SizedBox(
              width: double.infinity,
              child: IOSButton(
                label: '错题重刷（${_questions.length}）',
                icon: Icons.replay,
                onPressed: _openPractice,
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
    final colors = IOSColors.of(context);
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.cloud_off_outlined,
              size: 44,
              color: colors.danger,
            ),
            const SizedBox(height: IOSSpacing.s12),
            Text(
              message,
              textAlign: TextAlign.center,
              style: IOSTypography.body(color: colors.text2),
            ),
            const SizedBox(height: IOSSpacing.s16),
            IOSButton(label: '重试', icon: Icons.refresh, onPressed: onRetry),
          ],
        ),
      ),
    );
  }
}
