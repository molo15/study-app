# -*- coding: utf-8 -*-
"""v0.13.0 打包：formatVersion=4 —— 基于 v0.11.0 数据源（knowledge + v010 basic + v09 保留轨），
古代文学史新增 110 道名词解释转基础题。清理过时 v0.12.0（旧重拆 refined 数据，App 按最高版本号误选）。
"""
import json, os, random, re, shutil, zipfile
from collections import Counter

BASE = r"D:\study_app\tools\seed-builder"
OUT_DIR = os.path.join(BASE, "out", "packages", "v013")
ASSETS = r"D:\study_app\app\assets\banks"
KNOW = os.path.join(BASE, "out", "knowledge")
VBASIC = os.path.join(BASE, "out", "v010", "basic")
PAPERS = os.path.join(BASE, "out", "papers", "papers.json")
REPORT = os.path.join(BASE, "out", "reports", "pack_report_v013.md")
VERSION = "0.13.0"

BANKS = {
    "bank-xiandai-hanyu": ("考研 · 现代汉语", "现代汉语", "out/v09/bank-xiandai-hanyu.v09.json"),
    "bank-gudai-hanyu": ("考研 · 古代汉语", "古代汉语", "out/v09gudaihanyu/bank-gudai-hanyu.v09.json"),
    "bank-zhongguo-gudai-wenxue": ("考研 · 中国古代文学史", "中国古代文学史", "out/v09gudaiwenxue/bank-zhongguo-gudai-wenxue.v09.json"),
    "bank-zhongguo-xiandai-wenxue": ("考研 · 中国现代文学史", "中国现代文学史", "out/v09xiandaiwenxue/bank-zhongguo-xiandai-wenxue.v09.json"),
    "bank-zhongguo-dangdai-wenxue": ("考研 · 中国当代文学史", "中国当代文学史", "out/v09dangdai/bank-zhongguo-dangdai-wenxue.v09.json"),
}
GROUPS = {
    "bank-xiandai-hanyu": [
        ("上编 语音与文字", ["文字", "绪论", "语音"]),
        ("下编 修辞", ["修辞"]),
        ("中编 词汇与语法", ["词汇", "语法", "标点符号"]),
    ],
    "bank-gudai-hanyu": [
        ("上编 基础知识", ["修辞", "古书的文体", "古书的标点", "工具书简介", "绪论"]),
        ("中编 语言文字学", ["文字（上）", "文字（下）", "词汇", "语法（上）", "语法（下）"]),
        ("下编 音韵训诂与格律", ["训诂", "诗词格律", "音韵"]),
    ],
    "bank-zhongguo-gudai-wenxue": [
        ("上编 先秦两汉文学", ["先秦文学", "秦汉文学"]),
        ("中编 魏晋隋唐文学", ["隋唐五代文学", "魏晋南北朝文学"]),
        ("下编 宋元明清文学", ["元代文学", "宋代文学", "明代文学", "清代文学", "近代文学"]),
    ],
    "bank-zhongguo-xiandai-wenxue": [
        ("五四时期（1917-1927）", ["小说（一）", "市民通俗小说（一）", "戏剧", "散文（一）", "文学思潮与运动（一）", "新诗（一）", "郭沫若", "鲁迅（一）"]),
        ("三十年代（1928-1937）", ["小说（二）", "巴金", "戏剧（二）", "散文（二）", "文学思潮与运动（二）", "新诗（二）", "曹禺", "沈从文", "老舍", "茅盾", "鲁迅（二）"]),
        ("四十年代（1937-1949）", ["小说（三）", "戏剧（三）", "散文（三）", "文学思潮与运动（三）", "新诗（三）", "艾青", "赵树理"]),
        ("综合专题", ["综合专题"]),
    ],
    "bank-zhongguo-dangdai-wenxue": [
        ("上编 十七年文学（1949-1976）", ["第一章 1949-1976 文学思潮", "第二章 50、60 年代小说", "第三章 50、60 年代新诗", "第四章 50、60 年代戏剧、散文"]),
        ("中编 新时期文学（1978-1999）", ["第五章 80、90 年代文学思潮", "第六章 80 年代小说", "第七章 90 年代小说", "第八章 80、90 年代新诗", "第九章 80、90 年代戏剧", "第十章 80、90 年代散文"]),
        ("下编 台港文学与世纪之交", ["第十一章 台港文学", "第十二章 2000-2016 年文学概述"]),
    ],
}
DD_MAP = {
    "文学思潮（1949-1976）": "第一章 1949-1976 文学思潮",
    "小说（50-60年代）": "第二章 50、60 年代小说",
    "新诗（50-60年代）": "第三章 50、60 年代新诗",
    "戏剧散文（50-60年代）": "第四章 50、60 年代戏剧、散文",
    "文学思潮（80-90年代）": "第五章 80、90 年代文学思潮",
    "小说（80年代）": "第六章 80 年代小说",
    "小说（90年代）": "第七章 90 年代小说",
    "新诗（80-90年代）": "第八章 80、90 年代新诗",
    "戏剧（80-90年代）": "第九章 80、90 年代戏剧",
    "散文（80-90年代）": "第十章 80、90 年代散文",
    "台港文学": "第十一章 台港文学",
    "2000-2016年文学": "第十二章 2000-2016 年文学概述",
}
PLACEHOLDER = re.compile(r"^(见原文|见教材|见参考|参考答案见|参考解析|同解析|略[。]?|见上|见下|见解析|。|…)$")

