# -*- coding: utf-8 -*-
"""评估 docx 客观题 vs 现有知识点 的重叠度（现代文学史 文学思潮与运动一）"""
import io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

docx = json.load(open(r'D:\study_app\tools\seed-builder\out\reports\docx题库_解析.json', encoding='utf-8'))
kp = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国现代文学史.knowledge.json', encoding='utf-8'))

# 现代文学史 第1章
ch_docx = docx['现代文学三十年'].get('第1章 文学思潮与运动（一）', {})
print('=== docx 文学思潮与运动（一） 客观题 ===')
for ty in ['填空题', '选择题']:
    for q in ch_docx.get(ty, []):
        print(f'[{ty}] {q["stem"][:50]} => {q["answer"][:30]}')

print()
print('=== 现有知识点 ===')
for k in kp['knowledge']:
    if k['chapter'] == '文学思潮与运动（一）':
        qs = k.get('basicQuestions', [])
        print(f'[{k["id"]}] {k["name"]} ({len(qs)}题)')
        for q in qs:
            print(f'    - {q["stem"][:45]}')
