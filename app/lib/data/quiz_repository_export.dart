part of 'quiz_repository.dart';

/// 存档类型：手动导出（跨端流转）/ 自动存档（本地保险）
enum ArchiveKind { manual, auto }

/// 存档解析预览（导入确认前展示，不写库）
class ArchivePreview {
  ArchivePreview({
    required this.formatVersion,
    this.exportedAt,
    this.kind,
    this.bankVersions = const {},
    this.bankMismatches = const [],
  });

  final int formatVersion;
  final String? exportedAt;
  final ArchiveKind? kind;

  /// 存档记录的题库版本 {bankId: version}
  final Map<String, String> bankVersions;

  /// 与本地题库版本不一致/未安装的题库提示（导入确认时展示）
  final List<String> bankMismatches;
}

/// 存档恢复结果
class RestoreResult {
  RestoreResult({
    this.restoredLogs = 0,
    this.restoredCards = 0,
    this.bankMismatches = const [],
  });

  final int restoredLogs;
  final int restoredCards;
  final List<String> bankMismatches;
}

/// 当前 App 版本（写入存档 appVersion，供展示；打包时更新）
const String kArchiveAppVersion = '1.2.0';

/// 数据维护（题库清单/清理归档）、存档导出与恢复、审题标记
mixin _ExportMixin on RepositoryMixinBase {
  /// 已导入题库包（含已归档题）的清单
  /// [includeHidden] = true 时包含被用户卸载/隐藏的库（设置页管理用）；
  /// 首页默认过滤隐藏库。
  Future<List<BankInfo>> banks({bool includeHidden = false}) async {
    final rows = await _db.rawQuery('''
      SELECT bank_id,
             COUNT(*) AS total,
             SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active,
             SUM(CASE WHEN user_edited = 1 THEN 1 ELSE 0 END) AS edited
      FROM questions GROUP BY bank_id ORDER BY bank_id
    ''');
    final result = <BankInfo>[];
    for (final r in rows) {
      final bankId = r['bank_id'] as String;
      final hidden = await setting('bank_${bankId}_hidden') == 'true';
      if (hidden && !includeHidden) continue;
      result.add(
        BankInfo(
          bankId: bankId,
          name: await setting('bank_${bankId}_name') ?? bankId,
          version: await importedVersion(bankId) ?? '',
          total: r['total'] as int,
          active: (r['active'] as int?) ?? 0,
          archived: (r['total'] as int) - ((r['active'] as int?) ?? 0),
          userEdited: (r['edited'] as int?) ?? 0,
          hidden: hidden,
        ),
      );
    }
    return result;
  }

  /// 彻底清理某题库包的已归档题（删除题与其作答历史；设计方案 §3.4）
  Future<int> purgeArchived(String bankId) async {
    final rows = await _db.rawQuery(
      "SELECT id FROM questions WHERE bank_id = ? AND status = 'archived'",
      [bankId],
    );
    final ids = rows.map((r) => r['id'] as String).toList();
    await _db.transaction((txn) async {
      for (final id in ids) {
        await txn.delete(
          'answer_logs',
          where: 'question_id = ?',
          whereArgs: [id],
        );
        await txn.delete(
          'card_scheduling',
          where: 'question_id = ?',
          whereArgs: [id],
        );
        await txn.delete(
          'wrong_book_exclusions',
          where: 'question_id = ?',
          whereArgs: [id],
        );
        await txn.delete('questions', where: 'id = ?', whereArgs: [id]);
      }
    });
    return ids.length;
  }

  // ============ 存档 v3（多端文件存档，多端同步实施方案 §2） ============

  /// 导出当前全部**用户状态**为压缩存档（zip 内 archive.json）。
  ///
  /// - formatVersion=3，只含用户状态（做题记录/调度/背题/错题/模拟考/审题标记/设置），
  ///   **不含题库**（题库以 App 内置包为准，见方案 §2.5）；
  /// - 带 [ArchiveKind]（manual 跨端流转 / auto 本地保险）与题库版本清单（跨端校验）。
  Future<Uint8List> exportArchive({
    ArchiveKind kind = ArchiveKind.manual,
  }) async {
    final json = const JsonEncoder.withIndent('  ').convert(
      await _archivePayload(kind),
    );
    final archive = Archive()
      ..addFile(ArchiveFile.string('archive.json', json));
    final bytes = ZipEncoder().encode(archive);
    return Uint8List.fromList(bytes);
  }

  Future<Map<String, dynamic>> _archivePayload(ArchiveKind kind) async {
    final logs = await _db.query('answer_logs', orderBy: 'id');
    final cards = await _db.query('card_scheduling', orderBy: 'question_id');
    final memos = await _db.query('memorize_progress', orderBy: 'card_key');
    final exclusions = await _db.query(
      'wrong_book_exclusions',
      orderBy: 'question_id',
    );
    final papers = await _db.query('mock_papers', orderBy: 'id');
    final sessions = await _db.query('mock_sessions', orderBy: 'id');
    final flags = await _db.query('review_flags', orderBy: 'question_id');
    final settings = await _db.query('settings');
    final bankRows =
        await _db.query('questions', columns: ['bank_id'], distinct: true);
    final bankVersions = <String, String>{};
    for (final b in bankRows) {
      final bid = b['bank_id'] as String;
      final v = await importedVersion(bid);
      if (v != null) bankVersions[bid] = v;
    }
    return {
      'formatVersion': 3,
      'exportedAt': DateTime.now().toIso8601String(),
      'appVersion': kArchiveAppVersion,
      'kind': kind.name,
      'bankVersions': bankVersions,
      'userState': {
        'answerLogs': logs,
        'cardScheduling': cards,
        'memorizeProgress': memos,
        'wrongBookExclusions': exclusions,
        'mockPapers': papers,
        'mockSessions': sessions,
        'reviewFlags': flags,
        'settings': settings,
      },
    };
  }

  /// 解析存档/旧备份，返回预览（不写库）。导入确认前调用。
  ///
  /// 自动识别 zip（PK 魔数）与 v1/v2 纯 JSON 文本；v1/v2 兼容解析。
  Future<ArchivePreview> parseArchive(Uint8List bytes) async {
    final data = await _decodeArchive(bytes);
    final version = data['formatVersion'];
    if (version is! int || version < 1 || version > 3) {
      throw FormatException('存档格式版本不受支持: $version');
    }
    if (version == 3) {
      final userState = data['userState'];
      if (userState is! Map) throw FormatException('存档缺少 userState');
      for (final key in [
        'answerLogs',
        'cardScheduling',
        'memorizeProgress',
        'settings',
      ]) {
        if (userState[key] is! List) throw FormatException('存档缺少字段: $key');
      }
    } else {
      for (final key in ['answerLogs', 'cardScheduling', 'settings']) {
        if (data[key] is! List) throw FormatException('备份缺少字段: $key');
      }
    }
    final bankVersions = <String, String>{};
    final bv = data['bankVersions'];
    if (bv is Map) {
      bv.forEach((k, v) {
        if (k is String && v is String) bankVersions[k] = v;
      });
    }
    final mismatches = <String>[];
    for (final e in bankVersions.entries) {
      final local = await importedVersion(e.key);
      if (local == null) {
        mismatches.add('${e.key}（本地未安装该题库）');
      } else if (local != e.value) {
        mismatches.add('${e.key}（存档 v${e.value} vs 本地 v$local）');
      }
    }
    return ArchivePreview(
      formatVersion: version,
      exportedAt: data['exportedAt'] as String?,
      kind: _archiveKindFrom(data['kind']),
      bankVersions: bankVersions,
      bankMismatches: mismatches,
    );
  }

  static ArchiveKind? _archiveKindFrom(Object? value) {
    if (value is! String) return null;
    for (final k in ArchiveKind.values) {
      if (k.name == value) return k;
    }
    return null;
  }

  /// 从存档恢复：全量覆盖**用户状态**（做题记录/调度/背题/错题/模拟考/审题标记/设置）。
  ///
  /// - **不动 questions 表**（题库以 App 内置包为准，多端方案 §2.5）；
  /// - 事务内整体回滚：任何一步失败都不落库，杜绝损坏文件静默清空数据；
  /// - 兼容 v1/v2 旧备份（自动识别，v1/v2 忽略其题目字段只恢复用户状态）。
  Future<RestoreResult> restoreArchive(Uint8List bytes) async {
    final data = await _decodeArchive(bytes);
    final version = data['formatVersion'];
    if (version is! int || version < 1 || version > 3) {
      throw FormatException('存档格式版本不受支持: $version');
    }
    if (version == 3) {
      final userState = data['userState'];
      if (userState is! Map) throw FormatException('存档缺少 userState');
      for (final key in [
        'answerLogs',
        'cardScheduling',
        'memorizeProgress',
        'settings',
      ]) {
        if (userState[key] is! List) throw FormatException('存档缺少字段: $key');
      }
    } else {
      for (final key in ['answerLogs', 'cardScheduling', 'settings']) {
        if (data[key] is! List) throw FormatException('备份缺少字段: $key');
      }
    }
    // 题库版本比对（数据层不阻止，UI 已用 parseArchive 先行提示）
    final bankVersions = <String, String>{};
    final bv = data['bankVersions'];
    if (bv is Map) {
      bv.forEach((k, v) {
        if (k is String && v is String) bankVersions[k] = v;
      });
    }
    final mismatches = <String>[];
    for (final e in bankVersions.entries) {
      final local = await importedVersion(e.key);
      if (local == null || local != e.value) {
        mismatches.add(e.key);
      }
    }

    final userState =
        version == 3 ? (data['userState'] as Map) : data;

    int restoredLogs = 0;
    int restoredCards = 0;
    await _db.transaction((txn) async {
      await txn.delete('answer_logs');
      await txn.delete('card_scheduling');
      await txn.delete('memorize_progress');
      await txn.delete('wrong_book_exclusions');
      await txn.delete('mock_sessions');
      await txn.delete('mock_papers');
      await txn.delete('review_flags');
      await txn.delete('settings');
      // 注意：不删/不写 questions（题库以本地内置包为准）

      final logs = _listOf(userState, 'answerLogs');
      for (final l in logs) {
        await txn.insert('answer_logs', l);
      }
      restoredLogs = logs.length;

      final cards = _listOf(userState, 'cardScheduling');
      for (final c in cards) {
        await txn.insert(
          'card_scheduling',
          c,
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }
      restoredCards = cards.length;

      final memos = _listOf(userState, 'memorizeProgress');
      for (final m in memos) {
        await txn.insert(
          'memorize_progress',
          m,
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }

      final exclusions = _listOf(userState, 'wrongBookExclusions');
      for (final e in exclusions) {
        await txn.insert(
          'wrong_book_exclusions',
          e,
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }

      final papers = _listOf(userState, 'mockPapers');
      for (final p in papers) {
        await txn.insert(
          'mock_papers',
          p,
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }

      final sessions = _listOf(userState, 'mockSessions');
      for (final s in sessions) {
        await txn.insert('mock_sessions', s);
      }

      final flags = _listOf(userState, 'reviewFlags');
      for (final f in flags) {
        await txn.insert(
          'review_flags',
          f,
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }

      final settings = _listOf(userState, 'settings');
      for (final s in settings) {
        await txn.insert(
          'settings',
          s,
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }
    });
    return RestoreResult(
      restoredLogs: restoredLogs,
      restoredCards: restoredCards,
      bankMismatches: mismatches,
    );
  }

  static List<Map<String, dynamic>> _listOf(Map state, String key) =>
      ((state[key] as List<dynamic>?) ?? const [])
          .cast<Map<String, dynamic>>();

  /// 解析存档字节：zip（PK 魔数）解压出 archive.json，否则按纯 JSON 文本解析。
  Future<Map<String, dynamic>> _decodeArchive(Uint8List bytes) async {
    final isZip = bytes.length >= 4 &&
        bytes[0] == 0x50 &&
        bytes[1] == 0x4B &&
        bytes[2] == 0x03 &&
        bytes[3] == 0x04;
    if (isZip) {
      final archive = ZipDecoder().decodeBytes(bytes);
      ArchiveFile? file;
      for (final f in archive.files) {
        if (f.name == 'archive.json') {
          file = f;
          break;
        }
      }
      if (file == null) throw FormatException('存档缺少 archive.json');
      return jsonDecode(utf8.decode(file.content)) as Map<String, dynamic>;
    }
    return jsonDecode(utf8.decode(bytes)) as Map<String, dynamic>;
  }

  /// 导出全部数据为 JSON 文本（v2 备份，向后兼容；新功能请用 [exportArchive]）
  ///
  /// 导出净化：剥离思源块溯源字段（所有题型），并移除简答题的解析字段，
  /// 避免导出文件携带出题来源的块信息。
  @Deprecated('使用 exportArchive（v3 压缩存档）替代')
  Future<String> exportJson() async {
    final rawQuestions = await _db.query('questions', orderBy: 'id');
    final questions = [
      for (final r in rawQuestions)
        _sanitizedExportQuestion(Map<String, dynamic>.from(r)),
    ];
    final logs = await _db.query('answer_logs', orderBy: 'id');
    final cards = await _db.query('card_scheduling', orderBy: 'question_id');
    final exclusions = await _db.query(
      'wrong_book_exclusions',
      orderBy: 'question_id',
    );
    final papers = await _db.query('mock_papers', orderBy: 'id');
    final sessions = await _db.query('mock_sessions', orderBy: 'id');
    final settings = await _db.query('settings');
    return const JsonEncoder.withIndent('  ').convert({
      'formatVersion': 2,
      'exportedAt': DateTime.now().toIso8601String(),
      'questions': questions,
      'answerLogs': logs,
      'cardScheduling': cards,
      'wrongBookExclusions': exclusions,
      'mockPapers': papers,
      'mockSessions': sessions,
      'settings': settings,
    });
  }

  /// 导出时剥离敏感/冗余字段：
  /// - 所有题型移除思源块溯源（source_block_id / source_doc_path）；
  /// - 简答题（short_answer）额外移除解析（explanation）。
  Map<String, dynamic> _sanitizedExportQuestion(Map<String, dynamic> row) {
    row.remove('source_block_id');
    row.remove('source_doc_path');
    if (row['type'] == 'short_answer') {
      row.remove('explanation');
    }
    return row;
  }

  /// 从 v2 备份 JSON 文本恢复（向后兼容旧入口；新功能请用 [restoreArchive]）。
  ///
  /// 注意：v2 备份含题目字段，此处忽略题目、只恢复用户状态，
  /// 与 v3 行为统一（题库以本地内置包为准，多端方案 §2.5）。
  @Deprecated('使用 restoreArchive（支持 zip/json 自动识别）替代')
  Future<void> restoreJson(String jsonText) async {
    final bytes = Uint8List.fromList(utf8.encode(jsonText));
    await restoreArchive(bytes);
  }

  /// 标记一道题为"待审/需修改"，返回是否为新标记（true=新增，false=已存在）
  Future<bool> flagQuestion(
    String questionId,
    String bankId, {
    String? comment,
  }) async {
    final count = await _db.insert(
      'review_flags',
      {
        'question_id': questionId,
        'bank_id': bankId,
        'comment': comment,
        'created_at': DateTime.now().millisecondsSinceEpoch,
      },
      // ignore：已标记的题跳过（保留原 comment/created_at），0=已存在
      conflictAlgorithm: ConflictAlgorithm.ignore,
    );
    return count > 0;
  }

  /// 取消一道题的标记
  Future<void> unflagQuestion(String questionId) async {
    await _db.delete(
      'review_flags',
      where: 'question_id = ?',
      whereArgs: [questionId],
    );
  }

  /// 判断某题是否已标记
  Future<bool> isFlagged(String questionId) async {
    final rows = await _db.query(
      'review_flags',
      columns: ['question_id'],
      where: 'question_id = ?',
      whereArgs: [questionId],
      limit: 1,
    );
    return rows.isNotEmpty;
  }

  /// 全部标记清单（含题干快照，便于导出）
  Future<List<Map<String, dynamic>>> reviewFlags() async {
    final rows = await _db.rawQuery(
      "SELECT r.question_id, r.bank_id, r.comment, r.created_at, "
      "q.stem, q.chapter, q.type FROM review_flags r "
      "LEFT JOIN questions q ON q.id = r.question_id "
      "ORDER BY r.created_at DESC",
    );
    return rows;
  }

  /// 导出审题标记为 JSON 文本（含题干快照，供回传修改）
  Future<String> exportReviewFlags() async {
    final rows = await reviewFlags();
    return const JsonEncoder.withIndent('  ').convert({
      'exportedAt': DateTime.now().toIso8601String(),
      'count': rows.length,
      'flags': rows,
    });
  }

  /// 清空全部标记
  Future<void> clearReviewFlags() async {
    await _db.delete('review_flags');
  }
}
