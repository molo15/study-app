# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json'
k = json.load(open(P, encoding='utf-8'))
for x in k['knowledge']:
    for i, bq in enumerate(x.get('basicQuestions', [])):
        if x['id'] == 'k_xdyy_yuyin_14' and i == 11:
            bq['explanation'] = '声调的调号应标在韵腹（主要元音）上。因为韵腹是音节中开口度最大、最响亮、最稳定的元音，标在韵腹上才能准确反映该音节的声调。如"花"huā标在a上，"国"guó标在o上。'
            print('fixed:', bq['explanation'])
json.dump(k, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('saved')
