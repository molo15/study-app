# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国现代文学史.knowledge.json', encoding='utf-8'))
for ch in ['市民通俗小说（一）', '市民通俗小说（二）', '散文（三）']:
    print('=' * 60)
    print('###', ch)
    for k in d['knowledge']:
        if k['chapter'] == ch:
            print(f"  [{k['id']}] {k['name']} ({len(k.get('basicQuestions',[]))}题)")
            for q in k.get('basicQuestions', []):
                print(f"    - {q['stem'][:55]} → {q['answer']}")
    print()
