# -*- coding: utf-8 -*-
import json, re
files = {
 '现汉':'out/refined/bank-xiandai-hanyu.refined2.json','古汉':'out/refined/bank-gudai-hanyu.v012.json',
 '古文史':'out/refined/bank-zhongguo-gudai-wenxue.v012.json','现文史':'out/refined/bank-zhongguo-xiandai-wenxue.quota.json',
 '当代':'out/refined/bank-zhongguo-dangdai-wenxue.refined2.json'}
for name,f in files.items():
    qs=json.load(open(f,encoding='utf-8'))
    hit=[]
    for q in qs:
        if q['type']!='blank': continue
        a=q.get('answer')
        parts=a if isinstance(a,list) else [a]
        for p in parts:
            p=str(p)
            if re.search(r'[/／、]', p) or (isinstance(a,str) and re.search(r'\s+', a)):
                hit.append((q['id'], repr(a)))
                break
    print('=====', name, '含分隔符 blank', len(hit), '=====')
    for i,(h,a) in enumerate(hit[:40]):
        print(f'  {h}: {a[:70]}')
    if len(hit)>40: print('  ... 共', len(hit))
