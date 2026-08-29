# -*- coding: utf-8 -*-
"""统计 docx 题库古代文学史各章各题型数量 vs 已导入"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
D = json.load(open(r'D:\study_app\tools\seed-builder\out\reports\docx题库_解析.json', encoding='utf-8'))
GD = D['袁行霈中国文学史']
total = {'填空题': 0, '选择题': 0, '名词解释': 0, '简答题': 0, '论述题': 0}
usable = {'填空题': 0, '选择题': 0}
for ch, types in GD.items():
    row = {}
    for t in ['填空题', '选择题', '名词解释', '简答题', '论述题']:
        qs = types.get(t, [])
        row[t] = len(qs)
        total[t] += len(qs)
        if t == '填空题':
            usable[t] += sum(1 for q in qs if q.get('answer'))
        if t == '选择题':
            usable[t] += sum(1 for q in qs if q.get('answer') in 'ABCDE' and len(q.get('answer',''))==1)
    print(ch, row)
print('\n合计:', total, '可用:', usable)
# 第一部分
P1 = json.load(open(r'D:\study_app\tools\seed-builder\out\reports\docx题库_第一部分.json', encoding='utf-8'))
p1 = P1['袁行霈中国文学史']
print('\n第一部分(古代):', {t: len(p1.get(t, [])) for t in ['填空题', '选择题', '名词解释', '简答题', '论述题']})
p1u = {'填空题': sum(1 for q in p1.get('填空题', []) if q.get('answer')),
       '选择题': sum(1 for q in p1.get('选择题', []) if q.get('answer') in 'ABCDE' and len(q.get('answer',''))==1)}
print('第一部分可用:', p1u)
