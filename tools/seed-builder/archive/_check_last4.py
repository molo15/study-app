# -*- coding: utf-8 -*-
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. kb_00033
k = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json', encoding='utf-8'))
for x in k['knowledge']:
    for i, bq in enumerate(x.get('basicQuestions', [])):
        if x['id'] == 'k_xdyy_yuyin_14' and i == 11:
            pass
for x in k['knowledge']:
    for i, bq in enumerate(x.get('basicQuestions', [])):
        e = re.sub(r'\s+', '', bq.get('explanation') or '')
        if len(e) < 20 and bq.get('type') not in ('blank', 'short_answer'):
            print('现代汉语 短:', x['id'], i, bq.get('stem','')[:24], '|', bq.get('explanation','')[:50])

# 2. q_000136/q_000172
v09 = json.load(open(r'D:\study_app\tools\seed-builder\out\v09gudaihanyu\bank-gudai-hanyu.v09.json', encoding='utf-8'))
for q in v09:
    if q['id'] in ('bank-gudai-hanyu:q_000136', 'bank-gudai-hanyu:q_000172'):
        print('古汉保留轨:', q['id'], '| type:', q.get('type'), '| stem:', (q.get('stem') or '')[:30], '| expl:', repr(q.get('explanation',''))[:60], '| ans:', repr(q.get('answer',''))[:40])

# 3. c_000128
v09m = json.load(open(r'D:\study_app\tools\seed-builder\out\v09xiandaiwenxue\bank-zhongguo-xiandai-wenxue.v09.json', encoding='utf-8'))
for q in v09m:
    if q['id'] == 'bank-zhongguo-xiandai-wenxue:c_000128':
        print('现代文学 c_000128:', '| type:', q.get('type'), '| expl:', (q.get('explanation') or '')[:120])
