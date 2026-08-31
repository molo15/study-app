import 'dart:io';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:path/path.dart' as p;
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

import 'package:quiz_app/data/app_database.dart';
import 'package:quiz_app/data/quiz_repository.dart';
import 'package:quiz_app/data/seed_loader.dart';
import 'package:quiz_app/services/archive_store.dart';
import 'package:quiz_app/services/auto_archive_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  sqfliteFfiInit();

  Future<String> demoBankJson() async =>
      await File('test/fixtures/demo_bank.json').readAsString();

  late Database db;
  late QuizRepository repo;
  late Directory tempDir;
  late FileArchiveStore store;
  late AutoArchiveService service;

  setUp(() async {
    db = await databaseFactoryFfi.openDatabase(inMemoryDatabasePath,
        options: OpenDatabaseOptions(
          version: 11,
          onConfigure: AppDatabase.configure,
          onCreate: (db, v) => AppDatabase.createSchema(db, v),
        ));
    repo = QuizRepository(db);
    await repo.importBank(SeedLoader.parse(await demoBankJson()));
    tempDir = await Directory.systemTemp.createTemp('archive_test_');
    store = FileArchiveStore(basePath: tempDir.path);
    service = AutoArchiveService();
  });

  tearDown(() async {
    service.dispose();
    await db.close();
    if (await tempDir.exists()) {
      await tempDir.delete(recursive: true);
    }
  });

  group('自动存档（多端方案 §2.2）', () {
    test('trigger 生成 zip 存档，可被 parseArchive 读取', () async {
      await service.start(repo, store);
      final path = await service.trigger();
      expect(path, isNotNull);
      expect(File(path!).existsSync(), isTrue);

      final list = await store.listAutoArchives();
      expect(list, hasLength(1));
      expect(list.first.fileName, startsWith('auto_'));
      expect(list.first.fileName, endsWith('.zip'));

      // 生成的文件是合法 v3 存档
      final bytes = File(list.first.fileName.isEmpty ? path : path)
          .readAsBytesSync();
      final preview = await repo.parseArchive(Uint8List.fromList(bytes));
      expect(preview.formatVersion, 3);
      expect(preview.kind, ArchiveKind.auto);
    });

    test('覆盖压缩：超过保留份数自动删最旧', () async {
      // 预置 7 份旧存档（文件名按时间倒序）
      final archives = Directory(p.join(tempDir.path, 'archives'));
      await archives.create(recursive: true);
      for (var i = 1; i <= 7; i++) {
        final name = 'auto_20260101_${i.toString().padLeft(6, '0')}.zip';
        await File(p.join(archives.path, name)).writeAsBytes([1, 2, 3]);
      }
      await service.start(repo, store);

      // 触发一次 → 共 8 份，保留 5 份（默认）
      await service.trigger();
      final list = await store.listAutoArchives();
      expect(list, hasLength(5));
      // 保留的是最新的（新生成 + 原 4 份最新）
      expect(list.first.fileName, startsWith('auto_'));
      expect(list.any((f) => f.fileName == 'auto_20260101_000001.zip'),
          isFalse); // 最旧的被删
    });

    test('开关状态可切换；手动立即存档始终可用', () async {
      await service.start(repo, store);
      await service.setEnabled(false);
      expect(service.autoArchiveEnabled, isFalse);
      // 手动立即存档不受开关影响
      final path = await service.trigger();
      expect(path, isNotNull);
      expect(await store.listAutoArchives(), hasLength(1));

      await service.setEnabled(true);
      expect(service.autoArchiveEnabled, isTrue);
    });
  });
}
