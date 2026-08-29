# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ---------- 1) models.dart: BankManifest 加 idSchema ----------
p1 = r'D:\study_app\app\lib\models\models.dart'
s1 = open(p1, encoding='utf-8').read()

old_ctor = """  const BankManifest({
    required this.formatVersion,
    required this.bankId,
    required this.name,
    required this.version,
    this.chapterGroups = const [],
    this.knowledge = const [],
    this.overviews = const [],
  });

  final int formatVersion;
  final String bankId;
  final String name;
  final String version;"""

new_ctor = """  const BankManifest({
    required this.formatVersion,
    required this.bankId,
    required this.name,
    required this.version,
    this.idSchema,
    this.chapterGroups = const [],
    this.knowledge = const [],
    this.overviews = const [],
  });

  final int formatVersion;
  final String bankId;
  final String name;
  final String version;

  /// 题 id 体系标识（v1.1.3）：v0.12 起为 'q-b'（题 id 用 q_/b_ 前缀）；
  /// 旧包（v0.11 及更早，kb_ 前缀）无此字段。idSchema 变化 = 不兼容升级，
  /// 导入时整库重建（见 seed_loader），避免旧题被整批软归档堆积。
  final String? idSchema;"""

if old_ctor not in s1:
    print('ERROR: BankManifest ctor block not found')
    sys.exit(1)
s1 = s1.replace(old_ctor, new_ctor, 1)

old_json = """      formatVersion: json['formatVersion'] as int,
      bankId: json['bankId'] as String,
      name: json['name'] as String,
      version: json['version'] as String,"""
new_json = """      formatVersion: json['formatVersion'] as int,
      bankId: json['bankId'] as String,
      name: json['name'] as String,
      version: json['version'] as String,
      idSchema: json['idSchema'] as String?,"""
if old_json not in s1:
    print('ERROR: BankManifest fromJson block not found')
    sys.exit(1)
s1 = s1.replace(old_json, new_json, 1)
open(p1, 'w', encoding='utf-8').write(s1)
print('OK: models.dart BankManifest.idSchema added')

# ---------- 2) seed_loader.dart: import() 加不兼容重建 ----------
p2 = r'D:\study_app\app\lib\data\seed_loader.dart'
s2 = open(p2, encoding='utf-8').read()

old_head = """    await db.transaction((txn) async {
      // 用户本地修改保护（v8）：user_edited=1 的题保留本地版本，
      // 内置式题库更新导入时跳过 REPLACE，避免覆盖用户修改
      final editedRows = await txn.query("""

new_head = """    await db.transaction((txn) async {
      // 不兼容升级重建（v1.1.3）：idSchema 变化（如 v0.11 kb_ 前缀 → v0.12 q_/b_ 前缀）
      // 时，整库清空再导入，避免旧 id 题被整批软归档堆积、且学习记录挂旧 id 无法匹配。
      // 兼容升级（idSchema 相同 / 老包无 idSchema）走下方 upsert + 软归档，保留作答记录。
      final newSchema = pack.manifest.idSchema;
      if (newSchema != null) {
        final schemaRows = await txn.query(
          'settings',
          columns: ['value'],
          where: 'key = ?',
          whereArgs: ['bank_${pack.manifest.bankId}_id_schema'],
        );
        final storedSchema = schemaRows.isEmpty
            ? null
            : schemaRows.first['value'] as String?;
        if (storedSchema == null ||
            storedSchema.isEmpty ||
            storedSchema != newSchema) {
          // 整库重建：先清关联数据（作答/调度/错题排除/审题标记/模拟卷）再清题。
          // 知识点树与章节概览在下方统一按 bank 清旧重写，无需在此处理。
          await txn.delete('answer_logs',
              where: 'question_id IN (SELECT id FROM questions WHERE bank_id = ?)',
              whereArgs: [pack.manifest.bankId]);
          await txn.delete('card_scheduling',
              where: 'question_id IN (SELECT id FROM questions WHERE bank_id = ?)',
              whereArgs: [pack.manifest.bankId]);
          await txn.delete('wrong_book_exclusions',
              where: 'question_id IN (SELECT id FROM questions WHERE bank_id = ?)',
              whereArgs: [pack.manifest.bankId]);
          await txn.delete('review_flags',
              where: 'bank_id = ?', whereArgs: [pack.manifest.bankId]);
          await txn.delete('mock_sessions',
              where: 'paper_id IN (SELECT id FROM mock_papers WHERE bank_id = ?)',
              whereArgs: [pack.manifest.bankId]);
          await txn.delete('mock_papers',
              where: 'bank_id = ?', whereArgs: [pack.manifest.bankId]);
          await txn.delete('questions',
              where: 'bank_id = ?', whereArgs: [pack.manifest.bankId]);
        }
      }
      // 用户本地修改保护（v8）：user_edited=1 的题保留本地版本，
      // 内置式题库更新导入时跳过 REPLACE，避免覆盖用户修改
      final editedRows = await txn.query("""

if old_head not in s2:
    print('ERROR: seed_loader transaction head not found')
    sys.exit(1)
s2 = s2.replace(old_head, new_head, 1)

# 导入末尾写 id_schema（在写 version/name 之后）
old_meta = """      await txn.insert('settings', {
        'key': 'bank_${pack.manifest.bankId}_name',
        'value': pack.manifest.name,
      }, conflictAlgorithm: ConflictAlgorithm.replace);"""

new_meta = """      await txn.insert('settings', {
        'key': 'bank_${pack.manifest.bankId}_name',
        'value': pack.manifest.name,
      }, conflictAlgorithm: ConflictAlgorithm.replace);
      // idSchema（v1.1.3）：记录本次导入的题 id 体系，用于不兼容升级判断
      await txn.insert('settings', {
        'key': 'bank_${pack.manifest.bankId}_id_schema',
        'value': pack.manifest.idSchema ?? '',
      }, conflictAlgorithm: ConflictAlgorithm.replace);"""

if old_meta not in s2:
    print('ERROR: seed_loader meta block not found')
    sys.exit(1)
s2 = s2.replace(old_meta, new_meta, 1)
open(p2, 'w', encoding='utf-8').write(s2)
print('OK: seed_loader.dart rebuild logic added')
