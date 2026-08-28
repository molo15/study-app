# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
KP = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国当代文学史.knowledge.json', encoding='utf-8'))
from collections import Counter
ids = Counter(k['id'] for k in KP['knowledge'])
for i, c in ids.items():
    if c > 1:
        print('重复id:', i, c)
        for k in KP['knowledge']:
            if k['id'] == i:
                print('   -', k['name'], '|', k['chapter'])
