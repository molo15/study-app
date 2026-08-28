# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'D:\study_app\app\lib\data\quiz_repository.dart'
s = open(p, encoding='utf-8').read()

# 模板：古汉多选 3→4，古代文学史多选 1→0（多选以现汉+古汉为主）
old = """    'bank-gudai-hanyu': {
      'single_choice': 11,
      'multi_choice': 3,
      'blank': 8,
      'short_answer': 3,
    },
    'bank-zhongguo-xiandai-wenxue': {
      'single_choice': 3,
      'multi_choice': 1,
      'blank': 2,
      'short_answer': 1,
    },
    'bank-zhongguo-dangdai-wenxue': {
      'single_choice': 3,
      'multi_choice': 1,
      'blank': 1,
      'short_answer': 1,
    },
    'bank-zhongguo-gudai-wenxue': {
      'single_choice': 2,
      'multi_choice': 1,
      'blank': 1,
      'short_answer': 0,
    },
  };"""
new = """    'bank-gudai-hanyu': {
      'single_choice': 11,
      'multi_choice': 4,
      'blank': 8,
      'short_answer': 3,
    },
    'bank-zhongguo-xiandai-wenxue': {
      'single_choice': 3,
      'multi_choice': 1,
      'blank': 2,
      'short_answer': 1,
    },
    'bank-zhongguo-dangdai-wenxue': {
      'single_choice': 3,
      'multi_choice': 1,
      'blank': 1,
      'short_answer': 1,
    },
    'bank-zhongguo-gudai-wenxue': {
      'single_choice': 2,
      'multi_choice': 0,
      'blank': 1,
      'short_answer': 0,
    },
  };"""
assert old in s, 'template anchor'
s = s.replace(old, new, 1)

open(p, 'w', encoding='utf-8').write(s)
print('[template] ok')

# generateCompositePaper 补足逻辑
p = r'D:\study_app\app\lib\data\quiz_repository_mock.dart'
s = open(p, encoding='utf-8').read()
old = """  Future<List<Question>> generateCompositePaper() async {
    final questions = <Question>[];
    final seen = <String>{};
    for (final entry in QuizRepository.compositeTemplate.entries) {
      final bankId = entry.key;
      for (final te in entry.value.entries) {
        final type = te.key;
        final want = te.value;
        if (want <= 0) continue;
        final rows = await _db.rawQuery(
          "SELECT * FROM questions WHERE bank_id = ? AND type = ? AND status = 'active' ORDER BY RANDOM() LIMIT ?",
          [bankId, type, want],
        );
        for (final r in rows) {
          final q = Question.fromMap(r);
          if (seen.add(q.id)) questions.add(q);
        }
      }
    }
    // 去重后若不足预期（题库缺题），不影响作答；排序保持学科顺序即可
    return questions;
  }"""
new = """  Future<List<Question>> generateCompositePaper() async {
    final questions = <Question>[];
    final seen = <String>{};
    // 各题型期望总数（跨学科求和），用于缺口补足
    final wantByType = <String, int>{};
    for (final entry in QuizRepository.compositeTemplate.entries) {
      for (final te in entry.value.entries) {
        wantByType[te.key] = (wantByType[te.key] ?? 0) + te.value;
      }
    }
    // 第一轮：按学科配额抽取（优先现汉/古汉；多选以两科为主）
    for (final entry in QuizRepository.compositeTemplate.entries) {
      final bankId = entry.key;
      for (final te in entry.value.entries) {
        final type = te.key;
        final want = te.value;
        if (want <= 0) continue;
        final rows = await _db.rawQuery(
          "SELECT * FROM questions WHERE bank_id = ? AND type = ? AND status = 'active' ORDER BY RANDOM() LIMIT ?",
          [bankId, type, want],
        );
        for (final r in rows) {
          final q = Question.fromMap(r);
          if (seen.add(q.id)) questions.add(q);
        }
      }
    }
    // 第二轮：某题型仍不足期望时，从全库同题型（排除已抽）随机补足，
    // 保证每卷题型数量稳定（放宽：多选等稀缺题型不再因单科不足而缺额）
    for (final te in wantByType.entries) {
      final type = te.key;
      final want = te.value;
      final have = questions.where((q) => q.type.json == type).length;
      if (have >= want) continue;
      final need = want - have;
      final rows = await _db.rawQuery(
        "SELECT * FROM questions WHERE type = ? AND status = 'active' ORDER BY RANDOM() LIMIT ?",
        [type, need],
      );
      for (final r in rows) {
        final q = Question.fromMap(r);
        if (seen.add(q.id)) questions.add(q);
      }
    }
    return questions;
  }"""
assert old in s, 'generate anchor'
s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(s)
print('[generate] ok')
