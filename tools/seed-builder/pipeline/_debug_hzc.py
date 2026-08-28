# -*- coding: utf-8 -*-
"""调试洪子诚 docx 结构"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document

fp = r"C:\Users\lenovo\Downloads\洪子诚《中国当代文学史》（修订版）配套题库1786884768.docx"
doc = Document(fp)
texts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
print('总段数:', len(texts))

# 找所有章节标题
for i, t in enumerate(texts):
    if re.match(r'^(第[一二三四五六七八九十百\d]+[章编])', t):
        print(f'[CH{i}] {t[:50]}')

print()
print('=== 第1章后 30 段 ===')
start = None
for i, t in enumerate(texts):
    if t.startswith('第1章'):
        start = i
        break
for i, t in enumerate(texts[start:start+30], start):
    print(f'[{i}] {t[:60]}')
