# -*- coding: utf-8 -*-
import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\study_app\tools\seed-builder\pipeline\pack_v013.py'
src = open(P, encoding='utf-8').read()

# 正则替换：给字母断言加 \s* 容忍空格，并扩展后瞻
old_pat = re.compile(r"pat = re\.compile\(r'\(选\|故选\|答案\|正确选项\(\?:为\|是\)\?\|应为\|应选\|故\|仅\|据此选\|根据\)\(\[ABCDEF\]\)\(?=\$|\[\，。；、:： \]\|项\|正确\|错误\|对\|不对\|符合\|不符合\|有误\|表述正确\|表述错误\|说法\|不是\|属\|均\)'\)")
new_pat = "pat = re.compile(r'(选|故选|答案(?:为|是)?|正确选项(?:为|是)?|应为|应选|故|仅|据此选|根据)\\s*([ABCDEF])(?=$|[，。；、:：\\s]|项|正确|错误|对|不对|符合|不符合|有误|表述正确|表述错误|说法|不是|属|均|！|？)')"

# 用简单字符串定位
if "故选|答案|正确选项(?:为|是)?|应为|应选|故|仅|据此选|根据)([ABCDEF])" in src:
    # 当前是旧正则（无 \s*），直接替换
    src = src.replace(
        "pat = re.compile(r'(选|故选|答案|正确选项(?:为|是)?|应为|应选|故|仅|据此选|根据)([ABCDEF])(?=$|[，。；、:： ]|项|正确|错误|对|不对|符合|不符合|有误|表述正确|表述错误|说法|不是|属|均)')",
        "pat = re.compile(r'(选|故选|答案(?:为|是)?|正确选项(?:为|是)?|应为|应选|故|仅|据此选|根据)\\s*([ABCDEF])(?=$|[，。；、:：\\s]|项|正确|错误|对|不对|符合|不符合|有误|表述正确|表述错误|说法|不是|属|均|！|？)')"
    )
    print('已替换为带 \\s* 的正则')
else:
    print('未找到旧正则，检查当前状态')
    i = src.find('def _remap_expl_letters')
    print(src[i:i+700])

open(P, 'w', encoding='utf-8').write(src)
import py_compile
py_compile.compile(P, doraise=True)
print('语法 OK')
