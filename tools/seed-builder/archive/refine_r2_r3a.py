# -*- coding: utf-8 -*-
"""R2 选项洗牌 + R3a 完全去重（5 库批量）。

输入：out/restored/{bank}.restored.json（旧基础 + 新基础 + 新测试，answer 新旧混杂）
处理：
- R3a 完全去重：同题干归一化（去空白/标点/数字字母）→ 保留优选版（新题优先、解析全优先）
- R2 选项洗牌：single_choice/multi_choice 洗牌 + answer 统一重算为正确项文本（v4 编码）
输出：out/refined/{bank}.refined.json
报告：洗牌后正确项 key 分布（验证不"连着选 A"）+ 去重统计
"""
import json, os, re, random
from collections import Counter, defaultdict

BASE = r"D:\study_app\tools\seed-builder\out"
OUT = os.path.join(BASE, "refined")
BANKS = ["bank-gudai-hanyu","bank-xiandai-hanyu","bank-zhongguo-gudai-wenxue",
         "bank-zhongguo-dangdai-wenxue","bank-zhongguo-xiandai-wenxue"]
NAMES = {"bank-gudai-hanyu":"古代汉语","bank-xiandai-hanyu":"现代汉语",
         "bank-zhongguo-gudai-wenxue":"古文史","bank-zhongguo-dangdai-wenxue":"当代",
         "bank-zhongguo-xiandai-wenxue":"现文史"}

def norm_stem(s):
    return re.sub(r"[\s，。、；：？！“”‘’（）()·—…《》<>0-9A-Za-z]","", s or "")

def is_new(q):
    """新题优先级更高（v4 标准化过）"""
    return "kb_" in q["id"]

def locate_ans_texts(q):
    """从 answer（key 或文本）定位正确项文本。"""
    t = q["type"]
    opts = q["options"] or []
    ans = q["answer"]
    def is_key(x):
        return isinstance(x, str) and len(x) == 1 and x in "ABCDEFGH"
    if isinstance(ans, list):
        if all(is_key(a) for a in ans):
            texts = [o["text"] for o in opts if o["key"] in ans]
        else:
            texts = list(ans)
    else:
        if is_key(ans):
            texts = [o["text"] for o in opts if o["key"] == ans]
        else:
            texts = [ans]
    return texts

def shuffle_q(q, rng):
    t = q["type"]
    if t not in ("single_choice", "multi_choice"):
        return
    opts = list(q["options"] or [])
    if not opts:
        return
    texts = locate_ans_texts(q)
    rng.shuffle(opts)
    keys = "ABCDEFGH"[:len(opts)]
    for o, k in zip(opts, keys):
        o["key"] = k
    q["options"] = opts
    if t == "single_choice":
        q["answer"] = texts[0] if texts else ""
    else:
        q["answer"] = sorted(set(texts))

def main():
    os.makedirs(OUT, exist_ok=True)
    lines = ["# R2+R3a 洗牌与完全去重报告", ""]
    total_in = total_out = 0
    for bank in BANKS:
        d = json.load(open(os.path.join(BASE, "restored", f"{bank}.restored.json"), encoding="utf-8"))
        rng = random.Random("r2_" + bank)

        # ---- R3a 完全去重 ----
        by_stem = defaultdict(list)
        for q in d:
            by_stem[norm_stem(q["stem"])].append(q)
        deduped = []
        removed = []
        for stem, grp in by_stem.items():
            if len(grp) == 1:
                deduped.append(grp[0])
                continue
            # 同题干：择优保留（新题优先 → 解析长优先 → id 排序稳定）
            grp_sorted = sorted(grp, key=lambda q: (0 if is_new(q) else 1,
                                                     -len(q.get("explanation") or ""),
                                                     q["id"]))
            deduped.append(grp_sorted[0])
            removed.extend(grp_sorted[1:])

        # ---- R2 洗牌 ----
        for q in deduped:
            shuffle_q(q, rng)

        # ---- 答案位置分布 ----
        key_dist = Counter()
        for q in deduped:
            if q["type"] == "single_choice":
                for o in q["options"]:
                    if o["text"] == q["answer"]:
                        key_dist[o["key"]] += 1
                        break

        out_p = os.path.join(OUT, f"{bank}.refined.json")
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(deduped, f, ensure_ascii=False, indent=1)

        total_in += len(d); total_out += len(deduped)
        basic = sum(1 for q in deduped if q.get("purpose") == "basic")
        test = sum(1 for q in deduped if q.get("purpose") == "test")
        dist = " ".join(f"{k}:{key_dist.get(k,0)}" for k in "ABCD")
        print(f"{NAMES[bank]}: {len(d)} → {len(deduped)}（去重{len(removed)}）| 基础{basic}/测试{test}")
        print(f"   答案位置: {dist}")
        lines.append(f"## {NAMES[bank]}（{bank}）")
        lines.append(f"- {len(d)} → **{len(deduped)}**（完全去重 {len(removed)} 题）| 基础 {basic} / 测试 {test}")
        lines.append(f"- 洗牌后正确项分布：{dist}")
        lines.append("")

    lines.insert(1, f"合计：{total_in} → **{total_out}**")
    rp = os.path.join(BASE, "reports", "refine_r2r3a.md")
    open(rp, "w", encoding="utf-8").write("\n".join(lines))
    print(f"\n合计 {total_in} → {total_out}\n报告 → {rp}")

if __name__ == "__main__":
    main()
