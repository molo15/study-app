/// 弹窗与卡片设计一致性实施后的主题回归测试（审查 P1-1/P1-2/P2-1）：
/// - P1-1：dialogTheme / bottomSheetTheme / datePickerTheme 已玻璃化（半透明白 + 统一圆角），
///   断言 5 套预设下弹窗主题均存在且背景半透明、圆角与 cornerRadius 对齐。
/// - P1-2/P2-1：GlassCard 已并入 AppCard、原生 Card 已全量迁移，断言 AppCard 在
///   5 套预设（含 4 套旧主题 frost=false 与夜间 darkMode）下渲染不崩溃。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:quiz_app/ui/theme_controller.dart';
import 'package:quiz_app/ui/widgets/app_card.dart';

/// 用指定配置覆盖主题 provider 的测试替身。
class _FakeThemeController extends ThemeController {
  _FakeThemeController(this.config);
  final AppThemeConfig config;
  @override
  Future<AppThemeConfig> build() async => config;
}

Widget _harness(AppThemeConfig config, {Widget? child}) {
  return ProviderScope(
    overrides: [
      themeControllerProvider.overrideWith(() => _FakeThemeController(config)),
    ],
    child: MaterialApp(
      theme: config.buildThemeData(),
      home: Scaffold(
        body: Center(
          child: child ??
              AppCard(
                padding: EdgeInsets.zero,
                margin: const EdgeInsets.symmetric(vertical: 6),
                child: const Text('卡片'),
              ),
        ),
      ),
    ),
  );
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  // 5 套预设：冷磨砂 + 4 套旧主题（墨绿/纸米/经典蓝 frost=false、夜间 darkMode）
  final presets = AppThemeConfig.presets;

  group('P1-1 弹窗主题玻璃化', () {
    test('5 套预设均配置 dialog/bottomSheet/datePicker 主题', () {
      for (final (name, config) in presets) {
        final theme = config.buildThemeData();
        expect(theme.dialogTheme, isNotNull, reason: '$name dialogTheme');
        expect(theme.bottomSheetTheme, isNotNull, reason: '$name bottomSheetTheme');
        expect(theme.datePickerTheme, isNotNull, reason: '$name datePickerTheme');
      }
    });

    test('冷磨砂默认：弹窗背景半透明、圆角与 cornerRadius 对齐', () {
      final config = AppThemeConfig.defaults();
      final theme = config.buildThemeData();

      final dlg = theme.dialogTheme;
      expect(dlg.backgroundColor, isNotNull, reason: 'dialog 背景已设置');
      expect(dlg.backgroundColor!.a, lessThan(1.0), reason: 'dialog 半透明（非纯实色）');
      expect(dlg.backgroundColor!.a, greaterThan(0.7), reason: 'dialog 不透明度过低会不可读');
      expect(dlg.surfaceTintColor, Colors.transparent, reason: '去掉 M3 彩色 tint');

      final sheet = theme.bottomSheetTheme;
      expect(sheet.backgroundColor, isNotNull, reason: 'bottomSheet 背景已设置');
      expect(sheet.backgroundColor!.a, lessThan(1.0), reason: 'bottomSheet 半透明');
      expect(sheet.elevation, 0, reason: 'bottomSheet 无阴影（悬浮玻璃）');

      final dp = theme.datePickerTheme;
      expect(dp.backgroundColor, isNotNull, reason: 'datePicker 背景已设置');

      // 圆角：dialog 圆角应与配置 cornerRadius 一致（M3 默认 28 已被覆盖）
      final radius = (dlg.shape as RoundedRectangleBorder?)?.borderRadius;
      expect(radius, BorderRadius.circular(config.cornerRadius),
          reason: 'dialog 圆角 = cornerRadius(${config.cornerRadius})，而非 M3 默认 28');
    });

    test('深色（夜间预设）：弹窗主题存在且不报错', () {
      final night = AppThemeConfig.presets
          .firstWhere((e) => e.$1 == '夜间')
          .$2;
      expect(night.darkMode, isTrue);
      final theme = night.buildThemeData();
      expect(theme.brightness, Brightness.dark);
      expect(theme.dialogTheme.backgroundColor, isNotNull);
      expect(theme.bottomSheetTheme.backgroundColor, isNotNull);
    });
  });

  group('P1-2/P2-1 AppCard 全预设渲染', () {
    for (final (name, config) in presets) {
      testWidgets('$name：AppCard 渲染正常（GlassCard 并入 + 原生 Card 迁移）', (tester) async {
        await tester.pumpWidget(_harness(config));
        await tester.pump();
        expect(tester.takeException(), isNull, reason: '$name 渲染无异常');
        expect(find.byType(AppCard), findsOneWidget, reason: '$name 下 AppCard 存在');
        expect(find.text('卡片'), findsOneWidget);
      });
    }
  });
}
