# -*- coding: utf-8 -*-
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'out\v09xiandaiwenxue\bank-zhongguo-xiandai-wenxue.v09.json'
d = json.load(open(p, encoding='utf-8'))
for q in d:
    e = (q.get('explanation') or '')
    if re.search(r'覆盖缺口|系统对比|须从|素材', e):
        print('='*70)
        print(q.get('id'), q.get('type'))
        print('解析:', e[:400])
        print('answer:', (q.get('answer') or '')[:60])
