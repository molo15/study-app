# -*- coding: utf-8 -*-
"""解析袁行霈《中国文学史》题库文本 → 结构化题目 JSON。

输出：out/extract/袁行霈题库.parsed.json（{part, chapter, type, stem, answer, analysis}）
"""
import json, re, os

SRC = r"D:\study_app\tools\seed-builder\out\extract\袁行霈中国文学史题库17.txt"
OUT = r"D:\study_app\tools\seed-builder\out\extract\袁行霈题库.parsed.json"

def main():
    t = open(SRC, encoding="utf-8").read()
    lines = t.split("\n")
    questions = []
    # 状态机
    part, chapter, qtype = "", "", ""
    cur = None  # 当前题 dict
    mode = None  # 'stem'/'answer'/'analysis'

    def flush():
        nonlocal cur
        if cur and cur.get("stem"):
            questions.append(cur)
        cur = None

    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        # 部分/章节/题型标题
        if re.match(r"^第[一二三四五六七八九十]+部分", s):
            flush(); part = s; chapter = ""; qtype = ""; continue
        if re.match(r"^第[一二三四五六七八九十百]+[篇章部编]", s) and len(s) <= 25 and "题" not in s[:4] and not s.startswith("【") and not re.search(r"[。？，]", s[:20]):
            flush(); chapter = s; continue
        if s in ("填空题","选择题","名词解释","简答题","论述题","分析题","判断题","单项选择题","多项选择题","综合题"):
            flush(); qtype = s; continue
        # 题号开头
        m = re.match(r"^(\d+)[.、]\s*(.*)", s)
        if m and not s.startswith("【"):
            flush()
            cur = {"part": part, "chapter": chapter, "type": qtype, "stem": m.group(2), "answer": "", "analysis": ""}
            mode = "stem"
            continue
        # 答案/解析
        if s.startswith("【答案】") or s.startswith("【答案】"):
            mode = "answer"
            if cur: cur["answer"] += s.replace("【答案】", "").strip()
            continue
        if s.startswith("【解析】"):
            mode = "analysis"
            if cur: cur["analysis"] += s.replace("【解析】", "").strip()
            continue
        # 正文续行
        if cur and mode in ("stem", "answer", "analysis"):
            cur[mode] = (cur[mode] + " " + s).strip() if mode != "stem" else (cur[mode] + s)
    flush()

    # 统计
    from collections import Counter
    print("题目总数:", len(questions))
    print("题型:", dict(Counter(q["type"] for q in questions)))
    print("带答案:", sum(1 for q in questions if q["answer"]))
    print("带解析:", sum(1 for q in questions if q["analysis"]))
    print("章节:")
    for ch, n in Counter(q["chapter"] for q in questions).most_common():
        print(f"  {ch or '(无章节)'}: {n}")
    json.dump(questions, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n已输出 {OUT}")

if __name__ == "__main__":
    main()
