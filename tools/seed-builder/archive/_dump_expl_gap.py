# -*- coding: utf-8 -*-
import json
files = {
 '现汉':'out/refined/bank-xiandai-hanyu.refined2.json','古汉':'out/refined/bank-gudai-hanyu.v012.json',
 '古文史':'out/refined/bank-zhongguo-gudai-wenxue.v012.json','当代':'out/refined/bank-zhongguo-dangdai-wenxue.refined2.json'}
knames = {}
for n in ['现代汉语','古代汉语','中国古代文学史','中国当代文学史']:
    k = json.load(open(rf'D:\study_app\tools\seed-builder\out\knowledge\{n}.knowledge.json', encoding='utf-8'))
    for kk in k.get('knowledge', []):
        knames[kk['id']] = kk['name']
out = []
for name,f in files.items():
    qs=json.load(open(f,encoding='utf-8'))
    gaps=[q for q in qs if not (q.get('explanation') or '').strip() or len((q.get('explanation') or '').strip())<15]
    for q in gaps:
        ans = q['answer']
        if isinstance(ans, list): ans = '/'.join(str(x) for x in ans)
        out.append(f"[{name}|{q['purpose']}|{q['type']}] {q['id']} | {knames.get(q.get('knowledgeId'),'?')}")
        out.append(f"   题干: {q['stem'][:95]}")
        if q.get('options'):
            out.append(f"   选项: {[o['text'][:22] for o in q['options']]}")
        out.append(f"   答案: {ans}")
        out.append('')
open(r'D:\study_app\tools\seed-builder\pipeline\_expl_gap_list.txt','w',encoding='utf-8').write('\n'.join(out))
print('已导出', sum(1 for l in out if l.startswith('[')), '题')
