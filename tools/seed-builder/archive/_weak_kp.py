# -*- coding: utf-8 -*-
"""列出古代文学史题量最薄弱的知识点"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
KP = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json', encoding='utf-8'))
rows = []
for k in KP['knowledge']:
    n = len(k.get('basicQuestions', []))
    rows.append((n, k['chapter'], k['name']))
rows.sort()
for n, ch, name in rows:
    flag = ' ⚠️' if n < 3 else ''
    print(f'{n:3d}题 | {ch:10s} | {name}{flag}')
