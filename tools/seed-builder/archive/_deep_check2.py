# -*- coding: utf-8 -*-
"""深查 3 条 P0 + 14 条 P1 的真实内容（v0.14.0 最终 zip）。"""
import io, sys, json, os, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load_qs(path):
    z = zipfile.ZipFile(path)
    qs = []
    for n in z.namelist():
        if n.startswith('questions/') and n.endswith('.json'):
            qs.extend(json.loads(z.read(n)))
    return qs

# P0 深查
qs_dd = load_qs(r'D:\study_app\app\assets\banks\bank-zhongguo-dangdai-wenxue-v0.14.0.zip')
for q in qs_dd:
    if q['id'] == 'bank-zhongguo-dangdai-wenxue:b_000318':
        print('=== b_000318')
        for o in q.get('options', []):
            m = ' <==正确' if o['text'] in (q.get('answer') if isinstance(q.get('answer'), list) else [q.get('answer')]) else ''
            print('    ', o.get('key'), o.get('text','')[:42], m)
        print('  answer:', q.get('answer'))
        print('  expl tail:', (q.get('explanation') or '')[-70:])

qs_xd = load_qs(r'D:\study_app\app\assets\banks\bank-zhongguo-xiandai-wenxue-v0.14.0.zip')
for q in qs_xd:
    if q['id'] in ('bank-zhongguo-xiandai-wenxue:q_000106', 'bank-zhongguo-xiandai-wenxue:q_000163'):
        print('===', q['id'])
        for o in q.get('options', []):
            m = ' <==正确' if o['text'] in (q.get('answer') if isinstance(q.get('answer'), list) else [q.get('answer')]) else ''
            print('    ', o.get('key'), o.get('text','')[:42], m)
        print('  answer:', q.get('answer'))
        print('  expl tail:', (q.get('explanation') or '')[-80:])
        print()
