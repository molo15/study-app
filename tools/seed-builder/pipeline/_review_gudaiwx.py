# -*- coding: utf-8 -*-
"""抽查古文史扩充题（ex_）答案/解析/选项质量 + 交叉验证知识点归属"""
import json, re, collections

g = json.load(open(r'D:\study_app\tools\seed-builder\out\refined\bank-zhongguo-gudai-wenxue.v012.json', encoding='utf-8'))
k = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json', encoding='utf-8'))['knowledge']
kid2 = {kk['id']: kk['name'] for kk in k}

ex = [q for q in g if q['id'].startswith('bank-zhongguo-gudai-wenxue:ex_') or q['id'].startswith('ex_')]
print('古文史扩充题数:', len(ex))
print('题型分布:', dict(collections.Counter(q['type'] for q in ex)))
print('解析长度: min', min(len(q.get('explanation','')) for q in ex), 'max', max(len(q.get('explanation','')) for q in ex))

# 1) 解析质量：占位/过短
bad_expl = [q for q in ex if len(q.get('explanation','')) < 20]
print('解析过短:', len(bad_expl))

# 2) 答案是否在选项中（选择题）
choice = [q for q in ex if q['type'] in ('single_choice','multi_choice')]
bad_ans = []
for q in choice:
    texts = {o['text'] for o in q['options']}
    ans = q['answer']
    if q['type']=='single_choice' and ans not in texts:
        bad_ans.append(q['id'])
    if q['type']=='multi_choice' and not set(ans).issubset(texts):
        bad_ans.append(q['id'])
print('选择题答案不在选项:', len(bad_ans))

# 3) 知识点归属（有 kid 且有效）
nokid = [q for q in ex if not q.get('knowledgeId') or q.get('knowledgeId') not in kid2]
print('扩充题无有效kid:', len(nokid))

# 4) 随机抽查 8 道含解析的题，人工审
import random
random.seed(7)
sample = random.sample(ex, 8)
for q in sample:
    print('='*60)
    print('['+q['id']+']', q['type'], '|', kid2.get(q.get('knowledgeId'),'?'))
    print('题干:', q['stem'][:80])
    if q['options']:
        print('选项:', [o['text'][:35] for o in q['options']])
    print('答案:', (q['answer'] if isinstance(q['answer'],str) else q['answer']))
    print('解析:', q.get('explanation','')[:110])
