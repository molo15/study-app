# -*- coding: utf-8 -*-
import json
files = {
    '古汉': r'D:\study_app\tools\seed-builder\out\refined\bank-gudai-hanyu.v012.json',
    '现汉': r'D:\study_app\tools\seed-builder\out\refined\bank-xiandai-hanyu.refined2.json',
    '古文史': r'D:\study_app\tools\seed-builder\out\refined\bank-zhongguo-gudai-wenxue.v012.json',
}
import re
for name, f in files.items():
    qs = json.load(open(f, encoding='utf-8'))
    print('=====', name, '=====')
    for q in qs:
        if q['type'] != 'blank':
            continue
        a = q.get('answer')
        joined = ' '.join(a) if isinstance(a, list) else str(a)
        if re.search(r'[（(]|研|：|:|\s{2,}', joined):
            print('['+q['id']+']', q.get('purpose'), q['chapter'])
            print('   stem:', q['stem'][:55])
            print('   answer:', repr(a)[:80])
