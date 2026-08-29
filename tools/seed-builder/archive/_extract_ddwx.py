# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
lines = open(r'D:\study_app\tools\mc_assets\dangdai-wenxue.md', encoding='utf-8').read().split('\n')
kw = ['代表作', '作品有', '人物', '成员', '社团', '流派', '诗集', '小说集', '主要包括', '主要有', '朦胧诗', '寻根', '先锋', '伤痕', '反思', '改革', '新生代']
cur = None
count = {}
for i, l in enumerate(lines, 1):
    if l.startswith('## /'):
        cur = l[4:].split('/')[-1]
        count[cur] = 0
    elif cur and '真题' not in cur and count[cur] < 12:
        t = l.strip()
        if t and 'siyuan://' not in t and '📄' not in t and '📑' not in t and '🆎' not in t and len(t) > 6:
            if any(k in t for k in kw) or re.search(r'[《》、“、，：]', t):
                count[cur] += 1
                print(f'[{cur}] {t[:95]}')
