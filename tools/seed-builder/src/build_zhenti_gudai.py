# -*- coding: utf-8 -*-
"""
Convert 思源「本章真题汇总」块流 for 古代汉语 into structured quiz questions.
Read-only on input docs; writes out/zhenti/gudai-hanyu.zhenti.json
"""
import json
import re
import os
import io
import sys
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DOCS = r"D:\study_app\tools\seed-builder\out\zhenti\docs"
OUT = r"D:\study_app\tools\seed-builder\out\zhenti\gudai-hanyu.zhenti.json"
BANK = "bank-gudai-hanyu"

FILES = [
    "00-bank-gudai-hanyu-古书的标点.json",
    "01-bank-gudai-hanyu-工具书简介.json",
    "02-bank-gudai-hanyu-文字（上）.json",
    "03-bank-gudai-hanyu-文字（下）.json",
    "04-bank-gudai-hanyu-绪论.json",
    "05-bank-gudai-hanyu-训诂.json",
    "06-bank-gudai-hanyu-词汇.json",
    "07-bank-gudai-hanyu-诗词格律.json",
    "08-bank-gudai-hanyu-语法（上）.json",
    "09-bank-gudai-hanyu-语法（下）.json",
    "10-bank-gudai-hanyu-音韵.json",
]

# ---------------- generic helpers ----------------

def strip_md(text):
    text = text.replace('\\_\\_\\_\\_\\_\\_', '______')
    text = re.sub(r'\*\*\s*([^*]+?)\s*\*\*', r'\1', text)
    text = text.replace('\\*', '*')
    text = re.sub(r'\*\s*([^\n*]+?)\s*\*', r'\1', text)
    text = re.sub(r'^\s*[>]+\s*', '', text, flags=re.M)
    text = text.replace('`', '')
    return text.strip()


def clean_stem(stem):
    stem = strip_md(stem)
    stem = re.sub(r'^\s*\d+[\.、]\s*', '', stem)              # leading list number
    stem = re.sub(r'^\s*（\s*[\d、\s]{2,12}\s*年）\s*', '', stem)  # year prefix
    stem = re.sub(r'^\s*（\s*[\d、\s]{2,12}\s*年）\s*', '', stem)  # again
    stem = re.sub(r'《\s*》', '《______》', stem)
    # expand blank followed by 2+ separators, e.g. ______、、、 -> ______、______、______、
    stem = re.sub(r'______((?:\s*[、，,]){2,})',
                  lambda mo: '______、' * (mo.group(1).count('、') + mo.group(1).count('，') + mo.group(1).count(',')),
                  stem)
    stem = stem.replace('\n', ' ')
    stem = re.sub(r'\s+', ' ', stem)
    return stem.strip()


def parse_year(stem):
    m = re.search(r'（\s*([\d、\s]{2,12})\s*年）', stem)
    if not m:
        return []
    years = []
    for tok in re.split(r'、|,|，', m.group(1).strip()):
        tok = tok.strip()
        if tok.isdigit():
            years.append(2000 + int(tok) if len(tok) == 2 else int(tok))
    return years


def split_list(md_text):
    """Split a markdown list block into items. Numbered lines start new items;
    bullet lines start new items only if no numbered item exists yet."""
    lines = md_text.split('\n')
    items = []
    cur = []
    cur_num = None
    seen_numbered = False
    for ln in lines:
        m_num = re.match(r'^\s*(\d+)[\.、]\s*', ln)
        m_bul = re.match(r'^\s*-\s*', ln)
        if m_num:
            if cur:
                items.append((cur_num, '\n'.join(cur).strip()))
            cur = [ln]
            cur_num = m_num.group(1)
            seen_numbered = True
        elif m_bul:
            if seen_numbered and cur:
                cur.append(ln)          # continuation of current numbered item
            else:
                if cur:
                    items.append((cur_num, '\n'.join(cur).strip()))
                cur = [ln]
                cur_num = None
        else:
            cur.append(ln)
    if cur:
        items.append((cur_num, '\n'.join(cur).strip()))
    return items


