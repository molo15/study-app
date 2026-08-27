# -*- coding: utf-8 -*-
"""v0.9.0 打包：现代汉语（基础题/测试题分类 + 等价答案 answerVariants）。

- 题库：读 out/v09/bank-xiandai-hanyu.v09.json（merge_v09.py 产出，每题带 purpose）
- questions/ 每章拆两个文件：基础-<章>.json / 测试-<章>.json（按 purpose 分文件）
- manifest.questionFiles 同步列出；purpose/answerVariants 字段原样透传（App 静默忽略 purpose，判分识别 answerVariants）
- 输出 out/packages/v09/bank-xiandai-hanyu-v0.9.0.zip，复制到 app/assets/banks/ 替换 v0.8.0
- 仅打现代汉语（其余 4 库保持 v0.8.0，待后续逐本重构）
"""
import json
import os
import re
import shutil
import zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # tools/seed-builder
V09 = os.path.join(BASE, 'out', 'v09', 'bank-xiandai-hanyu.v09.json')
PAPERS = os.path.join(BASE, 'out', 'papers', 'papers.json')
OUT_DIR = os.path.join(BASE, 'out', 'packages', 'v09')
ASSETS = os.path.join(BASE, '..', '..', 'app', 'assets', 'banks')

BANK_ID = 'bank-xiandai-hanyu'
NAME = '考研 · 现代汉语'
VERSION = '0.9.0'
OLD_VERSION = '0.8.0'


def sanitize(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name)


def group_of(chapter):
    if chapter in ('绪论', '语音', '文字'):
        return '上编 语音与文字'
    if chapter in ('词汇', '语法'):
        return '中编 词汇与语法'
    return '下编 修辞'


def validate(questions):
    errors = []
    ids = set()
    for q in questions:
        qid = q.get('id', '')
        if qid in ids:
            errors.append(f'id 重复: {qid}')
        ids.add(qid)
        t = q.get('type')
        ans = q.get('answer')
        if t == 'true_false':
            if ans not in ('正确', '错误'):
                errors.append(f'{qid} 判断答案: {ans}')
        elif t == 'single_choice':
            keys = {o['key'] for o in q.get('options', [])}
            if ans not in keys:
                errors.append(f'{qid} 单选答案: {ans}')
        elif t == 'multi_choice':
            keys = {o['key'] for o in q.get('options', [])}
            if not isinstance(ans, list) or not set(ans).issubset(keys):
                errors.append(f'{qid} 多选答案: {ans}')
        elif t in ('blank', 'short_answer'):
            if not ans:
                errors.append(f'{qid} 缺 answer')
        else:
            errors.append(f'{qid} 未知题型 {t}')
        if q.get('purpose') not in ('basic', 'test'):
            errors.append(f'{qid} purpose 非法: {q.get("purpose")}')
        av = q.get('answerVariants')
        if av is not None and not (isinstance(av, list) and all(isinstance(g, list) and g for g in av)):
            errors.append(f'{qid} answerVariants 非法: {av}')
    return errors


def main():
    questions = json.load(open(V09, encoding='utf-8'))
    errs = validate(questions)
    if errs:
        print(f'!! 校验失败 {len(errs)} 条：')
        for e in errs[:20]:
            print('   ', e)
        raise SystemExit(1)

    chapters_sorted = sorted({q['chapter'] for q in questions})
    groups = {}
    for ch in chapters_sorted:
        groups.setdefault(group_of(ch), []).append(ch)
    chapter_groups = [{'group': g, 'chapters': sorted(v)} for g, v in sorted(groups.items())]

    paper_data = json.load(open(PAPERS, encoding='utf-8'))
    papers = []
    for p in paper_data['papers']:
        if p.get('bankId') != BANK_ID:
            continue
        papers.append({
            'id': f'{BANK_ID}:paper_{len(papers) + 1:02d}',  # 按 bank 内序号，保持与 v0.8.0 的 paper_01 一致
            'bankId': BANK_ID,
            'name': p['name'],
            'durationMin': p['durationMin'],
            'questionIds': p['questionIds'],
        })

    manifest = {
        'formatVersion': 3,
        'bankId': BANK_ID,
        'name': NAME,
        'version': VERSION,
        'generatedAt': '2026-08-17T20:00:00+08:00',
        'chapters': chapter_groups,
        'questionFiles': [],
        'mockPapers': papers,
    }

    by_purpose_chapter = {}
    for q in questions:
        # 发布规范清洗：删 source；主观题(简答/论述)删解析 explanation
        cleaned = dict(q)
        cleaned.pop('source', None)
        if cleaned.get('type') == 'short_answer':
            cleaned.pop('explanation', None)
        by_purpose_chapter.setdefault((cleaned['purpose'], cleaned['chapter']), []).append(cleaned)

    # 出题排序：选择(单选/多选/判断) → 填空 → 简答/论述（同题型保持原有相对顺序）
    _type_order = {
        'single_choice': 0, 'multi_choice': 1, 'true_false': 2,
        'blank': 3, 'short_answer': 4,
    }
    for key in by_purpose_chapter:
        by_purpose_chapter[key].sort(key=lambda q: _type_order.get(q['type'], 99))

    os.makedirs(OUT_DIR, exist_ok=True)
    zip_path = os.path.join(OUT_DIR, f'{BANK_ID}-v{VERSION}.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for purpose in ('basic', 'test'):
            for ch in chapters_sorted:
                chunk = by_purpose_chapter.get((purpose, ch), [])
                if not chunk:
                    continue
                prefix = '基础' if purpose == 'basic' else '测试'
                fname = f'questions/{prefix}-{sanitize(ch)}.json'
                zf.writestr(fname, json.dumps(chunk, ensure_ascii=False, indent=2))
                manifest['questionFiles'].append(fname)
        zf.writestr('manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2))

    # 部署：替换 app/assets/banks/ 下的 v0.8.0
    os.makedirs(ASSETS, exist_ok=True)
    dst = os.path.join(ASSETS, f'{BANK_ID}-v{VERSION}.zip')
    shutil.copyfile(zip_path, dst)
    old = os.path.join(ASSETS, f'{BANK_ID}-v{OLD_VERSION}.zip')
    if os.path.exists(old):
        os.remove(old)

    from collections import Counter
    print(f'【{NAME} v{VERSION}】{len(questions)} 题')
    print('  purpose:', dict(Counter(q['purpose'] for q in questions)))
    print('  章节:', dict(Counter(q['chapter'] for q in questions)))
    print('  题型:', dict(Counter(q['type'] for q in questions)))
    print(f'  模拟卷 {len(papers)} 张 → {zip_path}')
    print(f'  ✅ 已部署到 {dst}（移除 v{OLD_VERSION}）')


if __name__ == '__main__':
    main()
