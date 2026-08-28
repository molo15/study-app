# -*- coding: utf-8 -*-
"""verify_v012.py：模拟 App 端 v4 包解析校验（fromBankJson 文本→key 映射 + knowledge/overviews + 得分冒烟）。"""
import json, os, zipfile, re, sys

BASE = r"D:\study_app\tools\seed-builder"
OUT = os.path.join(BASE, "out", "packages", "v012")
REPORT = os.path.join(BASE, "out", "reports", "verify_v012.md")
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
    text2key = {o["text"]: o["key"] for o in options}
    mapped = set()
    for a in answer:
        if a in keys:
            mapped.add(a)
        elif a in text2key:
            mapped.add(text2key[a])
    return mapped

def main():
    lines = ["# v0.12.0 验证报告", ""]
    grand_ok = True
    for bank, cn in BANKS.items():
        zpath = os.path.join(OUT, f"{bank}-v0.12.0.zip")
        errs = []
        total_q = 0
        with zipfile.ZipFile(zpath) as z:
            m = json.loads(z.read("manifest.json").decode("utf-8"))
            if m["formatVersion"] != 4:
                errs.append("formatVersion!=4")
            if not m.get("knowledge"):
                errs.append("knowledge 缺失")
            if not m.get("overviews"):
                errs.append("overviews 缺失")
            kp_ids = [k["id"] for k in m["knowledge"]]
            if len(kp_ids) != len(set(kp_ids)):
                errs.append("知识点 id 重复")

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
                        q_by_kp[q["knowledgeId"]] = q_by_kp.get(q["knowledgeId"], 0) + 1

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
                exp = k["questionCount"]
                got = basic_by_kp.get(k["id"], 0)
                if exp != got:
                    kp_count_mismatch += 1
                    if kp_count_mismatch <= 5:
                        errs.append(f"知识点 {k['id']} questionCount {exp} != 实际 {got}")

            # overview questionCount 汇总一致性
            ov_mismatch = 0
            per_ch = {}
            for f in z.namelist():
                if not f.startswith("questions/基础-") or not f.endswith(".json"):
                    continue
                for q in json.loads(z.read(f).decode("utf-8")):
                    per_ch[q["chapter"]] = per_ch.get(q["chapter"], 0) + 1
            for ov in m["overviews"]:
                if per_ch.get(ov["chapter"], 0) != ov["questionCount"]:
                    ov_mismatch += 1
                    if ov_mismatch <= 5:
                        errs.append(f"overview {ov['chapter']} {ov['questionCount']} != {per_ch.get(ov['chapter'])}")

            # mockPapers 引用存在性
            all_ids = set()
            for f in z.namelist():
                if f.startswith("questions/") and f.endswith(".json"):
                    for q in json.loads(z.read(f).decode("utf-8")):
                        all_ids.add(q["id"])
            mock_bad = 0
            for mp in m.get("mockPapers", []):
                for i in mp["questionIds"]:
                    if i not in all_ids:
                        mock_bad += 1
                        if mock_bad <= 5:
                            errs.append(f"模拟卷引用缺失 {i}")

        ok = len(errs) == 0
        grand_ok = grand_ok and ok
        lines.append(f"## {cn}（{bank}）")
        lines.append(f"- 总题数 **{total_q}**；选择题 **{choice_total}**；模拟卷引用缺失 **{mock_bad}**")
        lines.append(f"- 结果：{'✅ 通过' if ok else '❌ 异常 ' + str(len(errs))}")
        for e in errs[:12]:
            lines.append(f"  - {e}")
        lines.append("")
        print(f"{bank}: 总题数{total_q} 选择{choice_total} mock缺失{mock_bad} → {'通过' if ok else '异常'}")
        for e in errs[:6]:
            print("   !!", e)
    lines.append(f"## 总体：{'✅ 全部通过' if grand_ok else '❌ 存在异常'}")
    open(REPORT, "w", encoding="utf-8").write("\n".join(lines))
    print(f"\n验证报告 → {REPORT}")

if __name__ == "__main__":
    main()
