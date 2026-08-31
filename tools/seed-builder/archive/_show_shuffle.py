# -*- coding: utf-8 -*-
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\study_app\tools\seed-builder\pipeline\pack_v013.py'
src = open(P, encoding='utf-8').read()

# 定位 shuffle_options 函数体
m = re.search(r'def shuffle_options\(q, rng\):.*?\n\n', src, re.S)
if not m:
    print('NOT FOUND shuffle_options')
    sys.exit(1)
old_func = m.group(0)
print('=== 现有函数 ===')
print(old_func)
