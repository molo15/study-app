# -*- coding: utf-8 -*-
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
k = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\古代汉语.knowledge.json', encoding='utf-8'))
pat = re.compile(r'素材块|素材n|正文块|对应素材标题|覆盖缺口|本题答案为|存量题未覆盖|本题属[于]?.{0,12}常考')
n = 0
for x in k['knowledge']:
    for i, bq in enumerate(x.get('basicQuestions', [])):
        e = re.sub(r'\s+', '', bq.get('explanation') or '')
        if pat.search(e):
            n += 1
            if n <= 8:
                print(x['id'], x.get('name'), i)
                print('   expl:', (bq.get('explanation') or '')[:140])
                print()
print('残留:', n)
