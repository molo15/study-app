/// 通用状态视图：统一「加载中 / 出错 / 空数据」三种页面状态（需求：统一状态反馈）
///
/// 提供三种静态构造：
/// - [AppStateView.loading]：加载中，居中圆形进度指示器；
/// - [AppStateView.error]：出错，图标 + 说明 + 重试按钮（[onRetry] 为空时不显示按钮）；
/// - [AppStateView.empty]：空数据，图标 + 标题 + 说明 + 可选行动按钮。
///
/// 使用 Material 3 组件（CircularProgressIndicator / FilledButton 等）实现，
/// 颜色取自 ColorScheme 语义色，浅色 / 深色模式自动适配，无需额外传色。
///
/// 用法：
/// ```dart
/// AppStateView.loading()
/// AppStateView.error(message: '题库加载失败', onRetry: _reload)
/// AppStateView.empty(
///   icon: Icons.inbox_outlined,
///   title: '暂无错题',
///   message: '做错的题目会自动收集到这里',
///   actionLabel: '去刷题',
///   onAction: _goPractice,
/// )
/// ```
library;

import 'package:flutter/material.dart';

import '../theme_controller.dart' show AppSpacing;

class AppStateView extends StatelessWidget {
  /// 加载中：居中圆形进度指示器
  const AppStateView.loading({super.key})
    : _isLoading = true,
      _isError = false,
      _icon = null,
      _title = null,
      _message = null,
      _actionLabel = null,
      _onAction = null,
      _onRetry = null;

  /// 出错：图标 + 说明 + 重试按钮（[onRetry] 为空时只展示说明，不显示按钮）
  const AppStateView.error({super.key, required this._message, this._onRetry})
    : _isLoading = false,
      _isError = true,
      _icon = null,
      _title = null,
      _actionLabel = null,
      _onAction = null;

  /// 空数据：图标 + 标题 + 说明 + 可选行动按钮
  /// （[actionLabel] 与 [onAction] 同时提供时显示行动按钮）
  const AppStateView.empty({
    super.key,
    required this._icon,
    required this._title,
    this._message,
    this._actionLabel,
    this._onAction,
  }) : _isLoading = false,
       _isError = false,
       _onRetry = null;

  final bool _isLoading;
  final bool _isError;
  final IconData? _icon;
  final String? _title;
  final String? _message;
  final String? _actionLabel;
  final VoidCallback? _onAction;
  final VoidCallback? _onRetry;

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;

    // 错误态固定：出错图标 + 标题 + 重试按钮；空态按传入参数展示
    final String title;
    final IconData icon;
    final Color iconColor;
    final String? buttonLabel;
    final VoidCallback? onPressed;
    if (_isError) {
      title = '出错了';
      icon = Icons.error_outline;
      iconColor = colorScheme.error;
      buttonLabel = '重试';
      onPressed = _onRetry;
    } else {
      title = _title ?? '';
      icon = _icon ?? Icons.inbox_outlined;
      iconColor = colorScheme.onSurfaceVariant;
      buttonLabel = _actionLabel;
      onPressed = _onAction;
    }
    final message = _message;

    return Center(
      // 内容过长时可滚动，避免小屏 / 大字体下溢出（需求：320dp 无横向溢出）
      child: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.space8,
          vertical: AppSpacing.space8,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 56, color: iconColor),
            const SizedBox(height: AppSpacing.space4),
            Text(
              title,
              textAlign: TextAlign.center,
              style: textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
                height: 1.3,
              ),
            ),
            if (message != null && message.isNotEmpty) ...[
              const SizedBox(height: AppSpacing.space2),
              Text(
                message,
                textAlign: TextAlign.center,
                style: textTheme.bodyMedium?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                  height: 1.5,
                ),
              ),
            ],
            if (buttonLabel != null && onPressed != null) ...[
              const SizedBox(height: AppSpacing.space6),
              if (_isError)
                FilledButton.tonalIcon(
                  onPressed: onPressed,
                  icon: const Icon(Icons.refresh),
                  label: Text(buttonLabel),
                )
              else
                FilledButton.tonal(
                  onPressed: onPressed,
                  child: Text(buttonLabel),
                ),
            ],
          ],
        ),
      ),
    );
  }
}
