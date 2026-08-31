# -*- coding: utf-8 -*-
import io, sys, json, zipfile, glob, os, re
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

banks = glob.glob(r'D:\study_app\app\assets\banks\bank-*.zip')

pat = re.compile(r'本题答案为|答案为|答案[是为：]|故答案为')
result = defaultdict(lambda: defaultdict(int))
samples = defaultdict(list)
total = 0
for b in banks:
    bank = os.path.basename(b).replace('-v0.14.0.zip', '')
    z = zipfile.ZipFile(b)
    for n in z.namelist():
        if not n.startswith('questions/'):
            continue
        for q in json.loads(z.read(n)):
            total += 1
            expl = re.sub(r'\s+', '', q.get('explanation') or '')
            m = pat.search(expl)
            if m:
                result[bank]['含本题答案为'] += 1
                if len(samples['含本题答案为']) < 12:
                    samples['含本题答案为'].append((bank, q.get('id'), q.get('type'), (q.get('stem') or '')[:22], expl[:80]))

print('总题数:', total)
print('| 科目 | 含“本题答案为” |')
print('|---|---|')
for bank in sorted(result):
    print(f"| {bank} | {result[bank]['含本题答案为']} |")
print()
for c, ss in samples.items():
    for s in ss:
        print('   ', s[0], '|', s[1], '|', s[2], '|', s[3], '|', s[4])