def get_bold(text):
    return [f.strip() for f in re.findall(r'\*\*([^*]+?)\*\*', text) if f.strip()]


def split_answer_chunks(text):
    return [x.strip().strip('*').strip(' \n') for x in re.split(r'[；;]', text) if x.strip()]


def extract_blank_ans(aitem):
    """Extract the answer word(s) for a blank from an answer item text."""
    pre = re.split(r'【解析】|【答案】|【答案要点】|解析[：:]|参考答案[：:]', aitem)[0]
    pre_stripped = re.sub(r'^\s*\d+[\.、]\s*', '', strip_md(pre)).strip()
    stem_echo = bool(re.match(r'^（\s*[\d、]{2,12}\s*年）', pre_stripped))
    if stem_echo:
        bold = get_bold(aitem)
        if bold:
            chunks = []
            for b in bold:
                chunks.extend(split_answer_chunks(b))
            return chunks
        return []
    if pre_stripped:
        return split_answer_chunks(pre_stripped)
    bold = get_bold(aitem)
    if bold:
        chunks = []
        for b in bold:
            chunks.extend(split_answer_chunks(b))
        return chunks
    return []


# extension markers that should be cut from namedef / short-answer references
EXT_MARKERS = ['【欣途驿站·拓展知识】', '【欣途驿站】', '词牌≠题目', '同调异名', '记忆口诀',
               '易错点', '反切的局限', '系联法', '拓展知识']


def clean_block_text(text):
    """Clean an answer block (named-def / short-answer) into plain reference text."""
    text = strip_md(text)
    # cut extension content
    for mk in EXT_MARKERS:
        idx = text.find(mk)
        if idx != -1:
            text = text[:idx]
            break
    text = re.sub(r'^\s*\d+[\.、]\s*', '', text, count=1)
    for marker in ['【答案要点】', '【参考答案】', '【答案】', '【解析】', '参考答案：', '答案要点：', '答案：', '解析：']:
        text = re.sub(r'^[\s>]*' + re.escape(marker) + r'[\s]*', '', text, flags=re.M)
    text = re.sub(r'^[\s>*]+', '', text, flags=re.M)   # strip leading > * spaces
    text = re.sub(r'^[\s>]*\*\s*', '', text, flags=re.M)
    text = re.sub(r'^[\s>]*-+\s*', '', text, flags=re.M)
    text = re.sub(r'^[\s>]*(解析|答案要点|参考答案|答案)[\s:：]*$', '', text, flags=re.M)
    text = re.sub(r'\\\*', '', text)
    text = re.sub(r'\n{2,}', '\n', text)
    return text.strip()


def trim_answer_echo(ans, stem):
    s = clean_stem(stem)
    s = re.sub(r'^名词解释[：:]', '', s)
    a = re.sub(r'^\s*\d+[\.、]\s*', '', ans)                 # leading item number
    a = re.sub(r'^（\s*[\d、]{2,12}\s*年）\s*', '', a)         # year echo
    a = re.sub(r'^（\s*[\d、]{2,12}\s*年）\s*', '', a)
    a = re.sub(r'^[\s>*]+', '', a)
    if not s:
        return a.strip()
    if a.startswith(s):
        a = a[len(s):]
    a = a.lstrip('\n :：')
    a = re.sub(r'^\s*\d+[\.、]\s*', '', a)
    a = re.sub(r'\\\*', '', a)
    return a.strip()


def expl_of(ans_block_text):
    t = strip_md(ans_block_text)
    m = re.search(r'【解析】\s*(.*)$', t, re.S)
    if m and m.group(1).strip():
        return "解析：" + m.group(1).strip()
    m = re.search(r'解析[：:]\s*(.*)$', t, re.S)
    if m and m.group(1).strip():
        return "解析：" + m.group(1).strip()
    return None


