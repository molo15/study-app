# -*- coding: utf-8 -*-
import io, sys, json, zipfile, glob, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 读取 affected id 清单，统计各类题的 answer 字段质量
ids_files = {}
outdir = r'D:\study_app\tools\seed-builder\out\reports\expl_audit'
for fn in ['A_hard_conflict', 'B_material_residue', 'C_tail', 'D_grade', 'E_lead', 'F_hint', 'G_ans_template']:
    p = os.path.join(outdir, fn + '.txt')
    ids_files[fn] = set(l.strip() for l in open(p, encoding='utf-8') if l.strip())

# 加载五科 zip，按 id 找到题目
banks = glob.glob(r'D:\study_app\app\assets\banks\bank-*.zip')
q_by_id = {}
for b in banks:
    z = zipfile.ZipFile(b)
    for n in z.namelist():
        if not n.startswith('questions/'):
            continue
        for q in json.loads(z.read(n)):
            q_by_id[q['id']] = q

for fn in ['B_material_residue', 'F_hint', 'G_ans_template']:
    ids = ids_files[fn]
    types = {}
    ans_len = {'short': 0, 'long': 0, 'none': 0}
    ans_preview = []
    for i in ids:
        q = q_by_id.get(i)
        if not q:
            continue
        types[q.get('type')] = types.get(q.get('type'), 0) + 1
        a = q.get('answer') or ''
        if isinstance(a, list):
            a = '、'.join(a)
        a = re.sub(r'\s+', '', str(a))
        L = len(a)
        if L < 10:
            ans_len['short'] += 1
        elif L < 40:
            ans_len['long'] += 1
        else:
            ans_len['none'] += 1  # 命名改为 long
        if len(ans_preview) < 6:
            ans_preview.append((i, q.get('type'), a[:80]))
    print(f'== {fn} ({len(ids)})')
    print('   type:', types)
    print('   answer长度(短<10 / 中10-40 / 长>40):', ans_len)
    for pv in ans_preview:
        print('     ', pv)
    print()
