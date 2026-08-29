# -*- coding: utf-8 -*-
"""统计 5 科当前题量与目标对比"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'D:\study_app\tools\seed-builder\out\knowledge'
targets = {'现代汉语': 1100, '古代汉语': 1000, '中国古代文学史': 1000, '中国现代文学史': None, '中国当代文学史': 800}
for cn, tgt in targets.items():
    p = os.path.join(BASE, cn + '.knowledge.json')
    KP = json.load(open(p, encoding='utf-8'))
    b = sum(len(k.get('basicQuestions', [])) for k in KP['knowledge'])
    kp = len(KP['knowledge'])
    ch = len(set(k['chapter'] for k in KP['knowledge']))
    extra = f'目标{tgt} 缺口{tgt-b}' if tgt else '已达标'
    print(f'{cn:10s} 基础题{b:5d} 知识点{kp:4d} 章节{ch:3d}  {extra}')
