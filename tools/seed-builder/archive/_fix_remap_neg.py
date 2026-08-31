# -*- coding: utf-8 -*-
import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\study_app\tools\seed-builder\pipeline\pack_v013.py'
src = open(P, encoding='utf-8').read()

old = "pat = re.compile(r'(选|故选|答案(?:为|是)?|正确选项(?:为|是)?|应为|应选|故|仅|据此选|根据)\\s*([ABCDEF])(?=$|[，。；、:：\\s]|项|正确|错误|对|不对|符合|不符合|有误|表述正确|表述错误|说法|不是|属|均|！|？)')"
new = "pat = re.compile(r'(选|故选|答案(?:为|是)?|正确选项(?:为|是)?|应为|应选|故|仅|据此选|根据)\\s*([ABCDEF])(?=$|[，。；、:：\\s]|项|正确|错误|对|不对|符合|不符合|有误|表述正确|表述错误|说法|不是|不|属|均|！|？)')"

if old in src:
    src = src.replace(old, new)
    print('已补后瞻「不」')
else:
    print('旧正则未找到，定位：')
    i = src.find('def _remap_expl_letters')
    print(src[i:i+600])
    i2 = src.find('pat = re.compile')
    print('---', src[i2:i2+260])

open(P, 'w', encoding='utf-8').write(src)
import py_compile
py_compile.compile(P, doraise=True)
print('语法 OK')
