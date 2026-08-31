# -*- coding: utf-8 -*-
import io, sys, json, os, random, importlib.util, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

spec = importlib.util.spec_from_file_location('pv', r'D:\study_app\tools\seed-builder\pipeline\pack_v013.py')
pv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pv)

expl = '主谓式即名词/代词+动词/形容词。\n- A. 胆怯（胆+怯，主谓）——是\n- B. 笔直（偏正）——否\n- C. 报考（连动）——否\n- D. 悦耳（动宾）——否\n- 故选 A'
mapping = {'A': 'B', 'B': 'A', 'C': 'D', 'D': 'C'}
out = pv._remap_expl_letters(expl, mapping)
print('REMAP RESULT:')
print(out[-60:])
print()
# 单独测正则
pat = re.compile(r'(选|故选|答案(?:为|是)?|正确选项(?:为|是)?|应为|应选|故|仅|据此选|根据)\s*([ABCDEF])(?=$|[，。；、:：\s]|项|正确|错误|对|不对|符合|不符合|有误|表述正确|表述错误|说法|不是|属|均|！|？)')
print('MATCHES:')
for m in pat.finditer(expl):
    print('  ', repr(m.group(0)), '| g1:', m.group(1), '| g2:', m.group(2))
