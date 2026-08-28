# -*- coding: utf-8 -*-
"""生成 v0.11.0 题库报告"""
import io, sys, json
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

OUT = r"D:\study_app\tools\seed-builder\out\knowledge"
banks = {
    "现代汉语": "bank-xiandai-hanyu",
    "古代汉语": "bank-gudai-hanyu",
    "中国古代文学史": "bank-zhongguo-gudai-wenxue",
    "中国现代文学史": "bank-zhongguo-xiandai-wenxue",
    "中国当代文学史": "bank-zhongguo-dangdai-wenxue",
}

lines = []
lines.append("# 考研刷题 App 题库报告（v0.11.0）\n")
lines.append("> 生成时间：2026-08-28 ｜ 本轮完成 5 科知识点重拆（修稀疏章节 + 全科审查 + 历史错题修复）\n")

# 汇总表
rows = []
for name, bank in banks.items():
    d = json.load(open(f"{OUT}\\{name}.knowledge.json", encoding="utf-8"))
    ks = d["knowledge"]
    n_kp = len(ks)
    n_chap = len(set(k["chapter"] for k in ks))
    n_q = sum(len(k.get("basicQuestions", [])) for k in ks)
    tc = sum(1 for k in ks for q in k.get("basicQuestions", []) if q["type"] == "choice")
    tb = sum(1 for k in ks for q in k.get("basicQuestions", []) if q["type"] == "blank")
    rows.append((name, n_kp, n_chap, n_q, tc, tb))

lines.append("## 一、总览\n")
lines.append("| 科目 | 知识点数 | 章节数 | 基础题数 | 选择题 | 填空题 |")
lines.append("|---|---|---|---|---|---|")
tot = [0, 0, 0, 0, 0]
for r in rows:
    lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |")
    for i in range(5):
        tot[i] += r[i + 1]
lines.append(f"| **合计** | **{tot[0]}** | **{tot[1]}** | **{tot[2]}** | **{tot[3]}** | **{tot[4]}** |\n")

# 分科分章明细
lines.append("## 二、分科分章明细\n")
for name, bank in banks.items():
    d = json.load(open(f"{OUT}\\{name}.knowledge.json", encoding="utf-8"))
    ks = d["knowledge"]
    by_chap = defaultdict(list)
    for k in ks:
        by_chap[k["chapter"]].append(k)
    lines.append(f"### {name}\n")
    lines.append("| 章节 | 知识点数 | 基础题数 |")
    lines.append("|---|---|---|")
    for ch in sorted(by_chap):
        kps = by_chap[ch]
        nq = sum(len(k.get("basicQuestions", [])) for k in kps)
        lines.append(f"| {ch} | {len(kps)} | {nq} |")
    lines.append("")

# 每知识点题数分布
lines.append("## 三、知识点题量分布（1题/2题/3题/4题及以上）\n")
lines.append("| 科目 | 1题点 | 2题点 | 3题点 | ≥4题点 |")
lines.append("|---|---|---|---|---|")
for name, bank in banks.items():
    d = json.load(open(f"{OUT}\\{name}.knowledge.json", encoding="utf-8"))
    cnt = Counter(len(k.get("basicQuestions", [])) for k in d["knowledge"])
    lines.append(f"| {name} | {cnt.get(1,0)} | {cnt.get(2,0)} | {cnt.get(3,0)} | {sum(v for k,v in cnt.items() if k>=4)} |")
lines.append("")

# 本轮重拆内容
lines.append("## 四、本轮重拆内容一览\n")
lines.append("| 科目 | 章节 | 重拆前 | 重拆后 | 处理 |")
lines.append("|---|---|---|---|---|")
rb = [
    ("古代汉语", "修辞", "3点/7题", "10点/25题", "拉思源素材重拆"),
    ("古代汉语", "古书的标点", "3点/4题", "4点/9题", "重拆补充"),
    ("古代汉语", "古书的文体", "5点/10题", "9点/18题", "重拆补充"),
    ("古代汉语", "训诂", "5点/10题", "10点/22题", "重拆补充"),
    ("现代汉语", "标点符号", "4点/10题", "6点/16题", "拆细聚焦"),
    ("现代文学史", "市民通俗小说（一）", "2点/5题", "4点/10题", "重拆补充"),
    ("现代文学史", "市民通俗小说（二）", "1点/0题", "5点/10题", "素材重做"),
    ("现代文学史", "散文（三）", "3点/10题", "4点/11题", "补充总述"),
    ("当代文学史", "新诗（50-60年代）", "3点/6题", "5点/13题", "补充"),
    ("当代文学史", "台港文学", "4点/10题", "6点/15题", "补充"),
    ("当代文学史", "戏剧（80-90年代）", "4点/8题", "5点/12题", "补充"),
    ("古代文学史", "元代文学", "5点/8题", "8点/21题", "通用教材知识扩充"),
    ("古代文学史", "清代文学", "5点/6题", "8点/20题", "通用教材知识扩充"),
    ("古代文学史", "近代文学", "4点/4题", "6点/15题", "通用教材知识扩充"),
]
for r in rb:
    lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |")
lines.append("")

# 历史错题修复
lines.append("## 五、历史错题修复（打包会静默错配成首选项的问题）\n")
lines.append("- 古代汉语：修复 10 处 choice 题答案与选项文本不一致（带括号注释/措辞差异）")
lines.append("- 现代汉语：修复 1 处（绪论）+ 6 处解析过短")
lines.append("- 现代文学史：修复 8 处（作家章/戏剧/鲁迅等）")
lines.append("- 古代文学史：修复 2 处（先秦/魏晋）+ 6 处解析过短")
lines.append("- 当代文学史：0 处（全库校验通过）\n")

# 校验结论
lines.append("## 六、校验结论\n")
lines.append("- pack_v4 全 5 科：**校验异常 0**，全部部署到 `app/assets/banks/`（v0.11.0，移除 v0.10.0）")
lines.append("- verify_v011 模拟 App 解析：**总校验异常 0**，choice 答案→选项映射全部正确\n")
lines.append("> 备注：古代文学史元/清/近代三章在思源笔记中无对应素材文档，本轮依据通行古代文学史教材常识（考研标准考点）扩充，如需回退可用 `out/knowledge/backup/` 下备份。\n")

path = r"D:\study_app\tools\seed-builder\out\reports\题库报告_v011.md"
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("报告已生成:", path)
print()
print("\n".join(lines[:30]))
