# -*- coding: utf-8 -*-
"""分析 docx 客观题分布 + 现有 knowledge 缺口"""
import io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

data = json.load(open(r'D:\study_app\tools\seed-builder\out\reports\docx题库_解析.json', encoding='utf-8'))

for name, chapters in data.items():
    print('=' * 70)
    print('###', name)
    print('=' * 70)
    for ch, types in chapters.items():
        tian = len(types.get('填空题', []))
        xuan = len(types.get('选择题', []))
        ming = len(types.get('名词解释', []))
        jian = len(types.get('简答题', []))
        lun = len(types.get('论述题', []))
        print(f'  {ch[:30]:32s} 填空{tian:3d} 选择{xuan:3d} 名词{ming:3d} 简答{jian:3d} 论述{lun:3d}')
    print()
