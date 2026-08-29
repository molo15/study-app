# -*- coding: utf-8 -*-
import json
ids = ['bank-xiandai-hanyu:b_000091','bank-xiandai-hanyu:w_000296','bank-xiandai-hanyu:w_000305',
'bank-xiandai-hanyu:w_000067','bank-xiandai-hanyu:w_000073','bank-xiandai-hanyu:w_000078',
'bank-xiandai-hanyu:kb_00140','bank-gudai-hanyu:b_000002','bank-gudai-hanyu:b_000192',
'bank-gudai-hanyu:z_000045','bank-gudai-hanyu:m_000100','bank-gudai-hanyu:q_000232',
'bank-gudai-hanyu:kb_00111','bank-zhongguo-gudai-wenxue:t_000082',
'bank-zhongguo-xiandai-wenxue:t_000099','bank-zhongguo-dangdai-wenxue:q_000084']
files = {
 '现汉':'out/refined/bank-xiandai-hanyu.refined2.json','古汉':'out/refined/bank-gudai-hanyu.v012.json',
 '古文史':'out/refined/bank-zhongguo-gudai-wenxue.v012.json','现文史':'out/refined/bank-zhongguo-xiandai-wenxue.quota.json',
 '当代':'out/refined/bank-zhongguo-dangdai-wenxue.refined2.json'}
allq={}
for name,f in files.items():
    for q in json.load(open(f,encoding='utf-8')):
        allq[q['id']]=q
for i in ids:
    q=allq.get(i)
    if not q: continue
    print('['+i+']')
    print('   stem:', q['stem'][:80])
    print('   answer:', repr(q['answer'])[:90])
    if q.get('answerVariants'): print('   variants:', q['answerVariants'])
    print()
