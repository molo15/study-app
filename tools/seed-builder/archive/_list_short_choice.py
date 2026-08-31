# -*- coding: utf-8 -*-
"""列出所有 <20 字的非 blank 基础题解析，供补长。"""
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

FILES = [
    (r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json', '现代汉语'),
    (r'D:\study_app\tools\seed-builder\out\knowledge\古代汉语.knowledge.json', '古代汉语'),
    (r'D:\study_app\tools\seed-builder\out\knowledge\中国现代文学史.knowledge.json', '现代文学'),
    (r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json', '古代文学'),
    (r'D:\study_app\tools\seed-builder\out\knowledge\中国当代文学史.knowledge.json', '当代文学'),
]
for f, cn in FILES:
    k = json.load(open(f, encoding='utf-8'))
    print(f'===== {cn} =====')
    for x in k['knowledge']:
        for i, bq in enumerate(x.get('basicQuestions', [])):
            if bq.get('type') in ('blank', 'short_answer'):
                continue
            L = len(re.sub(r'\s+', '', bq.get('explanation') or ''))
            if L < 20:
                print(f"  [{x['id']}/{i}] {L}字 | stem:{(bq.get('stem') or '')[:26]} | ans:{(str(bq.get('answer')) or '')[:14]} | expl:{(bq.get('explanation') or '')[:40]}")
