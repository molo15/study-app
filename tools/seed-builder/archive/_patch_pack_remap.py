# -*- coding: utf-8 -*-
"""加固 pack_v013.py：洗牌时同步解析文本中的选项字母引用（P0 硬错配治本）。
在 shuffle_options 内建立 old_key->new_key 映射，并把 explanation 中形如
「选A/故选A/故A正确/A项…/仅A正确/据此选A/答案A」的字母按映射改写。
"""
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\study_app\tools\seed-builder\pipeline\pack_v013.py'
src = open(P, encoding='utf-8').read()

# 在 shuffle_options 中注入字母映射逻辑
old_func = '''def shuffle_options(q, rng):
    """洗牌选择题；返回洗牌后的正确项文本（v4 编码）。"""
    t = q["type"]
    if t not in ("single_choice", "multi_choice"):
        return None
    opts = list(q["options"])
    ans = q["answer"]
    ans_keys = set(ans) if isinstance(ans, list) else {ans}
    ans_texts = [o["text"] for o in opts if o["key"] in ans_keys]
    rng.shuffle(opts)
    keys = "ABCDEFGHIJKLMNOP"[:len(opts)]
    for o, k in zip(opts, keys):
        o["key"] = k
    q["options"] = opts
    # 记录正确项文本（供 v4 answer 编码）
    q["_ans_texts"] = ans_texts
    return ans_texts'''

new_func = '''def _remap_expl_letters(expl, mapping):
    """把解析文本中的选项字母引用按旧key->新key映射改写。
    覆盖「选A / 故选A / 故A正确 / A项… / 仅A正确 / 据此选A / 答案A / A… 等」形态。
    mapping: {old_key: new_key}
    """
    if not expl or not mapping:
        return expl
    # 若解析中出现字母，且这些字母确实是选项引用（前面/后面有选项语境词），才替换
    # 顺序替换，避免 A->X 后再被别的规则命中：一次性扫描更安全
    def repl(m):
        L = m.group(0)
        letter = m.group(2)
        if letter in mapping:
            return m.group(1) + mapping[letter] + m.group(3)
        return L
    pat = re.compile(r'(选|故选|答案|正确选项(?:为|是)?|应为|应选|故|仅|据此选|根据)([ABCDEF])(?=$|[，。；、:： ]|项|正确|错误|对|不对|符合|不符合|有误|表述正确|表述错误|说法|不是|属|均|。)')
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
    return ans_texts'''

assert old_func in src, "shuffle_options 原文未匹配"
src = src.replace(old_func, new_func)
open(P, 'w', encoding='utf-8').write(src)
print('pack_v013.py 已加固：洗牌同步解析字母映射')
