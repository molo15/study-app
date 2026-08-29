# -*- coding: utf-8 -*-
"""修复新增 choice 题选项中带括号注释的问题"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json'
KP = json.load(open(P, encoding='utf-8'))
n = 0
for k in KP['knowledge']:
    for q in k.get('basicQuestions', []):
        if q['type'] == 'choice':
            for i, o in enumerate(q.get('options', [])):
                if '(' in o or '（' in o or ')' in o or '）' in o:
                    q['options'][i] = o.replace('（', '·').replace('）', '').replace('(', '·').replace(')', '')
                    n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('修复选项', n, '处')
# 打印南戏和宫体诗现在的选项
for k in KP['knowledge']:
    for q in k.get('basicQuestions', []):
        if '南戏是中国戏剧' in q['stem'] or '宫体诗”是指以南朝' in q['stem']:
            print(q['stem'][:20], '→', q.get('options'))
