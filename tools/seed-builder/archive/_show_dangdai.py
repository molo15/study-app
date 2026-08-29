# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国当代文学史.knowledge.json', encoding='utf-8'))
from collections import Counter
chap = Counter()
for k in d['knowledge']:
    chap[k['chapter']] += 1
print('=== 当代各章知识点数 ===')
for c, n in chap.items():
    flag = '' if 4 <= n <= 15 else '  <<<'
    print(f"  {c}: {n}{flag}")

print()
focus = ['新诗（50-60）', '台港文学', '戏剧（80-90）', '2000-2016']
for k in d['knowledge']:
    if k['chapter'] in focus:
        print(f"  [{k['id']}] {k['name']} ({len(k.get('basicQuestions',[]))}题)")
