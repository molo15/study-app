# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json', encoding='utf-8'))
for ch in ['标点符号', '语音']:
    print('=' * 60)
    print('###', ch)
    print('=' * 60)
    for k in d['knowledge']:
        if k['chapter'] == ch:
            qs = k.get('basicQuestions', [])
            print(f"  [{k['id']}] {k['name']} (hot={k.get('hot')}) {len(qs)}题")
