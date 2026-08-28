# -*- coding: utf-8 -*-
"""提取三个 docx 的章节题库章节结构"""
import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document

FILES = {
    "现代文学三十年": r"C:\Users\lenovo\Downloads\钱理群《中国现代文学三十年》题库1786884768.docx",
    "袁行霈中国文学史": r"C:\Users\lenovo\Downloads\袁行霈中国文学史题库1786884768.docx",
    "洪子诚当代文学史": r"C:\Users\lenovo\Downloads\洪子诚《中国当代文学史》（修订版）配套题库1786884768.docx",
}

# 章节标题模式：通常为 "第X章 XXX" 或 "第一部分 第二部分" 等
for name, fp in FILES.items():
    print('=' * 70)
    print('###', name)
    print('=' * 70)
    doc = Document(fp)
    # 找"章节题库"部分起点
    texts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    start = None
    for i, t in enumerate(texts):
        if '章节题库' in t:
            start = i
            break
    print('章节题库起点:', start, texts[start] if start is not None else '未找到')
    if start is not None:
        for i, t in enumerate(texts[start:start+80], start):
            # 章节标题通常以 "第X章" 开头或类似
            if re.match(r'^(第[一二三四五六七八九十百\d]+[章节]|上编|中编|下编|第一部分|第二部分|第三部分|第一章|第1章)', t) or len(t) < 30:
                print(f'  [{i}] {t[:50]}')
    print()
