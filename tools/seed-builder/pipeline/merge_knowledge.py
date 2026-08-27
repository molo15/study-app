# -*- coding: utf-8 -*-
"""合并单章 knowledge JSON -> 整科 knowledge.json + knowledge.md"""
import json, glob, os

OUT = r'D:\study_app\tools\seed-builder\out\knowledge'
files = sorted(glob.glob(os.path.join(OUT, '现代汉语_*.knowledge.json')))
all_k = []
for f in files:
    d = json.load(open(f, encoding='utf-8'))
    for k in d['knowledge']:
        all_k.append(k)
bank = {
    'bankId': 'bank-现代汉语',
    'formatVersion': 4,
    'knowledgeCount': len(all_k),
    'knowledge': all_k
}
out_json = os.path.join(OUT, '现代汉语.knowledge.json')
json.dump(bank, open(out_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# MD
lines = ['# 现代汉语 · 知识点清单', '', f'知识点总数：**{len(all_k)}**', '']
cur_chap = None
for k in all_k:
    if k['chapter'] != cur_chap:
        cur_chap = k['chapter']
        lines.append(f'\n## {cur_chap}\n')
    hot = ' ★' if k.get('hot') else ''
    lines.append(f"### {k['name']}{hot}")
    lines.append(f"`{k['id']}`")
    lines.append(f"- 概述：{k['summary']}")
    if k.get('aliases'):
        lines.append(f"- 别名：{'、'.join(k['aliases'])}")
    if k.get('examRef'):
        lines.append(f"- 真题：{k['examRef']}")
    if k.get('basicQuestions'):
        lines.append('- 基础题规划：')
        for bq in k['basicQuestions']:
            lines.append(f"  - [{bq['type']}] {bq['stem']} → {bq['answer']}")
out_md = os.path.join(OUT, '现代汉语.knowledge.md')
open(out_md, 'w', encoding='utf-8').write('\n'.join(lines))

# 统计
from collections import Counter
print('知识点总数:', len(all_k))
print('分章:', dict(Counter(k['chapter'] for k in all_k)))
print('基础题总数:', sum(len(k.get('basicQuestions') or []) for k in all_k))
print('写出:', out_json, os.path.getsize(out_json), 'bytes')
print('写出:', out_md, os.path.getsize(out_md), 'bytes')
