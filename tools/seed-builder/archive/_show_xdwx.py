# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国现代文学史.knowledge.json', encoding='utf-8'))
from collections import Counter
chap = Counter()
for k in d['knowledge']:
    chap[k['chapter']] += 1
print('=== 各章知识点数 ===')
for c, n in chap.items():
    print(f"  {c}: {n}")

# 重点：作家章/市民通俗小说/散文三 的详细知识点
focus = ['市民通俗小说（一）', '市民通俗小说（二）', '散文（三）', '巴金', '老舍', '艾青', '赵树理', '鲁迅（二）', '沈从文', '茅盾', '郭沫若']
print()
print('=== 重点章节知识点 ===')
for k in d['knowledge']:
    if k['chapter'] in focus:
        qs = k.get('basicQuestions', [])
        print(f"  [{k['id']}] {k['name']} ({k['chapter']}) {len(qs)}题")
