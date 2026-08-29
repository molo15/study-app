# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
lines = open(r'D:\study_app\tools\mc_assets\xiandai-wenxue.md', encoding='utf-8').read().split('\n')
kw = ['代表作', '作品有', '人物有', '成员', '社团', '流派', '诗集', '小说集', '主要包括', '主要有', '名单']
out = []
for i, l in enumerate(lines, 1):
    t = l.strip()
    if t and 'siyuan://' not in t and len(t) > 6:
        if any(k in t for k in kw) and re.search(r'[《》、“、，：]', t):
            out.append((i, t[:100]))
shown = {}
for i, t in out:
    ch = None
    for j in range(i - 1, 0, -1):
        if lines[j - 1].startswith('## /'):
            ch = lines[j - 1][4:].split('/')[-1]
            break
    if ch and ch not in shown and '真题' not in ch:
        shown[ch] = t
for ch, t in list(shown.items())[:45]:
    print(f'[{ch}] {t}')
