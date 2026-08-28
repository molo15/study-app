# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
KP = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\古代汉语.knowledge.json', encoding='utf-8'))
for k in KP['knowledge']:
    for q in k.get('basicQuestions', []):
        if len(q.get('explanation', '')) < 12:
            print('SHORT-EXP:', repr(q['stem'][:30]), '|', repr(q.get('explanation', '')))
