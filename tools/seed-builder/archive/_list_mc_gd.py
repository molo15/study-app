# -*- coding: utf-8 -*-
"""列出古代文学史所有名词解释（章节题库 + 第一部分），用于评估转题"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

D = json.load(open(r'D:\study_app\tools\seed-builder\out\reports\docx题库_解析.json', encoding='utf-8'))
P1 = json.load(open(r'D:\study_app\tools\seed-builder\out\reports\docx题库_第一部分.json', encoding='utf-8'))

print('### 袁行霈 章节题库 名词解释（按编）')
for ch, types in D['袁行霈中国文学史'].items():
    n = types.get('名词解释', [])
    print(f'\n--- {ch} ({len(n)}) ---')
    for q in n:
        print(f'  {q["stem"][:40]}')

print()
print('### 袁行霈 第一部分 名词解释')
for q in P1['袁行霈中国文学史'].get('名词解释', []):
    print(f'  {q["stem"][:40]}')
