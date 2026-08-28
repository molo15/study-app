# -*- coding: utf-8 -*-
"""分析三个 docx 题库结构"""
import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document

FILES = [
    r"C:\Users\lenovo\Downloads\钱理群《中国现代文学三十年》题库1786884768.docx",
    r"C:\Users\lenovo\Downloads\袁行霈中国文学史题库1786884768.docx",
    r"C:\Users\lenovo\Downloads\洪子诚《中国当代文学史》（修订版）配套题库1786884768.docx",
]

for fp in FILES:
    print('=' * 70)
    print('FILE:', os.path.basename(fp))
    print('=' * 70)
    if not os.path.exists(fp):
        print('  !! 文件不存在')
        continue
    doc = Document(fp)
    paras = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    print(f'总段落数: {len(paras)}')
    # 打印前 60 段看结构
    for i, t in enumerate(paras[:60]):
        print(f'  [{i}] {t[:60]}')
    print('  ... (共', len(paras), '段)')
    print()
