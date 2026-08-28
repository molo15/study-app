/// 题库包加载与导入（设计方案 §3.4）
///
/// 支持两种容器：
/// - 单 JSON 文件（开发期/示例）：顶层即 manifest 字段 + questions 数组；
/// - zip 容器（生产格式，M4 打包含并）：manifest.json + questions.json + media/，
///   通过 [parseZipBytes] 解析，DB 导入逻辑共用。
library;

import 'dart:convert';

import 'package:archive/archive.dart';
import 'package:sqflite/sqflite.dart';

import '../models/models.dart';

/// 一个已解析的题库包（清单 + 题目列表）
class BankPack {
  const BankPack({
    required this.manifest,
    required this.questions,
    this.mockPapers = const [],
  });

  final BankManifest manifest;
  final List<Question> questions;

  /// 模拟卷（需求：formatVersion=2 起支持）
  final List<MockPaper> mockPapers;
}

/// 导入结果摘要
class ImportResult {
  const ImportResult({
    required this.bankId,
    required this.version,
    required this.imported,
    required this.archived,
  });

  final String bankId;
  final String version;
  final int imported;
  final int archived;

  @override
  String toString() =>
      '题库包 $bankId v$version：新增/更新 $imported 题，归档 $archived 题';
}

class SeedLoader {
  /// 解析单 JSON 题库包文本（审查 P2-14：剥离 UTF-8 BOM）
  static BankPack parse(String jsonText) {
    final text = jsonText.startsWith('\uFEFF') ? jsonText.substring(1) : jsonText;
    return parseMap(jsonDecode(text) as Map<String, dynamic>);
  }

  /// 仅读取 zip 包的 manifest 版本（轻量，不解析题目）。
  /// 内置题库启动同步用：版本不一致才全量 parseZipBytes + import（性能优化）。
  static String? manifestVersionFromZipBytes(List<int> bytes) {
    final archive = ZipDecoder().decodeBytes(bytes);
    final file = archive.files.firstWhere(
      (f) => f.isFile && f.name == 'manifest.json',
      orElse: () => throw FormatException('题库包缺少文件: manifest.json'),
    );
    var text = utf8.decode(file.content as List<int>);
    if (text.startsWith('\uFEFF')) text = text.substring(1);
    final map = jsonDecode(text) as Map<String, dynamic>;
    return map['version'] as String?;
  }

  /// 解析 zip 题库包（manifest.json + questions.json + media/，设计方案 §2.4）
  static BankPack parseZipBytes(List<int> bytes) {
    final archive = ZipDecoder().decodeBytes(bytes);
    String readText(String name) {
      final file = archive.files.firstWhere(
        (f) => f.isFile && f.name == name,
        orElse: () => throw FormatException('题库包缺少文件: $name'),
      );
      // 审查 P2-14：剥离 UTF-8 BOM
      var text = utf8.decode(file.content as List<int>);
      if (text.startsWith('\uFEFF')) text = text.substring(1);
      return text;
    }

    final manifestMap = jsonDecode(readText('manifest.json')) as Map<String, dynamic>;
    final manifest = BankManifest.fromJson(manifestMap);
    manifest.validate();
    // v3：questions/ 目录多文件（每章一个）；v2：单 questions.json
    final List<Question> questions;
    final questionFiles = archive.files
        .where((f) => f.isFile && f.name.startsWith('questions/') && f.name.endsWith('.json'))
        .toList();
    if (questionFiles.isNotEmpty) {
      final merged = <Question>[];
      for (final f in questionFiles) {
        // 审查 P2-14：与其它 JSON 读取路径一致，剥离 UTF-8 BOM
        var text = utf8.decode(f.content as List<int>);
        if (text.startsWith('\uFEFF')) text = text.substring(1);
        final items = jsonDecode(text) as List<dynamic>;
        merged.addAll(items
            .map((e) => Question.fromBankJson(e as Map<String, dynamic>, bankId: manifest.bankId))
            .map(_ensureTrueFalseOptions));
      }
      questions = merged;
    } else {
      questions = (jsonDecode(readText('questions.json')) as List<dynamic>)
          .map((e) => Question.fromBankJson(e as Map<String, dynamic>, bankId: manifest.bankId))
          .map(_ensureTrueFalseOptions) // 审查 P2-A：与 parseMap 路径一致
          .toList();
    }
    final mockPapers = (manifestMap['mockPapers'] as List<dynamic>? ?? const [])
        .map((e) => MockPaper.fromBankJson(e as Map<String, dynamic>, bankId: manifest.bankId))
        .toList();
    return BankPack(
      manifest: manifest,
      questions: questions,
      mockPapers: mockPapers,
    );
  }

