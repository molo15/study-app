# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json', encoding='utf-8'))
for ch in ['元代文学', '清代文学', '近代文学']:
    print('=' * 60)
    print('###', ch)
    for k in d['knowledge']:
        if k['chapter'] == ch:
            print(f"  [{k['id']}] {k['name']} ({len(k.get('basicQuestions',[]))}题)")
            for q in k.get('basicQuestions', []):
                print(f"    - {q['stem'][:45]} → {q['answer'][:25]}")
    print()
