# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P3 = r'D:\study_app\tools\seed-builder\out\v09xiandaiwenxue\bank-zhongguo-xiandai-wenxue.v09.json'
v09m = json.load(open(P3, encoding='utf-8'))
for q in v09m:
    if q['id'] == 'bank-zhongguo-xiandai-wenxue:q_000088':
        old = q.get('explanation', '')
        q['explanation'] = old.replace('故B、C项不选', '故B、C、D项不选')
        print('old:', old)
        print('new:', q['explanation'])
json.dump(v09m, open(P3, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('saved')