def sanitize(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name)

def norm_chapter(bank, ch):
    if bank == "bank-zhongguo-dangdai-wenxue" and ch in DD_MAP:
        return DD_MAP[ch]
    return ch

def _remap_expl_letters(expl, mapping):
    """把解析文本中的选项字母引用按旧key->新key映射改写。
    统一处理单字母断言（选X/故选X/故X不选）与整串枚举（故A、B、C项不选/不属于），
    一次 sub 完成，避免二次改写。"""
    if not expl or not mapping:
        return expl

    def remap_letters(s):
        return ''.join(mapping.get(ch, ch) for ch in s)

    def repl(m):
        pre, letters = m.group(1), m.group(2)
        return pre + remap_letters(letters)

    # 前缀（选/故选/答案…/故…）后跟字母序列，字母可带顿号分隔（A、B、C）；
    # 不匹配"A. 胆怯"式列举（点号后不带空格紧邻）
    pat = re.compile(r'(选|故选|答案(?:为|是)?|正确选项(?:为|是)?|应为|应选|故|仅|据此选|根据)\s*([ABCDEF](?:、?[ABCDEF]){0,5})(?=$|[，。；、:：\s]|项|正确|错误|对|不对|符合|不符合|有误|表述正确|表述错误|说法|不是|不|属|均|！|？)')
    return pat.sub(repl, expl)



def shuffle_options(q, rng):
    """洗牌选择题；返回洗牌后的正确项文本（v4 编码）。
    洗牌后同步改写解析文本中的选项字母引用（旧key->新key），防止解析与答案错位。"""
    t = q["type"]
    if t not in ("single_choice", "multi_choice"):
        return None
    opts = list(q["options"])
    ans = q["answer"]
    ans_keys = set(ans) if isinstance(ans, list) else {ans}
    ans_texts = [o["text"] for o in opts if o["key"] in ans_keys]
    # 洗牌前记录 旧key -> 文本
    old_texts = [o["text"] for o in opts]
    old_keys = [o["key"] for o in opts]
    rng.shuffle(opts)
    keys = "ABCDEFGHIJKLMNOP"[:len(opts)]
    new_by_text = {}
    for o, k in zip(opts, keys):
        o["key"] = k
        new_by_text[o["text"]] = k
    q["options"] = opts
    # 建立 旧key -> 新key 映射（按文本对齐）
    mapping = {}
    for oldk, txt in zip(old_keys, old_texts):
        if txt in new_by_text:
            mapping[oldk] = new_by_text[txt]
    if mapping:
        expl = q.get("explanation")
        if expl:
            q["explanation"] = _remap_expl_letters(expl, mapping)
    # 记录正确项文本（供 v4 answer 编码）
    q["_ans_texts"] = ans_texts
    return ans_texts



