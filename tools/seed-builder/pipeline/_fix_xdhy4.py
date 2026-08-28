# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json'
KP = json.load(open(P, encoding='utf-8'))
FIX = {
    '“巧克力”是____个语素。': '“巧克力”是音译外来词，整体一个语素，属于单纯词，不可再分。',
    '“咖啡”是一个音译外来词，由____个语素构成。': '“咖啡”整体是一个音译语素，不可再分，属于单纯词。',
}
n = 0
for k in KP['knowledge']:
    for q in k.get('basicQuestions', []):
        if q['stem'] in FIX:
            q['explanation'] = FIX[q['stem']]
            n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('修复', n)
