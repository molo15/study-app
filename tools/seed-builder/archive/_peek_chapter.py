# -*- coding: utf-8 -*-
"""抽样看现代文学三十年 第1章 完整段落结构"""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document

fp = r"C:\Users\lenovo\Downloads\钱理群《中国现代文学三十年》题库1786884768.docx"
doc = Document(fp)
texts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

# 定位第1章起点
start = None
for i, t in enumerate(texts):
    if t == '第1章 文学思潮与运动（一）':
        start = i
        break
print('第1章起点:', start)
for i, t in enumerate(texts[start:start+90], start):
    print(f'[{i}] {t[:70]}')
