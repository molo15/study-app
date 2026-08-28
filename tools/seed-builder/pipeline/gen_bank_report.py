# -*- coding: utf-8 -*-
"""题库总报告：统计 5 库章节/题量/题型/知识点覆盖，输出 docs/题库总报告-v0.12.0.md"""
import json, os
from collections import Counter, defaultdict

BASE = r"D:\study_app\tools\seed-builder"
OUT = os.path.join(BASE, "out")
DOC = r"D:\study_app\docs"

BANKS = [
    ("考研 · 古代汉语", "bank-gudai-hanyu", "out/refined/bank-gudai-hanyu.v012.json", "out/knowledge/古代汉语.knowledge.json", 13, "~1000"),
    ("考研 · 现代汉语", "bank-xiandai-hanyu", "out/refined/bank-xiandai-hanyu.refined2.json", "out/knowledge/现代汉语.knowledge.json", 7, "~1100 定稿"),
    ("考研 · 中国古代文学史", "bank-zhongguo-gudai-wenxue", "out/refined/bank-zhongguo-gudai-wenxue.v012.json", "out/knowledge/中国古代文学史.knowledge.json", 9, "~1000"),
    ("考研 · 中国现代文学史", "bank-zhongguo-xiandai-wenxue", "out/refined/bank-zhongguo-xiandai-wenxue.quota.json", "out/knowledge/中国现代文学史.knowledge.json", 27, "~1000 定稿"),
    ("考研 · 中国当代文学史", "bank-zhongguo-dangdai-wenxue", "out/refined/bank-zhongguo-dangdai-wenxue.refined2.json", "out/knowledge/中国当代文学史.knowledge.json", 12, "~800"),
]

TYPE_CN = {"single_choice": "单选", "multi_choice": "多选", "true_false": "判断", "blank": "填空", "short_answer": "简答"}
PURPOSE_CN = {"basic": "基础", "test": "测试"}

