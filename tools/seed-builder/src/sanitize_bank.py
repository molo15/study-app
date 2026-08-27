# -*- coding: utf-8 -*-
"""
P0 题库清洗与质量门禁脚本（重新设计方案 §4 / §6-P0）

功能（输入 v09 库 → 输出清洗版 + 质量报告）：
  1. 选项洗牌：打乱选择题选项顺序并重写 answer（基于正确项文本匹配，固定 seed 可复现）
  2. answerVariants 修复：等价表述被拆成多组的，归一化后有交集即合并为一个组（组内任一命中即该空/要点对）
  3. 完全重复去重：归一化题干完全相同者仅保留第 1 条（报告留痕）
  4. 质量检测：解析缺失/占位/过短、近义重复、真题改编统计、章节/题型分布、答案位置分布
  5. 输出：out/sanitized/<bank>.sanitized.json + report_<bank>.md + summary.md

用法：python src/sanitize_bank.py
不改动任何源文件；清洗版与报告均写入 out/sanitized/。
"""
import json
import os
import re
import hashlib
import random
from collections import Counter, defaultdict

BASE = os.path.join(os.path.dirname(__file__), "..", "out")
FILES = {
    "古代汉语": os.path.join(BASE, "v09gudaihanyu", "bank-gudai-hanyu.v09.json"),
    "现代汉语": os.path.join(BASE, "v09", "bank-xiandai-hanyu.v09.json"),
    "中国古代文学史": os.path.join(BASE, "v09gudaiwenxue", "bank-zhongguo-gudai-wenxue.v09.json"),
    "中国现代文学史": os.path.join(BASE, "v09xiandaiwenxue", "bank-zhongguo-xiandai-wenxue.v09.json"),
    "中国当代文学史": os.path.join(BASE, "v09dangdai", "bank-zhongguo-dangdai-wenxue.v09.json"),
}
OUT_DIR = os.path.join(BASE, "sanitized")

# 归一化：去空白 + 全角/半角标点 + 大小写
_PUNCT = r"[\s\u3000，。、；：？！,.!?;:\"'“”‘’（）()\[\]【】—…·《》〈〉<>《》\-]+"
def _norm(s):
    return re.sub(_PUNCT, "", str(s or "")).lower()

# 解析占位黑名单（G4）
LAZY_RE = re.compile(r"^(见原文|见教材|见参考|参考答案见|参考解析|同解析|略[。]?|见上|见下|见解析|。?)$")

def _rng_for(qid):
    seed = int(hashlib.md5(qid.encode("utf-8")).hexdigest(), 16) % (2 ** 32)
    return random.Random(seed)

def shuffle_options(q):
    """选项洗牌；返回 (是否处理, 原answer, 新answer)。无法匹配文本则不动。"""
    opts = q.get("options") or []
    if len(opts) < 2:
        return q, None
    ans = q.get("answer")
    ans_keys = ans if isinstance(ans, list) else [ans]
    key_to_text = {o["key"]: o["text"] for o in opts}
    ordered_texts = [key_to_text[k] for k in ans_keys if k in key_to_text]
    if not ordered_texts:
        return q, None  # answer 无法对应到选项，跳过（报告会标注）
    new_opts = opts[:]
    _rng_for(q["id"]).shuffle(new_opts)
    letters = "ABCDEFGHIJ"
    for i, o in enumerate(new_opts):
        o["key"] = letters[i]
    text_to_newkey = {o["text"]: o["key"] for o in new_opts}
    new_ans = [text_to_newkey[t] for t in ordered_texts]
    q["options"] = new_opts
    q["answer"] = new_ans if isinstance(ans, list) else new_ans[0]
    return q, (ans, q["answer"])

def fix_variants(q):
    """等价答案修复（保守）：仅当两组指纹（归一化+去重）完全相同才合并为一组，
    即同一答案的不同等价表述；不同空/要点（即使共享部分元素）绝不合并。
    返回修复组数。"""
    v = q.get("answerVariants")
    if not v:
        return q, 0

    def fingerprint(group):
        return frozenset(_norm(x) for x in group if _norm(x))

    from collections import defaultdict
    by_fp = defaultdict(list)
    for group in v:
        fp = fingerprint(group)
        if fp:
            by_fp[fp].append(group)
    merged = []
    for fp, groups in by_fp.items():
        combined, seen = [], set()
        for g in groups:
            for x in g:
                n = _norm(x)
                if n and n not in seen:
                    seen.add(n)
                    combined.append(x)
        merged.append(combined)
    fixed = len(v) - len(merged)
    q["answerVariants"] = merged
    return q, fixed

