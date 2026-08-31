# -*- coding: utf-8 -*-
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. 残留检查
pat = re.compile(r'素材块|素材n|正文块|对应素材标题|覆盖缺口|本题答案为|存量题未覆盖|本题属[于]?.{0,12}常考|即可应对同类题目|掌握其概念')
for f in [r'D:\study_app\tools\seed-builder\out\knowledge\古代汉语.knowledge.json',
          r'D:\study_app\tools\seed-builder\out\knowledge\中国当代文学史.knowledge.json']:
    k = json.load(open(f, encoding='utf-8'))
    res = [(x['id'], i, bq.get('explanation','')) for x in k['knowledge'] for i, bq in enumerate(x.get('basicQuestions',[]))
           if pat.search(re.sub(r'\s+','',bq.get('explanation') or ''))]
    print(os.path.basename(f), '残留:', len(res))
    for r in res[:3]:
        print('  ', r[0], r[1], r[2][:80])

# 2. 解析长度分布（15-20 字）
for f in [r'D:\study_app\tools\seed-builder\out\knowledge\古代汉语.knowledge.json',
          r'D:\study_app\tools\seed-builder\out\knowledge\中国当代文学史.knowledge.json']:
    k = json.load(open(f, encoding='utf-8'))
    d = {}
    for x in k['knowledge']:
        for bq in x.get('basicQuestions', []):
            L = len(re.sub(r'\s+','',bq.get('explanation') or ''))
            if L < 20:
                d.setdefault(L, []).append((x['id'], bq.get('stem','')[:18]))
    print(os.path.basename(f), '解析<20字的长度分布:', {k2: len(v) for k2, v in sorted(d.items())})
