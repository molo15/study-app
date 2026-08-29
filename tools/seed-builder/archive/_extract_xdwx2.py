# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
lines = open(r'D:\study_app\tools\mc_assets\xiandai-wenxue.md', encoding='utf-8').read().split('\n')
# 打印指定章节的内容前若干行
targets = ['鲁迅（一）', '郭沫若', '艾青', '赵树理', '新诗（一）', '小说（一）', '市民通俗小说（一）', '戏剧', '文学思潮与运动（一）', '综合专题']
cur = None
count = {}
for i, l in enumerate(lines, 1):
    if l.startswith('## /'):
        cur = l[4:].split('/')[-1]
        count[cur] = 0
    elif cur in targets and count[cur] < 9:
        t = l.strip()
        if t and 'siyuan://' not in t and '📄' not in t and '📑' not in t and '🆎' not in t:
            count[cur] += 1
            print(f'[{cur}] {t[:100]}')
print('DONE')