def dedup(data):
    """完全重复题干去重。返回 (保留列表, 删除记录[(id, 保留的id)])。"""
    seen, keep, removed = {}, [], []
    for q in data:
        n = _norm(q.get("stem"))
        if not n:
            keep.append(q)
            continue
        if n in seen:
            removed.append((q["id"], seen[n]))
            continue
        seen[n] = q["id"]
        keep.append(q)
    return keep, removed

def near_dups(data):
    """近义重复报告（编辑距离/序列相似度，长度差≤2 的题干间比较；仅报告不删除）。"""
    from difflib import SequenceMatcher
    by_len = defaultdict(list)
    for q in data:
        by_len[len(_norm(q.get("stem")))].append(q)
    near = []
    for length, bucket in by_len.items():
        for other_len in (length, length + 1, length + 2):
            if other_len not in by_len or other_len == length:
                continue
            for q in bucket:
                for r in by_len[other_len]:
                    if q["id"] >= r["id"]:
                        continue
                    a, b = _norm(q.get("stem")), _norm(r.get("stem"))
                    if not a or not b:
                        continue
                    ratio = SequenceMatcher(None, a, b).ratio()
                    if ratio >= 0.85:
                        near.append((q["id"], r["id"], round(ratio, 2), q.get("stem")[:30]))
    # 同长度桶内比较
    for length, bucket in by_len.items():
        for i in range(len(bucket)):
            for j in range(i + 1, len(bucket)):
                a, b = _norm(bucket[i].get("stem")), _norm(bucket[j].get("stem"))
                if not a or not b:
                    continue
                ratio = SequenceMatcher(None, a, b).ratio()
                if ratio >= 0.88:
                    near.append((bucket[i]["id"], bucket[j]["id"], round(ratio, 2), bucket[i].get("stem")[:30]))
    # 去重排序，限制输出量
    seen_pairs, uniq = set(), []
    for x, y, r, s in near:
        k = tuple(sorted([x, y]))
        if k not in seen_pairs:
            seen_pairs.add(k)
            uniq.append((x, y, r, s))
    return sorted(uniq, key=lambda t: -t[2])[:50]

def check_explanation(q):
    """解析检测。返回问题类型：missing / lazy / too_short / ok。"""
    e = q.get("explanation") or ""
    e = e.strip()
    if not e:
        return "missing"
    if LAZY_RE.match(e):
        return "lazy"
    min_len = 40 if q.get("type") == "short_answer" else 20
    if len(e) < min_len:
        return "too_short"
    return "ok"

