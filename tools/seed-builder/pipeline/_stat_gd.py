# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
KP = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json', encoding='utf-8'))
tot_b = 0
tot_r = 0
for k in KP['knowledge']:
    b = len(k.get('basicQuestions', []))
    r = len(k.get('retainedQuestions', []))
    tot_b += b
    tot_r += r
    print(f"{k['chapter']:8s} | {k['name'][:24]:24s} | 基础{b:3d} 保留{r:3d}")
print('=' * 60)
print('基础题总数', tot_b, '| 保留题总数', tot_r, '| 合计', tot_b + tot_r)
