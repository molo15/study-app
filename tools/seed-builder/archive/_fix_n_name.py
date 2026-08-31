# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json'
k = json.load(open(P, encoding='utf-8'))
for x in k['knowledge']:
    for i, bq in enumerate(x.get('basicQuestions', [])):
        if x['id'] == 'k_xdyy_yuyin_16' and i == 5:
            bq['answer'] = 'nê'
            print('fixed:', bq['answer'], bq['options'])
json.dump(k, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('saved')
