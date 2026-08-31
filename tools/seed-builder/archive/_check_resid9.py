# -*- coding: utf-8 -*-
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

targets = [
    (r'out\v09gudaihanyu\bank-gudai-hanyu.v09.json', ['m_000543', 'c_000020']),
    (r'out\v09xiandaiwenxue\bank-zhongguo-xiandai-wenxue.v09.json', ['c_000011', 'c_000026', 'c_000030', 'c_000031', 'c_000120']),
]
for p, tails in targets:
    d = json.load(open(p, encoding='utf-8'))
    for q in d:
        if any(q.get('id', '').endswith(t) for t in tails):
            print('='*80)
            print(q.get('id'), '|', q.get('type'))
            print('解析:', q.get('explanation'))
