# -*- coding: utf-8 -*-
"""修 4 条源头解析字母错误（非洗牌导致）：
- b_000318 当代：C、D不属于 → 应说 A、B不属于
- q_000163 现代文学：故E不选 → 故B不选
- q_000088 现代文学：故C、C、D项不选 → 故A、B、C项不选
- q_000142 现代文学：故E不选 → 故D不选
"""
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 当代 b_000318
P4 = r'D:\study_app\tools\seed-builder\out\v09dangdai\bank-zhongguo-dangdai-wenxue.v09.json'
v09d = json.load(open(P4, encoding='utf-8'))
for q in v09d:
    if q['id'] == 'bank-zhongguo-dangdai-wenxue:b_000318':
        print('b_000318 old:', q.get('explanation','')[-60:])
        q['explanation'] = (q.get('explanation','')
            .replace('C、D不属于其内容分类', 'A、B不属于其内容分类'))
        print('b_000318 new:', q['explanation'][-60:])
json.dump(v09d, open(P4, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 现代文学 3 条
P3 = r'D:\study_app\tools\seed-builder\out\v09xiandaiwenxue\bank-zhongguo-xiandai-wenxue.v09.json'
v09m = json.load(open(P3, encoding='utf-8'))
for q in v09m:
    if q['id'] == 'bank-zhongguo-xiandai-wenxue:q_000163':
        q['explanation'] = (q.get('explanation','')).replace('故E不选', '故B不选')
        print('q_000163:', q['explanation'][-30:])
    if q['id'] == 'bank-zhongguo-xiandai-wenxue:q_000088':
        q['explanation'] = (q.get('explanation','')).replace('故C、C、D项不选', '故A、B、C项不选')
        print('q_000088:', q['explanation'][-40:])
    if q['id'] == 'bank-zhongguo-xiandai-wenxue:q_000142':
        q['explanation'] = (q.get('explanation','')).replace('故E不选', '故D不选')
        print('q_000142:', q['explanation'][-30:])
json.dump(v09m, open(P3, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('done')
