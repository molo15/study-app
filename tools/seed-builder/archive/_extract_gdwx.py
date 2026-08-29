# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
lines = open(r'D:\study_app\tools\mc_assets\gudai-wenxue.md', encoding='utf-8').read().split('\n')
kw = ['代表', '作品', '作家', '流派', '诗人', '乐府', '风骚', '志怪', '传奇', '古文', '格律', '婉约', '豪放', '散曲', '话本', '章回', '世情', '神魔', '演义', '四大', '骈文', '七子', '三曹', '建安', '正始', '田园', '山水']
cur = None
count = {}
for i, l in enumerate(lines, 1):
    if l.startswith('## /'):
        cur = l[4:].split('/')[-1]
        count[cur] = 0
    elif cur and '真题' not in cur and count[cur] < 10:
        t = l.strip()
        if t and 'siyuan://' not in t and '📄' not in t and '📑' not in t and '🆎' not in t and len(t) > 6:
            if any(k in t for k in kw) and re.search(r'[《》、“、，：]', t):
                count[cur] += 1
                print(f'[{cur}] {t[:95]}')
