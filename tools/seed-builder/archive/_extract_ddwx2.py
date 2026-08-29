# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
lines = open(r'D:\study_app\tools\mc_assets\dangdai-wenxue.md', encoding='utf-8').read().split('\n')
# 读取指定行段，抽取含列举/流派/代表作的句子
segs = [(1333, 1496, '80年代小说'), (1193, 1252, '80年代新诗'), (1158, 1185, '80/90思潮'), (852, 918, '90年代小说'), (578, 668, '2000小说/莫言'), (1265, 1333, '朦胧诗')]
for a, b, name in segs:
    print(f'======== {name} ========')
    n = 0
    for l in lines[a-1:b]:
        t = l.strip()
        if t and 'siyuan://' not in t and '📄' not in t and '📑' not in t and '🆎' not in t and len(t) > 6:
            if re.search(r'[《》、“、，：]', t) and ('代表' in t or '作品' in t or '流派' in t or '小说' in t or '诗人' in t or '作家' in t or '运动' in t or '主义' in t or '派' in t):
                n += 1
                if n > 14:
                    break
                print(' ', t[:100])
