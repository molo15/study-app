# -*- coding: utf-8 -*-
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
pat = re.compile(r'本题属[于]?.{0,12}常考|即可应对同类题目|掌握其概念|本题答案为|素材块')
# 检查 v010 basic 生成物
b = json.load(open(r'D:\study_app\tools\seed-builder\out\v010\basic\bank-gudai-hanyu.basic.json', encoding='utf-8'))
res = [q['id'] for q in b if pat.search(re.sub(r'\s+','',q.get('explanation') or ''))]
print('basic 残留:', len(res))
for r in res[:5]:
    q = next(x for x in b if x['id']==r)
    print('  ', r, q.get('explanation','')[:90])
