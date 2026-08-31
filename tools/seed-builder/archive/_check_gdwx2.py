# -*- coding: utf-8 -*-
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'out\v09gudaiwenxue\bank-zhongguo-gudai-wenxue.v09.json'
d = json.load(open(p, encoding='utf-8'))
# 抽查之前的提示语样本
targets = ['lun_084', 't_000275', 't_000411', 'lun_047', 'lun_027', 'lun_050']
for q in d:
    if any(q.get('id', '').endswith(t) for t in targets):
        print(q.get('id'), '| 解析:', (q.get('explanation') or '')[:80])
        print('   answer:', (q.get('answer') or '')[:60])
        print()
