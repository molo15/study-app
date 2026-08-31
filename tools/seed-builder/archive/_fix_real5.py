# -*- coding: utf-8 -*-
"""修 5 条真实残留：
- q_000088 解析笔误（C、C->C、D）
- c_000034/c_000035 素材引用残留
- q_000015 古汉 blank 工作标注残留
- q_000014 当代 blank 工作标注残留
另：q_000045/q_000066 是扫描误报，不改。
"""
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. q_000088 现代文学（先定位它在哪个源：v09xiandaiwenxue）
P3 = r'D:\study_app\tools\seed-builder\out\v09xiandaiwenxue\bank-zhongguo-xiandai-wenxue.v09.json'
v09m = json.load(open(P3, encoding='utf-8'))
for q in v09m:
    if q['id'] == 'bank-zhongguo-xiandai-wenxue:q_000088':
        old = q.get('explanation', '')
        q['explanation'] = old.replace('故C、C项不选', '故C、D项不选')
        print('q_000088 修笔误:')
        print('  old:', old)
        print('  new:', q['explanation'])
    if q['id'] in ('bank-zhongguo-xiandai-wenxue:c_000034', 'bank-zhongguo-xiandai-wenxue:c_000035'):
        q['explanation'] = re.sub(r'[。]?依据[-0-9a-z]+、[\s\S]*$', '', q.get('explanation', '')).strip()
        print(q['id'], '清素材引用 ->', q['explanation'][-60:])
json.dump(v09m, open(P3, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 2. q_000015 古汉
P2 = r'D:\study_app\tools\seed-builder\out\v09gudaihanyu\bank-gudai-hanyu.v09.json'
v09 = json.load(open(P2, encoding='utf-8'))
for q in v09:
    if q['id'] == 'bank-gudai-hanyu:q_000015':
        q['explanation'] = re.sub(r'（基础）（修复：[\s\S]*$', '', q.get('explanation', '')).strip()
        print('q_000015 ->', q['explanation'])
json.dump(v09, open(P2, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 3. q_000014 当代
P4 = r'D:\study_app\tools\seed-builder\out\v09dangdai\bank-zhongguo-dangdai-wenxue.v09.json'
v09d = json.load(open(P4, encoding='utf-8'))
for q in v09d:
    if q['id'] == 'bank-zhongguo-dangdai-wenxue:q_000014':
        q['explanation'] = re.sub(r'（变式）（修复：[\s\S]*$', '', q.get('explanation', '')).strip()
        print('q_000014 ->', q['explanation'])
json.dump(v09d, open(P4, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('done')
