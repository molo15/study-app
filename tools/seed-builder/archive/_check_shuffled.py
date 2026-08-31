# -*- coding: utf-8 -*-
"""检查 v0.14.0 现代汉语 3 条洗牌后最终状态：正确项 key vs 解析字母。"""
import io, sys, json, os, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load_qs(path):
    z = zipfile.ZipFile(path)
    qs = []
    for n in z.namelist():
        if n.startswith('questions/') and n.endswith('.json'):
            qs.extend(json.loads(z.read(n)))
    return qs

qs = load_qs(r'D:\study_app\app\assets\banks\bank-xiandai-hanyu-v0.14.0.zip')
for q in qs:
    if q['id'] in ('bank-xiandai-hanyu:q_000009', 'bank-xiandai-hanyu:z_000109', 'bank-xiandai-hanyu:q_000004'):
        print('===', q['id'])
        for o in q.get('options', []):
            mark = ' <==正确' if o['text'] == q.get('answer') else ''
            print('    ', o.get('key'), '|', o.get('text','')[:40], mark)
        print('  answer:', q.get('answer'))
        print('  expl tail:', (q.get('explanation') or '')[-40:])
        print()
