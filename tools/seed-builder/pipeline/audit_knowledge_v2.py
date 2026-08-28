# -*- coding: utf-8 -*-
"""全科知识点粒度审查（按 v2 新规则）
规则：
- 每章知识点数 6~15 健康；<6 稀疏（偏粗）；>15 偏密
- 每知识点基础题 1~3 健康；0 空；>3 可能过粗（一个点塞太多内容）
- 知识点必须有非空 summary、清晰命名、id 唯一
"""
import io, sys, json, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from collections import Counter, defaultdict

OK, WARN, BAD = 'OK', 'WARN', 'BAD'

def audit_bank(path):
    d = json.load(open(path, encoding='utf-8'))
    ks = d['knowledge']
    chap = defaultdict(list)
    for k in ks:
        chap[k['chapter']].append(k)
    print('=' * 70)
    print('### ' + (d.get('name') or path.split('\\')[-1]))
    print('=' * 70)
    issues = []
    for ch, items in chap.items():
        n = len(items)
        q = sum(len(k.get('basicQuestions', [])) for k in items)
        n_status = OK if 6 <= n <= 15 else (BAD if n < 4 else WARN)
        # 每点题数分布
        per = [len(k.get('basicQuestions', [])) for k in items]
        empty = sum(1 for x in per if x == 0)
        heavy = sum(1 for x in per if x > 3)
        mark = '  '
        if n_status != OK:
            mark = ' ⚠'
        print(f'{mark} {ch}: {n}点/{q}题   [题数分布 {min(per) if per else 0}-{max(per) if per else 0}, 空{empty} 超3题{heavy}]')
        if n_status == BAD:
            issues.append(f'{ch}: 知识点过少({n})')
        if empty:
            issues.append(f'{ch}: {empty} 个知识点无题')
        # summary 检查
        for k in items:
            if not (k.get('summary') or '').strip():
                issues.append(f'  {ch}/{k["name"]}: 缺 summary')
            if not (k.get('name') or '').strip():
                issues.append(f'  {ch}: 知识点无名')
    # id 唯一性
    ids = [k['id'] for k in ks]
    dup = [x for x, c in Counter(ids).items() if c > 1]
    if dup:
        issues.append(f'重复知识点 id: {dup[:5]}')
    print()
    if issues:
        print('  [问题清单]')
        for i in issues:
            print('   -', i)
    else:
        print('  [无问题]')
    print()

for f in sorted(glob.glob(r'D:\study_app\tools\seed-builder\out\knowledge\*.knowledge.json')):
    name = f.split('\\')[-1]
    if '_' in name.replace('.knowledge.json', ''):
        continue
    audit_bank(f)
