# -*- coding: utf-8 -*-
"""处理最后 4 条异常：
- k_xdyy_xiuci_05/5 现代汉语 choice 补长
- q_000172/q_000136 古汉简答：解析无实质置空（answer 已完整）
- c_000128 现代文学简答：工作残留置空（answer 已完整）
"""
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. 现代汉语 choice 补长
P1 = r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json'
k = json.load(open(P1, encoding='utf-8'))
for x in k['knowledge']:
    for i, bq in enumerate(x.get('basicQuestions', [])):
        if x['id'] == 'k_xdyy_xiuci_05' and i == 5:
            bq['explanation'] = '以“巾帼”这一服饰特征代指女性，是借代。借代以部分代整体、以特征代本体，重在相关性；与之相对的是重在相似性的比喻。'
            print('补长:', bq['explanation'])
json.dump(k, open(P1, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 2. 古汉简答置空
P2 = r'D:\study_app\tools\seed-builder\out\v09gudaihanyu\bank-gudai-hanyu.v09.json'
v09 = json.load(open(P2, encoding='utf-8'))
for q in v09:
    if q['id'] in ('bank-gudai-hanyu:q_000136', 'bank-gudai-hanyu:q_000172'):
        q['explanation'] = ''
        print('古汉置空:', q['id'])
json.dump(v09, open(P2, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 3. 现代文学 c_000128 置空
P3 = r'D:\study_app\tools\seed-builder\out\v09xiandaiwenxue\bank-zhongguo-xiandai-wenxue.v09.json'
v09m = json.load(open(P3, encoding='utf-8'))
for q in v09m:
    if q['id'] == 'bank-zhongguo-xiandai-wenxue:c_000128':
        q['explanation'] = ''
        print('现代文学置空:', q['id'])
json.dump(v09m, open(P3, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('done')
