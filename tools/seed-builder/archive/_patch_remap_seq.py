# -*- coding: utf-8 -*-
"""增强 _remap_expl_letters：支持「故X、Y、Z项不选/不属于」整串枚举映射。"""
import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\study_app\tools\seed-builder\pipeline\pack_v013.py'
src = open(P, encoding='utf-8').read()

old_fn = '''def _remap_expl_letters(expl, mapping):
    """把解析文本中的选项字母引用按旧key->新key映射改写。"""
    if not expl or not mapping:
        return expl

    def repl(m):
        pre, letter = m.group(1), m.group(2)
        if letter in mapping:
            return pre + mapping[letter]
        return m.group(0)

    # 选项字母引用的语境：选X / 故选X / 故X正确 / X项 / 仅X正确 / 据此选X / 答案X / 应选X
    # 容忍「选 A」「故选 A」等字母前空格；不匹配"A. 胆怯"式列举（点号后不带空格紧邻）
    pat = re.compile(r'(选|故选|答案(?:为|是)?|正确选项(?:为|是)?|应为|应选|故|仅|据此选|根据)\\s*([ABCDEF])(?=$|[，。；、:：\\s]|项|正确|错误|对|不对|符合|不符合|有误|表述正确|表述错误|说法|不是|不|属|均|！|？)')
    return pat.sub(repl, expl)'''

new_fn = '''def _remap_expl_letters(expl, mapping):
    """把解析文本中的选项字母引用按旧key->新key映射改写。
    覆盖单字母断言（选X/故选X/故X不选）与整串枚举（故X、Y、Z项不选/不属于）。"""
    if not expl or not mapping:
        return expl

    def remap_letters(s):
        """把 s 中的选项字母逐个映射。"""
        out = []
        for ch in s:
            out.append(mapping.get(ch, ch))
        return ''.join(out)

    def repl1(m):
        pre, letter = m.group(1), m.group(2)
        if letter in mapping:
            return pre + mapping[letter]
        return m.group(0)

    def repl_seq(m):
        pre, letters = m.group(1), m.group(2)
        return pre + remap_letters(letters)

    # 1) 整串枚举：故A、B、C项不选 / 故A、B、C不属于 / 故A、B、C正确 / A、B、C、D项不选
    pat_seq = re.compile(r'(故|即|因此|所以|因此)([ABCDEF](?:、[ABCDEF]){1,5})(?=(?:项|均)?(?:不选|排除|错误|不对|有误|不符合|不属|正确|对|属于))')
    expl = pat_seq.sub(repl_seq, expl)

    # 2) 单字母断言：选X / 故选X / 故X正确 / X项 / 仅X正确 / 据此选X / 答案X / 应选X
    #    容忍「选 A」「故选 A」等字母前空格；不匹配"A. 胆怯"式列举（点号后不带空格紧邻）
    pat = re.compile(r'(选|故选|答案(?:为|是)?|正确选项(?:为|是)?|应为|应选|故|仅|据此选|根据)\\s*([ABCDEF])(?=$|[，。；、:：\\s]|项|正确|错误|对|不对|符合|不符合|有误|表述正确|表述错误|说法|不是|不|属|均|！|？)')
    return pat.sub(repl1, expl)'''

assert old_fn in src, "_remap_expl_letters 原文未匹配"
src = src.replace(old_fn, new_fn)
open(P, 'w', encoding='utf-8').write(src)
import py_compile
py_compile.compile(P, doraise=True)
print('已增强整串枚举映射，语法 OK')
