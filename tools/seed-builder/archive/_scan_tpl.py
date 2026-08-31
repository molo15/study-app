# -*- coding: utf-8 -*-
import io, sys, json, zipfile, glob, os, re
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

banks = glob.glob(r'D:\study_app\app\assets\banks\bank-*.zip')

# 模式A：解析即"本题考查…本题答案为X"模板（客观题，无实质解析）
pat_ans_template = re.compile(r'本题考查.{0,40}知识点.{0,20}本题答案为')
# 模式B：解析以"本题考查/本题为"开头且后面是答题提示
pat_hint2 = re.compile(r'^(本题考查|本题为|本题属|本题是)')
# 模式C：解析只有"本题考查X知识点"而无实质解释（不足40字即视为模板）
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
            cats = []
            if pat_ans_template.search(expl):
                cats.append('本题答案为模板')
            if pat_hint2.match(expl) and len(expl) < 70 and '答案为' not in expl:
                cats.append('短提示语')
            for c in cats:
                result[bank][c] += 1
                if len(samples[c]) < 8:
                    samples[c].append((bank, q.get('id'), q.get('type'), (q.get('stem') or '')[:24], expl[:70]))

print('总题数:', total)
print()
print('| 科目 | 本题答案为模板 | 短提示语 |')
print('|---|---|---|')
for bank in sorted(result):
    print(f"| {bank} | {result[bank].get('本题答案为模板',0)} | {result[bank].get('短提示语',0)} |")
print()
for c, ss in samples.items():
    print(f'### {c}:')
    for s in ss:
        print('   ', s[0], '|', s[1], '|', s[2], '|', s[3], '|', s[4])
