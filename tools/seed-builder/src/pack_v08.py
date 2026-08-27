# -*- coding: utf-8 -*-
"""v0.8.0 打包：题库内容（= v0.7.0 全量）+ 模拟卷 mockPapers。

- 题库：读 out/v08/{bank_id}.v08.json（Agent A 产出，内容与 v0.7.0 一致）
- 模拟卷：读 out/papers/papers.json（Agent B 产出），补 paper id 后注入各库 manifest.mockPapers
- 输出 out/packages/v08/{bank_id}-v0.8.0.zip，并复制到 app/assets/banks/ 替换 v0.7.0
"""
import json
import os
import re
import shutil
import zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # tools/seed-builder
V08_DIR = os.path.join(BASE, 'out', 'v08')
PAPERS = os.path.join(BASE, 'out', 'papers', 'papers.json')
OUT_DIR = os.path.join(BASE, 'out', 'packages', 'v08')
ASSETS = os.path.join('app', 'assets', 'banks')

VERSION = '0.8.0'

BANKS = [
    ('bank-gudai-hanyu', '考研 · 古代汉语'),
    ('bank-xiandai-hanyu', '考研 · 现代汉语'),
    ('bank-zhongguo-gudai-wenxue', '考研 · 中国古代文学史'),
    ('bank-zhongguo-xiandai-wenxue', '考研 · 中国现代文学史'),
    ('bank-zhongguo-dangdai-wenxue', '考研 · 中国当代文学史'),
]

LUNSHU = '论述题专题'


def sanitize(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name)


def group_of(bank_id, chapter):
    """沿用 v0.7.0 的分组逻辑（pack_t1.chapter_groups），保证分组一致。"""
    def xiandai_wenxue(ch):
        if ch.startswith('五四'):
            return '五四时期（1917-1927）'
        if ch.startswith('三十'):
            return '三十年代（1928-1937）'
        if ch.startswith('四十'):
            return '四十年代（1937-1949）'
        return '综合专题'

    def dangdai_wenxue(ch):
        pre = ch[:2]
        if pre in ('第一', '第二', '第三', '第四'):
            return '上编 十七年文学（1949-1976）'
        if pre in ('第五', '第六', '第七', '第八', '第九', '第十'):
            return '中编 新时期文学（1978-1999）'
        return '下编 台港文学与世纪之交'

    MAPS = {
        'bank-gudai-hanyu': lambda c: '上编 基础知识' if c in ('修辞', '古书的标点', '工具书简介') else (
            '中编 语言文字学' if c.startswith(('文字', '词汇', '语法')) else '下编 音韵训诂与格律'),
        'bank-xiandai-hanyu': lambda c: '上编 语音与文字' if c in ('绪论', '语音', '文字') else (
            '中编 词汇与语法' if c in ('词汇', '语法') else '下编 修辞'),
        'bank-zhongguo-gudai-wenxue': lambda c: '上编 先秦两汉文学' if c in ('先秦文学', '秦汉文学') else (
            '中编 魏晋隋唐文学' if c in ('魏晋南北朝文学', '隋唐五代文学') else '下编 宋元明清文学'),
        'bank-zhongguo-xiandai-wenxue': xiandai_wenxue,
        'bank-zhongguo-dangdai-wenxue': dangdai_wenxue,
    }
    fn = MAPS.get(bank_id, lambda c: '全部')
    return LUNSHU if chapter == LUNSHU else fn(chapter)


def validate(bank_id, questions):
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
        if not q.get('chapter'):
            errors.append(f'{qid} 缺 chapter')
    return errors


def pack(bank_id, name, questions, papers):
    chapters_sorted = sorted({q['chapter'] for q in questions})
    groups = {}
    for ch in chapters_sorted:
        groups.setdefault(group_of(bank_id, ch), []).append(ch)
    chapter_groups = [{'group': g, 'chapters': sorted(v)} for g, v in sorted(groups.items())]

    manifest = {
        'formatVersion': 3,
        'bankId': bank_id,
        'name': name,
        'version': VERSION,
        'generatedAt': '2026-08-17T20:00:00+08:00',
        'chapters': chapter_groups,
        'questionFiles': [],
        'mockPapers': papers,
    }
    by_chapter = {}
    for q in questions:
        by_chapter.setdefault(q['chapter'], []).append(q)

    os.makedirs(OUT_DIR, exist_ok=True)
    zip_path = os.path.join(OUT_DIR, f'{bank_id}-v{VERSION}.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for ch in sorted(by_chapter):
            fname = f'questions/{sanitize(ch)}.json'
            zf.writestr(fname, json.dumps(by_chapter[ch], ensure_ascii=False, indent=2))
            manifest['questionFiles'].append(fname)
        zf.writestr('manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2))
    return zip_path


def main():
    paper_data = json.load(open(PAPERS, encoding='utf-8'))
    papers_by_bank = {}
    for p in paper_data['papers']:
        bank_id = p['bankId']
        idx = len(papers_by_bank.get(bank_id, [])) + 1
        paper = {
            'id': f'{bank_id}:paper_{idx:02d}',
            'bankId': bank_id,
            'name': p['name'],
            'durationMin': p['durationMin'],
            'questionIds': p['questionIds'],
        }
        papers_by_bank.setdefault(bank_id, []).append(paper)

    for bank_id, name in BANKS:
        v08 = os.path.join(V08_DIR, f'{bank_id}.v08.json')
        if not os.path.exists(v08):
            print(f'!! 缺失 v08: {v08}')
            continue
        questions = json.load(open(v08, encoding='utf-8'))
        errs = validate(bank_id, questions)
        papers = papers_by_bank.get(bank_id, [])
        if not papers:
            print(f'!! {bank_id} 无模拟卷')
        zip_path = pack(bank_id, name, questions, papers)
        print(f'【{name}】{len(questions)} 题 · 模拟卷 {len(papers)} 张 → {zip_path}')
        if errs:
            print(f'   ❌ 校验错误 {len(errs)}: {errs[:5]}')

    # 复制到 app/assets/banks/，删除旧 v0.7.0
    for bank_id, _ in BANKS:
        src = os.path.join(OUT_DIR, f'{bank_id}-v{VERSION}.zip')
        dst = os.path.join(ASSETS, f'{bank_id}-v{VERSION}.zip')
        shutil.copyfile(src, dst)
        old = os.path.join(ASSETS, f'{bank_id}-v0.7.0.zip')
        if os.path.exists(old):
            os.remove(old)
    print('\n✅ 已复制 v0.8.0 到 app/assets/banks/ 并移除 v0.7.0')


if __name__ == '__main__':
    main()
