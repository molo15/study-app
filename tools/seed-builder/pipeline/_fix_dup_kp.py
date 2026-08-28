# -*- coding: utf-8 -*-
"""修复当代文学史重复知识点 id：合并 basicQuestions 到第一个，删除多余"""
import io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'D:\study_app\tools\seed-builder\out\knowledge\中国当代文学史.knowledge.json'
KP = json.load(open(P, encoding='utf-8'))

def norm(s):
    return re.sub(r'[（）()。，、；：""“”\'  ]', '', s)

from collections import defaultdict
by_id = defaultdict(list)
for i, k in enumerate(KP['knowledge']):
    by_id[k['id']].append((i, k))

merged = 0
for kid, lst in by_id.items():
    if len(lst) <= 1:
        continue
    keep_idx, keep = lst[0]
    for idx, k in lst[1:]:
        for q in k.get('basicQuestions', []):
            if not any(norm(q['stem']) == norm(e['stem']) for e in keep.get('basicQuestions', [])):
                keep['basicQuestions'].append(q)
                merged += 1
        # 标记删除
        KP['knowledge'][idx] = None

KP['knowledge'] = [k for k in KP['knowledge'] if k is not None]
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('合并重复题', merged, '个；去重后知识点数', len(KP['knowledge']))

# 复验
ids = defaultdict(int)
for k in KP['knowledge']:
    ids[k['id']] += 1
dup = {i: c for i, c in ids.items() if c > 1}
print('剩余重复 id:', dup)
