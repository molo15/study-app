# -*- coding: utf-8 -*-
import io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'D:\study_app\tools\seed-builder\out\knowledge\中国当代文学史.knowledge.json'
KP = json.load(open(P, encoding='utf-8'))
FIX = {
    '韩少功《爸爸爸》中的人物“丙崽”具有': (['象征', '写实', '讽刺', '抒情'], '象征'),
    '路遥《平凡的世界》属于': (['农村', '工业改革', '军事', '武侠'], '农村'),
    '《茶馆》共写了': (['三个', '两个', '四个', '五个'], '三个'),
}
for k in KP['knowledge']:
    for q in k.get('basicQuestions', []):
        if q['type'] != 'choice':
            continue
        for key, (opts, ans) in FIX.items():
            if key in q['stem']:
                q['options'] = opts
                q['answer'] = ans
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('done')
