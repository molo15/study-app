# -*- coding: utf-8 -*-
"""R3c 现文史章节配额提炼（v2，修复版）

无条件保留：模拟卷引用题 + kb_ 骨架题 + short_answer 简答/名词解释（综合题）
配额对象：旧客观题（single/multi/blank/true_false 且非 kb_ 非 protected）
  - 基础旧客观：每章 cap_basic_old=8
  - 测试旧客观：每章 cap_test=5
目标：~1030-1050（kb 504 + 短答 182 + 旧客观基础 216 + 测试 135）
"""
import json, os, re
from collections import defaultdict

BASE = r"D:\study_app\tools\seed-builder\out"
BANK = "bank-zhongguo-xiandai-wenxue"
CAP_BASIC_OLD = 8
CAP_TEST = 5

def norm_stem(s):
    return re.sub(r"[\s，。、；：？！“”‘’（）()·—…《》<>0-9A-Za-z]","", s or "")

def quality(q):
    return (len(q.get("explanation") or ""), len(norm_stem(q["stem"])), q["id"])

def main():
    d = json.load(open(os.path.join(BASE, "refined", f"{BANK}.refined2.json"), encoding="utf-8"))
    papers = json.load(open(os.path.join(BASE, "papers", "papers.json"), encoding="utf-8"))["papers"]
    protected = set()
    for pp in papers:
        if pp.get("bankId") == BANK:
            protected.update(pp.get("questionIds", []))
    print(f"模拟卷引用保护: {len(protected)} 题")

    by_ch = defaultdict(list)
    for q in d:
        by_ch[q.get("chapter")].append(q)

    kept = []
    del_list = []
    for ch in sorted(by_ch):
        qs = by_ch[ch]
        # 无条件保留
        always = [q for q in qs if q["id"] in protected or "kb_" in q["id"] or q["type"] == "short_answer"]
        # 旧客观题
        obj_old = [q for q in qs if q not in always]
        n_basic = n_test = 0
        tags_used = defaultdict(int)
        for q in sorted(obj_old, key=lambda q: (-quality(q)[0], -quality(q)[1], q["id"])):
            purpose = q.get("purpose")
            if purpose == "basic":
                if n_basic >= CAP_BASIC_OLD:
                    del_list.append(q); continue
                tgs = tuple(sorted(t for t in (q.get("tags") or []) if t != "文学史题库"))
                if tags_used[tgs] >= 3:
                    del_list.append(q); continue
                tags_used[tgs] += 1
                n_basic += 1
                always.append(q)
            else:
                if n_test >= CAP_TEST:
                    del_list.append(q); continue
                n_test += 1
                always.append(q)
        kept.extend(always)

    out_p = os.path.join(BASE, "refined", f"{BANK}.quota.json")
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(kept, f, ensure_ascii=False, indent=1)

    basic = sum(1 for q in kept if q.get("purpose")=="basic")
    test = sum(1 for q in kept if q.get("purpose")=="test")
    kb = sum(1 for q in kept if "kb_" in q["id"])
    sa = sum(1 for q in kept if q["type"]=="short_answer")
    print(f"现文史配额v2: 总{len(kept)}（基础{basic}/测试{test}）| kb{kb} 短答{sa} | 删除{len(del_list)}")

    from collections import Counter
    by_ch_del = Counter(q.get("chapter") for q in del_list)
    lines = ["# R3c 现文史章节配额删除候选清单（v2）", "",
             f"保留 {len(kept)}（基础 {basic} / 测试 {test}）| kb {kb} / 短答 {sa} | 删除候选 {len(del_list)}",
             "保护：模拟卷 + kb_ 骨架 + short_answer 无条件保留", ""]
    lines.append("| 章节 | 删除候选 |")
    lines.append("|---|---|")
    for ch, n in sorted(by_ch_del.items()):
        lines.append(f"| {ch} | {n} |")
    lines.append("")
    lines.append("## 抽样删除明细（每章最多4条）")
    shown = defaultdict(int)
    for q in del_list:
        ch = q.get("chapter")
        if shown[ch] >= 4: continue
        shown[ch] += 1
        lines.append(f"- `{q['id']}` [{ch}][{q['type']}] {q['stem'][:50]}")
    rp = os.path.join(BASE, "reports", "refine_r3c_xiandai_quota.md")
    open(rp, "w", encoding="utf-8").write("\n".join(lines))
    print(f"删除清单 → {rp}")

if __name__ == "__main__":
    main()
