# -*- coding: utf-8 -*-
import json, collections
files = {
 '现汉':'out/refined/bank-xiandai-hanyu.refined2.json',
 '古汉':'out/refined/bank-gudai-hanyu.v012.json',
 '古文史':'out/refined/bank-zhongguo-gudai-wenxue.v012.json',
 '现文史':'out/refined/bank-zhongguo-xiandai-wenxue.quota.json',
 '当代':'out/refined/bank-zhongguo-dangdai-wenxue.refined2.json',
}
for name, f in files.items():
    qs = json.load(open(f, encoding='utf-8'))
    basic = [q for q in qs if q.get('purpose')=='basic' and q.get('knowledgeId')]
    ntest = sum(1 for q in qs if q.get('purpose')=='test')
    c = collections.Counter(q['knowledgeId'] for q in basic)
    vals = sorted(c.values(), reverse=True)
    avg = sum(vals)/len(vals) if vals else 0
    print(f'{name}: basic {len(basic)} / test {ntest} | 总{len(qs)} 知识点{len(c)} 集中度{vals[0]/avg:.1f}x')

print()
g = json.load(open('out/refined/bank-gudai-hanyu.v012.json', encoding='utf-8'))
for q in g:
    if q.get('purpose')=='basic' and '郤克伤于矢' in q.get('stem',''):
        print('于表被动题 ->', q.get('knowledgeId'))
    if q.get('purpose')=='basic' and '定语后置' in q.get('stem',''):
        print('定语后置题 ->', q.get('knowledgeId'))
