import 'dart:typed_data';

export 'archive_store_io.dart'
    if (dart.library.js_interop) 'archive_store_web.dart';

/// 自动存档条目
class ArchiveFileEntry {
  ArchiveFileEntry({required this.fileName, required this.modifiedAt});

  final String fileName;
  final DateTime modifiedAt;
}

/// 存档存储后端抽象（多端同步方案 §2.4）
///
/// - Android / Windows / 桌面：文件系统 `应用文档目录/archives/`（`FileArchiveStore` io 实现）
/// - Web：浏览器 localStorage（`FileArchiveStore` web 实现，保留最近 1 份，wasm 兼容）
///
/// 两个平台实现同名类 `FileArchiveStore`，由条件导出按平台切换，调用方无感知。
abstract class ArchiveStore {
  /// 写入一份自动存档，返回落盘位置（用于展示）
  Future<String> saveAutoArchive(String fileName, Uint8List bytes);

  /// 列出全部自动存档（建议按时间倒序）
  Future<List<ArchiveFileEntry>> listAutoArchives();

  /// 删除指定自动存档
  Future<void> deleteAutoArchive(String fileName);
}
