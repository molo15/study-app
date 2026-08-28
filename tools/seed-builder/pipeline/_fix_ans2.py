# -*- coding: utf-8 -*-
"""修复 answer 字段带括号未与选项同步的问题"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json'
KP = json.load(open(P, encoding='utf-8'))
n = 0
for k in KP['knowledge']:
    for q in k.get('basicQuestions', []):
        if q['type'] == 'choice':
            if q['answer'] not in q.get('options', []):
                # 尝试去掉括号后的匹配
                fixed = q['answer'].replace('（', '·').replace('）', '').replace('(', '·').replace(')', '')
                if fixed in q.get('options', []):
                    q['answer'] = fixed
                    n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('修复答案错配', n, '处')
# 复验
bad = 0
for k in KP['knowledge']:
    for q in k.get('basicQuestions', []):
        if q['type'] == 'choice' and q['answer'] not in q.get('options', []):
            bad += 1
            print('残留:', q['stem'][:20], q['answer'])
print('复验残留错配:', bad)