def analyze(data):
    """清洗后的统计。返回 dict。"""
    types = Counter(q.get("type") for q in data)
    pos = Counter()
    for q in data:
        if q.get("type") == "single_choice":
            opts = q.get("options") or []
            ans = q.get("answer")
            keys = [o["key"] for o in opts]
            ans_set = ans if isinstance(ans, list) else [ans]
            if ans_set and ans_set[0] in keys:
                pos[keys.index(ans_set[0])] += 1
    chapters = Counter(q.get("chapter") or "未分类" for q in data)
    zhenti = sum(
        1 for q in data
        if (q.get("source") or {}).get("kind") == "zhengtikaobian"
        or any("真题" in (t or "") for t in (q.get("tags") or []))
    )
    expl = Counter(check_explanation(q) for q in data)
    variants_cnt = sum(1 for q in data if q.get("answerVariants"))
    purpose = Counter(q.get("purpose") or "普通" for q in data)
    return {
        "total": len(data),
        "types": dict(types),
        "ans_pos": dict(sorted(pos.items())),
        "ans_pos_A_pct": round(pos.get(0, 0) / sum(pos.values()) * 100, 1) if pos else 0,
        "chapters": dict(chapters),
        "zhenti": zhenti,
        "explanation": dict(expl),
        "variants_cnt": variants_cnt,
        "purpose": dict(purpose),
    }

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    summary_rows, all_lines = [], []
    for name, path in FILES.items():
        if not os.path.exists(path):
            print(f"!! {name} 缺失: {path}")
            continue
        data = json.load(open(path, encoding="utf-8"))
        bank_id = (data[0].get("bankId") if data and "bankId" in data[0] else "") or name
        lines = [f"# {name} 清洗报告", f"来源: {os.path.relpath(path, BASE)}", ""]
        before_total = len(data)

        # 1) 选项洗牌
        shuffled, unshuffled = 0, 0
        for q in data:
            if q.get("options") and len(q["options"]) >= 2:
                q, moved = shuffle_options(q)
                if moved:
                    shuffled += 1
                else:
                    unshuffled += 1

        # 2) answerVariants 修复
        fixed_variants = 0
        for q in data:
            q, f = fix_variants(q)
            fixed_variants += f

        # 3) 完全重复去重
        data, removed = dedup(data)
        # 4) 近义重复报告
        near = near_dups(data)

        # 5) 统计
        st = analyze(data)

        # —— 写清洗版 ——
        out_json = os.path.join(OUT_DIR, f"{name}.sanitized.json")
        json.dump(data, open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

        # —— 写报告 ——
        lines += [
            f"- 原始题数: {before_total} → 清洗后: {st['total']}",
            f"- 选项洗牌: {shuffled} 题（含选项且可匹配）；未洗牌: {unshuffled} 题",
            f"- answerVariants 等价组合并: 修复 {fixed_variants} 组",
            f"- 完全重复删除: {len(removed)} 题",
            f"- 近义重复(相似度≥0.85, 报告不删除): {len(near)} 对",
            "",
            "## 题型分布", str(st["types"]),
            "## 单选答案位置分布", f"A={st['ans_pos'].get(0,0)} B={st['ans_pos'].get(1,0)} C={st['ans_pos'].get(2,0)} D={st['ans_pos'].get(3,0)} → A占比 {st['ans_pos_A_pct']}%",
            "## 章节分布",
            "、".join(f"{k}({v})" for k, v in sorted(st["chapters"].items(), key=lambda x: -x[1])),
            f"## 真题改编题数: {st['zhenti']}",
            f"## 解析质量: 缺失={st['explanation'].get('missing',0)} 占位={st['explanation'].get('lazy',0)} 过短={st['explanation'].get('too_short',0)} 正常={st['explanation'].get('ok',0)}",
            f"## purpose 分布: {st['purpose']}",
            f"## 含 answerVariants 题数: {st['variants_cnt']}",
        ]
        if removed:
            lines += ["", "## 删除的完全重复题（保留第一条）"]
            lines += [f"- 删除 {d} ← 保留 {k}" for d, k in removed[:30]]
        if near:
            lines += ["", "## 近义重复候选（需人工确认）"]
            lines += [f"- {x} ≈ {y} ({r}) {s}" for x, y, r, s in near[:20]]
        lines += ["", f"清洗版: {os.path.relpath(out_json, BASE)}", ""]
        report = "\n".join(lines)
        out_md = os.path.join(OUT_DIR, f"report_{name}.md")
        open(out_md, "w", encoding="utf-8").write(report)
        all_lines.append(report)
        summary_rows.append({
            "bank": name, "before": before_total, "after": st["total"],
            "shuffled": shuffled, "variants_fixed": fixed_variants,
            "dup_removed": len(removed), "near": len(near),
            "A_pct": st["ans_pos_A_pct"],
            "expl_missing": st["explanation"].get("missing", 0),
            "expl_lazy": st["explanation"].get("lazy", 0),
            "expl_short": st["explanation"].get("too_short", 0),
        })
        print(f"✓ {name}: {before_total}→{st['total']} | 洗牌{shuffled} | 变体修复{fixed_variants} | 去重{len(removed)} | A占比{st['ans_pos_A_pct']}% | 解析缺失{st['explanation'].get('missing',0)}")

    # —— 汇总 ——
    summ = ["# P0 清洗汇总", "", "| bank | 题数(前→后) | 洗牌 | 变体修复 | 删重 | 近义 | A占比 | 解析缺/占/短 |", "|---|---|---|---|---|---|---|---|---|"]
    for r in summary_rows:
        summ.append(f"| {r['bank']} | {r['before']}→{r['after']} | {r['shuffled']} | {r['variants_fixed']} | {r['dup_removed']} | {r['near']} | {r['A_pct']}% | {r['expl_missing']}/{r['expl_lazy']}/{r['expl_short']} |")
    open(os.path.join(OUT_DIR, "summary.md"), "w", encoding="utf-8").write("\n".join(summ))
    print("\n完成。输出: out/sanitized/  (清洗版 + report_*.md + summary.md)")

if __name__ == "__main__":
    main()
