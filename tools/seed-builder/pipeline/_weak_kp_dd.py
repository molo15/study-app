# -*- coding: utf-8 -*-
"""列出当代文学史各知识点题量与章节"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
KP = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国当代文学史.knowledge.json', encoding='utf-8'))
rows = []
for k in KP['knowledge']:
    rows.append((len(k.get('basicQuestions', [])), k['chapter'], k['name']))
rows.sort()
for n, ch, name in rows:
    flag = ' ⚠️' if n < 3 else ''
    print(f'{n:3d} | {ch:22s} | {name}{flag}')
