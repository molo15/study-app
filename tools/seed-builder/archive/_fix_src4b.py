# -*- coding: utf-8 -*-
"""修正 q_000163/q_000142 的解析字母结论（按源选项顺序）：
- q_000163: 故B不选 -> 故E不选（E=严格三一律，源顺序唯一错误项）
- q_000142: 故D不选 -> 故E不选（E=完全否定古典文学传统，源顺序唯一错误项）
"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P3 = r'D:\study_app\tools\seed-builder\out\v09xiandaiwenxue\bank-zhongguo-xiandai-wenxue.v09.json'
v09m = json.load(open(P3, encoding='utf-8'))
for q in v09m:
    if q['id'] == 'bank-zhongguo-xiandai-wenxue:q_000163':
        old = q.get('explanation','')
        q['explanation'] = old.replace('故B不选', '故E不选')
        print('q_000163 ->', q['explanation'][-30:])
    if q['id'] == 'bank-zhongguo-xiandai-wenxue:q_000142':
        old = q.get('explanation','')
        q['explanation'] = old.replace('故D不选', '故E不选')
        print('q_000142 ->', q['explanation'][-30:])
json.dump(v09m, open(P3, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('saved')
