# -*- coding: utf-8 -*-
"""输出古代文学史名词解释定义摘要，用于设计转题"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

D = json.load(open(r'D:\study_app\tools\seed-builder\out\reports\docx题库_解析.json', encoding='utf-8'))

for ch, types in D['袁行霈中国文学史'].items():
    n = types.get('名词解释', [])
    print(f'\n### {ch} ({len(n)})')
    for q in n:
        expl = q['expl'][:110].replace('\n', ' ')
        print(f'◆ {q["stem"][:30]}')
        print(f'  {expl}')
