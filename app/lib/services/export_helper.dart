import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';

/// 审题标记功能（刷题页旗子 + 设置页导出入口）。
/// 常驻功能（用户决策 2026-08-24）：不再按构建隐藏，正式版同样可见。
const bool reviewModeEnabled = true;

/// 把文本文件导出到系统公共「下载」目录（方便在文件管理/下载中取用），
/// 返回展示给用户的路径。
///
/// - Android：通过原生 MediaStore 写入公共 Downloads（Android 10+ 免权限）。
/// - 其他平台：回退到应用文档目录。
Future<String> exportToDownloads(String fileName, String content) async {
  if (defaultTargetPlatform == TargetPlatform.android) {
    try {
      const ch = MethodChannel('dev.kaoyan.quiz_app/exporter');
      final path = await ch.invokeMethod<String>('saveToDownloads', {
        'fileName': fileName,
        'content': content,
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
  await file.writeAsString(content);
  return file.path;
}
