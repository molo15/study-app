# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
D = json.load(open(r'D:\study_app\tools\seed-builder\out\reports\docx题库_第一部分.json', encoding='utf-8'))
# 结构探查
print(type(D))
if isinstance(D, dict):
    for k in list(D.keys())[:5]:
        print('KEY:', k)
        v = D[k]
        if isinstance(v, dict):
            print('  sub:', list(v.keys())[:8])