def main():
    lines = ["# 考研题库总报告（v0.12.0）", ""]
    lines.append("> 生成时间：2026-08-27；数据源：`tools/seed-builder/out/refined/` 最终产物。")
    lines.append("")
    lines.append("## 一、总览")
    lines.append("")
    lines.append("| 科目 | 总题数 | 基础轨 | 测试轨 | 题型数(选/填/判/简) | 章节 | 知识点 | 目标 | 状态 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    grand = 0
    for name, bank, rel, krel, nch, target in BANKS:
        qs = json.load(open(os.path.join(BASE, rel), encoding="utf-8"))
        kp = json.load(open(os.path.join(BASE, krel), encoding="utf-8"))
        kps = kp.get("knowledge", kp.get("nodes", []))
        basic = [q for q in qs if q.get("purpose") == "basic"]
        test = [q for q in qs if q.get("purpose") == "test"]
        tc = Counter(q["type"] for q in qs)
        tstr = f"{tc.get('single_choice',0)+tc.get('multi_choice',0)}/{tc.get('blank',0)}/{tc.get('true_false',0)}/{tc.get('short_answer',0)}"
        kp_covered = len({q.get("knowledgeId") for q in basic if q.get("knowledgeId")})
        grand += len(qs)
        if "定稿" in target:
            status = "✅ 定稿"
        else:
            status = "✅" if abs(len(qs) - int(target.strip("~"))) <= 60 else "○"
        lines.append(f"| {name} | **{len(qs)}** | {len(basic)} | {len(test)} | {tstr} | {nch} | {len(kps)}({kp_covered}有题) | {target} | {status} |")
    lines.append(f"| **合计** | **{grand}** | | | | | | | |")
    lines.append("")

    # 章节明细
    lines.append("## 二、章节分布明细")
    lines.append("")
    for name, bank, rel, krel, nch, target in BANKS:
        qs = json.load(open(os.path.join(BASE, rel), encoding="utf-8"))
        by_ch = Counter(q["chapter"] for q in qs)
        by_ch_basic = Counter(q["chapter"] for q in qs if q.get("purpose") == "basic")
        lines.append(f"### {name}")
        lines.append("")
        lines.append("| 章节 | 基础 | 测试 | 合计 |")
        lines.append("|---|---|---|---|")
        for ch, n in sorted(by_ch.items(), key=lambda x: -x[1]):
            lines.append(f"| {ch} | {by_ch_basic.get(ch,0)} | {n - by_ch_basic.get(ch,0)} | {n} |")
        lines.append("")

    # 题型分布
    lines.append("## 三、题型分布")
    lines.append("")
    lines.append("| 科目 | 单选 | 多选 | 填空 | 判断 | 简答 | 合计 |")
    lines.append("|---|---|---|---|---|---|---|")
    for name, bank, rel, krel, nch, target in BANKS:
        qs = json.load(open(os.path.join(BASE, rel), encoding="utf-8"))
        tc = Counter(q["type"] for q in qs)
        lines.append(f"| {name} | {tc.get('single_choice',0)} | {tc.get('multi_choice',0)} | {tc.get('blank',0)} | {tc.get('true_false',0)} | {tc.get('short_answer',0)} | {len(qs)} |")
    lines.append("")

    # 知识点覆盖
    lines.append("## 四、知识点覆盖")
    lines.append("")
    lines.append("| 科目 | 知识点总数 | 有基础题的知识点 | 覆盖率 | 每点平均基础题 |")
    lines.append("|---|---|---|---|---|")
    for name, bank, rel, krel, nch, target in BANKS:
        qs = json.load(open(os.path.join(BASE, rel), encoding="utf-8"))
        kp = json.load(open(os.path.join(BASE, krel), encoding="utf-8"))
        kps = kp.get("knowledge", kp.get("nodes", []))
        basic = [q for q in qs if q.get("purpose") == "basic" and q.get("knowledgeId")]
        by_kid = Counter(q["knowledgeId"] for q in basic)
        covered = len(by_kid)
        avg = len(basic) / max(covered, 1)
        lines.append(f"| {name} | {len(kps)} | {covered} | {covered/len(kps)*100:.0f}% | {avg:.1f} |")
    lines.append("")

    lines.append("## 五、本轮变更说明")
    lines.append("")
    lines.append("1. **R1 恢复旧题**：自 `out/legacy_banks_backup` 恢复 4025 道旧基础题，与既有题合并（旧基础轨与新版零冲突）。")
    lines.append("2. **R2 选项洗牌**：全部选择题洗牌，答案位置均匀分布，杜绝“连着选 A”。")
    lines.append("3. **R3a 完全去重**：删除完全重复题干 34 题。")
    lines.append("4. **R3b 变式删除**：同章节高相似度变式仅保留代表题，删 638 题。")
    lines.append("5. **R3c 现文史配额**：压缩旧客观题至目标配额，保留知识点骨架/简答/模拟卷引用题。")
    lines.append("6. **古文史扩充**：袁行霈题库 205 道填空解析后转为基础题（145 题入库），并按知识点补元/清/近代三章知识节点（62→76）。")
    lines.append("7. **古代汉语扩充**：依据《古代汉语考研经典笔记》补充 47 道基础题（词汇/文字/音韵/工具书），并全量补 knowledgeId。")
    lines.append("8. **knowledgeId 全覆盖**：5 库基础题全部挂接知识点（现汉 918 / 当代 536 / 现文史 229 / 古汉 658 / 古文史 468 题补打标）。")
    lines.append("9. **打包 v0.12.0**：formatVersion=4，含知识点树+章节概览+分组+模拟卷，已部署 `app/assets/banks/` 并移除 v0.10.0。")
    lines.append("")

    path = os.path.join(DOC, "题库总报告-v0.12.0.md")
    os.makedirs(DOC, exist_ok=True)
    open(path, "w", encoding="utf-8").write("\n".join(lines))
    print("报告 →", path)
    print("总题数", grand)

if __name__ == "__main__":
    main()
