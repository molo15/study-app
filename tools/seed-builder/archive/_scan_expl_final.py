# -*- coding: utf-8 -*-
import io, sys, json, zipfile, glob, os, re
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

banks = glob.glob(r'D:\study_app\app\assets\banks\bank-*.zip')

# 全量：对每题分类打标（可叠加），输出统计表 + 受影响 id 清单
pat_resid = re.compile(r'素材块|对应素材标题|正文块|素材n')
pat_tail = re.compile(r'本题属于.{0,20}常考基础点')
pat_grade = re.compile(r'[（(](基础|变式|拓展|提升|综合|识记|理解)[）)]$')
pat_lead = re.compile(r'^解析[:：]')
pat_hint = re.compile(r'^(解析[:：]?\s*)?(须答出|本题考查|本题为|答题要点|须从|注意从|可从)')

result = defaultdict(lambda: defaultdict(int))
detail = defaultdict(list)
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
            if pat_resid.search(expl): cats.append('素材底稿残留')
            if pat_tail.search(expl): cats.append('本题属于尾巴')
            if pat_grade.search(expl): cats.append('等级标注尾巴')
            if pat_lead.match(expl): cats.append('解析冒号前缀')
            if pat_hint.match(expl) and q.get('type') == 'short_answer': cats.append('简答提示语')
            for c in cats:
                result[bank][c] += 1
                if len(detail[c]) < 1000:
                    detail[c].append(q.get('id'))

print('总题数:', total)
print()
hdr = ['科目', '素材底稿残留', '本题属于尾巴', '等级标注尾巴', '解析冒号前缀', '简答提示语']
print('| ' + ' | '.join(hdr) + ' |')
print('|' + '---|' * len(hdr))
for bank in sorted(result):
    row = [bank] + [str(result[bank].get(h, 0)) for h in hdr[1:]]
    print('| ' + ' | '.join(row) + ' |')

# 汇总去重后受影响题数
union = defaultdict(set)
for c, ids in detail.items():
    for i in ids:
        union[i].add(c)
print()
print('受影响题目总数(去重):', len(union))
# 各科受影响去重数
by_bank_union = defaultdict(set)
for i, cs in union.items():
    bank = i.split(':')[0]
    by_bank_union[bank].add(i)
for bank in sorted(by_bank_union):
    print(f'  {bank}: {len(by_bank_union[bank])} 题')

# 输出受影响 id 清单文件
os.makedirs(r'D:\study_app\tools\seed-builder\out\reports\expl_audit', exist_ok=True)
with open(r'D:\study_app\tools\seed-builder\out\reports\expl_audit\affected_ids.txt', 'w', encoding='utf-8') as f:
    for i in sorted(union):
        f.write(i + '\n')
print()
print('受影响 id 清单 → out/reports/expl_audit/affected_ids.txt')
