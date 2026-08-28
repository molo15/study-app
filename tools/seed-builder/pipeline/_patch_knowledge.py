# -*- coding: utf-8 -*-
import json
f = r'D:\study_app\tools\seed-builder\out\knowledge\古代汉语.knowledge.json'
k = json.load(open(f, encoding='utf-8'))
add = '语序类还包含定语后置（如“太子及宾客知其事者”即知其事之宾客，中心语在前、定语后置）、状语后置等。'
for kk in k.get('knowledge', []):
    if kk['id'] == 'k_gdyy_yufa_xia_08':
        kk['summary'] = (kk.get('summary') or '') + add
        print('已补 08 summary')
json.dump(k, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
