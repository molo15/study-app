# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
KP = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json', encoding='utf-8'))
for k in KP['knowledge']:
    print(k['chapter'] + ' | ' + k['name'] + ' | ' + str(len(k.get('basicQuestions', []))) + '题')
