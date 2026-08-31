# -*- coding: utf-8 -*-
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 看古代汉语 knowledge 里的模板解析形态
k = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\古代汉语.knowledge.json', encoding='utf-8'))
cnt = 0
for x in k['knowledge']:
    for i, bq in enumerate(x.get('basicQuestions', [])):
        e = re.sub(r'\s+', '', bq.get('explanation') or '')
        if re.search(r'本题属于.{0,20}常考|本题答案为', e):
            cnt += 1
            if cnt <= 6:
                print(x['id'], x.get('name'), i)
                print('   stem:', (bq.get('stem') or '')[:40])
                print('   expl:', (bq.get('explanation') or '')[:130])
                print()
print('古代汉语模板类:', cnt)

k2 = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国当代文学史.knowledge.json', encoding='utf-8'))
cnt2 = 0
for x in k2['knowledge']:
    for i, bq in enumerate(x.get('basicQuestions', [])):
        e = re.sub(r'\s+', '', bq.get('explanation') or '')
        if re.search(r'本题属于.{0,20}常考|本题答案为', e):
            cnt2 += 1
            if cnt2 <= 4:
                print(x['id'], x.get('name'), i)
                print('   stem:', (bq.get('stem') or '')[:40])
                print('   expl:', (bq.get('explanation') or '')[:130])
                print()
print('当代模板类:', cnt2)
