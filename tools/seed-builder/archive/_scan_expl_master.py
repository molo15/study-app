# -*- coding: utf-8 -*-
"""题目-解析匹配性全量审查：v0.14.0 五科题库
问题类型：
A 硬错配(解析明示字母≠答案)
B 素材底稿残留(解析是出题工作底稿)
C 本题属于…尾巴
D 等级标注尾巴(基础/变式/拓展)
E 解析冒号前缀
F 简答提示语(解析只是答题要点)
G 本题答案为模板(现代汉语客观题)
"""
import io, sys, json, zipfile, glob, os, re
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

banks = glob.glob(r'D:\study_app\app\assets\banks\bank-*.zip')

# F: 硬错配 14 条清单（已人工核实）
hard_conflicts = {
    'bank-xiandai-hanyu:z_000109', 'bank-xiandai-hanyu:q_000009', 'bank-xiandai-hanyu:q_000004',
    'bank-zhongguo-dangdai-wenxue:t_000073',
    'bank-zhongguo-gudai-wenxue:q_000080', 'bank-zhongguo-gudai-wenxue:q_000001', 'bank-zhongguo-gudai-wenxue:q_000010',
    'bank-zhongguo-xiandai-wenxue:t_000336', 'bank-zhongguo-xiandai-wenxue:t_000373',
    'bank-zhongguo-xiandai-wenxue:t_000124', 'bank-zhongguo-xiandai-wenxue:t_000207',
    'bank-zhongguo-xiandai-wenxue:t_000313', 'bank-zhongguo-xiandai-wenxue:t_000217',
    'bank-zhongguo-xiandai-wenxue:t_000178',
}

pat_resid = re.compile(r'素材块|对应素材标题|正文块|素材n|素材[0-9a-z]{5,}')
pat_tail = re.compile(r'本题属于.{0,25}常考基础点')
pat_grade = re.compile(r'[（(](基础|变式|拓展|提升|综合|识记|理解)[）)]$')
pat_lead = re.compile(r'^解析[:：]')
pat_ans_tpl = re.compile(r'本题答案为')
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
            qid = q.get('id', '')
            expl = re.sub(r'\s+', '', q.get('explanation') or '')
            t = q.get('type', '')
            cats = []
            if qid in hard_conflicts:
                cats.append('A硬错配字母')
            if pat_resid.search(expl):
                cats.append('B素材底稿残留')
            if pat_tail.search(expl):
                cats.append('C本题属于尾巴')
            if pat_grade.search(expl):
                cats.append('D等级标注尾巴')
            if pat_lead.match(expl):
                cats.append('E解析冒号前缀')
            if pat_hint.match(expl) and t == 'short_answer':
                cats.append('F简答提示语')
            if pat_ans_tpl.search(expl):
                cats.append('G本题答案为模板')
            for c in cats:
                result[bank][c] += 1
                detail[c].append(qid)

print('总题数:', total)
print()
hdr = ['科目', 'A硬错配', 'B素材残留', 'C本题属于', 'D等级标注', 'E冒号前缀', 'F简答提示', 'G答案为模板']
catnames = ['A硬错配字母', 'B素材底稿残留', 'C本题属于尾巴', 'D等级标注尾巴', 'E解析冒号前缀', 'F简答提示语', 'G本题答案为模板']
print('| ' + ' | '.join(hdr) + ' |')
print('|' + '---|' * len(hdr))
for bank in sorted(result):
    row = [bank] + [str(result[bank].get(cn, 0)) for cn in catnames]
    print('| ' + ' | '.join(row) + ' |')

union = defaultdict(set)
for c, ids in detail.items():
    for i in ids:
        union[i].add(c)
print()
print('受影响题目总数(去重):', len(union))
by_bank_union = defaultdict(set)
for i, cs in union.items():
    by_bank_union[i.split(':')[0]].add(i)
for bank in sorted(by_bank_union):
    print(f'  {bank}: {len(by_bank_union[bank])} 题')

# 输出分类清单
outdir = r'D:\study_app\tools\seed-builder\out\reports\expl_audit'
for c, ids in detail.items():
    fn = {'A硬错配字母': 'A_hard_conflict', 'B素材底稿残留': 'B_material_residue',
          'C本题属于尾巴': 'C_tail', 'D等级标注尾巴': 'D_grade', 'E解析冒号前缀': 'E_lead',
          'F简答提示语': 'F_hint', 'G本题答案为模板': 'G_ans_template'}[c]
    with open(os.path.join(outdir, fn + '.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(sorted(ids)))
print()
print('清单 → out/reports/expl_audit/*.txt')
