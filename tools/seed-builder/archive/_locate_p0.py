# -*- coding: utf-8 -*-
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# P0 硬错配 14 条：定位其在源 json（v09 / v010 basic / knowledge）中的位置
targets = {
    'bank-xiandai-hanyu': ['z_000109', 'q_000009', 'q_000004'],
    'bank-zhongguo-dangdai-wenxue': ['t_000073'],
    'bank-zhongguo-gudai-wenxue': ['q_000080', 'q_000001', 'q_000010'],
    'bank-zhongguo-xiandai-wenxue': ['t_000336', 't_000373', 't_000124', 't_000207', 't_000313', 't_000217', 't_000178'],
}
sources = {
    'bank-xiandai-hanyu': r'out\v09\bank-xiandai-hanyu.v09.json',
    'bank-gudai-hanyu': r'out\v09gudaihanyu\bank-gudai-hanyu.v09.json',
    'bank-zhongguo-gudai-wenxue': r'out\v09gudaiwenxue\bank-zhongguo-gudai-wenxue.v09.json',
    'bank-zhongguo-xiandai-wenxue': r'out\v09xiandaiwenxue\bank-zhongguo-xiandai-wenxue.v09.json',
    'bank-zhongguo-dangdai-wenxue': r'out\v09dangdai\bank-zhongguo-dangdai-wenxue.v09.json',
}
for bank, tails in targets.items():
    p = sources[bank]
    d = json.load(open(p, encoding='utf-8'))
    for q in d:
        qid = q.get('id', '')
        if any(qid.endswith(t) for t in tails):
            print('='*80)
            print('FOUND:', qid, 'in', p)
            print('  type:', q.get('type'))
            print('  answer:', q.get('answer'))
            print('  options:')
            for o in q.get('options', []):
                print('    ', o.get('key'), o.get('text'))
            print('  explanation:', (q.get('explanation') or '')[:300])
