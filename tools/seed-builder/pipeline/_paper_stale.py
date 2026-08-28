# -*- coding: utf-8 -*-
import json, collections
BASE = r'D:\study_app\tools\seed-builder'
refined = {
 'bank-gudai-hanyu':'out/refined/bank-gudai-hanyu.v012.json',
 'bank-xiandai-hanyu':'out/refined/bank-xiandai-hanyu.refined2.json',
 'bank-zhongguo-gudai-wenxue':'out/refined/bank-zhongguo-gudai-wenxue.v012.json',
 'bank-zhongguo-xiandai-wenxue':'out/refined/bank-zhongguo-xiandai-wenxue.quota.json',
 'bank-zhongguo-dangdai-wenxue':'out/refined/bank-zhongguo-dangdai-wenxue.refined2.json',
}
allq = {}
for b, f in refined.items():
    for q in json.load(open(f'{BASE}/{f}', encoding='utf-8')):
        allq[q['id']] = q
p = json.load(open(f'{BASE}/out/papers/papers.json', encoding='utf-8'))
print('失效引用清单：')
for pp in p['papers']:
    bids = [i for i in pp['questionIds'] if i not in allq]
    for bid in bids:
        print(f"  {pp['bankId']} 失效 {bid}")
print('总计', sum(1 for pp in p['papers'] for i in pp['questionIds'] if i not in allq))
