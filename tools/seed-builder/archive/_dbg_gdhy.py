# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
KP = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\古代汉语.knowledge.json', encoding='utf-8'))
keys = ['句读之不知', '古汉语中“衣”指上衣', '下列属于词义扩大', '“尔雅”中“尔”']
for k in KP['knowledge']:
    for q in k.get('basicQuestions', []):
        if any(x in q['stem'] for x in keys):
            print('STEM:', q['stem'])
            print('ANS:', repr(q['answer']))
            print('OPTS:', q.get('options'))
            print('EXP:', repr(q.get('explanation', '')))
            print('---')
