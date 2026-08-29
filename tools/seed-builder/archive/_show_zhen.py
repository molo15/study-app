# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
KP = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国现代文学史.knowledge.json', encoding='utf-8'))
n = 0
for k in KP['knowledge']:
    if '真题补充' in k['name']:
        for q in k.get('basicQuestions', []):
            print('[' + k['name'] + '] ' + q['stem'][:45] + ' => ' + q['answer'][:25])
            n += 1
print('补充点题数:', n)
