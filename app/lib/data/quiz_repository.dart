/// 仓储层：所有数据库读写集中在此，UI/ViewModel 不直接碰 SQL
/// （沿用 schedule_app 的约定：UI → ViewModel → Repository → DB）
///
/// 历史：早期为单一 1260 行 God 类。现按职责把方法拆分到 `part` 文件中的
/// mixin（_SettingsMixin / _QuestionsMixin / _SrsMixin / _MockMixin / _ExportMixin），
/// 公开方法签名与行为完全不变，UI 与上层调用无需任何改动。
library;

import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fsrs/fsrs.dart' show Card;
import 'package:sqflite/sqflite.dart';

import '../models/models.dart';
import 'app_database.dart';
import 'grading.dart';
import 'seed_loader.dart';
import 'srs_service.dart';

part 'quiz_repository_settings.dart';
part 'quiz_repository_questions.dart';
part 'quiz_repository_knowledge.dart';
part 'quiz_repository_srs.dart';
part 'quiz_repository_mock.dart';
part 'quiz_repository_export.dart';

/// 数据库单例 provider
final databaseProvider = Provider<Future<Database>>(
  (ref) => AppDatabase.instance,
);

/// 仓储 provider
final quizRepositoryProvider = Provider<Future<QuizRepository>>((ref) async {
  final db = await ref.watch(databaseProvider);
  return QuizRepository(db);
});

/// SRS 调度服务 provider
final srsProvider = Provider<Future<SrsService>>((ref) async {
  final db = await ref.watch(databaseProvider);
  return SrsService(db);
});

/// 所有 mixin 共享的抽象基类：持有 [_db]，并声明被其它 mixin 间接调用的抽象成员，
/// 使 `this.xxx()` 跨 mixin 调用可被静态分析解析（避免 mixin 直接 `on QuizRepository`
/// 造成的递归接口继承）。
abstract class RepositoryMixinBase {
  RepositoryMixinBase(this._db);

  final Database _db;

  // 跨 mixin 调用的方法声明（具体实现分布在对应 mixin 中）
  Future<String?> setting(String key);
  Future<String?> importedVersion(String bankId);
  Future<int> dueCount({DateTime? now, String? bankId});
}

class QuizRepository extends RepositoryMixinBase with
    _SettingsMixin,
    _QuestionsMixin,
    _KnowledgeMixin,
    _SrsMixin,
    _MockMixin,
    _ExportMixin {
  QuizRepository(super._db);

  // 与 UI 约定的静态常量/键（定义在 QuizRepository 上，供上层静态访问）
  static const practiceTimerVisibleKey = 'show_practice_timer';
  static String practiceProgressKey(String key) => 'practice_progress:$key';
  static String practiceResultsKey(String key) => 'practice_results:$key';
  static const wrongBookRetireThreshold = 2;

  /// 题库包导入（委托 SeedLoader）
  Future<ImportResult> importBank(BankPack pack) =>
      SeedLoader.import(_db, pack);
}

/// 题库包概要信息（设置页展示）
class BankInfo {
  const BankInfo({
    required this.bankId,
    required this.name,
    required this.version,
    required this.total,
    required this.active,
    required this.archived,
    this.userEdited = 0,
    this.hidden = false,
  });

  final String bankId;
  final String name;
  final String version;
  final int total;
  final int active;
  final int archived;

  /// 本地修改题数（user_edited=1，更新时保留用户版本）
  final int userEdited;

  /// 是否被用户卸载/隐藏（内置式题库更新自动导入跳过）
  final bool hidden;
}