DOMAIN_TERMS = [
    "说文解字", "许慎", "六书", "象形", "指事", "会意", "形声", "转注", "假借",
    "四体二用", "本义", "引申义", "词义", "通假字", "假借字", "异体字", "古今字",
    "使动用法", "意动用法", "被动句", "判断句", "词类活用", "平仄", "词牌", "近体诗",
    "律诗", "绝句", "对仗", "押韵", "反切", "广韵", "切韵", "中原音韵", "平水韵",
    "中古音", "声母", "韵母", "声调", "入声", "五音", "等韵", "训诂", "五经",
    "十三经注疏", "集解", "马氏文通", "金文", "甲骨文", "小篆", "隶变",
    "汉字", "词义扩大", "词义缩小", "词义转移", "古今词义", "虚词", "实词",
    "类书", "字典", "词典", "广雅", "尔雅", "汉语大词典", "康熙字典", "论语",
    "声训", "义训", "字义", "造字法", "文言文", "语法", "词汇", "判断句式",
]


def knowledge_tags(stem, answer):
    text = stem + ' ' + (answer if isinstance(answer, str) else ' '.join(answer))
    found = []
    for term in DOMAIN_TERMS:
        if term in text and term not in found:
            found.append(term)
    found.sort(key=len, reverse=True)
    return found[:3]


def build_tags(years, stem, answer, chapter):
    tags = ["真题"]
    for y in years:
        tags.append(f"{y}真题")
    kt = knowledge_tags(stem, answer) or [chapter]
    for t in kt:
        tags.append(t)
    seen = set()
    out = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


# ---------------- builders ----------------

def load(fname):
    with open(os.path.join(DOCS, fname), encoding='utf-8') as f:
        return json.load(f)


def q_blank(stem, ans_chunks, years, chapter, doc_path, block_id, expl=None):
    return {
        "type": "blank",
        "stem": clean_stem(stem),
        "answer": ans_chunks,
        "explanation": expl or "本题为历年真题，答案见出处。",
        "tags": build_tags(years, stem, ans_chunks, chapter),
        "difficulty": "easy",
        "source": {"blockId": block_id, "docPath": doc_path},
        "chapter": chapter,
    }


def q_true_false(stem, verdict, years, chapter, doc_path, block_id, expl=None):
    return {
        "type": "true_false",
        "stem": clean_stem(stem),
        "options": [],
        "answer": verdict,
        "explanation": expl or "本题为历年真题，答案见出处。",
        "tags": build_tags(years, stem, verdict, chapter),
        "difficulty": "easy",
        "source": {"blockId": block_id, "docPath": doc_path},
        "chapter": chapter,
    }


def q_single(stem, options, answer_letter, years, chapter, doc_path, block_id, expl=None):
    return {
        "type": "single_choice",
        "stem": clean_stem(stem),
        "options": options,
        "answer": answer_letter,
        "explanation": expl or "本题为历年真题，答案见出处。",
        "tags": build_tags(years, stem, answer_letter, chapter),
        "difficulty": "medium",
        "source": {"blockId": block_id, "docPath": doc_path},
        "chapter": chapter,
    }


def q_namedef(stem, ans_text, years, chapter, doc_path, block_id, expl=None):
    ans = trim_answer_echo(clean_block_text(ans_text), stem)
    return {
        "type": "short_answer",
        "stem": "名词解释：" + clean_stem(stem),
        "answer": ans,
        "answerFormat": "作答格式：①定义 ②核心特征 ③代表例证",
        "explanation": expl or "本题为历年真题，答案见出处。",
        "tags": build_tags(years, stem, ans, chapter),
        "difficulty": "medium",
        "source": {"blockId": block_id, "docPath": doc_path},
        "chapter": chapter,
    }