def encode_answer_v4(q):
    """v4：选择题 answer 存正确项文本。"""
    t = q["type"]
    texts = q.pop("_ans_texts", None)
    if t == "single_choice":
        q["answer"] = texts[0] if texts else ""
    elif t == "multi_choice":
        q["answer"] = sorted(texts) if texts else []

def validate_basic(q, know_ids, report, bank):
    errs = []
    if q["id"] in report["ids"]:
        errs.append("id重复")
    report["ids"].add(q["id"])
    if not q["id"].startswith(bank + ":"):
        errs.append("id前缀")
    if q["type"] == "single_choice":
        opts = q["options"]
        if len(opts) != 4:
            errs.append("选项数!=4")
        if q["answer"] not in {o["text"] for o in opts}:
            errs.append("答案文本失效")
        if any(re.search(r"[（(]", o["text"]) for o in opts):
            errs.append("选项含括号")
    elif q["type"] == "multi_choice":
        texts = {o["text"] for o in q["options"]}
        if not isinstance(q["answer"], list) or not set(q["answer"]).issubset(texts):
            errs.append("多选答案失效")
    elif q["type"] == "true_false":
        if q["answer"] not in ("正确", "错误"):
            errs.append("判断答案非法")
    elif q["type"] in ("blank", "short_answer"):
        if not q["answer"]:
            errs.append("缺answer")
    expl = q.get("explanation", "")
    _expl_len = len(re.sub(r"\s+", "", expl))
    _min_len = 5 if q["type"] in ("blank", "short_answer") else 20
    if not expl or _expl_len < _min_len:
        errs.append(f"解析过短({_expl_len}字)")
    if PLACEHOLDER.search(expl.strip()):
        errs.append("解析占位")
    # 解析黑名单（出题工作底稿/模板残留）
    _expl_norm = re.sub(r"\s+", "", expl)
    if re.search(r"素材块|素材n|正文块|对应素材标题|覆盖缺口|本题答案为|存量题未覆盖|本题属[于]?.{0,12}常考|即可应对同类题目|掌握其概念", _expl_norm):
        errs.append("解析含工作底稿/模板残留")
    if re.search(r"[（(](基础|变式|拓展|提升|综合|识记|理解)[）)]$", _expl_norm):
        errs.append("解析带等级标注尾巴")
    if re.match(r"^解析[:：]", _expl_norm):
        errs.append("解析冒号前缀")
    if not q.get("knowledgeId") or q["knowledgeId"] not in know_ids:
        errs.append("knowledgeId缺失/无效")
    return errs

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    papers_data = json.load(open(PAPERS, encoding="utf-8"))["papers"]
    paper_q_by_bank, paper_meta = {}, {}
    for pp in papers_data:
        paper_q_by_bank.setdefault(pp["bankId"], set()).update(pp.get("questionIds", []))
        paper_meta[pp["bankId"]] = pp

    report_lines = ["# v0.13.0（formatVersion=4）打包报告", ""]
    summary = []
    grand_basic = grand_keep = grand_kp = 0

    for bank, (name, cn, v09rel) in BANKS.items():
        rng = random.Random("v4_" + bank)
        report = {"ids": set(), "bad": []}
        know = json.load(open(os.path.join(KNOW, f"{cn}.knowledge.json"), encoding="utf-8"))
        kp_nodes = know["knowledge"]
        know_ids = {k["id"] for k in kp_nodes}
        basic = json.load(open(os.path.join(VBASIC, f"{bank}.basic.json"), encoding="utf-8"))
        v09 = json.load(open(os.path.join(BASE, v09rel), encoding="utf-8"))
        v09_by_id = {q["id"]: q for q in v09}

        # ---- 基础轨：章节归一化 + 洗牌 + v4 answer 编码 + 校验 ----
        basic_out = []
        for q in basic:
            q = dict(q)
            q["chapter"] = norm_chapter(bank, q["chapter"])
            shuffle_options(q, rng)
            encode_answer_v4(q)
            q.pop("source", None)
            basic_out.append(q)
            for e in validate_basic(q, know_ids, report, bank):
                report["bad"].append(f"{q['id']} [{e}]")

        # ---- 保留轨（v09 test + 模拟卷引用）：同样洗牌 + v4 编码 ----
        paper_ids = paper_q_by_bank.get(bank, set())
        keep_ids = {q["id"] for q in v09 if q["purpose"] == "test"} | paper_ids
        keep = [v09_by_id[i] for i in keep_ids if i in v09_by_id]
        keep_out = []
        for q in keep:
            nq = dict(q)
            nq.pop("source", None)
            shuffle_options(nq, rng)
            encode_answer_v4(nq)
            keep_out.append(nq)
            if nq["id"] in report["ids"]:
                report["bad"].append(f"{nq['id']} [id重复]")
            report["ids"].add(nq["id"])
            # 保留轨解析黑名单校验（不含 id/knowledgeId 等基础校验）
            _en = re.sub(r"\s+", "", nq.get("explanation", ""))
            if re.search(r"素材块|素材n|正文块|对应素材标题|覆盖缺口|本题答案为|存量题未覆盖|本题属[于]?.{0,12}常考|即可应对同类题目|掌握其概念", _en):
                report["bad"].append(f"{nq['id']} [保留轨解析含工作残留]")
            if re.search(r"[（(](基础|变式|拓展|提升|综合|识记|理解)[）)]$", _en):
                report["bad"].append(f"{nq['id']} [保留轨解析带等级尾巴]")
            if re.match(r"^解析[:：]", _en):
                report["bad"].append(f"{nq['id']} [保留轨解析冒号前缀]")
            _el = len(_en)
            _ml = 5 if nq["type"] in ("blank", "short_answer") else 20
            if _el and _el < _ml:
                report["bad"].append(f"{nq['id']} [保留轨解析过短({_el}字)]")

        if len(report["ids"]) != len(basic_out) + len(keep_out):
            report["bad"].append(f"id集合不一致")

        # ---- 每知识点基础题数（questionCount）----
        kp_count = Counter(q.get("knowledgeId") for q in basic_out if q.get("knowledgeId"))
        knowledge = []
        for k in kp_nodes:
            knowledge.append({
                "id": k["id"],
                "name": k["name"],
                "chapter": norm_chapter(bank, k["chapter"]),
                "parent": k.get("parent"),
                "summary": k.get("summary", ""),
                "hot": bool(k.get("hot")),
                "examRef": k.get("examRef", ""),
                "questionCount": kp_count.get(k["id"], 0),
            })

        # ---- overviews：每章知识概览 ----
        from collections import defaultdict
        by_ch_kp = defaultdict(list)
        for k in knowledge:
            by_ch_kp[k["chapter"]].append(k)
        overviews = []
        for ch in sorted(by_ch_kp):
            kps = by_ch_kp[ch]
            hot_names = [k["name"] for k in kps if k["hot"]]
            total_q = sum(k["questionCount"] for k in kps)
            sum_line = f"本章共 {len(kps)} 个知识点、{total_q} 道基础题。"
            if hot_names:
                sum_line += f"高频考点：{'、'.join(hot_names[:5])}{'等' if len(hot_names)>5 else ''}。"
            overviews.append({
                "chapter": ch,
                "knowledgeCount": len(kps),
                "questionCount": total_q,
                "summary": sum_line,
            })

        # ---- 分组 ----
        all_ch = sorted({q["chapter"] for q in basic_out + keep_out})
        chapter_groups = []
        for g, chs in GROUPS[bank]:
            keep_ch = [c for c in chs if c in all_ch]
            if keep_ch:
                chapter_groups.append({"group": g, "chapters": keep_ch})
        extra = [c for c in all_ch if not any(c in chs for _, chs in GROUPS[bank])]
        if extra:
            chapter_groups.append({"group": "其他", "chapters": extra})

        # ---- 模拟卷 ----
        mock = []
        if bank in paper_meta:
            pp = paper_meta[bank]
            mock.append({
                "id": f"{bank}:paper_01", "bankId": bank, "name": pp["name"],
                "durationMin": pp["durationMin"], "questionIds": pp["questionIds"],
            })

        manifest = {
            "formatVersion": 4,
            "bankId": bank,
            "name": name,
            "version": VERSION,
            "generatedAt": "2026-08-28T12:00:00+08:00",
            "chapters": chapter_groups,
            "questionFiles": [],
            "mockPapers": mock,
            "knowledge": knowledge,
            "overviews": overviews,
        }

        _type_order = {"single_choice": 0, "multi_choice": 1, "true_false": 2, "blank": 3, "short_answer": 4}
        by_purpose_ch = {}
        for q in basic_out:
            by_purpose_ch.setdefault(("基础", q["chapter"]), []).append(q)
        for q in keep_out:
            by_purpose_ch.setdefault(("测试", q["chapter"]), []).append(q)
        for key in by_purpose_ch:
            by_purpose_ch[key].sort(key=lambda q: _type_order.get(q["type"], 99))

        zip_path = os.path.join(OUT_DIR, f"{bank}-v{VERSION}.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for (prefix, ch) in sorted(by_purpose_ch.keys()):
                chunk = by_purpose_ch[(prefix, ch)]
                if not chunk:
                    continue
                fname = f"questions/{prefix}-{sanitize(ch)}.json"
                zf.writestr(fname, json.dumps(chunk, ensure_ascii=False, indent=1))
                manifest["questionFiles"].append(fname)
            zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=1))

        n_basic, n_keep = len(basic_out), len(keep_out)
        grand_basic += n_basic; grand_keep += n_keep; grand_kp += len(kp_nodes)
        print(f"== {bank} v{VERSION}：基础{n_basic} + 保留{n_keep}；知识点{len(kp_nodes)}；overviews{len(overviews)}")
        print(f"   校验异常 {len(report['bad'])}")
        for b in report["bad"][:8]:
            print("   !!", b)
        summary.append((bank, n_basic, n_keep, len(kp_nodes), len(report["bad"])))

        os.makedirs(ASSETS, exist_ok=True)
        dst = os.path.join(ASSETS, f"{bank}-v{VERSION}.zip")
        shutil.copyfile(zip_path, dst)
        # 移除 v0.12.0（旧重拆 refined 数据，App 按最高版本号误选）与 v0.11.0，只保留 v0.13.0
        for old in os.listdir(ASSETS):
            if old.startswith(bank + "-") and old.endswith(".zip") and ".bak" not in old and "_tmp" not in old:
                if old != f"{bank}-v{VERSION}.zip":
                    os.remove(os.path.join(ASSETS, old))
        print(f"   ✅ 已部署 {dst}（清理旧版本）")

        report_lines.append(f"## {name}（{bank}）")
        report_lines.append(f"- 基础轨 **{n_basic}**；保留轨 **{n_keep}**；知识点 **{len(kp_nodes)}**；overviews **{len(overviews)}**")
        report_lines.append(f"- 校验异常 **{len(report['bad'])}**")
        report_lines.append("")

    report_lines.append("## 汇总")
    report_lines.append("| 科目 | 基础轨 | 保留轨 | 知识点 | 校验异常 |")
    report_lines.append("|---|---|---|---|---|")
    for bank, nb, nk, nkp, bad in summary:
        report_lines.append(f"| {bank} | {nb} | {nk} | {nkp} | {bad} |")
    report_lines.append(f"| **合计** | **{grand_basic}** | **{grand_keep}** | **{grand_kp}** | |")
    report_lines.append("")
    report_lines.append("## 说明")
    report_lines.append("- formatVersion=4：manifest 新增 knowledge（知识点树，含每点基础题数）与 overviews（每章概览）。")
    report_lines.append("- 选择题 answer 改为正确项文本编码（洗牌后重算）；App 端 fromBankJson 映射回 key，新旧包兼容。")
    report_lines.append("- 版本 0.13.0；已部署 app/assets/banks/ 并清理 v0.11.0 / v0.12.0（仅保留 v0.13.0）。")
    report_lines.append("- 本轮变更：古代文学史新增 110 道名词解释转基础题（先秦/秦汉/魏晋/隋唐/宋/元/明/清/近代）。")
    open(REPORT, "w", encoding="utf-8").write("\n".join(report_lines))
    print(f"\n打包报告 → {REPORT}")

if __name__ == "__main__":
    main()
