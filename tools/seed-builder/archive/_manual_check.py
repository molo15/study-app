# -*- coding: utf-8 -*-
"""人工精读 7 条 P0 候选 + 14 条 P1 候选。"""
import io, sys, json, os, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load_qs(path):
    z = zipfile.ZipFile(path)
    qs = []
    for n in z.namelist():
        if n.startswith('questions/') and n.endswith('.json'):
            qs.extend(json.loads(z.read(n)))
    return qs

# P0 候选
targets = {
    'bank-xiandai-hanyu-v0.14.0.zip': ['q_000009', 'z_000109', 'q_000004'],
    'bank-zhongguo-dangdai-wenxue-v0.14.0.zip': ['b_000318'],
    'bank-zhongguo-xiandai-wenxue-v0.14.0.zip': ['q_000163', 'q_000088', 'q_000142'],
}
for f, ids in targets.items():
    print('==========', f)
    qs = load_qs(os.path.join(r'D:\study_app\app\assets\banks', f))
    for q in qs:
        if any(q['id'].endswith(i) for i in ids):
            print('---', q['id'], '| type:', q.get('type'))
            print('  stem:', (q.get('stem') or ''))
            for o in q.get('options', []):
                print('    ', o.get('key'), o.get('text',''))
            print('  answer:', q.get('answer'))
            print('  expl:', (q.get('explanation') or ''))
            print()