def q_short(stem, ans_text, years, chapter, doc_path, block_id, expl=None, fmt=None):
    ans = trim_answer_echo(clean_block_text(ans_text), stem)
    return {
        "type": "short_answer",
        "stem": clean_stem(stem),
        "answer": ans,
        "answerFormat": fmt or "作答格式：①要点分条 ②每条一句话说清",
        "explanation": expl or "本题为历年真题，答案见出处。",
        "tags": build_tags(years, stem, ans, chapter),
        "difficulty": "hard",
        "source": {"blockId": block_id, "docPath": doc_path},
        "chapter": chapter,
    }


def parse_choices(stem):
    """Parse single-choice options; returns (cleaned_stem, options)."""
    lines = [l.strip() for l in stem.split('\n') if l.strip()]
    opts = []
    stem_lines = []
    for ln in lines:
        if re.match(r'^(选项解析|解析|参考答案|答案|>|【解析】)', ln):
            break
        m = re.match(r'^([A-D])[\.、]\s*(.+)$', ln)
        if m:
            opts.append({"key": m.group(1), "text": strip_md(m.group(2)).strip()})
        else:
            stem_lines.append(ln)
    return clean_stem('\n'.join(stem_lines)), opts


def first_letter_ans(text):
    m = re.search(r'\b([A-D])\b', text)
    return m.group(1) if m else None


# =====================================================================
# Per-file extraction
# =====================================================================

