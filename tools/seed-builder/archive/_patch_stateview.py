# -*- coding: utf-8 -*-
f = r'D:\study_app\app\lib\ui\widgets\app_state_view.dart'
s = open(f, encoding='utf-8').read()

old1 = """  /// 出错：图标 + 说明 + 重试按钮（[onRetry] 为空时只展示说明，不显示按钮）
  const AppStateView.error({super.key, required this._message, this._onRetry})
    : _isLoading = false,
      _isError = true,
      _icon = null,
      _title = null,
      _actionLabel = null,
      _onAction = null;"""
new1 = """  /// 出错：图标 + 说明 + 重试按钮（[onRetry] 为空时只展示说明，不显示按钮）
  const AppStateView.error({
    super.key,
    required String message,
    VoidCallback? onRetry,
  }) : _message = message,
       _onRetry = onRetry,
       _isLoading = false,
       _isError = true,
       _icon = null,
       _title = null,
       _actionLabel = null,
       _onAction = null;"""
assert old1 in s, 'anchor1 not found'
s = s.replace(old1, new1)

old2 = """  /// 空数据：图标 + 标题 + 说明 + 可选行动按钮
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
       _onRetry = null;"""
new2 = """  /// 空数据：图标 + 标题 + 说明 + 可选行动按钮
  /// （[actionLabel] 与 [onAction] 同时提供时显示行动按钮）
  const AppStateView.empty({
    super.key,
    required IconData icon,
    required String title,
    String? message,
    String? actionLabel,
    VoidCallback? onAction,
  }) : _icon = icon,
       _title = title,
       _message = message,
       _actionLabel = actionLabel,
       _onAction = onAction,
       _isLoading = false,
       _isError = false,
       _onRetry = null;"""
assert old2 in s, 'anchor2 not found'
s = s.replace(old2, new2)

open(f, 'w', encoding='utf-8').write(s)
print('app_state_view.dart: error/empty 构造参数公开化 已改')
print('  error 公开:', s.count('required String message'), '| empty 公开:', s.count('required IconData icon'))
