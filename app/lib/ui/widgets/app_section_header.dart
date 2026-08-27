/// 区块标题（需求：统一页面区块标题）
///
/// 标题使用 `titleMedium` + w700（见《界面UI改版设计方案》4.3 字体层级），
/// 可选辅助文本（标题下方的次级说明）与尾部操作（如「查看全部」按钮）。
/// 浅色 / 深色模式自动适配，颜色取自 ColorScheme 语义色。
///
/// 用法：
/// ```dart
/// AppSectionHeader(
///   title: '今日任务',
///   helperText: '先完成待复习，再刷新题',
///   trailing: TextButton(onPressed: _viewAll, child: const Text('查看全部')),
/// )
/// ```
library;

import 'package:flutter/material.dart';

import '../theme_controller.dart' show AppSpacing;

class AppSectionHeader extends StatelessWidget {
  const AppSectionHeader({
    super.key,
    required this.title,
    this.helperText,
    this.trailing,
    this.padding = const EdgeInsets.only(
      left: AppSpacing.space1,
      right: AppSpacing.space1,
      bottom: AppSpacing.space3,
    ),
  });

  /// 区块标题
  final String title;

  /// 辅助文本（标题下方的次级说明，可空）
  final String? helperText;

  /// 尾部操作（如「查看全部」按钮，可空）
  final Widget? trailing;

  /// 外边距（默认左右 4dp / 下 12dp，可覆盖）
  final EdgeInsetsGeometry padding;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final helper = helperText;
    return Padding(
      padding: padding,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Expanded(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                    height: 1.3,
                  ),
                ),
                if (helper != null && helper.isNotEmpty) ...[
                  const SizedBox(height: AppSpacing.space1),
                  Text(
                    helper,
                    style: textTheme.bodySmall?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ],
            ),
          ),
          ?trailing,
        ],
      ),
    );
  }
}
