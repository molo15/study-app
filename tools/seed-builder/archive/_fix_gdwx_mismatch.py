# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json', encoding='utf-8'))
fixes = [
    ('“民之归仁也，犹水之就下”体现了《孟子》散文善于', '用譬喻说明事理', '善用譬喻'),
    ('中国文学批评史上第一部品评诗歌的专著是', '钟嵘《诗品》', '《诗品》'),
]
n = 0
for k in d['knowledge']:
    for q in k.get('basicQuestions', []):
        for stemf, old, new in fixes:
            if stemf in q.get('stem', '') and q.get('answer') == old:
                q['answer'] = new
                n += 1
json.dump(d, open(r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('修复:', n, '处')
