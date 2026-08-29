# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
KP = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\古代汉语.knowledge.json', encoding='utf-8'))
for k in KP['knowledge']:
    for q in k.get('basicQuestions', []):
        if 0 < len(q.get('explanation', '')) < 20:
            print(len(q['explanation']), '|', k['name'], '|', q['stem'][:22], '|', q['explanation'])
