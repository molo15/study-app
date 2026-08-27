# -*- coding: utf-8 -*-
"""Merge <bank>_<chapter>.knowledge.json -> <bank>.knowledge.json + .md for any bank"""
import json, glob, os, re
from collections import Counter

OUT = r'D:\study_app\tools\seed-builder\out\knowledge'
# 合并指定的 bank 前缀；不传则处理所有
targets = [a for a in __import__('sys').argv[1:]] or None

groups = {}
for f in sorted(glob.glob(os.path.join(OUT, '*_*.knowledge.json'))):
    base = os.path.basename(f)
    if base.endswith('.knowledge.json'):
        m = re.match(r'^(.+?)_([^_].*?)\.knowledge\.json$', base)
        if not m:
            continue
        bank = m.group(1)
        if targets and bank not in targets:
            continue
        d = json.load(open(f, encoding='utf-8'))
        groups.setdefault(bank, []).append(d)

for bank, chapters in groups.items():
    chapters.sort(key=lambda c: c.get('chapter', ''))
    all_k = []
    for c in chapters:
        for k in c.get('knowledge', []):
            all_k.append(k)
    bankjson = {
        'bankId': bank,
        'formatVersion': 4,
        'knowledgeCount': len(all_k),
        'chapters': [c['chapter'] for c in chapters],
        'knowledge': all_k,
    }
    out_json = os.path.join(OUT, f'{bank}.knowledge.json')
    json.dump(bankjson, open(out_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    lines = [f'# {bank} · 知识点清单', '', f'知识点总数：**{len(all_k)}**', '']
    cur = None
    for k in all_k:
        if k['chapter'] != cur:
            cur = k['chapter']
            lines.append(f"\n## {cur}\n")
        hot = ' ★' if k.get('hot') else ''
        lines.append(f"### {k['name']}{hot}")
        lines.append(f"`{k['id']}`")
        lines.append(f"- 概述：{k['summary']}")
        if k.get('aliases'):
            lines.append(f"- 别名：{'、'.join(k['aliases'])}")
        if k.get('examRef'):
            lines.append(f"- 真题：{k['examRef']}")
        if k.get('note'):
            lines.append(f"- 备注：{k['note']}")
        if k.get('basicQuestions'):
            lines.append('- 基础题规划：')
            for bq in k['basicQuestions']:
                lines.append(f"  - [{bq['type']}] {bq['stem']} → {bq['answer']}")
    out_md = os.path.join(OUT, f'{bank}.knowledge.md')
    open(out_md, 'w', encoding='utf-8').write('\n'.join(lines))

    print(f'== {bank} ==')
    print('  知识点总数:', len(all_k))
    print('  分章:', dict(Counter(k['chapter'] for k in all_k)))
    print('  基础题总数:', sum(len(k.get('basicQuestions') or []) for k in all_k))
    print('  json:', out_json, os.path.getsize(out_json))
    print('  md:', out_md, os.path.getsize(out_md))
