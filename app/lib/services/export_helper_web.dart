import 'dart:js_interop';
import 'dart:typed_data';

import 'package:web/web.dart' as web;

/// Web 端导出：通过浏览器 Blob 触发下载（wasm 兼容）。
/// 返回展示给用户的提示（非本地路径，浏览器没有文件系统路径概念）。

/// 把文本文件导出为浏览器下载
Future<String> exportToDownloads(String fileName, String content) =>
    exportToDownloadsBytes(fileName, Uint8List.fromList(content.codeUnits));

/// 把**二进制**文件（如 zip 存档）导出为浏览器下载
Future<String> exportToDownloadsBytes(
  String fileName,
  Uint8List bytes,
) async {
  final blob = web.Blob(<web.BlobPart>[bytes.toJS].toJS);
  final url = web.URL.createObjectURL(blob);
  final anchor = web.HTMLAnchorElement()
    ..href = url
    ..download = fileName;
  anchor.click();
  web.URL.revokeObjectURL(url);
  return '浏览器已开始下载 $fileName';
}
