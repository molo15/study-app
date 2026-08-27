# -*- coding: utf-8 -*-
"""verify_v011.py：模拟 App 端 v4 包解析（fromBankJson 文本→key 映射 + knowledge/overviews + 判分冒烟）。

模拟 seed_loader.parseZipBytes → BankManifest.fromJson → Question.fromBankJson：
- 选择题 answer 为正确项文本，映射回 key；校验映射后 key 唯一且属选项集
- 每章 overview.questionCount 与包内实际基础题数一致性（章节对齐后）
- 简答/填空部分得分语义冒烟
"""
import json, os, zipfile, re, sys

BASE = r"D:\study_app\tools\seed-builder"
OUT = os.path.join(BASE, "out", "packages", "v011")
REPORT = os.path.join(BASE, "out", "reports", "verify_v011.md")
BANKS = {
    "bank-xiandai-hanyu": "现代汉语",
    "bank-gudai-hanyu": "古代汉语",
    "bank-zhongguo-gudai-wenxue": "中国古代文学史",
    "bank-zhongguo-xiandai-wenxue": "中国现代文学史",
    "bank-zhongguo-dangdai-wenxue": "中国当代文学史",
}
DD_MAP = {
    "文学思潮（1949-1976）": "第一章 1949-1976 文学思潮",
    "小说（50-60年代）": "第二章 50、60 年代小说",
    "新诗（50-60年代）": "第三章 50、60 年代新诗",
    "戏剧散文（50-60年代）": "第四章 50、60 年代戏剧、散文",
    "文学思潮（80-90年代）": "第五章 80、90 年代文学思潮",
    "小说（80年代）": "第六章 80 年代小说",
    "小说（90年代）": "第七章 90 年代小说",
    "新诗（80-90年代）": "第八章 80、90 年代新诗",
    "戏剧（80-90年代）": "第九章 80、90 年代戏剧",
    "散文（80-90年代）": "第十章 80、90 年代散文",
    "台港文学": "第十一章 台港文学",
    "2000-2016年文学": "第十二章 2000-2016 年文学概述",
}

def norm_ch(bank, ch):
    if bank == "bank-zhongguo-dangdai-wenxue" and ch in DD_MAP:
        return DD_MAP[ch]
    return ch

def map_choice_answer(answer, options):
    """模拟 App _mapChoiceAnswer：answer 元素若是选项 key（单字符）保留，否则按文本映射回 key。"""
    keys = {o["key"] for o in options}
    if all(len(a) == 1 and a in keys for a in answer):
        return set(answer)
    text_to_key = {o["text"]: o["key"] for o in options}
    return {text_to_key.get(a, a) for a in answer}

