# -*- coding: utf-8 -*-
"""生成古文史扩充候选：袁行霈题库 205 个填空题 → 归章 → 候选 JSON。

编→章映射；考研真题精选的填空需语义归章，先标 '未分类' 由后续人工/AI 归。
输出：out/refined/gudaiwenxue_expand_candidates.json
"""
import json, re

SRC = r"D:\study_app\tools\seed-builder\out\extract\袁行霈题库.parsed.json"
OUT = r"D:\study_app\tools\seed-builder\out\refined\gudaiwenxue_expand_candidates.json"

BIAN2CH = {
    "第一编 先秦文学": "先秦文学",
    "第二编 秦汉文学": "秦汉文学",
    "第三编 魏晋南北朝文学": "魏晋南北朝文学",
    "第四编 隋唐五代文学": "隋唐五代文学",
    "第五编 宋代文学": "宋代文学",
    "第六编 元代文学": "元代文学",
    "第七编 明代文学": "明代文学",
    "第八编 清代文学": "清代文学",
    "第九编 近代文学": "近代文学",
}

def main():
    qs = json.load(open(SRC, encoding="utf-8"))
    cands = []
    for q in qs:
        if q["type"] != "填空题":
            continue
        ch = BIAN2CH.get(q["chapter"], "未分类")
        cands.append({
            "chapter": ch,
            "source_part": q["part"],
            "source_chapter": q["chapter"],
            "stem": q["stem"],
            "answer": q["answer"],
            "analysis": q["analysis"],
        })
    from collections import Counter
    print("候选总数:", len(cands))
    print("按章:", dict(Counter(c["chapter"] for c in cands)))
    json.dump(cands, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"已输出 {OUT}")
    # 打印未分类（考研真题）的全部，供后续归章
    print("\n=== 未分类（考研真题精选填空）===")
    for i, c in enumerate(cands):
        if c["chapter"] == "未分类":
            print(f"{i}: {c['stem'][:50]} | 答:{c['answer'][:15]}")

if __name__ == "__main__":
    main()
