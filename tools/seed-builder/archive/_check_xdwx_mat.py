# -*- coding: utf-8 -*-
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'out\v09xiandaiwenxue\bank-zhongguo-xiandai-wenxue.v09.json'
d = json.load(open(p, encoding='utf-8'))
n = 0
for q in d:
    e = q.get('explanation') or ''
    if re.search(r'素材块|正文块|素材n|素材[0-9a-zA-Z]{5,}|对应素材标题', e):
        print(q.get('id'), q.get('type'), '|', e[:110])
        n += 1
        if n >= 15:
            break
print('total shown', n)
