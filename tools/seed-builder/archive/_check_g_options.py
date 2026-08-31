# -*- coding: utf-8 -*-
"""检查 G 模板 127 题：选项污染（含标点/杂字符）+ 答案不在选项中"""
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

data = json.load(open(r'D:\study_app\tools\seed-builder\out\reports\expl_audit\G_modern_detail.json', encoding='utf-8'))

# 1. 选项含奇怪标点
pat_bad = re.compile(r'[。；;：:，,、（）\[\]]')
print('== 选项含标点/污染 ==')
for o in data:
    for opt in o.get('options', []):
        if pat_bad.search(opt):
            print(f"  {o['kp_name']} | {o['stem'][:24]} | OPT: {opt!r}")

# 2. 答案不在选项中
print()
print('== 答案不在选项 ==')
for o in data:
    if o.get('type') == 'choice' and o.get('answer') not in o.get('options', []):
        print(f"  {o['kp_name']} | {o['stem'][:24]} | ANS: {o['answer']!r}")
        print(f"     opts: {o.get('options')}")
