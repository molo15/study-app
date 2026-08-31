# -*- coding: utf-8 -*-
"""修复 _remap_expl_letters：合并整串枚举与单字母为一个正则，避免二次改写。
模式：(选|故选|答案...|故|...)\s* 后跟 [A-F]（可含、分隔的多个字母）
一次 sub 完成映射，防止整串映射后又单字母改回。
"""
import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\study_app\tools\seed-builder\pipeline\pack_v013.py'
src = open(P, encoding='utf-8').read()

m = re.search(r'def _remap_expl_letters\(expl, mapping\):.*?(?=\ndef shuffle_options)', src, re.S)
assert m, '函数未找到'
body = m.group(0)

new_body = '''def _remap_expl_letters(expl, mapping):
    """把解析文本中的选项字母引用按旧key->新key映射改写。
    统一处理单字母断言（选X/故选X/故X不选）与整串枚举（故A、B、C项不选/不属于），
    一次 sub 完成，避免二次改写。"""
    if not expl or not mapping:
        return expl

    def remap_letters(s):
        return ''.join(mapping.get(ch, ch) for ch in s)

    def repl(m):
        pre, letters = m.group(1), m.group(2)
        return pre + remap_letters(letters)

    # 前缀（选/故选/答案…/故…）后跟字母序列，字母可带顿号分隔（A、B、C）；
    # 不匹配"A. 胆怯"式列举（点号后不带空格紧邻）
    pat = re.compile(r'(选|故选|答案(?:为|是)?|正确选项(?:为|是)?|应为|应选|故|仅|据此选|根据)\\s*([ABCDEF](?:、?[ABCDEF]){0,5})(?=$|[，。；、:：\\s]|项|正确|错误|对|不对|符合|不符合|有误|表述正确|表述错误|说法|不是|不|属|均|！|？)')
    return pat.sub(repl, expl)


'''
src = src.replace(body, new_body)
open(P, 'w', encoding='utf-8').write(src)
import py_compile
py_compile.compile(P, doraise=True)
print('已统一 remap 正则，语法 OK')