  /// 从已解码的 map 构造题库包（单 JSON 与 zip 的 questions.json 共用）
  static BankPack parseMap(Map<String, dynamic> map) {
    final manifest = BankManifest.fromJson(map);
    manifest.validate();
    final questions = (map['questions'] as List<dynamic>)
        .map((e) => Question.fromBankJson(e as Map<String, dynamic>, bankId: manifest.bankId))
        .map(_ensureTrueFalseOptions)
        .toList();
    final mockPapers = (map['mockPapers'] as List<dynamic>? ?? const [])
        .map((e) => MockPaper.fromBankJson(e as Map<String, dynamic>, bankId: manifest.bankId))
        .toList();
    return BankPack(
      manifest: manifest,
      questions: questions,
      mockPapers: mockPapers,
    );
  }

  /// 判断题若题库包未提供选项，强制补齐「正确/错误」（审查 P0-1）
  static Question _ensureTrueFalseOptions(Question q) {
    if (q.type == QuestionType.trueFalse && q.options.isEmpty) {
      return q.copyWith(
        options: const [
          QuestionOption(key: '正确', text: '正确'),
          QuestionOption(key: '错误', text: '错误'),
        ],
      );
    }
    return q;
  }

  /// 空章节兜底：未声明章节的题归入「未分类」（需求：章节系统自动划分）
  static const defaultChapter = '未分类';

