# -*- coding: utf-8 -*-
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\study_app\tools\seed-builder\pipeline\pack_v013.py'
src = open(P, encoding='utf-8').read()

# 用正则定位整个 shuffle_options 函数（到下一个 def 前）
m = re.search(r'def shuffle_options\(q, rng\):.*?(?=\ndef )', src, re.S)
if not m:
    print('NOT FOUND')
    sys.exit(1)
old_func = m.group(0)

new_func = '''def _remap_expl_letters(expl, mapping):
    """把解析文本中的选项字母引用按旧key->新key映射改写。"""
    if not expl or not mapping:
        return expl

    def repl(m):
        pre, letter, post = m.group(1), m.group(2), m.group(3)
        if letter in mapping:
            return pre + mapping[letter] + post
        return m.group(0)

    # 选项字母引用的语境：选X / 故选X / 故X正确 / X项 / 仅X正确 / 据此选X / 答案X / 应选X
    pat = re.compile(r'(选|故选|答案|正确选项(?:为|是)?|应为|应选|故|仅|据此选|根据)([ABCDEF])(?=$|[，。；、:： ]|项|正确|错误|对|不对|符合|不符合|有误|表述正确|表述错误|说法|不是|属|均)')
    return pat.sub(repl, expl)


def shuffle_options(q, rng):
    """洗牌选择题；返回洗牌后的正确项文本（v4 编码）。
    洗牌后同步改写解析文本中的选项字母引用（旧key->新key），防止解析与答案错位。"""
    t = q["type"]
    if t not in ("single_choice", "multi_choice"):
        return None
    opts = list(q["options"])
    ans = q["answer"]
    ans_keys = set(ans) if isinstance(ans, list) else {ans}
    ans_texts = [o["text"] for o in opts if o["key"] in ans_keys]
    # 洗牌前记录 旧key -> 文本
    old_texts = [o["text"] for o in opts]
    old_keys = [o["key"] for o in opts]
    rng.shuffle(opts)
    keys = "ABCDEFGHIJKLMNOP"[:len(opts)]
    new_by_text = {}
    for o, k in zip(opts, keys):
        o["key"] = k
        new_by_text[o["text"]] = k
    q["options"] = opts
    # 建立 旧key -> 新key 映射（按文本对齐）
    mapping = {}
    for oldk, txt in zip(old_keys, old_texts):
        if txt in new_by_text:
            mapping[oldk] = new_by_text[txt]
    if mapping:
        expl = q.get("explanation")
        if expl:
            q["explanation"] = _remap_expl_letters(expl, mapping)
    # 记录正确项文本（供 v4 answer 编码）
    q["_ans_texts"] = ans_texts
    return ans_texts


'''
src = src.replace(old_func, new_func)
open(P, 'w', encoding='utf-8').write(src)
print('shuffle_options 已加固')
# 校验语法
import py_compile
py_compile.compile(P, doraise=True)
print('语法 OK')
