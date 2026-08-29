# -*- coding: utf-8 -*-
"""R1 恢复旧基础题：从归档旧包提取基础题，合并当前 v0.11.0 新包（基础+测试）。

输出：out/restored/{bank}.restored.json（该库全部题）
- 旧基础题（v0.9.x 格式，answer 可能为 key 编码，R2 统一洗牌+文本重算）
- 新基础题 + 新测试题（v0.11.0，answer 已文本编码）
id 零冲突（旧 b_/m_/w_/t_... 新 kb_/q_...，全格式无交集）→ 直接拼接。
"""
import json, os, zipfile

BASE = r"D:\study_app\tools\seed-builder\out"
LEGACY = os.path.join(BASE, "legacy_banks_backup")
ASSETS = r"D:\study_app\app\assets\banks"
OUT = os.path.join(BASE, "restored")

M = {
    "bank-gudai-hanyu": ("bank-gudai-hanyu-v0.9.0.zip.bak4", "bank-gudai-hanyu-v0.11.0.zip"),
    "bank-xiandai-hanyu": ("bank-xiandai-hanyu-v0.9.0.zip.bak4", "bank-xiandai-hanyu-v0.11.0.zip"),
    "bank-zhongguo-dangdai-wenxue": ("bank-zhongguo-dangdai-wenxue-v0.9.0.zip.bak4", "bank-zhongguo-dangdai-wenxue-v0.11.0.zip"),
    "bank-zhongguo-gudai-wenxue": ("bank-zhongguo-gudai-wenxue-v0.9.0.zip.bak3", "bank-zhongguo-gudai-wenxue-v0.11.0.zip"),
    "bank-zhongguo-xiandai-wenxue": ("bank-zhongguo-xiandai-wenxue-v0.9.0.zip.bak4", "bank-zhongguo-xiandai-wenxue-v0.11.0.zip"),
}

def read_questions(zp, prefix_filter=None):
    """读取包内题目列表。prefix_filter: '基础'/'测试'/None(全部)"""
    z = zipfile.ZipFile(zp)
    out = []
    for f in z.namelist():
        if not f.startswith("questions/") or not f.endswith(".json"):
            continue
        if prefix_filter is not None and prefix_filter not in f:
            continue
        out.extend(json.loads(z.read(f).decode("utf-8")))
    return out

def main():
    os.makedirs(OUT, exist_ok=True)
    total_old_basic = total_new_basic = total_new_test = 0
    report = []
    for bank, (old_f, new_f) in M.items():
        old_basic = read_questions(os.path.join(LEGACY, old_f), "基础")
        new_basic = read_questions(os.path.join(ASSETS, new_f), "基础")
        new_test = read_questions(os.path.join(ASSETS, new_f), "测试")
        merged = old_basic + new_basic + new_test
        # 去重（id 零冲突，理论无重复，保险）
        seen = set()
        dedup = []
        for q in merged:
            if q["id"] in seen:
                continue
            seen.add(q["id"])
            dedup.append(q)
        out_p = os.path.join(OUT, f"{bank}.restored.json")
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(dedup, f, ensure_ascii=False, indent=1)
        total_old_basic += len(old_basic)
        total_new_basic += len(new_basic)
        total_new_test += len(new_test)
        report.append((bank, len(old_basic), len(new_basic), len(new_test), len(dedup)))
        print(f"{bank}: 旧基础 {len(old_basic)} + 新基础 {len(new_basic)} + 新测试 {len(new_test)} = 合并 {len(dedup)}")
    print(f"\n合计: 旧基础 {total_old_basic} + 新基础 {total_new_basic} + 新测试 {total_new_test} = {total_old_basic+total_new_basic+total_new_test}")
    # 报告
    lines = ["# R1 恢复旧基础题报告", "", "| 题库 | 旧基础 | 新基础 | 新测试 | 合并 |", "|---|---|---|---|---|"]
    for bank, ob, nb, nt, dd in report:
        lines.append(f"| {bank} | {ob} | {nb} | {nt} | {dd} |")
    lines.append(f"| **合计** | **{total_old_basic}** | **{total_new_basic}** | **{total_new_test}** | **{total_old_basic+total_new_basic+total_new_test}** |")
    rp = os.path.join(BASE, "reports", "restore_r1.md")
    with open(rp, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"报告 → {rp}")

if __name__ == "__main__":
    main()
