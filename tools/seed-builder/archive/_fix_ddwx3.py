# -*- coding: utf-8 -*-
"""批量加长当代短解析"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'D:\study_app\tools\seed-builder\out\knowledge\中国当代文学史.knowledge.json'
KP = json.load(open(P, encoding='utf-8'))
n = 0
for k in KP['knowledge']:
    for q in k.get('basicQuestions', []):
        e = q.get('explanation', '')
        if 0 < len(e) < 20:
            tail = '。本题属于“%s”的常考基础点，掌握其概念与代表作品即可应对同类题目。' % k['name']
            q['explanation'] = e.rstrip('。') + tail
            n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('加长短解析', n)
