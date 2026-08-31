# -*- coding: utf-8 -*-
"""背题存档 v11：数据库层修改"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\study_app\app\lib\data\app_database.dart'
s = open(p, encoding='utf-8').read()

# 1. 版本号 10 -> 11
s = s.replace("static const _dbVersion = 10;", "static const _dbVersion = 11;")

# 2. onUpgrade 加 v11
old_up = """    if (oldVersion < 10) {
      // v10: 模拟卷逐题回顾 —— answer_logs 加 user_answer（存用户作答快照）
      final acols = await db.rawQuery('PRAGMA table_info(answer_logs)');
      if (!acols.any((c) => c['name'] == 'user_answer')) {
        await db.execute('ALTER TABLE answer_logs ADD COLUMN user_answer TEXT');
      }
    }
  }"""
new_up = """    if (oldVersion < 10) {
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
  }"""
assert old_up in s, 'onUpgrade anchor missing'
s = s.replace(old_up, new_up)

# 3. 建表 DDL 常量
old_ddl = """  static const _cardSchedulingDdl = '''"""
new_ddl = """  /// v11：背题存档 —— 每张记忆卡一条记录（知识点卡 kp:xx / 题目卡 q:xx）
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

  static const _cardSchedulingDdl = '''"""
assert old_ddl in s, 'DDL anchor missing'
s = s.replace(old_ddl, new_ddl)

# 4. createSchema 加建表
old_cs = """    // 知识点树与章节概览（v9, formatVersion=4）
    await db.execute(_knowledgePointsDdl);
    await db.execute(_chapterOverviewsDdl);
    await db.execute(
        'CREATE INDEX IF NOT EXISTS idx_questions_knowledge ON questions(knowledge_id)');
"""
new_cs = """    // 知识点树与章节概览（v9, formatVersion=4）
    await db.execute(_knowledgePointsDdl);
    await db.execute(_chapterOverviewsDdl);
    await db.execute(
        'CREATE INDEX IF NOT EXISTS idx_questions_knowledge ON questions(knowledge_id)');

    // 背题存档（v11）
    await db.execute(_memorizeProgressDdl);
    await db.execute(
        'CREATE INDEX IF NOT EXISTS idx_memo_chapter ON memorize_progress(bank_id, chapter, card_type)');
"""
assert old_cs in s, 'createSchema anchor missing'
s = s.replace(old_cs, new_cs)

open(p, 'w', encoding='utf-8', newline='').write(s)
print('app_database v11 完成')
print('  _dbVersion=11:', 'static const _dbVersion = 11;' in s)
print('  _memorizeProgressDdl:', '_memorizeProgressDdl' in s)
print('  onUpgrade v11:', 'oldVersion < 11' in s)
