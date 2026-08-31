import 'dart:convert';
import 'dart:typed_data';

import 'package:web/web.dart' as web;

import 'archive_store.dart';

/// Web 后端：浏览器 localStorage（wasm 兼容，无需额外依赖）。
///
/// 多端同步以「手动导出文件」为核心；浏览器内自动存档仅作最近状态保险，
/// 因此 Web 端保留最近 1 份（覆盖式）。localStorage 容量上限约 5MB，
/// 写入失败时先清空旧自动存档再写入。
class FileArchiveStore implements ArchiveStore {
  static const _prefix = 'auto_archive:';

  static String _key(String fileName) => '$_prefix$fileName';

  @override
  Future<String> saveAutoArchive(String fileName, Uint8List bytes) async {
    final b64 = base64Encode(bytes);
    try {
      web.window.localStorage.setItem(_key(fileName), b64);
    } catch (_) {
      // 容量不足：清掉历史自动存档后重试
      _clearAll();
      try {
        web.window.localStorage.setItem(_key(fileName), b64);
      } catch (_) {
        // 单份存档即超限（base64 膨胀后超 localStorage ~5MB 上限），无法写入。
        // 抛出友好异常，调用方可提示用户改用手动导出文件备份。
        throw Exception(
          '浏览器本地存储容量不足，自动存档失败。'
          '请使用「导出备份」将数据保存为文件，或清理做题记录后重试。',
        );
      }
    }
    return 'localStorage:$fileName';
  }

  @override
  Future<List<ArchiveFileEntry>> listAutoArchives() async {
    final entries = <ArchiveFileEntry>[];
    final keys = <String>[];
    for (var i = 0; i < web.window.localStorage.length; i++) {
      final k = web.window.localStorage.key(i);
      if (k != null && k.startsWith(_prefix)) keys.add(k);
    }
    keys.sort();
    for (final k in keys.reversed) {
      entries.add(ArchiveFileEntry(
        fileName: k.substring(_prefix.length),
        modifiedAt: DateTime.now(),
      ));
    }
    return entries;
  }

  @override
  Future<void> deleteAutoArchive(String fileName) async {
    web.window.localStorage.removeItem(_key(fileName));
  }

  void _clearAll() {
    final keys = <String>[];
    for (var i = 0; i < web.window.localStorage.length; i++) {
      final k = web.window.localStorage.key(i);
      if (k != null && k.startsWith(_prefix)) keys.add(k);
    }
    for (final k in keys) {
      web.window.localStorage.removeItem(k);
    }
  }
}
