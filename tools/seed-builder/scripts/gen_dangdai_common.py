# -*- coding: utf-8 -*-
"""Common helpers for converting 洪子诚当代文学史 items into bank questions."""
import re, hashlib, json

BANK_ID = "bank-zhongguo-dangdai-wenxue"

CH_NAMES = {
    1: "第一章 1949-1976 文学思潮",
    2: "第二章 50、60 年代小说",
    3: "第三章 50、60 年代新诗",
    4: "第四章 50、60 年代戏剧、散文",
    5: "第五章 80、90 年代文学思潮",
    6: "第六章 80 年代小说",
    7: "第七章 90 年代小说",
    8: "第八章 80、90 年代新诗",
    9: "第九章 80、90 年代戏剧",
    10: "第十章 80、90 年代散文",
    11: "第十一章 台港文学",
    12: "第十二章 2000-2016 年文学概述",
}

ANS_FORMAT = {
    "single_choice": "单选：从所给选项中选出唯一正确答案",
    "multi_choice": "多选：选出所有符合题意的选项",
    "blank": "填空：在横线处填出正确答案（多个空依次填写）",
    "short_answer": "简答/论述：分要点作答，先摆结论再给依据",
    "true_false": "判断：判断下列说法的正误（正确或错误）",
}

def extract_school_year(s):
    """Extract '中山大学2012年研' style source tags from stem."""
    m = re.search(r'\[([^\]]*?(?:大学|学院|人大)[^\]]*研)\]', s)
    if m:
        return m.group(1)
    m = re.search(r'（([^）]*?(?:大学|学院|人大)[^）]*研)）', s)
    if m:
        return m.group(1)
    return ""

def clean_meta(s):
    """Strip school-year tags, word-count requirements, leading numbering."""
    s = re.sub(r'\[[^\]]*?(?:大学|学院|人大)[^\]]*研\]', '', s)
    s = re.sub(r'（[^）]*?(?:大学|学院|人大)[^）]*研）', '', s)
    s = re.sub(r'（\d+\s*字以上）', '', s)
    s = re.sub(r'（\d+字以上）', '', s)
    s = re.sub(r'^\s*[\d]+[\.、、]\s*', '', s)
    return s.strip()

def make_blank(text, n=1):
    return '＿' * (3 * n)

def condense(text, limit=90):
    text = re.sub(r'\s+', '', text or '')
    return text[:limit] + ('…' if len(text) > limit else '')

def qid(idx):
    return f"{BANK_ID}:t_{idx:06d}"

def build_question(idx, qtype, stem, answer, explanation="", options=None,
                   chapter=None, tags=None, difficulty="medium", ans_fmt=None,
                   doc_chapter=None, school_year=""):
    if tags is None:
        tags = ["文学史题库"]
    if chapter is None:
        chapter = CH_NAMES[5]
    tags = ["文学史题库", "当代文学"] + [t for t in (tags or []) if t not in ("文学史题库", "当代文学")]
    exp = explanation.strip()
    if school_year:
        sy = school_year.strip()
        if exp:
            exp = f"（{sy}）" + exp if not exp.startswith("（") and sy not in exp else exp
        else:
            exp = f"（{sy}）"
    doc_path = f"洪子诚当代文学史题库.docx（章节：{doc_chapter or '考研真题精选'}）"
    return {
        "id": qid(idx),
        "type": qtype,
        "stem": stem,
        "options": options or [],
        "answer": answer,
        "explanation": exp,
        "answerFormat": ans_fmt or ANS_FORMAT[qtype],
        "chapter": chapter,
        "tags": tags,
        "difficulty": difficulty,
        "source": {"blockId": "", "docPath": doc_path},
    }
