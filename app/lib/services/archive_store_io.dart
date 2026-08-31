import 'dart:io';
import 'dart:typed_data';

import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

import 'archive_store.dart';

/// 文件系统后端：应用文档目录 `archives/`（Android / Windows / 桌面 / 测试）
class FileArchiveStore implements ArchiveStore {
  /// [basePath] 可注入（测试用临时目录）；默认应用文档目录。
  FileArchiveStore({this._basePath});

  final String? _basePath;

  Future<Directory> _dir() async {
    final base = _basePath ?? (await getApplicationDocumentsDirectory()).path;
    final dir = Directory(p.join(base, 'archives'));
    if (!await dir.exists()) {
      await dir.create(recursive: true);
    }
    return dir;
  }

  @override
  Future<String> saveAutoArchive(String fileName, Uint8List bytes) async {
    final dir = await _dir();
    final file = File(p.join(dir.path, fileName));
    await file.writeAsBytes(bytes);
    return file.path;
  }

  @override
  Future<List<ArchiveFileEntry>> listAutoArchives() async {
    final dir = await _dir();
    final files = <File>[];
    for (final e in dir.listSync()) {
      if (e is File && e.path.endsWith('.zip')) files.add(e);
    }
    // 按文件名倒序（自动存档文件名带时间戳，倒序 = 最新在前）
    files.sort((a, b) => b.path.compareTo(a.path));
    return [
      for (final f in files)
        ArchiveFileEntry(
          fileName: p.basename(f.path),
          modifiedAt: f.lastModifiedSync(),
        ),
    ];
  }

  @override
  Future<void> deleteAutoArchive(String fileName) async {
    final dir = await _dir();
    final file = File(p.join(dir.path, fileName));
    if (await file.exists()) {
      await file.delete();
    }
  }
}
