# -*- coding: utf-8 -*-
"""看源头 v09 中 3 条现代汉语保留轨题的 options/answer/expl 原始形态。"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
v09 = json.load(open(r'D:\study_app\tools\seed-builder\out\v09\bank-xiandai-hanyu.v09.json', encoding='utf-8'))
for q in v09:
    if q['id'] in ('bank-xiandai-hanyu:q_000009', 'bank-xiandai-hanyu:z_000109', 'bank-xiandai-hanyu:q_000004'):
        print('===', q['id'])
        print('  type:', q.get('type'))
        print('  options:')
        for o in q.get('options', []):
            print('    ', o.get('key'), '|', o.get('text','')[:40])
        print('  answer:', repr(q.get('answer')))
        print('  expl:', (q.get('explanation') or '')[-80:])
        print()
