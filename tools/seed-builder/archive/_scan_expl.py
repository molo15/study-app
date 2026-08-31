# -*- coding: utf-8 -*-
import io, sys, json, zipfile, glob, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

banks = glob.glob(r'D:\study_app\app\assets\banks\bank-*.zip')

pat_resid = re.compile(r'素材块|本题属于|常考基础点|覆盖缺口|存量题|出题依据|补齐项|重点复习|知识点掌握')
pat_lead = re.compile(r'^解析[:：]')

resid = []
lead = []
for b in banks:
    z = zipfile.ZipFile(b)
    for n in z.namelist():
        if not n.startswith('questions/'):
            continue
        qs = json.loads(z.read(n))
        for q in qs:
            expl = q.get('explanation') or ''
            e = re.sub(r'\s+', '', expl)
            if pat_resid.search(e):
                resid.append((os.path.basename(b), n, q.get('id'), (q.get('stem') or '')[:22], expl[:100]))
            if pat_lead.match(e):
                lead.append((os.path.basename(b), n, q.get('id'), (q.get('stem') or '')[:22], expl[:80]))

print('含出题工作残留:', len(resid))
for x in resid[:30]:
    print('  R', x[0], '|', x[1], '|', x[2], '|', x[3], '|', x[4])
print()
print('解析以“解析：”开头:', len(lead))
for x in lead[:15]:
    print('  L', x[0], '|', x[1], '|', x[2], '|', x[3], '|', x[4])
