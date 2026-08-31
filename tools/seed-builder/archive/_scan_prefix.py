# -*- coding: utf-8 -*-
import io, sys, json, zipfile, glob, os, re
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

banks = glob.glob(r'D:\study_app\app\assets\banks\bank-*.zip')

# id 前缀统计
prefix_stat = Counter()
# 素材块残留按文件统计
by_file = defaultdict(list)
total = 0
for b in banks:
    bank = os.path.basename(b).replace('-v0.14.0.zip', '')
    z = zipfile.ZipFile(b)
    for n in z.namelist():
        if not n.startswith('questions/'): continue
        for q in json.loads(z.read(n)):
            total += 1
            qid = q.get('id', '')
            m = re.match(r'^[^:]+:([a-z_]+)_', qid)
            if m: prefix_stat[(bank, m.group(1))] += 1
            e = re.sub(r'\s+', '', q.get('explanation') or '')
            if '素材块' in e:
                by_file[(bank, n)].append((q.get('id'), (q.get('stem') or '')[:20]))

print('总题数:', total)
print()
print('== id 前缀分布（按科）==')
for (bank, pref), c in sorted(prefix_stat.items()):
    print(f'  {bank}: {pref} = {c}')
print()
print('== 素材块残留按文件 ==')
for (bank, n), items in sorted(by_file.items()):
    print(f'  {bank} {n}: {len(items)} 条')
    for i in items[:3]:
        print('      ', i)
