# -*- coding: utf-8 -*-
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
k = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json', encoding='utf-8'))
for x in k['knowledge']:
    for i, bq in enumerate(x.get('basicQuestions', [])):
        e = bq.get('explanation') or ''
        if len(re.sub(r'\s+', '', e)) < 20:
            print(x['id'], x.get('name'), i)
            print('   stem:', bq.get('stem'))
            print('   answer:', bq.get('answer'))
            print('   expl:', e)
