# -*- coding: utf-8 -*-
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

k = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json', encoding='utf-8'))

# 1. 统计剩余"本题答案为"模板
n_tpl = 0
for x in k['knowledge']:
    for bq in x.get('basicQuestions', []):
        if '本题答案为' in re.sub(r'\s+', '', bq.get('explanation', '')):
            n_tpl += 1
print('剩余本题答案为模板:', n_tpl)

# 2. n 名称题现状
for x in k['knowledge']:
    for i, bq in enumerate(x.get('basicQuestions', [])):
        if x['id'] == 'k_xdyy_yuyin_16' and i == 5:
            print('n名称题:', bq)
