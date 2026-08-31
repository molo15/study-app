# -*- coding: utf-8 -*-
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 现代汉语 G 模板题的 knowledge 节点 summary 长度统计
k = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json', encoding='utf-8'))
kp_by_id = {}
for x in k['knowledge']:
    kp_by_id[x['id']] = x

# 找出含模板解析的知识点
tpl_kids = set()
n_tpl = 0
for x in k['knowledge']:
    for bq in x.get('basicQuestions', []):
        e = re.sub(r'\s+', '', bq.get('explanation') or '')
        if '本题答案为' in e:
            tpl_kids.add(x['id'])
            n_tpl += 1
print('模板解析题:', n_tpl, '涉及知识点:', len(tpl_kids))
print()
for kid in sorted(tpl_kids):
    x = kp_by_id[kid]
    s = re.sub(r'\s+', '', x.get('summary') or '')
    print(f'- {kid} {x.get("name")} summary_len={len(s)}: {s[:60]}')
