# -*- coding: utf-8 -*-
"""精确提取三个 docx 章节题库的章节标题列表"""
import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document

FILES = {
    "现代文学三十年": r"C:\Users\lenovo\Downloads\钱理群《中国现代文学三十年》题库1786884768.docx",
    "袁行霈中国文学史": r"C:\Users\lenovo\Downloads\袁行霈中国文学史题库1786884768.docx",
    "洪子诚当代文学史": r"C:\Users\lenovo\Downloads\洪子诚《中国当代文学史》（修订版）配套题库1786884768.docx",
}

for name, fp in FILES.items():
    print('=' * 70)
    print('###', name)
    print('=' * 70)
    doc = Document(fp)
    texts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    # 找第二部分起点
    part2 = None
    for i, t in enumerate(texts):
        if re.match(r'^第二[部分编卷]', t) or ('章节题库' in t and i > 500):
            part2 = i
            break
    print('第二部分起点 index:', part2, '->', texts[part2] if part2 is not None else '')
    if part2 is None:
        # 退而求其次，找"第X章"
        pass
    cnt = 0
    for i, t in enumerate(texts[part2:] if part2 is not None else texts, part2 if part2 is not None else 0):
        # 章节标题：第X章/第X编/上编/中编/下编
        if re.match(r'^(第[一二三四五六七八九十百\d]+[章编]|上编|中编|下编|第一编|第二部分)', t):
            print(f'  [{i}] {t[:55]}')
            cnt += 1
        if cnt > 80:
            break
    print()