  /// 幂等导入：按稳定 id upsert；同 bank_id 下不在新包中的题软归档为
  /// archived（保留作答历史，设计方案 §3.4「题目删除语义」）；记录导入版本。
  ///
  /// 审查修复：NOT IN 按 500 一批分块，避免占位符超 SQLITE_MAX_VARIABLE_NUMBER
  /// （老设备 999，超大题库导入崩溃，P1-1）；包内重复 id 去重并校验 {bankId}: 前缀（P2-7）。
  static Future<ImportResult> import(Database db, BankPack pack) async {
    final now = DateTime.now().millisecondsSinceEpoch;
    // 去重 + 前缀校验 + 章节兜底
    final byId = <String, Question>{};
    for (final q in pack.questions) {
      if (!q.id.startsWith('${pack.manifest.bankId}:')) {
        throw FormatException('题目 id「${q.id}」不符合 {bankId}:{序号} 约定，拒绝导入');
      }
      final chapter = q.chapter.trim().isEmpty ? defaultChapter : q.chapter.trim();
      // 用 copyWith 保留全部字段（含 answerFormat——修复：重建漏字段 bug）
      byId[q.id] = q.copyWith(chapter: chapter); // 后出现的覆盖先出现的（与 upsert 语义一致）
    }
    final questions = byId.values.toList();
    final ids = byId.keys.toSet();
    var imported = 0;
    var archivedCount = 0;

    await db.transaction((txn) async {
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
      final editedRows = await txn.query(
        'questions',
        columns: ['id'],
        where: 'bank_id = ? AND user_edited = 1',
        whereArgs: [pack.manifest.bankId],
      );
      final editedIds = editedRows.map((r) => r['id'] as String).toSet();
      for (final q in questions) {
        if (editedIds.contains(q.id)) {
          // 保留本地修改：不覆盖内容，但恢复可见性（若此前被软归档，审查修复）
          await txn.update(
            'questions',
            {'status': 'active', 'updated_at': now},
            where: 'id = ?',
            whereArgs: [q.id],
          );
          continue;
        }
        await txn.insert('questions', q.toMap()..['status'] = 'active',
            conflictAlgorithm: ConflictAlgorithm.replace);
        imported++;
      }
      // 软归档：同库内不在新包 id 集中的 active 题（空包跳过，P1-1）。
      // 先取全量 active id，Dart 侧求差集，再逐条归档——
      // 彻底绕开 NOT IN 占位符数量上限（SQLITE_MAX_VARIABLE_NUMBER，P1-1）
      if (ids.isNotEmpty) {
        final activeRows = await txn.query('questions',
            columns: ['id'],
            where: "bank_id = ? AND status = 'active'",
            whereArgs: [pack.manifest.bankId]);
        final archivedIds =
            activeRows.map((r) => r['id'] as String).where((id) => !ids.contains(id));
        for (final id in archivedIds) {
          await txn.update('questions', {'status': 'archived', 'updated_at': now},
              where: 'id = ?', whereArgs: [id]);
          archivedCount++;
        }
      }
      // 模拟卷 upsert + 软归档（需求：题库含模拟卷可导入）
      final paperIds = <String>{};
      for (final paper in pack.mockPapers) {
        if (!paper.id.startsWith('${pack.manifest.bankId}:')) {
          throw FormatException('模拟卷 id「${paper.id}」不符合 {bankId}:{序号} 约定，拒绝导入');
        }
        paperIds.add(paper.id);
        await txn.insert('mock_papers', paper.toMap()..['status'] = 'active',
            conflictAlgorithm: ConflictAlgorithm.replace);
      }
      if (paperIds.isNotEmpty) {
        final activePapers = await txn.query('mock_papers',
            columns: ['id'],
            where: "bank_id = ? AND status = 'active'",
            whereArgs: [pack.manifest.bankId]);
        for (final row in activePapers) {
          final id = row['id'] as String;
          if (!paperIds.contains(id)) {
            await txn.update('mock_papers', {'status': 'archived', 'updated_at': now},
                where: 'id = ?', whereArgs: [id]);
          }
        }
      }
      await txn.insert('settings', {
        'key': 'bank_${pack.manifest.bankId}_version',
        'value': pack.manifest.version,
      }, conflictAlgorithm: ConflictAlgorithm.replace);
      await txn.insert('settings', {
        'key': 'bank_${pack.manifest.bankId}_name',
        'value': pack.manifest.name,
      }, conflictAlgorithm: ConflictAlgorithm.replace);
      // idSchema（v1.1.3）：记录本次导入的题 id 体系，用于不兼容升级判断
      await txn.insert('settings', {
        'key': 'bank_${pack.manifest.bankId}_id_schema',
        'value': pack.manifest.idSchema ?? '',
      }, conflictAlgorithm: ConflictAlgorithm.replace);
      // 章节分组元数据（v3 两级；旧包单个"全部"分组）——供章节树展示
      await txn.insert('settings', {
        'key': 'bank_${pack.manifest.bankId}_groups',
        'value': const JsonEncoder().convert(pack.manifest.chapterGroups
            .map((g) => {'group': g.group, 'chapters': g.chapters})
            .toList()),
      }, conflictAlgorithm: ConflictAlgorithm.replace);

      // 知识点树 + 章节概览（v4）：按 bank 清旧再写入当前包（旧包无此字段则不写）
      await txn.delete('knowledge_points',
          where: 'bank_id = ?', whereArgs: [pack.manifest.bankId]);
      for (final kp in pack.manifest.knowledge) {
        await txn.insert('knowledge_points', {
          'id': kp.id,
          'bank_id': pack.manifest.bankId,
          'name': kp.name,
          'chapter': kp.chapter,
          'parent': kp.parent,
          'summary': kp.summary,
          'hot': kp.hot ? 1 : 0,
          'exam_ref': kp.examRef,
          'question_count': kp.questionCount,
          'version': pack.manifest.version,
        }, conflictAlgorithm: ConflictAlgorithm.replace);
      }
      await txn.delete('chapter_overviews',
          where: 'bank_id = ?', whereArgs: [pack.manifest.bankId]);
      for (final ov in pack.manifest.overviews) {
        await txn.insert('chapter_overviews', {
          'bank_id': pack.manifest.bankId,
          'chapter': ov.chapter,
          'knowledge_count': ov.knowledgeCount,
          'question_count': ov.questionCount,
          'summary': ov.summary,
          'version': pack.manifest.version,
        }, conflictAlgorithm: ConflictAlgorithm.replace);
      }
    });

    return ImportResult(
      bankId: pack.manifest.bankId,
      version: pack.manifest.version,
      imported: imported,
      archived: archivedCount,
    );
  }
}
