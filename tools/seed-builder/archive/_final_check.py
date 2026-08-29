# -*- coding: utf-8 -*-
import json, collections
BASE = r'D:\study_app\tools\seed-builder'
files = {
 '现汉':'out/refined/bank-xiandai-hanyu.refined2.json','古汉':'out/refined/bank-gudai-hanyu.v012.json',
 '古文史':'out/refined/bank-zhongguo-gudai-wenxue.v012.json','现文史':'out/refined/bank-zhongguo-xiandai-wenxue.quota.json',
 '当代':'out/refined/bank-zhongguo-dangdai-wenxue.refined2.json'}
print('=== 终检1：解析缺口（basic 轨，须 0） ===')
for name,f in files.items():
    qs=json.load(open(f'{BASE}/{f}',encoding='utf-8'))
    basic=[q for q in qs if q.get('purpose')=='basic']
    gap=[q['id'] for q in basic if not (q.get('explanation') or '').strip() or len((q.get('explanation') or '').strip())<20]
    print(f'  {name}: basic{len(basic)} 解析缺口{len(gap)}')
print()
print('=== 终检2：知识点分布集中度 ===')
for name,f in files.items():
    qs=json.load(open(f'{BASE}/{f}',encoding='utf-8'))
    basic=[q for q in qs if q.get('purpose')=='basic' and q.get('knowledgeId')]
    c=collections.Counter(q['knowledgeId'] for q in basic)
    vals=sorted(c.values(),reverse=True); avg=sum(vals)/len(vals)
    print(f'  {name}: 知识点{len(c)} 最大{vals[0]} 集中度{vals[0]/avg:.1f}x')
print()
print('=== 终检3：模拟卷完整性 ===')
p=json.load(open(f'{BASE}/out/papers/papers.json',encoding='utf-8'))
allq={}
for name,f in files.items():
    for q in json.load(open(f'{BASE}/{f}',encoding='utf-8')):
        allq[q['id']]=q
for pp in p['papers']:
    ids=pp['questionIds']
    stale=[i for i in ids if i not in allq]
    dup=len(ids)-len(set(ids))
    print(f'  {pp["bankId"]}: {len(ids)}题 失效{len(stale)} 重复{dup}')
