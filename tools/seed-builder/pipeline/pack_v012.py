# -*- coding: utf-8 -*-
"""v0.12.0 打包：formatVersion=4，输入 refined 完整题库（basic+test 同源）。

基于 pack_v4.py 改造：
- 输入改为 5 个 refined 产物（每库一个完整文件），按 purpose 分基础/测试轨
- 统一题 id 前缀为 bank-xxx:
- 选择题洗牌（兼容 answer 的 key 编码与文本编码），v4 answer 存正确项文本
- basic 无 knowledgeId 的题自动降级为测试轨；basic 解析过短自动补齐
- 模拟卷引用 id 需存在于题库，缺失则过滤并告警
"""
import json, os, random, re, shutil, zipfile
from collections import Counter, defaultdict

BASE = r"D:\study_app\tools\seed-builder"
OUT_DIR = os.path.join(BASE, "out", "packages", "v012")
ASSETS = r"D:\study_app\app\assets\banks"
KNOW = os.path.join(BASE, "out", "knowledge")
PAPERS = os.path.join(BASE, "out", "papers", "papers.json")
REPORT = os.path.join(BASE, "out", "reports", "pack_report_v012.md")
VERSION = "0.12.0"
GENERATED_AT = "2026-08-27T19:00:00+08:00"

BANKS = {
    "bank-xiandai-hanyu": ("考研 · 现代汉语", "现代汉语", "out/refined/bank-xiandai-hanyu.refined2.json"),
    "bank-gudai-hanyu": ("考研 · 古代汉语", "古代汉语", "out/refined/bank-gudai-hanyu.v012.json"),
    "bank-zhongguo-gudai-wenxue": ("考研 · 中国古代文学史", "中国古代文学史", "out/refined/bank-zhongguo-gudai-wenxue.v012.json"),
    "bank-zhongguo-xiandai-wenxue": ("考研 · 中国现代文学史", "中国现代文学史", "out/refined/bank-zhongguo-xiandai-wenxue.quota.json"),
    "bank-zhongguo-dangdai-wenxue": ("考研 · 中国当代文学史", "中国当代文学史", "out/refined/bank-zhongguo-dangdai-wenxue.refined2.json"),
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

def norm_id(bank, qid):
    if qid.startswith(bank + ":"):
        return qid
    return f"{bank}:{qid}"

def shuffle_options(q, rng):
    """洗牌选择题，answer 兼容 key 编码与文本编码；返回正确项文本。"""
    t = q["type"]
    if t not in ("single_choice", "multi_choice"):
        return None
    opts = list(q["options"])
    ans = q["answer"]
    ans_set = set(ans) if isinstance(ans, list) else {ans}
    keys = {o["key"] for o in opts}
    if ans_set <= keys:
        # key 编码 → 文本
        ans_texts = {o["text"] for o in opts if o["key"] in ans_set}
    else:
        ans_texts = ans_set
    rng.shuffle(opts)
    newkeys = "ABCDEFGH"[:len(opts)]
    for o, k in zip(opts, newkeys):
        o["key"] = k
    q["options"] = opts
    q["_ans_texts"] = list(ans_texts)
    return list(ans_texts)

def encode_answer_v4(q):
    t = q["type"]
    texts = q.pop("_ans_texts", None)
    if t == "single_choice":
        q["answer"] = texts[0] if texts else ""
    elif t == "multi_choice":
        q["answer"] = sorted(texts) if texts else []

def pad_explanation(q, kp_name):
    """basic 解析过短/缺失时自动补齐。"""
    expl = q.get("explanation") or ""
    if len(expl.strip()) >= 20 and not PLACEHOLDER.search(expl.strip()):
        return
    stem = q.get("stem", "")[:80]
    q["explanation"] = f"本题考察“{kp_name}”知识点。题干：{stem}。答案为：{q.get('answer', '')}。"

def fix_single_options(q):
    """单选选项数!=4 时自动裁剪到 4 个（保留正确项）。"""
    if q["type"] != "single_choice":
        return
    opts = list(q["options"])
    if len(opts) == 4:
        return
    ans = q["answer"]
    ans_set = set(ans) if isinstance(ans, list) else {ans}
    # 正确项优先保留（key 或文本）
    keep = [o for o in opts if o["text"] in ans_set or o["key"] in ans_set]
    others = [o for o in opts if o not in keep]
    need = 4 - len(keep)
    if need > 0:
        keep += others[:need]
    q["options"] = keep[:4]

def validate_basic(q, know_ids, report):
    errs = []
    if q["id"] in report["ids"]:
        errs.append("id重复")
    report["ids"].add(q["id"])
    if not q["id"].startswith("bank-") or q["id"].count(":") != 1:
        errs.append("id格式")
    if q["type"] == "single_choice":
        opts = q["options"]
        if len(opts) != 4:
            errs.append("选项数!=4")
        if q["answer"] not in {o["text"] for o in opts}:
            errs.append("答案文本失效")
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
    if not expl or len(expl.strip()) < 20:
        errs.append("解析过短")
    if PLACEHOLDER.search(expl.strip()):
        errs.append("解析占位")
    if not q.get("knowledgeId") or q["knowledgeId"] not in know_ids:
        errs.append("knowledgeId缺失/无效")
    return errs

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    papers_data = json.load(open(PAPERS, encoding="utf-8"))["papers"]
    paper_meta = {pp["bankId"]: pp for pp in papers_data}

    report_lines = [f"# v{VERSION}（formatVersion=4）打包报告", ""]
    summary = []
    grand_basic = grand_test = grand_kp = 0

    for bank, (name, cn, rel) in BANKS.items():
        rng = random.Random("v012_" + bank)
        report = {"ids": set(), "bad": []}
        know = json.load(open(os.path.join(KNOW, f"{cn}.knowledge.json"), encoding="utf-8"))
        kp_nodes = know["knowledge"]
        know_ids = {k["id"] for k in kp_nodes}
        kp_by_id = {k["id"]: k for k in kp_nodes}

        qs = json.load(open(os.path.join(BASE, rel), encoding="utf-8"))
        # 统一 id + 章节归一
        for q in qs:
            q["id"] = norm_id(bank, q["id"])
            q["chapter"] = norm_chapter(bank, q["chapter"])
            q.pop("source", None)

        # 分轨：basic 无 kid 降级 test
        basic = [q for q in qs if q.get("purpose") == "basic" and q.get("knowledgeId")]
        test = [q for q in qs if q not in basic]
        n_demote = len([q for q in qs if q.get("purpose") == "basic" and not q.get("knowledgeId")])

        # 基础轨：洗牌 + 解析补齐 + 校验
        basic_out = []
        for q in basic:
            nq = dict(q)
            kp_name = kp_by_id.get(q.get("knowledgeId"), {}).get("name", "")
            pad_explanation(nq, kp_name)
            fix_single_options(nq)
            shuffle_options(nq, rng)
            encode_answer_v4(nq)
            basic_out.append(nq)
            for e in validate_basic(nq, know_ids, report):
                report["bad"].append(f"{nq['id']} [{e}]")

        # 测试轨：洗牌 + v4 编码（宽松校验 id 唯一）
        test_out = []
        for q in test:
            nq = dict(q)
            fix_single_options(nq)
            shuffle_options(nq, rng)
            encode_answer_v4(nq)
            if nq["id"] in report["ids"]:
                report["bad"].append(f"{nq['id']} [id重复]")
            report["ids"].add(nq["id"])
            test_out.append(nq)

        if len(report["ids"]) != len(basic_out) + len(test_out):
            report["bad"].append("id集合不一致")

        # 每知识点基础题数
        kp_count = Counter(q.get("knowledgeId") for q in basic_out if q.get("knowledgeId"))
        knowledge = []
        for k in kp_nodes:
            knowledge.append({
                "id": k["id"], "name": k["name"],
                "chapter": norm_chapter(bank, k["chapter"]),
                "parent": k.get("parent"), "summary": k.get("summary", ""),
                "hot": bool(k.get("hot")), "examRef": k.get("examRef", ""),
                "questionCount": kp_count.get(k["id"], 0),
            })

        # overviews
        by_ch_kp = defaultdict(list)
        for k in knowledge:
            by_ch_kp[k["chapter"]].append(k)
        overviews = []
        for ch in sorted(by_ch_kp):
            kps_ = by_ch_kp[ch]
            hot_names = [k["name"] for k in kps_ if k["hot"]]
            total_q = sum(k["questionCount"] for k in kps_)
            sum_line = f"本章共 {len(kps_)} 个知识点、{total_q} 道基础题。"
            if hot_names:
                sum_line += f"高频考点：{'、'.join(hot_names[:5])}{'等' if len(hot_names) > 5 else ''}。"
            overviews.append({"chapter": ch, "knowledgeCount": len(kps_),
                              "questionCount": total_q, "summary": sum_line})

        # 分组
        all_ch = sorted({q["chapter"] for q in basic_out + test_out})
        chapter_groups = []
        for g, chs in GROUPS[bank]:
            keep_ch = [c for c in chs if c in all_ch]
            if keep_ch:
                chapter_groups.append({"group": g, "chapters": keep_ch})
        extra = [c for c in all_ch if not any(c in chs for _, chs in GROUPS[bank])]
        if extra:
            chapter_groups.append({"group": "其他", "chapters": extra})

        # 模拟卷（校验引用 id 存在）
        all_ids = report["ids"]
        mock = []
        if bank in paper_meta:
            pp = paper_meta[bank]
            valid = [i for i in pp["questionIds"] if i in all_ids]
            dropped = len(pp["questionIds"]) - len(valid)
            if dropped:
                report["bad"].append(f"模拟卷引用 {dropped} 个 id 缺失")
            mock.append({"id": f"{bank}:paper_01", "bankId": bank, "name": pp["name"],
                         "durationMin": pp["durationMin"], "questionIds": valid})

        manifest = {
            "formatVersion": 4, "bankId": bank, "name": name, "version": VERSION,
            "idSchema": "q-b",  # v1.1.3: 题 id 前缀体系标识（q_/b_），供 App 端不兼容升级判断
            "generatedAt": GENERATED_AT, "chapters": chapter_groups,
            "questionFiles": [], "mockPapers": mock,
            "knowledge": knowledge, "overviews": overviews,
        }

        _type_order = {"single_choice": 0, "multi_choice": 1, "true_false": 2, "blank": 3, "short_answer": 4}
        by_purpose_ch = {}
        for q in basic_out:
            by_purpose_ch.setdefault(("基础", q["chapter"]), []).append(q)
        for q in test_out:
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

        n_basic, n_test = len(basic_out), len(test_out)
        grand_basic += n_basic; grand_test += n_test; grand_kp += len(kp_nodes)
        print(f"== {bank} v{VERSION}：基础{n_basic} + 测试{n_test}（降级{n_demote}）；知识点{len(kp_nodes)}；overviews{len(overviews)}")
        print(f"   校验异常 {len(report['bad'])}")
        for b in report["bad"][:10]:
            print("   !!", b)
        summary.append((bank, n_basic, n_test, len(kp_nodes), len(report["bad"])))

        os.makedirs(ASSETS, exist_ok=True)
        dst = os.path.join(ASSETS, f"{bank}-v{VERSION}.zip")
        shutil.copyfile(zip_path, dst)
        for old in os.listdir(ASSETS):
            if old.startswith(bank + "-v0.10") and old.endswith(".zip") and ".bak" not in old and "_tmp" not in old:
                os.remove(os.path.join(ASSETS, old))
        print(f"   ✅ 已部署 {dst}（移除 v0.10.0）")

        report_lines.append(f"## {name}（{bank}）")
        report_lines.append(f"- 基础轨 **{n_basic}**；测试轨 **{n_test}**（含降级 {n_demote}）；知识点 **{len(kp_nodes)}**；overviews **{len(overviews)}**")
        report_lines.append(f"- 校验异常 **{len(report['bad'])}**")
        report_lines.append("")

    report_lines.append("## 汇总")
    report_lines.append("| 科目 | 基础轨 | 测试轨 | 知识点 | 校验异常 |")
    report_lines.append("|---|---|---|---|---|")
    for bank, nb, nt, nkp, bad in summary:
        report_lines.append(f"| {bank} | {nb} | {nt} | {nkp} | {bad} |")
    report_lines.append(f"| **合计** | **{grand_basic}** | **{grand_test}** | **{grand_kp}** | |")
    report_lines.append("")
    report_lines.append("## 说明")
    report_lines.append("- formatVersion=4：manifest 含 knowledge（知识点树+每点基础题数）与 overviews（每章概览）。")
    report_lines.append(f"- 选择题 answer 存正确项文本（洗牌后重算），App 端 fromBankJson 映射回 key。")
    report_lines.append(f"- 版本 {VERSION}；已部署 app/assets/banks/ 并移除 v0.10.0。")
    open(REPORT, "w", encoding="utf-8").write("\n".join(report_lines))
    print(f"\n打包报告 → {REPORT}")

if __name__ == "__main__":
    main()
