# -*- coding: utf-8 -*-
import json
BASE = r'D:\study_app\tools\seed-builder'
files = {
 '现汉':'out/refined/bank-xiandai-hanyu.refined2.json','古汉':'out/refined/bank-gudai-hanyu.v012.json',
 '古文史':'out/refined/bank-zhongguo-gudai-wenxue.v012.json','当代':'out/refined/bank-zhongguo-dangdai-wenxue.refined2.json'}
for name,f in files.items():
    qs=json.load(open(f'{BASE}/{f}',encoding='utf-8'))
    gap=[q for q in qs if q.get('purpose')=='basic' and ((not (q.get('explanation') or '').strip()) or len((q.get('explanation') or '').strip())<20)]
    print(f'===== {name} {len(gap)} =====')
    for q in gap:
        e=(q.get('explanation') or '').strip()
        print(f"  {q['id']} [{len(e)}字] {q['stem'][:35]} | 解析:{e[:40]}")
