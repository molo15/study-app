# -*- coding: utf-8 -*-
import io, sys, json, zipfile, glob, os, re
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

banks = glob.glob(r'D:\study_app\app\assets\banks\bank-*.zip')

# 分类
cats = Counter()
samples = {}
def add(cat, item):
    cats[cat] += 1
    samples.setdefault(cat, []).append(item)

tot = 0
for b in banks:
    z = zipfile.ZipFile(b)
    for n in z.namelist():
        if not n.startswith('questions/'):
            continue
        qs = json.loads(z.read(n))
        for q in qs:
            tot += 1
            expl = q.get('explanation') or ''
            e = re.sub(r'\s+', '', expl)
            st = (q.get('stem') or '')
            t = q.get('type', '')
            # A. 出题底稿尾巴
            if '本题属于' in e and '常考' in e:
                add('A_出题底稿尾巴_本题属于', (os.path.basename(b), q.get('id'), st[:20], e[-40:]))
            # B. 答题提示而非答案（简答/名词解释/论述类）
            if t in ('short_answer',) and re.search(r'^(解析[:：]?\s*)?(须答出|本题考查|本题为|答题要点|应从|从.{1,6}作答|可分|建议|注意)', e):
                add('B_简答解析是提示语', (os.path.basename(b), q.get('id'), st[:24], e[:70]))
            # C. 解析带(基础)(变式)(拓展)等级标注
            if re.search(r'[（(](基础|变式|拓展|提升|综合|识记|理解)[）)]$', e):
                add('C_解析带等级标注', (os.path.basename(b), q.get('id'), st[:20], e[-24:]))
            # D. 解析以“解析：”开头
            if re.match(r'^解析[:：]', e):
                add('D_解析冒号前缀', (os.path.basename(b), q.get('id'), st[:20], e[:40]))
            # E. 解析引用素材块（AI工作残留）
            if '素材块' in e:
                add('E_素材块残留', (os.path.basename(b), q.get('id'), st[:24], e[:60]))

print('总题数:', tot)
for c in ['A_出题底稿尾巴_本题属于','B_简答解析是提示语','C_解析带等级标注','D_解析冒号前缀','E_素材块残留']:
    print()
    print(f'== {c}: {cats[c]}')
    for x in samples.get(c, [])[:12]:
        print('   ', x[0], '|', x[1], '|', x[2], '|', x[3])

# 简答题总数
sa = 0
for b in banks:
    z = zipfile.ZipFile(b)
    for n in z.namelist():
        if not n.startswith('questions/'):
            continue
        for q in json.loads(z.read(n)):
            if q.get('type') == 'short_answer':
                sa += 1
print()
print('简答题总数:', sa)
