# -*- coding: utf-8 -*-
import io, sys, json, os, random, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

spec = importlib.util.spec_from_file_location('pv', r'D:\study_app\tools\seed-builder\pipeline\pack_v013.py')
pv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pv)

# 直接调 _remap_expl_letters 测试
expl = '田汉前期浪漫剧…并不遵循“三一律”，故E不选'
mapping = {'A': 'C', 'B': 'A', 'C': 'B', 'D': 'E', 'E': 'D'}
out = pv._remap_expl_letters(expl, mapping)
print('REMAP:', out)
print()
# 单独看正则能否匹配故E
import re
pat = re.compile(r'(选|故选|答案(?:为|是)?|正确选项(?:为|是)?|应为|应选|故|仅|据此选|根据)\s*([ABCDEF])(?=$|[，。；、:：\s]|项|正确|错误|对|不对|符合|不符合|有误|表述正确|表述错误|说法|不是|属|均|！|？)')
for m in pat.finditer(expl):
    print('match:', m.group(0), 'g1:', m.group(1), 'g2:', m.group(2))
