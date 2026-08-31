# -*- coding: utf-8 -*-
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 从 knowledge.json 导出所有含"本题答案为"模板的基础题
k = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json', encoding='utf-8'))
out = []
for x in k['knowledge']:
    for i, bq in enumerate(x.get('basicQuestions', [])):
        e = re.sub(r'\s+', '', bq.get('explanation') or '')
        if '本题答案为' in e:
            out.append({
                'kp_id': x['id'],
                'kp_name': x.get('name', ''),
                'bq_idx': i,
                'stem': bq.get('stem', ''),
                'answer': bq.get('answer', ''),
                'options': bq.get('options', []),
                'type': bq.get('type', 'single_choice'),
                'explanation': bq.get('explanation', ''),
            })
print('模板题总数:', len(out))
# 按知识点聚类统计
from collections import Counter
kp_cnt = Counter(o['kp_name'] for o in out)
print('知识点数:', len(kp_cnt))
for kpn, c in kp_cnt.most_common():
    print(f'  {kpn}: {c}')
# 写出全量信息供重写
with open(r'D:\study_app\tools\seed-builder\out\reports\expl_audit\G_modern_detail.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('已导出 → out/reports/expl_audit/G_modern_detail.json')
