# -*- coding: utf-8 -*-
import json, collections
files = {
 '现汉':'out/refined/bank-xiandai-hanyu.refined2.json','古汉':'out/refined/bank-gudai-hanyu.v012.json',
 '古文史':'out/refined/bank-zhongguo-gudai-wenxue.v012.json','当代':'out/refined/bank-zhongguo-dangdai-wenxue.refined2.json'}
for name,f in files.items():
    qs=json.load(open(f,encoding='utf-8'))
    gaps=[q for q in qs if not (q.get('explanation') or '').strip() or len((q.get('explanation') or '').strip())<15]
    print('=====', name, '缺口', len(gaps), '=====')
    print('  purpose:', dict(collections.Counter(q.get('purpose') for q in gaps)))
    print('  题型:', dict(collections.Counter(q['type'] for q in gaps)))
    # 无解析的样例
    noe=[q for q in gaps if not (q.get('explanation') or '').strip()]
    for q in noe[:6]:
        print('   [无解析]', q['id'], q['type'], q['stem'][:40])
