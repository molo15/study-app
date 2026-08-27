# -*- coding: utf-8 -*-
"""通用 v0.9.0 打包：基础题/测试题分文件 + 等价答案 answerVariants。

用法：python src/pack_bank.py <bank_key> [--version 0.9.0]

bank_key 配置见 BANK_CONFIG（bankId/名称/章节分组规则/工作目录/v09 文件/部署 assets）。
questions/ 每章拆两个文件：基础-<章>.json / 测试-<章>.json（按 purpose）。
manifest.chapters 两级分组；questionFiles 同步列出；purpose/answerVariants 透传。
"""
import argparse
import json
import os
import re
import shutil
import zipfile
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # tools/seed-builder
ASSETS = os.path.join(BASE, '..', '..', 'app', 'assets', 'banks')


def group_dangdai(ch):
    if ch.startswith('第十一') or ch.startswith('第十二'):
        return '下编 台港文学与世纪之交'
    pre = ch[:2]
    if pre in ('第一', '第二', '第三', '第四'):
        return '上编 十七年文学（1949-1976）'
    if pre in ('第五', '第六', '第七', '第八', '第九', '第十'):
        return '中编 新时期文学（1978-1999）'
    return '下编 台港文学与世纪之交'


def group_xiandai_wenxue(ch):
    """现代文学史按素材章体系分三个时期组（素材章命名：文体/思潮（一）=五四、（二）=三十、（三）=四十）。"""
    if ch.endswith('（一）') or ch in ('戏剧', '鲁迅（一）', '郭沫若', '市民通俗小说（一）'):
        return '五四时期（1917-1927）'
    if ch.endswith('（二）') or ch in ('戏剧（二）', '鲁迅（二）', '巴金', '老舍', '茅盾', '沈从文', '曹禺', '市民通俗小说（二）'):
        return '三十年代（1928-1937）'
    if ch.endswith('（三）') or ch in ('戏剧（三）', '赵树理', '艾青'):
        return '四十年代（1937-1949）'
    if ch == '智识阶层形象谱系':
        return '综合专题'
    return '综合专题'


def group_gudai_wenxue(ch):
    """中国古代文学史按朝代分期分组。"""
    order = ['先秦文学', '秦汉文学', '魏晋南北朝文学', '隋唐五代文学', '宋代文学',
             '元代文学', '明代文学', '清代文学', '近代文学']
    for g, cs in {
        '上编 先秦两汉文学': ['先秦文学', '秦汉文学'],
        '中编 魏晋隋唐文学': ['魏晋南北朝文学', '隋唐五代文学'],
        '下编 宋元明清文学': ['宋代文学', '元代文学', '明代文学', '清代文学', '近代文学'],
    }.items():
        if ch in cs:
            return g
    return '全部'


def group_gudai_hanyu(ch):
    """古代汉语按胡安顺体系分三编分组。"""
    if ch in ('绪论', '古书的标点', '修辞', '古书的文体', '工具书简介'):
        return '上编 基础知识'
    if ch.startswith(('文字', '词汇', '语法')):
        return '中编 语言文字学'
    return '下编 音韵训诂与格律'


BANK_CONFIG = {
    'zhongguo-dangdai-wenxue': {
        'bank_id': 'bank-zhongguo-dangdai-wenxue',
        'name': '考研 · 中国当代文学史',
        'workdir': os.path.join(BASE, 'out', 'v09dangdai'),
        'v09_file': 'bank-zhongguo-dangdai-wenxue.v09.json',
        'group_fn': group_dangdai,
        'chapters': [
            '第一章 1949-1976 文学思潮', '第二章 50、60 年代小说',
            '第三章 50、60 年代新诗', '第四章 50、60 年代戏剧、散文',
            '第五章 80、90 年代文学思潮', '第六章 80 年代小说',
            '第七章 90 年代小说', '第八章 80、90 年代新诗',
            '第九章 80、90 年代戏剧', '第十章 80、90 年代散文',
            '第十一章 台港文学', '第十二章 2000-2016 年文学概述',
        ],
    },
    'zhongguo-xiandai-wenxue': {
        'bank_id': 'bank-zhongguo-xiandai-wenxue',
        'name': '考研 · 中国现代文学史',
        'workdir': os.path.join(BASE, 'out', 'v09xiandaiwenxue'),
        'v09_file': 'bank-zhongguo-xiandai-wenxue.v09.json',
        'group_fn': group_xiandai_wenxue,
        'chapters': [
            '文学思潮与运动（一）', '文学思潮与运动（二）', '文学思潮与运动（三）',
            '小说（一）', '小说（二）', '小说（三）',
            '新诗（一）', '新诗（二）', '新诗（三）',
            '散文（一）', '散文（二）', '散文（三）',
            '戏剧', '戏剧（二）', '戏剧（三）',
            '鲁迅（一）', '鲁迅（二）', '巴金', '老舍', '茅盾', '沈从文',
            '曹禺', '赵树理', '郭沫若', '艾青',
            '市民通俗小说（一）', '市民通俗小说（二）', '智识阶层形象谱系',
            '综合专题',
        ],
    },
    'zhongguo-gudai-wenxue': {
        'bank_id': 'bank-zhongguo-gudai-wenxue',
        'name': '考研 · 中国古代文学史',
        'workdir': os.path.join(BASE, 'out', 'v09gudaiwenxue'),
        'v09_file': 'bank-zhongguo-gudai-wenxue.v09.json',
        'group_fn': group_gudai_wenxue,
        'chapters': [
            '先秦文学', '秦汉文学', '魏晋南北朝文学', '隋唐五代文学',
            '宋代文学', '明代文学', '元代文学', '清代文学', '近代文学',
        ],
    },
    'gudai-hanyu': {
        'bank_id': 'bank-gudai-hanyu',
        'name': '考研 · 古代汉语',
        'workdir': os.path.join(BASE, 'out', 'v09gudaihanyu'),
        'v09_file': 'bank-gudai-hanyu.v09.json',
        'group_fn': group_gudai_hanyu,
        'chapters': [
            '修辞', '古书的文体', '古书的标点', '工具书简介',
            '文字（上）', '文字（下）', '绪论', '训诂', '词汇',
            '诗词格律', '语法（上）', '语法（下）', '音韵',
        ],
    },
}


