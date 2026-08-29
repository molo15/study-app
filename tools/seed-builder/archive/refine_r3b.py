# -*- coding: utf-8 -*-
"""R3b 变式提炼（阶段一：高相似变式对删除）

规则：同 chapter 内，题干归一化后字符相似度 >= 0.72 的题对 → 判定为"同句/高度相似换问法"变式重复。
每对保留代表题（新题优先 → 解析长优先 → id 稳定），其余标记删除。

输出：
- out/refined/{bank}.refined2.json（删除后）
- out/reports/refine_r3b.md（删除清单 + 各科题量）
"""
import json, os, re
from collections import defaultdict

BASE = r"D:\study_app\tools\seed-builder\out"
OUT = os.path.join(BASE, "refined")
BANKS = ["bank-gudai-hanyu","bank-xiandai-hanyu","bank-zhongguo-gudai-wenxue",
         "bank-zhongguo-dangdai-wenxue","bank-zhongguo-xiandai-wenxue"]
NAMES = {"bank-gudai-hanyu":"古代汉语","bank-xiandai-hanyu":"现代汉语",
         "bank-zhongguo-gudai-wenxue":"古文史","bank-zhongguo-dangdai-wenxue":"当代",
         "bank-zhongguo-xiandai-wenxue":"现文史"}

def norm(s):
    return re.sub(r"[\s，。、；：？！“”‘’（）()·—…《》<>0-9A-Za-z]","", s or "")

def sim(a, b):
    sa, sb = set(a), set(b)
    if not sa or not sb: return 0.0
    return 2*len(sa&sb)/(len(sa)+len(sb))

def score(q):
    """代表题评分：新题优先 → 解析长优先 → id 稳定"""
    return (0 if "kb_" in q["id"] else 1,
            -len(q.get("explanation") or ""),
            q["id"])

def main():
    lines = ["# R3b 变式提炼报告（高相似变式删除）", ""]
    lines.append("规则：同 chapter 内题干归一化相似度 ≥0.72 判为变式重复，每对保留代表题。")
    lines.append("")
    total_before = total_after = 0
    for bank in BANKS:
        d = json.load(open(os.path.join(OUT, f"{bank}.refined.json"), encoding="utf-8"))
        by_ch = defaultdict(list)
        for q in d:
            by_ch[q.get("chapter")].append(q)

        del_ids = set()
        del_detail = []
        for ch, qs in by_ch.items():
            ns = [(q, norm(q["stem"])) for q in qs]
            pairs = []
            for i in range(len(ns)):
                for j in range(i+1, len(ns)):
                    if sim(ns[i][1], ns[j][1]) >= 0.72:
                        pairs.append((i, j))
            # 贪心合并删除：对每个相似对，删"非代表"那一个
            # 先按对处理，用并查集思想：同属一个相似簇的题，只保留该簇代表
            # 简单实现：对每对，若两个都未被删除，删掉评分低的
            for i, j in pairs:
                qi, qj = ns[i][0], ns[j][0]
                if qi["id"] in del_ids or qj["id"] in del_ids:
                    continue
                if score(qi) <= score(qj):  # qi 更优
                    del_ids.add(qj["id"]); del_detail.append((qj, qi))
                else:
                    del_ids.add(qi["id"]); del_detail.append((qi, qj))

        kept = [q for q in d if q["id"] not in del_ids]
        out_p = os.path.join(OUT, f"{bank}.refined2.json")
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(kept, f, ensure_ascii=False, indent=1)

        basic = sum(1 for q in kept if q.get("purpose")=="basic")
        test = sum(1 for q in kept if q.get("purpose")=="test")
        total_before += len(d); total_after += len(kept)
        print(f"{NAMES[bank]}: {len(d)} → {len(kept)}（删{len(del_ids)}）| 基础{basic}/测试{test}")
        lines.append(f"## {NAMES[bank]}（{bank}）")
        lines.append(f"- {len(d)} → **{len(kept)}**（变式删除 {len(del_ids)}）| 基础 {basic} / 测试 {test}")
        lines.append("")
        lines.append("| 删除题 | 保留代表题 |")
        lines.append("|---|---|")
        for rem, rep in del_detail[:20]:
            lines.append(f"| {rem['id']} `{rem['stem'][:32]}` | {rep['id']} `{rep['stem'][:32]}` |")
        lines.append("")

    lines.insert(1, f"合计：{total_before} → **{total_after}**")
    rp = os.path.join(BASE, "reports", "refine_r3b.md")
    open(rp, "w", encoding="utf-8").write("\n".join(lines))
    print(f"\n合计 {total_before} → {total_after}\n报告 → {rp}")

if __name__ == "__main__":
    main()
