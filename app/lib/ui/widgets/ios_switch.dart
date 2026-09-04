/// V3 iOS 风格开关
///
/// B2 审查修复：包装 CupertinoSwitch，统一 activeTrackColor 为系统蓝，
/// 深浅色下圆钮自动适配，消除 Material Switch 安卓味。
library;

import 'package:flutter/cupertino.dart';

import '../theme/ios_tokens.dart';

class IOSSwitch extends StatelessWidget {
  const IOSSwitch({
    super.key,
    required this.value,
    required this.onChanged,
  });

  final bool value;
  final ValueChanged<bool> onChanged;

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    return CupertinoSwitch(
      value: value,
      activeTrackColor: colors.primary,
      onChanged: onChanged,
    );
  }
}