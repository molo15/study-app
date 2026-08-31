/// Web/大屏布局修复验证（Phase 2.2 审查）：
/// _BackgroundStack 由 Center 垂直居中改为 Align(topCenter)+SizedBox.expand 后，
/// 在 1920x1077 宽视口下，App 内容顶部对齐、底部导航栏应固定在视口底部
/// （修复前 Center 会把整个界面垂直浮到中间，导航栏不在底部）。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

import 'package:quiz_app/data/app_database.dart';
import 'package:quiz_app/data/quiz_repository.dart';
import 'package:quiz_app/main.dart';
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

  testWidgets('1920x1077 大屏：底部导航栏固定在视口底部', (tester) async {
    // 用 view.physicalSize + dpr 设置 MediaQuery 视口（setSurfaceSize 只改渲染
    // surface、不改 MediaQuery，MediaQuery.sizeOf 会一直是默认 600 导致测试失真）
    tester.view.physicalSize = const Size(1920, 1077);
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

    final nav = tester.widget<GlassTabBar>(find.byType(GlassTabBar));
    expect(nav, isNotNull);
    final rect = tester.getRect(find.byType(GlassTabBar));
    // 导航栏应贴近视口底部（允许沉浸式扩展的少量偏差）
    expect(rect.bottom, greaterThan(1077 - 40),
        reason: '修复后导航栏应在视口底部，实际 bottom=${rect.bottom}');
  });
}
