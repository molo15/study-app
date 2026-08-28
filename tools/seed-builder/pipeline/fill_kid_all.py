# -*- coding: utf-8 -*-
"""给 basic 题补 knowledgeId：知识点名关键词匹配 + 兜底归章内首知识点。
目标库：现汉/现文史/当代（古汉/古文史已在各自脚本补齐）。"""
import json, os, re
from collections import defaultdict, Counter

BASE = r"D:\study_app\tools\seed-builder"
OUT = os.path.join(BASE, "out")

FILES = {
    "bank-xiandai-hanyu": ("out/refined/bank-xiandai-hanyu.refined2.json", "现代汉语.knowledge.json"),
    "bank-zhongguo-xiandai-wenxue": ("out/refined/bank-zhongguo-xiandai-wenxue.quota.json", "中国现代文学史.knowledge.json"),
    "bank-zhongguo-dangdai-wenxue": ("out/refined/bank-zhongguo-dangdai-wenxue.refined2.json", "中国当代文学史.knowledge.json"),
    "bank-gudai-hanyu": ("out/refined/bank-gudai-hanyu.v012.json", "古代汉语.knowledge.json"),
}
# 需要保护 id 前缀的题（手工精确映射的扩充题，不重映射）
PROTECT = {"bank-gudai-hanyu": ("gh_",)}

STOP = set("“””‘’、，。；：！？（）()·与和及等或及其之的在上中下后部这那是些被把", )

# 当代：题 chapter（DD_MAP 后）→ 知识点 chapter（原名）
DD_MAP = {
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
REV_DD = DD_MAP  # 题新名 → 知识点原名（直接用正向表）

def norm(s):
    if not s: return ""
    s = re.sub(r"[（(][^）)]*[）)]", "", s)
    s = re.sub(r"[《》“”\"'。，、；：？！·…—\- ]", "", s)
    return s

FILTER = set("概念定义简介概况分类方法数量性质构成特点特征种类类别简况结构方式区别关系异同作用意义价值内容范围问题规律系统研究简况上下中前后部主次本末以及等等如下下列哪些表述正确的是正确的说法不正确不属于")

def _split_terms(text):
    """把一段文本拆成核心术语词。先剔除引号内例句（“…” “…” "…"），避免例句被当关键词。"""
    text = re.sub(r"[“”\"'][^“”\"']*[“”\"']", " ", text)   # 剔除引号内容（例句）
    text = text.replace("：", " ").replace(":", " ").replace("、", " ").replace("，", " ").replace("；", " ").replace("/", " ")
    out = []
    seen = set()
    for p in re.split(r"\s+", text.strip()):
        if not p:
            continue
        for s in re.split(r"[的与和及等或]", p):
            s = re.sub(r"[（）()《》“”\"']", "", s).strip()
            if not s or s in FILTER:
                continue
            if 2 <= len(s) <= 8 and s not in seen:
                seen.add(s)
                out.append(s)
    return out

def kws_from_name(name, summary=""):
    """知识点关键词 = name 术语 + summary 术语（summary 更长，放在后面降低优先级）。"""
    out = _split_terms(name or "")
    if summary:
        out += _split_terms(summary)
    return out

def build_kid_map(kps):
    """章 → [(kw, kid, shared)]，长词优先、非共享词（特异性）优先。"""
    from collections import Counter
    by_ch = defaultdict(list)
    first_kid = {}
    kw_kid = defaultdict(dict)   # ch -> {kw: kid}
    kw_cnt = defaultdict(Counter)  # ch -> Counter(kw)
    for kp in kps:
        ch = kp.get("chapter", "")
        if ch not in first_kid:
            first_kid[ch] = kp["id"]
        for kw in kws_from_name(kp.get("name", ""), kp.get("summary", "")):
            kw_kid[ch][kw] = kp["id"]
            kw_cnt[ch][kw] += 1
    for ch in kw_kid:
        for kw, kid in kw_kid[ch].items():
            shared = kw_cnt[ch][kw] > 1
            by_ch[ch].append((kw, kid, shared))
        by_ch[ch].sort(key=lambda x: (-len(x[0]), x[2]))
    return by_ch, first_kid

def main():
    for bank, (rel, kfile) in FILES.items():
        path = os.path.join(BASE, rel)
        qs = json.load(open(path, encoding="utf-8"))
        kp = json.load(open(os.path.join(OUT, "knowledge", kfile), encoding="utf-8"))
        kps = kp.get("knowledge", kp.get("nodes", []))
        kid_map, first_kid = build_kid_map(kps)
        matched = fallback = demote = protected = 0
        prot = PROTECT.get(bank, ())
        for q in qs:
            if q.get("purpose") != "basic":
                continue
            if any(q["id"].startswith(p) for p in prot):
                protected += 1
                continue
            ch = q.get("chapter", "")
            kch = REV_DD.get(ch, ch) if bank == "bank-zhongguo-dangdai-wenxue" else ch
            # 匹配目标 = 题干 + 选项文本
            target = q.get("stem", "") + " " + " ".join(o.get("text", "") for o in q.get("options", []))
            kid = None
            if kch in kid_map:
                for kw, kid_, shared in kid_map[kch]:
                    if kw and kw in target:
                        kid = kid_; break
            if kid:
                q["knowledgeId"] = kid
                q["purpose"] = "basic"
                matched += 1
            else:
                # 无法精确归属：降级为测试轨（不再强制挂知识点）
                q.pop("knowledgeId", None)
                q["purpose"] = "test"
                demote += 1
        nokid = sum(1 for q in qs if q.get("purpose") == "basic" and not q.get("knowledgeId"))
        nbasic = sum(1 for q in qs if q.get("purpose") == "basic")
        ntest = sum(1 for q in qs if q.get("purpose") == "test")
        print(f"{bank}: 精确匹配 {matched} | 降级test {demote} | 保护 {protected} | basic {nbasic} / test {ntest} | basic缺kid {nokid}")
        json.dump(qs, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
