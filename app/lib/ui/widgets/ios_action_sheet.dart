/// V3 iOS 风格底部选择弹窗（Action Sheet）
///
/// 替代 Material showModalBottomSheet 的安卓味实现：
/// - 顶部大圆角 + 毛玻璃背景
/// - 选项 inset grouped 卡片分组，组间间距
/// - 选中项右侧蓝色对勾
/// - 底部独立「取消」分组
/// - 统一转场动效（IOSDuration.standard 上滑）
///
/// 用法：
/// ```dart
/// final v = await showIOSActionSheet<int>(
///   context: context,
///   title: '选择随机刷题量',
///   selectedValue: current,
///   items: [
///     IOSActionItem(value: 50, title: '50 题', subtitle: '整本随机'),
///     IOSActionItem(value: 100, title: '100 题', subtitle: '整本随机'),
///   ],
/// );
/// ```
library;

import 'package:flutter/material.dart';

import '../theme/ios_tokens.dart';
import 'liquid_glass.dart';

/// 单个选项
class IOSActionItem<T> {
  const IOSActionItem({
    required this.value,
    required this.title,
    this.subtitle,
    this.icon,
    this.destructive = false,
  });

  final T value;
  final String title;
  final String? subtitle;
  final IconData? icon;
  final bool destructive;
}

/// 弹出 iOS 风格底部选择弹窗，返回选中项的 value，取消返回 null。
Future<T?> showIOSActionSheet<T>({
  required BuildContext context,
  String? title,
  required List<IOSActionItem<T>> items,
  T? selectedValue,
  String cancelLabel = '取消',
}) {
  return showModalBottomSheet<T>(
    context: context,
    backgroundColor: Colors.transparent,
    barrierColor: Colors.black.withValues(alpha: 0.35),
    elevation: 0,
    isScrollControlled: true,
    builder: (ctx) => _IOSActionSheetView<T>(
      title: title,
      items: items,
      selectedValue: selectedValue,
      cancelLabel: cancelLabel,
    ),
  );
}

/// 弹出 iOS 风格自定义内容底部弹窗（毛玻璃容器 + 大圆角 + 取消留白）。
///
/// 用于日期选择器、答题卡、表单等**非选项列表**内容。
/// 内容通过 [builder] 传入，自动包裹毛玻璃卡片与安全区域。
Future<T?> showIOSModalSheet<T>({
  required BuildContext context,
  required WidgetBuilder builder,
  bool isScrollControlled = true,
  double maxHeightFactor = 0.82,
}) {
  return showModalBottomSheet<T>(
    context: context,
    backgroundColor: Colors.transparent,
    barrierColor: Colors.black.withValues(alpha: 0.35),
    elevation: 0,
    isScrollControlled: isScrollControlled,
    builder: (ctx) {
      final mq = MediaQuery.of(ctx);
      return SafeArea(
        top: false,
        child: Padding(
          padding: EdgeInsets.fromLTRB(
            IOSSpacing.s12,
            0,
            IOSSpacing.s12,
            MediaQuery.paddingOf(ctx).bottom > 0
                ? IOSSpacing.s8
                : IOSSpacing.s16,
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(IOSRadius.md),
            child: LiquidGlass(
              variant: LiquidGlassVariant.regular,
              borderRadius: BorderRadius.circular(IOSRadius.md),
              showShadow: true,
              padding: EdgeInsets.zero,
              child: ConstrainedBox(
                constraints: BoxConstraints(
                  maxHeight: mq.size.height * maxHeightFactor,
                ),
                // Material 透明层：内部 ListTile/TextField 等需要 Material 祖先
                child: Material(
                  color: Colors.transparent,
                  child: builder(ctx),
                ),
              ),
            ),
          ),
        ),
      );
    },
  );
}

class _IOSActionSheetView<T> extends StatelessWidget {
  const _IOSActionSheetView({
    required this.title,
    required this.items,
    required this.selectedValue,
    required this.cancelLabel,
  });

  final String? title;
  final List<IOSActionItem<T>> items;
  final T? selectedValue;
  final String cancelLabel;

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    final safeBottom = MediaQuery.paddingOf(context).bottom;

    return SafeArea(
      top: false,
      child: Padding(
        padding: EdgeInsets.fromLTRB(
          IOSSpacing.s12,
          0,
          IOSSpacing.s12,
          safeBottom > 0 ? IOSSpacing.s8 : IOSSpacing.s16,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // —— 选项分组 ——
            ClipRRect(
              borderRadius: BorderRadius.circular(IOSRadius.md),
              child: LiquidGlass(
                variant: LiquidGlassVariant.regular,
                borderRadius: BorderRadius.circular(IOSRadius.md),
                showShadow: true,
                padding: EdgeInsets.zero,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (title != null) ...[
                      Padding(
                        padding: const EdgeInsets.symmetric(
                          vertical: IOSSpacing.s12,
                          horizontal: IOSSpacing.s16,
                        ),
                        child: Text(
                          title!,
                          textAlign: TextAlign.center,
                          style: IOSTypography.footnote(
                            color: colors.text2,
                          ).copyWith(fontWeight: FontWeight.w500),
                        ),
                      ),
                      Divider(height: 0.5, thickness: 0.5, color: colors.separator),
                    ],
                    for (var i = 0; i < items.length; i++) ...[
                      if (i > 0 || title != null)
                        Divider(
                          height: 0.5,
                          thickness: 0.5,
                          color: colors.separator,
                          indent: IOSSpacing.s16,
                        ),
                      _ActionRow<T>(
                        item: items[i],
                        selected: items[i].value == selectedValue,
                        onTap: () => Navigator.of(context).pop(items[i].value),
                      ),
                    ],
                  ],
                ),
              ),
            ),
            const SizedBox(height: IOSSpacing.s8),
            // —— 取消分组（独立卡片）——
            ClipRRect(
              borderRadius: BorderRadius.circular(IOSRadius.md),
              child: LiquidGlass(
                variant: LiquidGlassVariant.regular,
                borderRadius: BorderRadius.circular(IOSRadius.md),
                showShadow: false,
                padding: EdgeInsets.zero,
                child: InkWell(
                  onTap: () => Navigator.of(context).pop(),
                  child: SizedBox(
                    height: 52,
                    child: Center(
                      child: Text(
                        cancelLabel,
                        style: IOSTypography.body(
                          color: colors.primary,
                        ).copyWith(fontWeight: FontWeight.w600),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// 单行选项
class _ActionRow<T> extends StatelessWidget {
  const _ActionRow({
    required this.item,
    required this.selected,
    required this.onTap,
  });

  final IOSActionItem<T> item;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    final titleColor = item.destructive ? colors.danger : colors.text;

    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: IOSSpacing.s16,
          vertical: IOSSpacing.s12,
        ),
        child: Row(
          children: [
            if (item.icon != null) ...[
              Icon(item.icon, size: 22, color: titleColor),
              const SizedBox(width: IOSSpacing.s12),
            ],
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.title,
                    style: IOSTypography.body(color: titleColor),
                  ),
                  if (item.subtitle != null) ...[
                    const SizedBox(height: 2),
                    Text(
                      item.subtitle!,
                      style: IOSTypography.caption1(color: colors.text2),
                    ),
                  ],
                ],
              ),
            ),
            // 选中态：蓝色对勾
            if (selected)
              Icon(Icons.check, color: colors.primary, size: 22)
            else
              const SizedBox(width: 22),
          ],
        ),
      ),
    );
  }
}
