# -*- coding: utf-8 -*-
import io, sys, json, zipfile, glob, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

outdir = r'D:\study_app\tools\seed-builder\out\reports\expl_audit'
ids = set(l.strip() for l in open(os.path.join(outdir, 'G_ans_template.txt'), encoding='utf-8') if l.strip())

banks = glob.glob(r'D:\study_app\app\assets\banks\bank-*.zip')
q_by_id = {}
for b in banks:
    z = zipfile.ZipFile(b)
    for n in z.namelist():
        if not n.startswith('questions/'):
            continue
        for q in json.loads(z.read(n)):
            q_by_id[q['id']] = q

# G 类模板题：展示带选项的样本
shown = 0
for i in sorted(ids):
    q = q_by_id.get(i)
    if not q:
        continue
    if q.get('type') == 'single_choice':
        print('='*80)
        print(i, q.get('type'), q.get('chapter'))
        print('题干:', (q.get('stem') or '')[:70])
        for o in q.get('options', []):
            mark = ' <==ans' if o.get('text') == q.get('answer') else ''
            print('   ', o.get('key'), o.get('text'), mark)
        print('解析:', (q.get('explanation') or '')[:110])
        print('knowledgeId:', q.get('knowledgeId'))
        shown += 1
        if shown >= 10:
            break
