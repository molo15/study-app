# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国当代文学史.knowledge.json', encoding='utf-8'))
for ch in ['新诗（50-60年代）', '台港文学', '戏剧（80-90年代）']:
    print('=' * 60)
    print('###', ch)
    for k in d['knowledge']:
        if k['chapter'] == ch:
            print(f"  [{k['id']}] {k['name']} ({len(k.get('basicQuestions',[]))}题)")
            for q in k.get('basicQuestions', []):
                print(f"    - {q['stem'][:50]} → {q['answer'][:30]}")
    print()
