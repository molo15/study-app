# -*- coding: utf-8 -*-
"""修正 _remap_expl_letters 正则：容忍「选 A」中字母前的空格，并支持列举序号 A. 的情形。
同时把「故选 A」「据此选 B」「选A」统一处理。
"""
import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\study_app\tools\seed-builder\pipeline\pack_v013.py'
src = open(P, encoding='utf-8').read()

old = '''    def repl(m):
        pre, letter = m.group(1), m.group(2)
        if letter in mapping:
            return pre + mapping[letter]
        return m.group(0)

    # 选项字母引用的语境：选X / 故选X / 故X正确 / X项 / 仅X正确 / 据此选X / 答案X / 应选X
    pat = re.compile(r'(选|故选|答案|正确选项(?:为|是)?|应为|应选|故|仅|据此选|根据)([ABCDEF])(?=$|[，。；、:： ]|项|正确|错误|对|不对|符合|不符合|有误|表述正确|表述错误|说法|不是|属|均)')
    return pat.sub(repl, expl)'''

new = '''    def repl(m):
        pre, letter = m.group(1), m.group(2)
        if letter in mapping:
            return pre + mapping[letter]
        return m.group(0)

    # 选项字母引用的语境：选X / 故选X / 故X正确 / X项 / 仅X正确 / 据此选X / 答案X / 应选X
    # 容忍「选 A」「故选 A」等字母前空格；不匹配"A. 胆怯"式列举（后跟点号）
    pat = re.compile(r'(选|故选|答案(?:为|是)?|正确选项(?:为|是)?|应为|应选|故|仅|据此选|根据)\\s*([ABCDEF])(?=$|[，。；、:：\\s]|项|正确|错误|对|不对|符合|不符合|有误|表述正确|表述错误|说法|不是|属|均|！|？)')
    return pat.sub(repl, expl)'''

assert old in src, "remap 正则段未匹配"
src = src.replace(old, new)
open(P, 'w', encoding='utf-8').write(src)
import py_compile
py_compile.compile(P, doraise=True)
print('remap 正则已修正，语法 OK')
