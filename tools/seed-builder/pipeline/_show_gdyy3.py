# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\古代汉语.knowledge.json', encoding='utf-8'))
for ch in ['古书的标点', '古书的文体', '训诂']:
    print('=' * 60)
    print('###', ch)
    print('=' * 60)
    for k in d['knowledge']:
        if k['chapter'] == ch:
            qs = k.get('basicQuestions', [])
            print(f"\n  [{k['id']}] {k['name']}  (hot={k.get('hot')})  {len(qs)}题")
            print(f"    summary: {(k.get('summary') or '')[:80]}")
            for q in qs:
                print(f"      - {q['stem'][:45]} → {q['answer']}")
