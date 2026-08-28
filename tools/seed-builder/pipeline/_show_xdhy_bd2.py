# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json', encoding='utf-8'))
for k in d['knowledge']:
    if k['chapter'] == '标点符号':
        print(f"### [{k['id']}] {k['name']}  {len(k.get('basicQuestions',[]))}题")
        print('  summary:', (k.get('summary') or '')[:120])
        for q in k.get('basicQuestions', []):
            print(f"    - [{q['type']}] {q['stem'][:60]} → {q['answer']}")
        print()
