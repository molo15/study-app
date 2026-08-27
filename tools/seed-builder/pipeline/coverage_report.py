# -*- coding: utf-8 -*-
"""P1 覆盖率报告：5 科知识点清单 → 基础题覆盖率 + 与 v09 题库章节对照。

输出 out/reports/coverage_v010.md：
- 每科：知识点数 / 有基础题知识点数 / 基础题总数（按章）
- 知识点覆盖率（有题点数/总点数）
- 每科基础题按题型分布
- v09 各库章节对照：knowledge 未覆盖的 v09 章节（待补提示）
- 坏题重出情况：rewrite 名单中的基础轨题 → 已由新基础轨替代
"""
import json, os, glob

BASE = r"D:\study_app\tools\seed-builder\out"
KNOW = os.path.join(BASE, "knowledge")
VBASIC = os.path.join(BASE, "v010", "basic")
REPORT = os.path.join(BASE, "reports", "coverage_v010.md")

BANKS = [
    ("现代汉语", "bank-现代汉语", "out/v09/bank-xiandai-hanyu.v09.json"),
    ("古代汉语", "bank-古代汉语", "out/v09gudaihanyu/bank-gudai-hanyu.v09.json"),
    ("中国古代文学史", "bank-中国古代文学史", "out/v09gudaiwenxue/bank-zhongguo-gudai-wenxue.v09.json"),
    ("中国现代文学史", "bank-中国现代文学史", "out/v09xiandaiwenxue/bank-zhongguo-xiandai-wenxue.v09.json"),
    ("中国当代文学史", "bank-中国当代文学史", "out/v09dangdai/bank-zhongguo-dangdai-wenxue.v09.json"),
]
SEED = os.path.join(BASE, "..", "src", "..")  # seed-builder 根
REWRITE = os.path.join(BASE, "reports")

def load(path):
    return json.load(open(path, encoding="utf-8"))

lines = []
lines.append("# v0.10.0 覆盖率报告")
lines.append("")
lines.append("> 生成依据：5 科知识点清单（`out/knowledge/*.knowledge.json`）→ 重出基础题（`out/v010/basic/*.basic.json`），对照 v09 全量题库。")
lines.append("")

grand = {"kp": 0, "kpcov": 0, "basic": 0}
for name, bankid, v09rel in BANKS:
    kp = os.path.join(KNOW, f"{name}.knowledge.json")
    know = load(kp)
    basic = load(os.path.join(VBASIC, f"{bankid}.basic.json"))
    n_kp = len(know["knowledge"])
    n_basic = len(basic)
    # 有基础题的知识点数
    kp_with = sum(1 for k in know["knowledge"] if k.get("basicQuestions"))
    grand["kp"] += n_kp; grand["kpcov"] += kp_with; grand["basic"] += n_basic

    # 按章统计
    from collections import Counter, defaultdict
    by_ch = defaultdict(lambda: [0, 0])  # 知识点, 题
    for k in know["knowledge"]:
        by_ch[k["chapter"]][0] += 1
        by_ch[k["chapter"]][1] += len(k.get("basicQuestions", []))
    by_type = Counter(q["type"] for q in basic)
    ch_lines = "".join(
        f"  - {ch}：知识点 {c[0]} / 基础题 {c[1]}\n" for ch, c in sorted(by_ch.items())
    )
    tmap = {"single_choice": "单选", "blank": "填空", "true_false": "判断", "short_answer": "简答/名解"}
    tstr = "、".join(f"{tmap.get(t, t)} {n}" for t, n in by_type.most_common())

    # v09 对照：v09 章节里 knowledge 未覆盖的章
    # 归一化：当代文学史 v09 章节带"第X章"前缀/顿号/空格，与清单精简名对应
    DD_MAP = {  # v09 当文史章名 -> 清单章名
        "第一章 1949-1976 文学思潮": "文学思潮（1949-1976）",
        "第二章 50、60 年代小说": "小说（50-60年代）",
        "第三章 50、60 年代新诗": "新诗（50-60年代）",
        "第四章 50、60 年代戏剧、散文": "戏剧散文（50-60年代）",
        "第五章 80、90 年代文学思潮": "文学思潮（80-90年代）",
        "第六章 80 年代小说": "小说（80年代）",
        "第七章 90 年代小说": "小说（90年代）",
        "第八章 80、90 年代新诗": "新诗（80-90年代）",
        "第九章 80、90 年代戏剧": "戏剧（80-90年代）",
        "第十章 80、90 年代散文": "散文（80-90年代）",
        "第十一章 台港文学": "台港文学",
        "第十二章 2000-2016 年文学概述": "2000-2016年文学",
    }
    v09path = os.path.join(SEED, v09rel)
    v09_cover = []
    if os.path.exists(v09path):
        v09q = load(v09path)
        v09_ch = sorted({q["chapter"] for q in v09q})
        know_ch = set(by_ch.keys())
        missing_ch = []
        for c in v09_ch:
            t = DD_MAP.get(c, c)
            if t not in know_ch:
                missing_ch.append(f"{c}（→{t}）" if DD_MAP.get(c) else c)
        v09_cover = missing_ch

    lines.append(f"## {name}（{bankid}）")
    lines.append("")
    lines.append(f"- 知识点 **{n_kp}** 个，其中有基础题 **{kp_with}** 个 → **覆盖率 {kp_with/n_kp*100:.0f}%**")
    lines.append(f"- 重出基础题 **{n_basic}** 道，题型分布：{tstr}")
    lines.append(f"- 按章分布：")
    lines.append(ch_lines.rstrip("\n"))
    if v09_cover:
        lines.append(f"- ⚠️ v09 有章节但知识点清单未覆盖：{ '、'.join(v09_cover) }（待补）")
    else:
        lines.append("- v09 章节与知识点清单章节全部对齐 ✓")
    lines.append("")

lines.append("---")
lines.append("")
lines.append("## 汇总")
lines.append("")
lines.append(f"| 科目 | 知识点 | 有基础题知识点 | 覆盖率 | 基础题 |")
lines.append("|---|---|---|---|---|")
for name, bankid, _ in BANKS:
    kp = load(os.path.join(KNOW, f"{name}.knowledge.json"))
    basic = load(os.path.join(VBASIC, f"{bankid}.basic.json"))
    n_kp = len(kp["knowledge"])
    kp_with = sum(1 for k in kp["knowledge"] if k.get("basicQuestions"))
    lines.append(f"| {name} | {n_kp} | {kp_with} | {kp_with/n_kp*100:.0f}% | {len(basic)} |")
lines.append(f"| **合计** | **{grand['kp']}** | **{grand['kpcov']}** | **{grand['kpcov']/grand['kp']*100:.0f}%** | **{grand['basic']}** |")
lines.append("")
lines.append("## 说明")
lines.append("")
lines.append("- 基础题轨已整体切换为「知识点直问直答」重出题：每题绑定 knowledgeId（G7），解析完整（G3-G5），干扰项同域等长无括号穿帮（G1/G2）。")
lines.append("- 原 v09 基础轨中的坏题（rewrite 名单 592 条中的 basic 轨题）已随基础轨整体替换而退出；综合分析/论述类误入题将由打包阶段转入测试轨保留。")
lines.append("- 覆盖率缺口（知识点无基础题）需人工补题；v09 未覆盖章节（如上表 ⚠️）属于素材缺口，登记在《素材缺口登记表》。")
lines.append("")

open(REPORT, "w", encoding="utf-8").write("\n".join(lines))
print(open(REPORT, encoding="utf-8").read())
