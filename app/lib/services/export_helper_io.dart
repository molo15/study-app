import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

/// 把文本文件导出到系统公共「下载」目录（方便在文件管理/下载中取用），
/// 返回展示给用户的路径。
///
/// - Android：通过原生 MediaStore 写入公共 Downloads（Android 10+ 免权限）。
/// - 其他平台：回退到应用文档目录。
Future<String> exportToDownloads(String fileName, String content) =>
    exportToDownloadsBytes(fileName, Uint8List.fromList(content.codeUnits));

/// 把**二进制**文件（如 zip 存档）导出到系统公共「下载」目录，
/// 返回展示给用户的路径。
///
/// - Android：通过原生 MediaStore 写入公共 Downloads（Android 10+ 免权限），
///   原生侧同时接受 String 与 ByteArray。
/// - 其他平台：回退到应用文档目录。
Future<String> exportToDownloadsBytes(
  String fileName,
  Uint8List bytes,
) async {
  if (defaultTargetPlatform == TargetPlatform.android) {
    try {
      const ch = MethodChannel('dev.kaoyan.quiz_app/exporter');
      final path = await ch.invokeMethod<String>('saveToDownloads', {
        'fileName': fileName,
        'content': bytes,
      });
      if (path != null) return path;
    } on PlatformException catch (e) {
      // Android 原生导出失败则回退文档目录
      debugPrint('saveToDownloads failed: ${e.message}');
    } catch (e) {
      debugPrint('saveToDownloads error: $e');
    }
  }
  final dir = await getApplicationDocumentsDirectory();
  final file = File('${dir.path}/$fileName');
  await file.writeAsBytes(bytes);
  return file.path;
}

/// 导出备份并按平台给出最佳交付方式：
/// - iOS：写入临时目录后弹出系统分享面板（UIActivityViewController），
///   用户可「存储到文件」/ AirDrop / 发送到其他 App——沙盒目录用户无法直接访问。
/// - Android / 其他：走 [exportToDownloadsBytes]（MediaStore 公共下载目录）。
/// 返回展示给用户的提示文本。
Future<String> exportBackupFile(String fileName, Uint8List bytes) async {
  if (defaultTargetPlatform == TargetPlatform.iOS) {
    final dir = await getTemporaryDirectory();
    final file = File('${dir.path}/$fileName');
    await file.writeAsBytes(bytes, flush: true);
    await SharePlus.instance.share(ShareParams(
      files: <XFile>[XFile(file.path, mimeType: 'application/zip')],
      subject: fileName,
      text: '考研刷题学习备份',
    ));
    return '已打开系统分享，可存储到「文件」App 或通过 AirDrop 发送';
  }
  return exportToDownloadsBytes(fileName, bytes);
}
