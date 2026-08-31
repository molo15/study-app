/// 本地 SQLite 数据库：建表与升级（沿用 schedule_app 的 AppDatabase 模式）
library;

import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class AppDatabase {
  static const _dbName = 'quiz_app.db';
  static const _dbVersion = 11;

  /// 用 Future 缓存而不是单个 Database，避免并发访问时重复 open
  static Future<Database>? _instance;

  static Future<Database> get instance => _instance ??= _open();

  static Future<Database> _open() async {
    final dir = await getDatabasesPath();
    final path = join(dir, _dbName);
    return openDatabase(
      path,
      version: _dbVersion,
      onConfigure: configure,
      onCreate: createSchema,
      onUpgrade: _onUpgrade,
    );
  }

  /// 审查 P2-3：打开失败时清除缓存，允许下次重试（DB 损坏后自愈，而非永久复用失败 Future）
  static Future<Database> open() async {
    try {
      return await instance;
    } catch (_) {
      _instance = null;
      rethrow;
    }
  }

  /// 启用外键约束（注：当前各表的 question_id 未声明 REFERENCES，
  /// PRAGMA 无约束可施；保留开关供后续 DDL 补充外键时生效，审查 P2-9）
  static Future<void> configure(Database db) async {
    await db.execute('PRAGMA foreign_keys = ON');
  }

  static Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    if (oldVersion < 2) {
      // v2: card_scheduling 对齐 fsrs 2.0.1 的 Card 字段（M1 原型结构无实际数据，
      // 直接重建最干净）；并新增 wrong_book_exclusions 表
      await db.execute('DROP TABLE IF EXISTS card_scheduling');
      await db.execute(_cardSchedulingDdl);
      await db.execute(_wrongBookExclusionsDdl);
    }
    // 幂等补齐索引（对已升级到 v2 但缺新索引的库，审查 P2-2/P2-3）
    await db.execute('CREATE INDEX IF NOT EXISTS idx_sched_due ON card_scheduling(due)');
    await db.execute(
        'CREATE INDEX IF NOT EXISTS idx_logs_qid_result ON answer_logs(question_id, result)');
    if (oldVersion < 3) {
      // v3: 模拟卷系统（需求）+ answer_logs 关联会话
      // 审查 P2-2：先检查列是否存在，避免重跑 onUpgrade 时 duplicate column
      final cols = await db.rawQuery('PRAGMA table_info(answer_logs)');
      final hasSession = cols.any((c) => c['name'] == 'session_id');
      if (!hasSession) {
        await db.execute('ALTER TABLE answer_logs ADD COLUMN session_id INTEGER');
      }
      await db.execute(_mockPapersDdl);
      await db.execute(_mockSessionsDdl);
      // 审查 P2-1：升级路径补索引
      await db.execute('CREATE INDEX IF NOT EXISTS idx_mock_papers_bank ON mock_papers(bank_id)');
    }
    if (oldVersion < 4) {
      // v4: 题库包 formatVersion=3 —— questions 加 answer_format（简答答题格式提示）
      final qcols = await db.rawQuery('PRAGMA table_info(questions)');
      if (!qcols.any((c) => c['name'] == 'answer_format')) {
        await db.execute('ALTER TABLE questions ADD COLUMN answer_format TEXT');
      }
    }
    if (oldVersion < 5) {
      // v5: 等价答案判分 —— questions 加 answer_variants（填空按空/简答按要点的等价表述分组）
      final qcols = await db.rawQuery('PRAGMA table_info(questions)');
      if (!qcols.any((c) => c['name'] == 'answer_variants')) {
        await db.execute('ALTER TABLE questions ADD COLUMN answer_variants TEXT');
      }
    }
    if (oldVersion < 6) {
      // v6: 基础/测试双轨 —— questions 加 purpose（basic=基础题，test=测试题，空=普通练习）
      final qcols = await db.rawQuery('PRAGMA table_info(questions)');
      if (!qcols.any((c) => c['name'] == 'purpose')) {
        await db.execute('ALTER TABLE questions ADD COLUMN purpose TEXT');
      }
      await db.execute(
          'CREATE INDEX IF NOT EXISTS idx_questions_purpose ON questions(bank_id, chapter, purpose)');
    }
    if (oldVersion < 7) {
      // v7: 审题标记 —— review_flags 记录用户标记待审/需修改的题
      await db.execute(_reviewFlagsDdl);
      await db.execute(
          'CREATE INDEX IF NOT EXISTS idx_review_flags_qid ON review_flags(question_id)');
    }
    if (oldVersion < 8) {
      // v8: 用户本地修改保护 —— questions.user_edited 标记本地编辑过的题，
      // 内置式题库更新导入时跳过这些题（保留本地版本，不被 REPLACE 覆盖）
      final qcols = await db.rawQuery('PRAGMA table_info(questions)');
      if (!qcols.any((c) => c['name'] == 'user_edited')) {
        await db.execute(
            'ALTER TABLE questions ADD COLUMN user_edited INTEGER DEFAULT 0');
      }
      await db.execute(
          'CREATE INDEX IF NOT EXISTS idx_questions_user_edited ON questions(bank_id, user_edited)');
    }
    if (oldVersion < 9) {
      // v9: 题库包 formatVersion=4 —— questions 加 knowledge_id（绑定知识点树），
      // 新增 knowledge_points（知识点树）与 chapter_overviews（章节知识概览）
      final qcols = await db.rawQuery('PRAGMA table_info(questions)');
      if (!qcols.any((c) => c['name'] == 'knowledge_id')) {
        await db.execute('ALTER TABLE questions ADD COLUMN knowledge_id TEXT');
      }
      await db.execute(_knowledgePointsDdl);
      await db.execute(_chapterOverviewsDdl);
      await db.execute(
          'CREATE INDEX IF NOT EXISTS idx_questions_knowledge ON questions(knowledge_id)');
    }
    if (oldVersion < 10) {
      // v10: 模拟卷逐题回顾 —— answer_logs 加 user_answer（存用户作答快照）
      final acols = await db.rawQuery('PRAGMA table_info(answer_logs)');
      if (!acols.any((c) => c['name'] == 'user_answer')) {
        await db.execute('ALTER TABLE answer_logs ADD COLUMN user_answer TEXT');
      }
    }
    if (oldVersion < 11) {
      // v11: 背题存档 —— memorize_progress 记录知识点卡/题目卡的记忆状态（跨会话）
      await db.execute(_memorizeProgressDdl);
      await db.execute(
          'CREATE INDEX IF NOT EXISTS idx_memo_chapter ON memorize_progress(bank_id, chapter, card_type)');
    }
  }

  /// v7：审题标记表（用户逐题审查时标记"需修改/待复核"）
  static const _reviewFlagsDdl = '''
    CREATE TABLE IF NOT EXISTS review_flags(
      question_id TEXT PRIMARY KEY,
      bank_id TEXT NOT NULL,
      comment TEXT,
      created_at INTEGER NOT NULL
    )
  ''';

  /// v9：知识点树（manifest.knowledge，每科一包版本；更新时按版本清旧）
  static const _knowledgePointsDdl = '''
    CREATE TABLE IF NOT EXISTS knowledge_points(
      id TEXT PRIMARY KEY,
      bank_id TEXT NOT NULL,
      name TEXT NOT NULL,
      chapter TEXT NOT NULL,
      parent TEXT,
      summary TEXT,
      hot INTEGER DEFAULT 0,
      exam_ref TEXT,
      question_count INTEGER DEFAULT 0,
      version TEXT NOT NULL
    )
  ''';

  /// v9：章节知识概览（manifest.overviews）
  static const _chapterOverviewsDdl = '''
    CREATE TABLE IF NOT EXISTS chapter_overviews(
      bank_id TEXT NOT NULL,
      chapter TEXT NOT NULL,
      knowledge_count INTEGER DEFAULT 0,
      question_count INTEGER DEFAULT 0,
      summary TEXT,
      version TEXT NOT NULL,
      PRIMARY KEY (bank_id, chapter)
    )
  ''';

  /// v11：背题存档 —— 每张记忆卡一条记录（知识点卡 kp:xx / 题目卡 q:xx）
  static const _memorizeProgressDdl = '''
    CREATE TABLE IF NOT EXISTS memorize_progress(
      card_key TEXT PRIMARY KEY,
      bank_id TEXT NOT NULL,
      chapter TEXT NOT NULL,
      card_type TEXT NOT NULL,
      knowledge_id TEXT,
      question_id TEXT,
      state TEXT NOT NULL DEFAULT 'learning',
      correct_streak INTEGER DEFAULT 0,
      reviewed_count INTEGER DEFAULT 0,
      last_reviewed_at INTEGER,
      updated_at INTEGER
    )
  ''';

  static const _cardSchedulingDdl = '''
    CREATE TABLE card_scheduling(
      question_id TEXT PRIMARY KEY,
      state TEXT NOT NULL DEFAULT 'learning',
      step INTEGER,
      stability REAL,
      difficulty REAL,
      due INTEGER NOT NULL,
      last_review INTEGER,
      updated_at INTEGER
    )
  ''';

  static const _wrongBookExclusionsDdl = '''
    CREATE TABLE IF NOT EXISTS wrong_book_exclusions(
      question_id TEXT PRIMARY KEY,
      created_at INTEGER NOT NULL
    )
  ''';

  // v3：模拟卷（需求：题库含模拟卷可导入/刷卷）
  static const _mockPapersDdl = '''
    CREATE TABLE IF NOT EXISTS mock_papers(
      id TEXT PRIMARY KEY,
      bank_id TEXT NOT NULL,
      name TEXT NOT NULL,
      duration_min INTEGER NOT NULL,
      question_ids TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'active',
      created_at INTEGER,
      updated_at INTEGER
    )
  ''';

  static const _mockSessionsDdl = '''
    CREATE TABLE IF NOT EXISTS mock_sessions(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      paper_id TEXT NOT NULL,
      started_at INTEGER NOT NULL,
      duration_min INTEGER NOT NULL,
      total INTEGER NOT NULL,
      correct INTEGER NOT NULL,
      partial INTEGER NOT NULL,
      wrong INTEGER NOT NULL,
      skipped INTEGER NOT NULL,
      score INTEGER NOT NULL,
      submitted_at INTEGER NOT NULL
    )
  ''';

  /// 建表 + 索引（测试可复用于内存 DB：`createSchema(db, 2)`）
  static Future<void> createSchema(Database db, int version) async {
    // 题目表：id = {bank_id}:{序号}，全局唯一（设计方案 §3.3）
    await db.execute('''
      CREATE TABLE questions(
        id TEXT PRIMARY KEY,
        bank_id TEXT NOT NULL,
        type TEXT NOT NULL,
        stem TEXT NOT NULL,
        options TEXT,
        answer TEXT NOT NULL,
        explanation TEXT,
        chapter TEXT,
        tags TEXT,
        difficulty TEXT,
        status TEXT NOT NULL DEFAULT 'active',
        source_block_id TEXT,
        source_doc_path TEXT,
        answer_format TEXT,
        answer_variants TEXT,
        purpose TEXT,
        knowledge_id TEXT,
        created_at INTEGER,
        updated_at INTEGER,
        user_edited INTEGER DEFAULT 0
      )
    ''');
    await db.execute('CREATE INDEX idx_questions_chapter ON questions(chapter)');
    await db.execute('CREATE INDEX idx_questions_bank ON questions(bank_id)');
    await db.execute(
        'CREATE INDEX idx_questions_purpose ON questions(bank_id, chapter, purpose)');
    await db.execute(
        'CREATE INDEX idx_questions_user_edited ON questions(bank_id, user_edited)');

    // 作答日志：append-only，统计与 SRS 的数据基石（设计方案 §3.3）
    await db.execute('''
      CREATE TABLE answer_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id TEXT NOT NULL,
        mode TEXT NOT NULL,
        result TEXT NOT NULL,
        rating INTEGER,
        time_ms INTEGER NOT NULL,
        answered_at INTEGER NOT NULL,
        session_id INTEGER,
        user_answer TEXT
      )
    ''');
    await db.execute('CREATE INDEX idx_logs_qid ON answer_logs(question_id)');
    await db.execute('CREATE INDEX idx_logs_time ON answer_logs(answered_at)');
    // 错题本/统计按 (question_id, result) 过滤（审查 P2-2）
    await db.execute(
        'CREATE INDEX idx_logs_qid_result ON answer_logs(question_id, result)');

    // 每道题的 FSRS 调度状态：字段与 fsrs 2.0.1 的 Card 一一对应
    // （state/step/stability/difficulty/due/last_review；reps/lapses 由 answer_logs 派生）
    await db.execute(_cardSchedulingDdl);
    // 到期队列按 due 排序/过滤（审查 P2-3）
    await db.execute('CREATE INDEX idx_sched_due ON card_scheduling(due)');

    // 错题本手动移出记录（answer_logs 保持 append-only，不移除历史）
    await db.execute(_wrongBookExclusionsDdl);

    // 模拟卷系统（需求）
    await db.execute(_mockPapersDdl);
    await db.execute(_mockSessionsDdl);
    await db.execute('CREATE INDEX IF NOT EXISTS idx_mock_papers_bank ON mock_papers(bank_id)');

    // 审题标记（v7）
    await db.execute(_reviewFlagsDdl);
    await db.execute(
        'CREATE INDEX IF NOT EXISTS idx_review_flags_qid ON review_flags(question_id)');

    // 知识点树与章节概览（v9, formatVersion=4）
    await db.execute(_knowledgePointsDdl);
    await db.execute(_chapterOverviewsDdl);
    await db.execute(
        'CREATE INDEX IF NOT EXISTS idx_questions_knowledge ON questions(knowledge_id)');

    // 背题存档（v11）
    await db.execute(_memorizeProgressDdl);
    await db.execute(
        'CREATE INDEX IF NOT EXISTS idx_memo_chapter ON memorize_progress(bank_id, chapter, card_type)');

    // 键值设置（desired_retention、每日新题数、题库包导入版本等）
    await db.execute('''
      CREATE TABLE settings(
        key TEXT PRIMARY KEY,
        value TEXT
      )
    ''');
  }
}
