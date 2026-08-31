# -*- coding: utf-8 -*-
"""深查 v0.14.0 里残留的 P0/P1 具体内容。"""
import io, sys, json, os, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ASSETS = r'D:\study_app\app\assets\banks'

def load_qs(path):
    z = zipfile.ZipFile(path)
    qs = []
    for n in z.namelist():
        if n.startswith('questions/') and n.endswith('.json'):
            qs.extend(json.loads(z.read(n)))
    return qs

targets = {
    'bank-zhongguo-xiandai-wenxue-v0.14.0.zip': ['q_000045', 'q_000088', 'q_000066', 'c_000034', 'c_000035'],
    'bank-gudai-hanyu-v0.14.0.zip': ['q_000015'],
    'bank-zhongguo-dangdai-wenxue-v0.14.0.zip': ['q_000014'],
}
for f, ids in targets.items():
    print('==========', f)
    qs = load_qs(os.path.join(ASSETS, f))
    for q in qs:
        if any(q['id'].endswith(i) for i in ids):
            print('---', q['id'])
            print('  type:', q.get('type'), '| stem:', (q.get('stem') or '')[:50])
            for o in q.get('options', [])[:6]:
                print('    ', o.get('key'), o.get('text','')[:28])
            print('  answer:', q.get('answer'))
            print('  expl:', (q.get('explanation') or '')[:180])
