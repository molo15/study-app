# -*- coding: utf-8 -*-
"""P1a: 合并解析补丁到清洗版。核对覆盖、遗漏，输出合并版 + 门禁复查。"""
import json, os, re, glob

SAN = r"D:\study_app\tools\seed-builder\out\sanitized"
LAZY_RE = re.compile(r"^(见原文|见教材|见参考|参考答案见|参考解析|同解析|略[。]?|见上|见下|见解析|。?)$")

def problem_type(q):
    e = (q.get("explanation") or "").strip()
    if not e:
        return "missing"
    if LAZY_RE.match(e):
        return "lazy"
    min_len = 40 if q.get("type") == "short_answer" else 20
    if len(e) < min_len:
        return "too_short"
    return None

def main():
    # 收集所有补丁
    patches = {}
    for pf in glob.glob(os.path.join(SAN, "patch_explanation_*.json")):
        p = json.load(open(pf, encoding="utf-8"))
        patches.update(p)
        print(f"补丁: {os.path.basename(pf)} -> {len(p)} 条")
    print(f"补丁合计: {len(patches)} 条")

    # 对每个清洗版合并
    totals = {"missing": 0, "lazy": 0, "too_short": 0, "ok": 0}
    total_patched = 0
    for bank_file in glob.glob(os.path.join(SAN, "*.sanitized.json")):
        bank = os.path.basename(bank_file).replace(".sanitized.json", "")
        data = json.load(open(bank_file, encoding="utf-8"))
        patched = 0
        missing_ids = []
        id_set = {q["id"] for q in data}
        for q in data:
            if q["id"] in patches:
                q["explanation"] = patches[q["id"]]
                patched += 1
        # 未匹配的补丁 id（补丁写了但库中没有）
        for pid in patches:
            if pid not in id_set:
                missing_ids.append(pid)
        # 统计
        from collections import Counter
        cnt = Counter(problem_type(q) for q in data)
        print(f"\n{bank}: 打了 {patched} 条补丁; 解析分布 {dict(cnt)}")
        for k in totals:
            totals[k] += cnt.get(k, 0)
        if missing_ids:
            print(f"  ⚠ 补丁中 {len(missing_ids)} 个 id 未匹配: {missing_ids[:5]}")
        # 写回（仅当打了补丁）
        if patched:
            json.dump(data, open(bank_file, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            total_patched += patched

    print(f"\n=== 汇总 === 共打补丁 {total_patched} 条; 剩余解析问题: missing={totals['missing']} lazy={totals['lazy']} too_short={totals['too_short']} ok={totals['ok']}")

if __name__ == "__main__":
    main()