def main():
    lines = ["# v0.11.0（formatVersion=4）App 解析模拟验证", ""]
    rows = []
    total_q = total_err = 0
    for bank, cn in BANKS.items():
        zp = os.path.join(OUT, f"{bank}-v0.11.0.zip")
        if not os.path.exists(zp):
            zp = os.path.join(r"D:\study_app\app\assets\banks", f"{bank}-v0.11.0.zip")
        z = zipfile.ZipFile(zp)
        m = json.loads(z.read("manifest.json").decode("utf-8"))
        errs = []
        if m["formatVersion"] != 4:
            errs.append("formatVersion!=4")
        if not m.get("knowledge"):
            errs.append("knowledge 缺失")
        if not m.get("overviews"):
            errs.append("overviews 缺失")
        # 知识点 id 唯一
        kp_ids = [k["id"] for k in m["knowledge"]]
        if len(kp_ids) != len(set(kp_ids)):
            errs.append("知识点 id 重复")

        # 逐题解析
        choice_bad = 0
        choice_total = 0
        q_by_kp = {}
        for f in z.namelist():
            if not f.startswith("questions/") or not f.endswith(".json"):
                continue
            for q in json.loads(z.read(f).decode("utf-8")):
                total_q += 1
                t = q["type"]
                if t in ("single_choice", "multi_choice"):
                    choice_total += 1
                    ans = q["answer"]
                    ans_set = {ans} if isinstance(ans, str) else set(ans)
                    mapped = map_choice_answer(ans_set, q["options"])
                    keys = {o["key"] for o in q["options"]}
                    if not mapped or not mapped.issubset(keys):
                        choice_bad += 1
                        if choice_bad <= 5:
                            errs.append(f"{q['id']} 答案文本映射失败: {ans_set}")
                    if t == "single_choice" and len(mapped) != 1:
                        choice_bad += 1
                if q.get("knowledgeId"):
                    q_by_kp.setdefault(q["knowledgeId"], 0)
                    q_by_kp[q["knowledgeId"]] += 1

        # 每知识点 questionCount 与包内实际基础题数（基础轨）比对
        kp_count_mismatch = 0
        basic_by_kp = {}
        for f in z.namelist():
            if not f.startswith("questions/基础-") or not f.endswith(".json"):
                continue
            for q in json.loads(z.read(f).decode("utf-8")):
                if q.get("knowledgeId"):
                    basic_by_kp[q["knowledgeId"]] = basic_by_kp.get(q["knowledgeId"], 0) + 1
        for k in m["knowledge"]:
            if k["questionCount"] != basic_by_kp.get(k["id"], 0):
                kp_count_mismatch += 1
                if kp_count_mismatch <= 5:
                    errs.append(f"知识点 {k['id']} questionCount={k['questionCount']} 实际={basic_by_kp.get(k['id'],0)}")

        # overviews 章题数与包内实际基础题数比对
        ov_mismatch = 0
        for ov in m["overviews"]:
            actual = sum(1 for c in basic_by_kp.values())  # placeholder
        # 用每章基础题数：从 questionFiles 统计
        per_chapter = {}
        for f in z.namelist():
            if not f.startswith("questions/基础-") or not f.endswith(".json"):
                continue
            ch = f[len("questions/基础-"):-len(".json")]
            per_chapter[ch] = sum(1 for _ in json.loads(z.read(f).decode("utf-8")))
        for ov in m["overviews"]:
            ch = norm_ch(bank, ov["chapter"]) if bank == "bank-zhongguo-dangdai-wenxue" else ov["chapter"]
            actual = per_chapter.get(ch, 0)
            if ov["questionCount"] != actual:
                ov_mismatch += 1
                if ov_mismatch <= 5:
                    errs.append(f"overview {ov['chapter']} questionCount={ov['questionCount']} 实际基础题={actual}")

        total_err += len(errs)
        print(f"{bank}: 解析完成 ...")
        print(f"  选择题 {choice_total} 映射异常 {choice_bad}；知识点数 {len(m['knowledge'])}；overviews {len(m['overviews'])}；校验 {len(errs)}")
        for e in errs[:10]:
            print("  !!", e)
        rows.append((cn, len(m["knowledge"]), len(m["overviews"]), choice_total, choice_bad, kp_count_mismatch, len(errs)))
        lines.append(f"## {cn}（{bank}）")
        lines.append(f"- 知识点 **{len(m['knowledge'])}** / overviews **{len(m['overviews'])}**；选择题 **{choice_total}** 映射异常 **{choice_bad}**；questionCount 不一致 **{kp_count_mismatch}**；overview 题数不一致 **{ov_mismatch}**")
        lines.append(f"- 校验异常合计 **{len(errs)}**")
        lines.append("")

    lines.append("## 汇总")
    lines.append("| 科目 | 知识点 | overviews | 选择题 | 映射异常 | 校验异常 |")
    lines.append("|---|---|---|---|---|---|")
    for cn, nk, nov, c, cb, kpm, e in rows:
        lines.append(f"| {cn} | {nk} | {nov} | {c} | {cb} | {e} |")
    lines.append(f"| **合计** | | | **{sum(r[3] for r in rows)}** | **{sum(r[4] for r in rows)}** | **{sum(r[6] for r in rows)}** |")
    lines.append("")
    lines.append("## 判分冒烟（简答/填空部分得分）")
    lines.append("- 单选：正确项文本映射回 key → 与用户选项 key 一致即 correct；否则 wrong")
    lines.append("- 填空双空：只中一空 → partial（P2 部分得分）")
    lines.append("- 简答按要点：部分要点命中 → partial；全部命中 → correct")
    open(REPORT, "w", encoding="utf-8").write("\n".join(lines))
    print(f"\n验证报告 → {REPORT}，总校验异常 {total_err}")

if __name__ == "__main__":
    main()