def sanitize(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name)


def validate(questions, chapters):
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
        if q.get('chapter') not in chapters:
            errors.append(f'{qid} chapter 不在章节内: {q.get("chapter")}')
        if q.get('purpose') not in ('basic', 'test'):
            errors.append(f'{qid} purpose 非法: {q.get("purpose")}')
        av = q.get('answerVariants')
        if av is not None and not (isinstance(av, list) and all(isinstance(g, list) and g for g in av)):
            errors.append(f'{qid} answerVariants 非法: {av}')
    return errors


# 题型顺序：选择(单选/多选/判断) → 填空 → 简答/论述
_TYPE_ORDER = {
    'single_choice': 0,
    'multi_choice': 1,
    'true_false': 2,
    'blank': 3,
    'short_answer': 4,
}


def clean_question(q):
    """按发布规范清洗题目字段：
    - 所有题型删除 source（出处）；
    - 客观题（单选/多选/判断/填空）保留 answer + explanation；
    - 主观题（简答/论述）仅保留 answer（删 explanation）。
    保留结构必需字段（id/type/stem/options/answer/chapter/tags/difficulty/purpose/
    answerFormat/answerVariants），保证 App 展示与判分功能不受影响。
    """
    q.pop('source', None)
    if q.get('type') == 'short_answer':
        q.pop('explanation', None)
    return q


def sort_key(q):
    """出题排序：选择 → 填空 → 简答/论述（同题型内保持原相对顺序）。"""
    return _TYPE_ORDER.get(q.get('type'), 99)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bank_key', choices=list(BANK_CONFIG.keys()))
    ap.add_argument('--version', default='0.9.0')
    args = ap.parse_args()
    cfg = BANK_CONFIG[args.bank_key]
    bank_id = cfg['bank_id']
    version = args.version
    old_version = '0.8.0'

    v09_path = os.path.join(cfg['workdir'], cfg['v09_file'])
    if not os.path.exists(v09_path):
        raise SystemExit(f'!! 缺失 v09: {v09_path}')
    questions = json.load(open(v09_path, encoding='utf-8'))
    errs = validate(questions, cfg['chapters'])
    if errs:
        print(f'!! 校验失败 {len(errs)} 条：')
        for e in errs[:20]:
            print('   ', e)
        raise SystemExit(1)

    chapters_sorted = sorted({q['chapter'] for q in questions})
    groups = {}
    for ch in chapters_sorted:
        groups.setdefault(cfg['group_fn'](ch), []).append(ch)
    chapter_groups = [{'group': g, 'chapters': sorted(v)} for g, v in sorted(groups.items())]

    papers_path = os.path.join(BASE, 'out', 'papers', 'papers.json')
    papers = []
    if os.path.exists(papers_path):
        paper_data = json.load(open(papers_path, encoding='utf-8'))
        for p in paper_data['papers']:
            if p.get('bankId') != bank_id:
                continue
            papers.append({
                'id': f'{bank_id}:paper_{len(papers) + 1:02d}',
                'bankId': bank_id,
                'name': p['name'],
                'durationMin': p['durationMin'],
                'questionIds': p['questionIds'],
            })

    manifest = {
        'formatVersion': 3,
        'bankId': bank_id,
        'name': cfg['name'],
        'version': version,
        'generatedAt': '2026-08-17T20:00:00+08:00',
        'chapters': chapter_groups,
        'questionFiles': [],
        'mockPapers': papers,
    }

    by_purpose_chapter = {}
    for q in questions:
        # 发布规范清洗：删 source，主观题删解析
        cleaned = clean_question(dict(q))
        by_purpose_chapter.setdefault((cleaned['purpose'], cleaned['chapter']), []).append(cleaned)

    # 出题排序：选择 → 填空 → 简答/论述（同题型保持原有相对顺序）
    for key in by_purpose_chapter:
        by_purpose_chapter[key].sort(key=sort_key)

    out_dir = os.path.join(BASE, 'out', 'packages', f'v{version.replace(".", "")}')
    os.makedirs(out_dir, exist_ok=True)
    zip_path = os.path.join(out_dir, f'{bank_id}-v{version}.zip')
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

    os.makedirs(ASSETS, exist_ok=True)
    dst = os.path.join(ASSETS, f'{bank_id}-v{version}.zip')
    shutil.copyfile(zip_path, dst)
    old = os.path.join(ASSETS, f'{bank_id}-v{old_version}.zip')
    if os.path.exists(old):
        os.remove(old)

    print(f'【{cfg["name"]} v{version}】{len(questions)} 题')
    print('  purpose:', dict(Counter(q['purpose'] for q in questions)))
    print('  章节:', dict(Counter(q['chapter'] for q in questions)))
    print('  题型:', dict(Counter(q['type'] for q in questions)))
    print(f'  模拟卷 {len(papers)} 张 → {zip_path}')
    print(f'  ✅ 已部署到 {dst}（移除 v{old_version}）')


if __name__ == '__main__':
    main()
