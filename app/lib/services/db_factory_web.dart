import 'package:sqflite/sqflite.dart';
import 'package:sqflite_common_ffi_web/sqflite_ffi_web.dart';

/// Web 平台：切换到 sqflite_common_ffi_web 数据库工厂
/// （sqlite3.wasm + shared worker + IndexedDB 持久化）。
Future<void> initPlatformDatabaseFactory() async {
  databaseFactory = databaseFactoryFfiWeb;
}
