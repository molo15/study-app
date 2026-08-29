# -*- coding: utf-8 -*-
import io, sys, glob, zipfile, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# 1) 选项<2 的题明细
print('===== 选项数<2 的题 =====')
cnt = 0
for zp in sorted(glob.glob(r'D:\study_app\app\assets\banks\*.zip')):
    with zipfile.ZipFile(zp) as z:
        for n in z.namelist():
            if n.startswith('questions/') and n.endswith('.json'):
                for q in json.loads(z.read(n)):
                    if q.get('type') in ('single_choice', 'multi_choice', 'true_false'):
                        nopt = len(q.get('options') or [])
                        if nopt < 2:
                            cnt += 1
                            if cnt <= 8:
                                print(zp.split('\\')[-1], '|', q['id'], '|', q.get('type'), '| opts', nopt, '|', (q.get('stem') or '')[:30])
print('总数:', cnt)
# 2) true_false 类选项数分布
print('===== true_false 选项数分布 =====')
dist = {}
for zp in sorted(glob.glob(r'D:\study_app\app\assets\banks\*.zip')):
    with zipfile.ZipFile(zp) as z:
        for n in z.namelist():
            if n.startswith('questions/') and n.endswith('.json'):
                for q in json.loads(z.read(n)):
                    if q.get('type') == 'true_false':
                        k = len(q.get('options') or [])
                        dist[k] = dist.get(k, 0) + 1
print(dist)
# 3) 重复 stem 具体 id
print('===== 重复题干明细 =====')
seen = {}
for zp in sorted(glob.glob(r'D:\study_app\app\assets\banks\*.zip')):
    with zipfile.ZipFile(zp) as z:
        for n in z.namelist():
            if n.startswith('questions/') and n.endswith('.json'):
                for q in json.loads(z.read(n)):
                    stem = q.get('stem', '')
                    seen.setdefault(stem, []).append((q['id'], q.get('type'), n.split('/')[-1]))
for stem, v in seen.items():
    if len(v) > 1:
        print(f'STEM: {stem[:36]}')
        for id_, t, f in v:
            print(f'    {id_} | {t} | {f}')
