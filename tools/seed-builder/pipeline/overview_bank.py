# -*- coding: utf-8 -*-
"""Build compact overview of xdwx file headers + key blocks"""
import json, os, re

bank = '中国现代文学史'
d = json.load(open(os.path.join(r'D:\study_app\tools\seed-builder\out', f'bank-{bank}.materials.json'), encoding='utf-8'))
ms = d['materials']
sections = {}
for m in ms:
    p = m.get('docPath', '')
    parts = [x for x in p.split('/') if x.strip()]
    sec = parts[1] if len(parts) >= 2 else '(root)'
    sections.setdefault(sec, []).append(m)

out = []
for sec in sorted(sections):
    lst = sections[sec]
    out.append(f'\n######## {sec}  ({len(lst)} blocks) ########')
    # 收集关键块：含 ★ / 名词解释 / 概念 / 定义 / 名解 标记的
    key_blocks = []
    for m in lst:
        c = (m.get('content') or '').strip()
        if not c or len(c) > 400:
            continue
        if re.search(r'★|名词解释|名解|概念|定义|是指|指.*(诗|文|小说|戏|体|派|风|话|学|故事)|是谁|代表作', c):
            key_blocks.append(c.replace('\n', ' '))
    # 去重保序
    seen = set()
    uniq = []
    for c in key_blocks:
        if c[:20] not in seen:
            seen.add(c[:20]); uniq.append(c)
    for c in uniq[:24]:
        out.append('  · ' + c[:90])
    # 也把长块的头一行列出（通常是论述题标题）
    heads = []
    for m in lst:
        c = (m.get('content') or '').strip()
        first = c.split('\n')[0][:60]
        if first and re.search(r'★|[一二三四五六七八九十]、|（[一二三四五]）|题', first) and first not in heads:
            heads.append(first)
    for h in heads[:10]:
        out.append('  ▸ ' + h)

open(r'D:\study_app\.workbuddy\xdwx_overview.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written', os.path.getsize(r'D:\study_app\.workbuddy\xdwx_overview.txt'))
