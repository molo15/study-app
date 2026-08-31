/// Phase 2.1 Web spike 入口：验证 sqflite_common_ffi_web 在浏览器跑通
///
/// 验证点：
/// 1. databaseFactoryFfiWeb 打开数据库（sqlite3.wasm + shared worker）
/// 2. 内置题库 zip seed（真实数据量）
/// 3. 查询题目数量
/// 4. 刷新重开后数据仍在（IndexedDB 持久化）
///
/// 仅作为 spike 验证用，不进入正式 App 依赖图。
/// 构建：flutter build web -t tools/web_spike/spike_main.dart
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show AssetManifest, rootBundle;
import 'package:quiz_app/data/app_database.dart';
import 'package:quiz_app/data/quiz_repository.dart';
import 'package:quiz_app/data/seed_loader.dart';
import 'package:sqflite/sqflite.dart';
import 'package:sqflite_common_ffi_web/sqflite_ffi_web.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // web 上切换数据库工厂（sqlite3.wasm + IndexedDB 持久化）
  databaseFactory = databaseFactoryFfiWeb;
  runApp(const SpikeApp());
}

class SpikeApp extends StatelessWidget {
  const SpikeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: SpikePage(),
    );
  }
}

class SpikePage extends StatefulWidget {
  const SpikePage({super.key});

  @override
  State<SpikePage> createState() => _SpikePageState();
}

class _SpikePageState extends State<SpikePage> {
  final List<String> _lines = <String>[];
  bool _busy = false;

  Future<void> _log(String s) async {
    setState(() => _lines.add(s));
    // 让 UI 逐行刷出
    await Future<void>.delayed(const Duration(milliseconds: 50));
  }

  Future<void> _run() async {
    if (_busy) return;
    setState(() {
      _busy = true;
      _lines.clear();
    });
    try {
      await _log('1/6 打开数据库 (databaseFactoryFfiWeb)...');
      final db = await AppDatabase.open();
      final repo = QuizRepository(db);

      final ver =
          (await db.rawQuery('select sqlite_version() as v')).first['v'];
      await _log('   sqlite 版本: $ver');

      await _log('2/6 检查是否已有数据（持久化验证）...');
      final qCount =
          (await db.rawQuery('SELECT COUNT(*) c FROM questions')).first['c']
              as int? ?? 0;
      final seeded = await repo.setting('spike_seeded');
      if (qCount > 0 && seeded == '1') {
        await _log('   已存在 $qCount 道题 → IndexedDB 持久化 OK（上次的数据还在）');
      } else {
        await _log('   首次运行，seed 内置题库...');
      }

      if (qCount == 0) {
        await _log('3/6 发现内置题库 zip...');
        final manifest = await AssetManifest.loadFromAssetBundle(rootBundle);
        final pattern = RegExp(
            r'^assets/banks/(bank-[a-z0-9-]+)-v(\d+)\.(\d+)\.(\d+)\.zip$');
        final zips = <String, String>{};
        for (final key in manifest.listAssets()) {
          final m = pattern.firstMatch(key);
          if (m != null) {
            zips[m.group(1)!] = key;
          }
        }
        await _log('   发现 ${zips.length} 个题库包: ${zips.keys.join(', ')}');

        for (final entry in zips.entries) {
          await _log('4/6 seed ${entry.key} ...');
          final bytes =
              (await rootBundle.load(entry.value)).buffer.asUint8List();
          final pack = SeedLoader.parseZipBytes(bytes);
          final r = await repo.importBank(pack);
          await _log('   ${entry.key}: ${r.imported} 导入, ${r.archived} 归档');
        }
        await repo.setSetting('spike_seeded', '1');
      }

      await _log('5/6 统计...');
      final total = (await db
              .rawQuery('SELECT COUNT(*) c FROM questions'))
          .first['c'] as int? ?? 0;
      final chapters = await db.rawQuery(
          'SELECT bank_id, COUNT(*) c FROM questions GROUP BY bank_id');
      for (final row in chapters) {
        await _log('   ${row['bank_id']}: ${row['c']} 题');
      }
      await _log('   合计 $total 题');

      await _log('6/6 验证完成 ✅');
      await _log('');
      await _log('现在刷新浏览器：若再次显示 "持久化 OK"，说明数据已写入 IndexedDB');
    } catch (e, st) {
      await _log('❌ 失败: $e');
      await _log('$st');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F1214),
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: FilledButton(
                onPressed: _busy ? null : _run,
                child: Text(_busy ? '运行中...' : '运行 Web spike 验证'),
              ),
            ),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                children: [
                  for (final l in _lines)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 6),
                      child: Text(l,
                          style: const TextStyle(
                              color: Colors.white70, fontSize: 14)),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