def extract():
    out = []

    # ---------- 00 古书的标点 ----------
    d = load(FILES[0])
    blocks = d["blocks"]
    chapter = d["chapter"]
    doc_path = d["docPath"]
    p = {i: b["c"] for i, b in enumerate(blocks) if b["t"] == "P"}
    trans_pairs = [
        ("若亡郑而有益于君，敢以烦执事。", 32),
        ("招招舟子，人涉卬否。人涉卬否，卬须我友。", 31),
        ("汉因循而不革，明简易，随时宜也。其后颇有所改。", 30),
        ("贡之不入，寡君之罪也。", 28),
        ("朝廷之臣莫不畏王，四境之内莫不有求于王。", 27),
    ]
    for stem, ans_idx in trans_pairs:
        ans = p.get(ans_idx, "")
        ans = re.sub(r'^（\s*23\s*年）\s*译文[：:]?\s*', '', ans.strip())
        out.append(q_short(
            "请翻译下列古文句子：" + stem, ans, [2023], chapter, doc_path,
            f"00-古书的标点#P{ans_idx}",
            fmt="作答格式：①逐句直译 ②重点字词落实",
        ))

    # 标点翻译（给古文断句并翻译）——题干块与答案块按年份配对
    punct_q = {2020: 8, 2021: 9, 2025: 12, 2022: 13, 2019: 16, 2024: 17}
    punct_a = {2020: 33, 2021: 35, 2025: 36, 2022: 34, 2019: 29, 2024: 25}
    for yr, qi in punct_q.items():
        stem = p[qi]
        ans = p[punct_a[yr]]
        ans = re.sub(r'^（\s*\d+\s*年）\s*', '', ans.strip())
        out.append(q_short(
            stem, ans, [yr], chapter, doc_path, f"00-古书的标点#P{punct_a[yr]}",
            fmt="作答格式：①为古文添加标点断句 ②翻译全文",
        ))

    # ---------- 01 工具书简介 ----------
    d = load(FILES[1])
    blocks = d["blocks"]
    chapter = d["chapter"]
    doc_path = d["docPath"]
    p = {i: b["c"] for i, b in enumerate(blocks) if b["t"] == "P"}
    blank_pairs = [(7, 22), (10, 20), (11, 17), (14, 19)]
    for qi, ai in blank_pairs:
        stem = p[qi]
        ans = p[ai]
        out.append(q_blank(stem, split_answer_chunks(strip_md(ans)), parse_year(stem),
                           chapter, doc_path, f"01-工具书简介#P{qi}"))
    tf_pairs = [(8, 15), (13, 18)]
    for qi, ai in tf_pairs:
        stem = p[qi]
        ans = p[ai]
        verdict = "正确" if ("√" in ans or "对" in ans) else "错误"
        out.append(q_true_false(stem, verdict, parse_year(stem), chapter, doc_path,
                                f"01-工具书简介#P{qi}"))
    namedef_pairs = [(9, 16), (12, 21)]
    for qi, ai in namedef_pairs:
        stem = p[qi]
        ans = p[ai]
        out.append(q_namedef(stem, ans, parse_year(stem), chapter, doc_path,
                             f"01-工具书简介#P{qi}"))

    # ---------- 02 文字（上） ----------
    d = load(FILES[2])
    blocks = d["blocks"]
    chapter = d["chapter"]
    doc_path = d["docPath"]
    m = {i: b["m"] for i, b in enumerate(blocks)}
    q_items = split_list(m[43])
    a_items = split_list(m[44])
    for qi, (num, qtext) in enumerate(q_items):
        stem, opts = parse_choices(qtext)
        aitem = a_items[qi][1] if qi < len(a_items) else ""
        letter = first_letter_ans(strip_md(aitem))
        if not letter or len(opts) < 2:
            continue
        out.append(q_single(stem, opts, letter, parse_year(qtext), chapter, doc_path,
                            "02-文字（上）#l44", expl_of(aitem)))
    q_items = split_list(m[55])
    a_items = split_list(m[71])
    for qi, (num, qtext) in enumerate(q_items):
        if '[图片]' in qtext or '图片' in qtext:
            continue
        aitem = a_items[qi][1] if qi < len(a_items) else ""
        chunks = extract_blank_ans(aitem)
        if not chunks:
            continue
        out.append(q_blank(qtext, chunks, parse_year(qtext), chapter, doc_path,
                           f"02-文字（上）#l{71}"))
    out.append(q_short("（19年）简述六书理论，并各举两个例子。", m[73], [2019],
                       chapter, doc_path, "02-文字（上）#l73"))
    q_items = split_list(m[69])
    a_items = split_list(m[77])
    for qi, (num, qtext) in enumerate(q_items):
        aitem = a_items[qi][1] if qi < len(a_items) else ""
        if not aitem.strip():
            continue
        out.append(q_namedef(qtext, aitem, parse_year(qtext), chapter, doc_path,
                             f"02-文字（上）#l77"))

    # ---------- 03 文字（下） ----------
    d = load(FILES[3])
    blocks = d["blocks"]
    chapter = d["chapter"]
    doc_path = d["docPath"]
    m = {i: b["m"] for i, b in enumerate(blocks)}
    stem, opts = parse_choices(m[76])
    aitem = strip_md(m[79])
    letter = first_letter_ans(aitem)
    if letter and len(opts) >= 2:
        out.append(q_single(stem, opts, letter, parse_year(m[76]), chapter, doc_path,
                            "03-文字（下）#l79", expl_of(aitem)))
    qtext = m[59]
    aitem = strip_md(m[60])
    verdict = "正确" if ("√" in aitem or "对" in aitem) else "错误"
    out.append(q_true_false(qtext, verdict, parse_year(qtext), chapter, doc_path,
                            "03-文字（下）#l60", expl_of(aitem)))
    q_items = split_list(m[50])
    a_items = split_list(m[83])
    for qi, (num, qtext) in enumerate(q_items):
        aitem = a_items[qi][1] if qi < len(a_items) else ""
        chunks = extract_blank_ans(aitem)
        if not chunks:
            continue
        out.append(q_blank(qtext, chunks, parse_year(qtext), chapter, doc_path,
                           f"03-文字（下）#l{83}"))
    out.append(q_namedef(m[64], m[70], parse_year(m[64]), chapter, doc_path, "03-文字（下）#l70"))
    sa_pairs = [
        (1, "（16年）说说汉字的发展演变及其两次重要的变化对汉字的影响。", 78),
        (2, "（23年）汉字形体的演变分为哪两个阶段，每个阶段的代表文字及其特点是怎样的？", 81),
    ]
    for qi, (num, qtext, ai) in enumerate(sa_pairs):
        out.append(q_short(qtext, m[ai], parse_year(qtext), chapter, doc_path,
                           f"03-文字（下）#l{ai}"))

    # ---------- 04 绪论 (no usable answer -> skip) ----------

    # ---------- 05 训诂 ----------
    d = load(FILES[5])
    blocks = d["blocks"]
    chapter = d["chapter"]
    doc_path = d["docPath"]
    m = {i: b["m"] for i, b in enumerate(blocks)}
    q_items = split_list(m[28])
    a_items = split_list(m[47])
    for qi, (num, qtext) in enumerate(q_items):
        aitem = a_items[qi][1] if qi < len(a_items) else ""
        chunks = extract_blank_ans(aitem)
        if not chunks:
            continue
        out.append(q_blank(qtext, chunks, parse_year(qtext), chapter, doc_path,
                           f"05-训诂#l{47}"))

    # ---------- 06 词汇 ----------
    d = load(FILES[6])
    blocks = d["blocks"]
    chapter = d["chapter"]
    doc_path = d["docPath"]
    m = {i: b["m"] for i, b in enumerate(blocks)}
    q_items = split_list(m[81])
    a_items = split_list(m[114])
    for qi, (num, qtext) in enumerate(q_items):
        if '合成词' in qtext:
            continue
        aitem = a_items[qi][1] if qi < len(a_items) else ""
        chunks = extract_blank_ans(aitem)
        if not chunks:
            continue
        out.append(q_blank(qtext, chunks, parse_year(qtext), chapter, doc_path,
                           f"06-词汇#l{114}"))
    q_items = split_list(m[84])
    a_items = split_list(m[120])
    for qi, (num, qtext) in enumerate(q_items):
        aitem = a_items[qi][1] if qi < len(a_items) else ""
        verdict = "正确" if ("√" in aitem or "对" in aitem) else "错误"
        out.append(q_true_false(qtext, verdict, parse_year(qtext), chapter, doc_path,
                                f"06-词汇#l{120}", expl_of(aitem)))
    # choice 「发」本义 (answer A from 选项解析)
    stem, opts = parse_choices(m[103])
    if len(opts) >= 2:
        out.append(q_single(stem, opts, "A", parse_year(m[103]), chapter, doc_path,
                            "06-词汇#l103",
                            expl="解析：根据选项解析，“发”的本义是把箭射出去（发射），A项“齐军万弩齐发”使用的是本义。"))
    # 名解 词的本义
    out.append(q_namedef(m[72], m[96], parse_year(m[72]), chapter, doc_path, "06-词汇#l96"))
    # 简答 x2  per-item answers
    q_items = split_list(m[75])
    a_items = split_list(m[115])
    for qi, (num, qtext) in enumerate(q_items):
        aitem = a_items[qi][1] if qi < len(a_items) else ""
        if not aitem.strip():
            continue
        out.append(q_short(qtext, aitem, parse_year(qtext), chapter, doc_path,
                           f"06-词汇#l{115}"))

    # ---------- 07 诗词格律 ----------
    d = load(FILES[7])
    blocks = d["blocks"]
    chapter = d["chapter"]
    doc_path = d["docPath"]
    m = {i: b["m"] for i, b in enumerate(blocks)}
    chunks = extract_blank_ans(m[42])
    if chunks:
        out.append(q_blank(m[32], chunks, parse_year(m[32]), chapter, doc_path, "07-诗词格律#l42"))
    out.append(q_short(m[49], m[43], parse_year(m[49]), chapter, doc_path, "07-诗词格律#l43"))
    q_items = split_list(m[56])
    namedef_ans = {1: 53, 2: 58}
    for qi, (num, qtext) in enumerate(q_items):
        ai = namedef_ans.get(qi + 1)
        if not ai:
            continue
        out.append(q_namedef(qtext, m[ai], parse_year(qtext), chapter, doc_path,
                             f"07-诗词格律#l{ai}"))

    # ---------- 08 语法（上） ----------
    d = load(FILES[8])
    blocks = d["blocks"]
    chapter = d["chapter"]
    doc_path = d["docPath"]
    m = {i: b["m"] for i, b in enumerate(blocks)}
    out.append(q_short(m[15], m[16], parse_year(m[15]), chapter, doc_path, "08-语法（上）#l16"))

    # ---------- 09 语法（下） ----------
    d = load(FILES[9])
    blocks = d["blocks"]
    chapter = d["chapter"]
    doc_path = d["docPath"]
    m = {i: b["m"] for i, b in enumerate(blocks)}
    q_items = split_list(m[67])
    a_items = split_list(m[61])
    for qi, (num, qtext) in enumerate(q_items):
        if qi >= len(a_items):
            continue
        stem, opts = parse_choices(qtext)
        aitem = strip_md(a_items[qi][1])
        letter = first_letter_ans(aitem)
        if not letter or len(opts) < 2:
            continue
        out.append(q_single(stem, opts, letter, [], chapter, doc_path,
                            "09-语法（下）#l61", expl_of(aitem)))
    q_items = split_list(m[80])
    a_items = split_list(m[82])
    for qi, (num, qtext) in enumerate(q_items):
        aitem = a_items[qi][1] if qi < len(a_items) else ""
        if not aitem.strip():
            continue
        out.append(q_short(qtext, aitem, parse_year(qtext), chapter, doc_path,
                           "09-语法（下）#l82"))
    q_items = split_list(m[86])
    a_items = split_list(m[87])
    for qi, (num, qtext) in enumerate(q_items):
        aitem = a_items[qi][1] if qi < len(a_items) else ""
        if not aitem.strip():
            continue
        out.append(q_namedef(qtext, aitem, [], chapter, doc_path, "09-语法（下）#l87"))

    # ---------- 10 音韵 ----------
    d = load(FILES[10])
    blocks = d["blocks"]
    chapter = d["chapter"]
    doc_path = d["docPath"]
    m = {i: b["m"] for i, b in enumerate(blocks)}
    q_items = split_list(m[52])
    a_items = split_list(m[65])
    for qi, (num, qtext) in enumerate(q_items):
        if qi >= len(a_items):
            continue
        chunks = extract_blank_ans(a_items[qi][1])
        if not chunks:
            continue
        if '五音' in qtext and len(chunks) == 1 and '、' in chunks[0]:
            chunks = [c for c in chunks[0].split('、') if c]
        out.append(q_blank(qtext, chunks, parse_year(qtext), chapter, doc_path,
                           f"10-音韵#l{65}"))
    stem, opts = parse_choices(m[68])
    aitem = strip_md(m[66])
    letter = first_letter_ans(aitem)
    if letter and len(opts) >= 2:
        out.append(q_single(stem, opts, letter, parse_year(m[68]), chapter, doc_path,
                            "10-音韵#l66", expl_of(aitem)))
    out.append(q_short(m[42], m[81], parse_year(m[42]), chapter, doc_path, "10-音韵#l81"))
    out.append(q_namedef(m[78], m[50], parse_year(m[78]), chapter, doc_path, "10-音韵#l50"))

    return out


def main():
    questions = extract()
    seen = set()
    uniq = []
    for q in questions:
        key = (q["chapter"], q["stem"], json.dumps(q.get("answer"), ensure_ascii=False))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(q)

    for n, q in enumerate(uniq, start=1):
        q["id"] = f"{BANK}:z_{n:06d}"

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"bankId": BANK, "questions": uniq}, f, ensure_ascii=False, indent=1)

    by_ch = defaultdict(Counter)
    for q in uniq:
        by_ch[q["chapter"]][q["type"]] += 1
    print("TOTAL:", len(uniq))
    for ch, c in by_ch.items():
        print(f"  {ch}: {sum(c.values())}  {dict(c)}")
    print("TYPE DIST:", dict(Counter(q['type'] for q in uniq)))


if __name__ == "__main__":
    main()
