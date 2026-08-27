# -*- coding: utf-8 -*-
"""Generate the human-readable report markdown for 语法 chapter."""
import json, io

with io.open("D:/study_app/tools/seed-builder/out/v09/existing/语法.json", "r", encoding="utf-8") as f:
    Q = {q["id"]: q for q in json.load(f)}
with io.open("D:/study_app/tools/seed-builder/out/v09/dispositions/语法.json", "r", encoding="utf-8") as f:
    D = json.load(f)
gaps = D.pop("_gaps")

def short_stem(stem, n=38):
    s = stem.replace("\n", " ").strip()
    return s if len(s) <= n else s[:n] + "…"

def type_cn(t):
    return {"single_choice": "单选", "blank": "填空", "multi_choice": "多选",
            "true_false": "判断", "short_answer": "简答"}.get(t, t)

order = ["keep_test", "keep_basic", "rewrite", "delete"]
lines = []
lines.append("# 语法章存量题审查报告")
lines.append("")
lines.append("## 处置汇总")
lines.append("")
from collections import Counter
cnt = Counter(v["action"] for v in D.values())
for a in order:
    lines.append("- **%s**：%d 题" % (a, cnt.get(a, 0)))
lines.append("")
lines.append("存量共 **249** 题，其中保留基础题 %d、测试题 %d、改写 %d，删除 %d，最终保留约 **%d** 题。" % (
    cnt.get("keep_basic", 0), cnt.get("keep_test", 0), cnt.get("rewrite", 0), cnt.get("delete", 0),
    cnt.get("keep_basic", 0) + cnt.get("keep_test", 0) + cnt.get("rewrite", 0)))
lines.append("")
lines.append("删除命中判定规则分布：")
lines.append("- 规则a（模板簇同壳题）：词类分析壳 9、短语结构壳 12、句型识别壳 10、复句第一层 2、没有语法错误壳 2、改错壳 2、病句换例 2、填空壳同考点 2 等。")
lines.append("- 规则b（镜像/正反互换）：w_000396（的「不属于」结构助词）↔ z_000142（真题），保留真题方。")
lines.append("- 规则c（跨来源同考点复制）：同考点在 z_真题/k_课后题/w_试题库 多来源重复，保留最优（真题优先）。")
lines.append("- 规则d（偏怪冷门）：w_000415 方位短语判断等。")
lines.append("- 规则e（题干硬伤）：q_000005、z_000147（改改写处理）。")
lines.append("")
lines.append("> 注：任务书预判的「「X」是（ ）填空壳 34 题」对应 w_000301–330 填空题系列。该系列虽同源同壳，但每题测的是不同知识点（词类依据/助词分类/补语七类/疑问句四类等），并非「同壳换词考同一考点」，故未整壳压到 1–2 题，而是删除其中与真题/课后题/多选题重复的 13 题（按规则c），保留 17 题作基础题——既消除重复又保住基础填空池。")
lines.append("")
lines.append("## 逐题处置")
lines.append("")
lines.append("| id | type | stem摘要 | 处置 | 理由 |")
lines.append("|---|---|---|---|---|")

def sort_key(qid):
    # keep stable ordering: q_ / z_ / k_ / w_ numeric
    prefix, num = qid.split(":")[1].split("_")
    return (prefix, int(num))

for qid in sorted(D.keys(), key=sort_key):
    q = Q[qid]
    v = D[qid]
    act = v["action"]
    act_cn = {"keep_basic": "保留基础", "keep_test": "保留测试", "delete": "删除", "rewrite": "改写"}[act]
    lines.append("| %s | %s | %s | %s | %s |" % (
        qid, type_cn(q["type"]), short_stem(q["stem"]), act_cn, v["reason"]))

lines.append("")
lines.append("## 覆盖缺口")
lines.append("")
lines.append("对照素材（374 条笔记块）中带 ★ 及真题标注的高频考点，下列考点在存量题中完全没有覆盖：")
lines.append("")
for i, g in enumerate(gaps, 1):
    lines.append("%d. **%s**：%s" % (i, g["考点"], g["素材证据"]))
lines.append("")
lines.append("## 等价答案建议（answerVariants）")
lines.append("")
lines.append("填空题/简答题/判断题尤其需要可等价表述答案。已随 dispositions JSON 下发的主要异名关系：")
lines.append("")
lines.append("- **兼语短语 = 兼语式 = 动宾短语与主谓短语套合**（z_000139、w_000311）")
lines.append("- **连谓句 = 连动句；连谓短语 = 连动短语**（z_000147、w_000318、w_000363）")
lines.append("- **把字句 = 处置式**（w_000366、q_000026）")
lines.append("- **被字句 = 受事主语句；施事 = 施动者**（w_000329、q_000073、k_000120）")
lines.append("- **中补短语 = 述补短语**（w_000411、w_000327）")
lines.append("- **趋向补语 = 趋向动词作补语**（q_000005）")
lines.append("- **时地补语 = 时间处所补语 = 介词短语补语**（w_000327）")
lines.append("- **可能补语 = 能性补语**（z_000158）")
lines.append("- **正反问 = 反复问**（w_000322、w_000393）")
lines.append("- **紧缩句 = 紧缩复句**（w_000369）")
lines.append("- **复说语 = 复指成分 = 称代式复说**（w_000355）")
lines.append("- **插说语 = 插入语 = 独立成分**（w_000356）")
lines.append("- **体词性短语 = 名词性短语；谓词性短语 = 动词性/形容词性短语**（w_000381、w_000349）")
lines.append("- **加词 = 区别词 + 副词**（w_000375）")
lines.append("- **多义短语 = 歧义短语**（q_000064、w_000420、z_000166）")
lines.append("- **「的」字短语 = 的字结构**（w_000417）")
lines.append("- **语调 = 句调**（z_000149）")
lines.append("- **条件复句（只有…才…）= 必要条件复句**（z_000140）")
lines.append("- **得 = 结构助词/补语标记**（k_000123）")
lines.append("")
lines.append("## 改写建议明细")
lines.append("")
lines.append("| id | 现题干 | 问题 | 改写建议 |")
lines.append("|---|---|---|---|")
lines.append("| %s | %s | 引文「他跳下了车」中没有「下来」（只有趋向补语「下」），引文与所问词不符，自相矛盾（规则e） | 引文改为「他从车上跳下来了」或「他跳下车来」，答案 C 趋向补语不变 |" % ("bank-xiandai-hanyu:q_000005", short_stem(Q["bank-xiandai-hanyu:q_000005"]["stem"], 40)))
lines.append("| %s | %s | 答案标 A 同位短语，解析却判连谓短语，且选项无连谓项，自相矛盾（规则e） | 选项加入「连谓短语」项并定其为正确答案，或重设 A 连谓 B 偏正 C 主谓 D 动宾 |" % ("bank-xiandai-hanyu:z_000147", short_stem(Q["bank-xiandai-hanyu:z_000147"]["stem"], 40)))

report = "\n".join(lines)
out_path = "D:/study_app/tools/seed-builder/out/v09/reports/语法.md"
with io.open(out_path, "w", encoding="utf-8") as f:
    f.write(report)
print("written:", out_path, "lines:", len(lines))
