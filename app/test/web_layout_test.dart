/// Web/大屏布局修复验证（Phase 2.2 审查 + P2 响应式）：
/// - _BackgroundStack 由 Center 垂直居中改为 Align(topCenter)+SizedBox.expand 后，
///   在任意宽视口下 App 内容顶部对齐、底部导航栏应固定在视口底部。
/// - P2 新增断点系统（responsive.dart）：手机/平板/桌面三档内容宽度，
///   本测试在 390x844 / 768x1024 / 1920x1077 三尺寸验证导航贴底 + 断点宽度。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

import 'package:quiz_app/data/app_database.dart';
import 'package:quiz_app/data/quiz_repository.dart';
import 'package:quiz_app/main.dart';
import 'package:quiz_app/ui/responsive.dart';
import 'package:quiz_app/ui/widgets/app_sidebar.dart';
import 'package:quiz_app/ui/widgets/glass_tab_bar.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  sqfliteFfiInit();

  Future<Database> openDb() async => databaseFactoryFfi.openDatabase(
        inMemoryDatabasePath,
        options: OpenDatabaseOptions(
          version: 11,
          onConfigure: AppDatabase.configure,
          onCreate: (db, v) => AppDatabase.createSchema(db, v),
        ),
      );

  group('responsive.dart 断点分级（P2）', () {
    test('内容宽度按窗口宽度分档', () {
      expect(contentWidthFromWidth(390), 560, reason: '手机竖屏 compact');
      expect(contentWidthFromWidth(599), 560, reason: 'compact 上限');
      expect(contentWidthFromWidth(600), 760, reason: 'medium 下界');
      expect(contentWidthFromWidth(768), 760, reason: '平板 medium');
      expect(contentWidthFromWidth(1199), 760, reason: 'medium 上限');
      expect(contentWidthFromWidth(1200), 920, reason: 'expanded 下界');
      expect(contentWidthFromWidth(1920), 920, reason: '桌面 expanded');
    });

    test('布局档位判定', () {
      expect(appLayoutFromWidth(390), AppLayout.compact);
      expect(appLayoutFromWidth(599), AppLayout.compact);
      expect(appLayoutFromWidth(600), AppLayout.medium);
      expect(appLayoutFromWidth(1199), AppLayout.medium);
      expect(appLayoutFromWidth(1200), AppLayout.expanded);
      expect(appLayoutFromWidth(1920), AppLayout.expanded);
    });
  });

  const viewports = <(String, Size)>[
    ('390x844 手机竖屏', Size(390, 844)),
    ('768x1024 平板', Size(768, 1024)),
    ('1920x1077 桌面', Size(1920, 1077)),
  ];

  for (final (name, size) in viewports) {
    testWidgets('$name：导航形态随断点切换（手机 dock / 平板桌面侧边栏）', (tester) async {
      // 用 view.physicalSize + dpr 设置 MediaQuery 视口（setSurfaceSize 只改渲染
      // surface、不改 MediaQuery，MediaQuery.sizeOf 会一直是默认 600 导致测试失真）
      tester.view.physicalSize = size;
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);

      await tester.runAsync(() async {
        final db = await openDb();
        final repo = QuizRepository(db);
        await tester.pumpWidget(ProviderScope(
          overrides: [
            databaseProvider.overrideWithValue(Future.value(db)),
            quizRepositoryProvider.overrideWithValue(Future.value(repo)),
          ],
          child: const QuizApp(),
        ));
        // 首页存在入场/生长动画（StaggeredItem/CircularRing），pumpAndSettle 会超时，
        // 用固定次数 pump 推进动画帧
        await tester.pump(const Duration(milliseconds: 200));
        await tester.pump(const Duration(milliseconds: 400));
        await tester.pump(const Duration(milliseconds: 400));
      });

      final layout = appLayoutFromWidth(size.width);
      if (layout == AppLayout.compact) {
        // 手机：底部 dock 固定贴底
        final nav = tester.widget<GlassTabBar>(find.byType(GlassTabBar));
        expect(nav, isNotNull);
        final rect = tester.getRect(find.byType(GlassTabBar));
        // 导航栏应贴近视口底部（允许沉浸式扩展的少量偏差）
        expect(rect.bottom, greaterThan(size.height - 40),
            reason: '修复后导航栏应在视口底部，实际 bottom=${rect.bottom}');
        expect(find.byType(AppSidebar), findsNothing,
            reason: '手机形态不显示侧边栏');
      } else {
        // 平板 / 桌面：隐藏底部 dock，改用侧边栏
        expect(find.byType(GlassTabBar), findsNothing,
            reason: '$name 应隐藏底部 dock（改用侧边栏）');
        expect(find.byType(AppSidebar), findsOneWidget,
            reason: '$name 应显示侧边栏');
        // 侧边栏宽度随断点：桌面 232 全宽 / 平板 66 图标栏（P1 规格）
        final sbRect = tester.getRect(find.byType(AppSidebar));
        if (layout == AppLayout.expanded) {
          expect(sbRect.width, closeTo(232, 1),
              reason: '桌面侧边栏 232px 全宽，实际 ${sbRect.width.toStringAsFixed(0)}');
        } else {
          expect(sbRect.width, closeTo(66, 1),
              reason: '平板侧边栏 66px 图标栏，实际 ${sbRect.width.toStringAsFixed(0)}');
        }
      }
    });
  }
}
