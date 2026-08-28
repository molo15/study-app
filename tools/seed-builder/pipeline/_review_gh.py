# -*- coding: utf-8 -*-
"""再审：古汉扩充题（gh_）内容 + 全库选择题一致性 + 解析质量"""
import json, collections, random

g = json.load(open(r'D:\study_app\tools\seed-builder\out\refined\bank-gudai-hanyu.v012.json', encoding='utf-8'))
gh = [q for q in g if q['id'].startswith('gh_')]
print('古汉扩充题 gh_ 数:', len(gh))
print('题型:', dict(collections.Counter(q['type'] for q in gh)))
random.seed(3)
for q in random.sample(gh, min(6, len(gh))):
    print('='*56)
    print('[', q['id'], ']', q['type'], '|', q.get('knowledgeId'))
    print('题干:', q['stem'][:75])
    if q['options']:
        print('选项:', [o['text'][:30] for o in q['options']])
    print('答案:', q['answer'])
    print('解析:', q.get('explanation','')[:80])

# 全库选择题一致性：答案在选项、无重复选项、选项数>=2
print()
print('===== 全库选择题一致性 =====')
files = {
 '现汉':'out/refined/bank-xiandai-hanyu.refined2.json','古汉':'out/refined/bank-gudai-hanyu.v012.json',
 '古文史':'out/refined/bank-zhongguo-gudai-wenxue.v012.json','现文史':'out/refined/bank-zhongguo-xiandai-wenxue.quota.json',
 '当代':'out/refined/bank-zhongguo-dangdai-wenxue.refined2.json'}
for name, f in files.items():
    qs = json.load(open(f, encoding='utf-8'))
    choice = [q for q in qs if q['type'] in ('single_choice','multi_choice')]
    bad_ans, dup_opt, short_opt = [], [], []
    for q in choice:
        texts = [o['text'] for o in q['options']]
        if len(texts) < 2: short_opt.append(q['id'])
        if len(set(texts)) != len(texts): dup_opt.append(q['id'])
        ans = q['answer']
        if q['type']=='single_choice':
            if isinstance(ans, list): ans = ans[0] if ans else ''
            if ans not in texts: bad_ans.append(q['id'])
        else:
            if not (isinstance(ans, list) and set(ans).issubset(set(texts))): bad_ans.append(q['id'])
    print(f'{name}: 选择题{len(choice)} | 答案异常{len(bad_ans)} | 重复选项{len(dup_opt)} | 选项<2 {len(short_opt)}')
    for t in bad_ans[:4]: print('   bad_ans:', t)
    for t in dup_opt[:4]: print('   dup:', t)
