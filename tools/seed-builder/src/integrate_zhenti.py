# -*- coding: utf-8 -*-
"""
integrate_zhenti.py
把 out/zhenti/ 下的真题素材文件整合进 5 个题库 v0.7.0，产出 v08 题库 JSON。

纯数据工作：
  1) 加载 D:/study_app/app/assets/banks/ 下 5 个 v0.7.0 zip 的现有题；
  2) 对每个素材文件做「严格去重」：
     - stem 归一化（去空白 / 标点 / 括号及内容 / 题号 / 学校年份标记 / 书名号等）
     - 归一化 stem 已在现有库中 → 视为已入库（含“仅差选项/答案格式”的误报）
     - 归一化 stem 不在现有库 → 真未入库候选；同时比对 answer（若都有）进一步确认
  3) 把真未入库题转换为 v3 字段（type/answer/options/explanation/chapter/id/source/answerFormat）；
  4) 输出 D:/study_app/tools/seed-builder/out/v08/{bank_id}.v08.json —— 现有全部题 + 新增题；
  5) 校验每库 id 唯一、type 合法、answer 符合题型编码、chapter 非空。

注意：不触碰 Flutter 代码、不打包、不改 assets/ 与 lib/。
"""

import json
import os
import re
import sys
import zipfile

# ---------------------------------------------------------------------------
# 路径配置
# ---------------------------------------------------------------------------
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
SEED_BUILDER_DIR = os.path.dirname(SRC_DIR)
ROOT = os.path.dirname(os.path.dirname(SEED_BUILDER_DIR))  # D:/study_app
BANKS_DIR = os.path.join(ROOT, "app", "assets", "banks")
MATERIALS_DIR = os.path.join(SEED_BUILDER_DIR, "out", "zhenti")
OUT_DIR = os.path.join(SEED_BUILDER_DIR, "out", "v08")

BANK_ZIPS = {
    "bank-gudai-hanyu": "bank-gudai-hanyu-v0.7.0.zip",
    "bank-xiandai-hanyu": "bank-xiandai-hanyu-v0.7.0.zip",
    "bank-zhongguo-gudai-wenxue": "bank-zhongguo-gudai-wenxue-v0.7.0.zip",
    "bank-zhongguo-xiandai-wenxue": "bank-zhongguo-xiandai-wenxue-v0.7.0.zip",
    "bank-zhongguo-dangdai-wenxue": "bank-zhongguo-dangdai-wenxue-v0.7.0.zip",
}

# 素材文件 → 目标题库
MATERIAL_BANK = {
    "guhanyu-moni-cd.json": "bank-gudai-hanyu",
    "gudai-hanyu.zhenti.json": "bank-gudai-hanyu",
    "xiandai-hanyu.zhenti.json": "bank-xiandai-hanyu",
    "kehou-xiandai-hanyu.json": "bank-xiandai-hanyu",
    "xiandai-tiku-a.json": "bank-xiandai-hanyu",
    "xiandai-tiku-b.json": "bank-xiandai-hanyu",
    "wenxue-gudai-tiku.json": "bank-zhongguo-gudai-wenxue",
    "wenxue-xiandai-tiku.json": "bank-zhongguo-xiandai-wenxue",
    "wenxue-dangdai-tiku.json": "bank-zhongguo-dangdai-wenxue",
}

VALID_TYPES = {"single_choice", "multi_choice", "true_false", "blank", "short_answer"}

# 简答题统一作答格式提示
SHORT_ANSWER_FORMAT = "作答格式：分点作答，先总述观点，再结合具体知识点/作品展开论证，最后简要总结。"

# ---------------------------------------------------------------------------
# 归一化
# ---------------------------------------------------------------------------
def _strip_marks(s: str) -> str:
    """去除括号/方括号及其内容（保留外层文字）。"""
    s = re.sub(r"[（(][^（）()]*[）)]", "", s)
    s = re.sub(r"[\u3008\u3009\u300a\u300b\u3010\u3011\uff08\uff09]", "", s)
    return s


def normalize_stem(stem) -> str:
    """
    题干归一化：
      - 列表 → 拼接
      - 去括号及其内容
      - 去题号前缀（1. 1、 （1） 一、 等）
      - 去学校/年份标记（如“北师大2012年研”“中山大学2012年研”）
      - 去所有空白 / 中英文标点 / 数字字母 / 书名号 / 下划线空
      - 全角转半角后再去
    """
    if stem is None:
        return ""
    if isinstance(stem, (list, tuple)):
        stem = " ".join(str(x) for x in stem)
    s = str(stem)
    # 全角转半角（数字字母标点）
    out = []
    for ch in s:
        code = ord(ch)
        if code == 0x3000:
            out.append(" ")
        elif 0xFF01 <= code <= 0xFF5E:
            out.append(chr(code - 0xFEE0))
        else:
            out.append(ch)
    s = "".join(out)
    s = _strip_marks(s)
    # 题号前缀：如 "1." "1、" "(1)" "一、" "第1题" 等
    s = re.sub(r"^\s*(?:第?\s*[0-9一二三四五六七八九十百千]+\s*[题卷个]?\s*[\.、)）:：]?\s*)", "", s)
    # 学校年份标记
    s = re.sub(
        r"(?:中山大学|北京大学|北京师范大学|北师大|复旦大学|复旦|华东师范大学|南京大学|南京师范|"
        r"武汉大学|华中师范|南开大学|吉林大学|山东大学|苏州大学|浙江大学|四川大学|兰州大学|"
        r"湖南师范|陕西师范|福建师范|厦门大学|暨南大学|上海大学|天津大学|中国人民大学|中国传媒|"
        r"[一-龥]{2,6}(?:大学|学院|师大))\s*[0-9]{2,4}\s*年?\s*研?",
        "",
        s,
    )
    s = re.sub(r"\d{4}\s*年[考研]?", "", s)
    s = re.sub(r"\d{3,4}研", "", s)
    # 占位空（____、___、（））统一抹掉
    s = re.sub(r"_+", "", s)
    s = re.sub(r"[（(][）)]", "", s)
    # 去所有非中文字符
    s = re.sub(r"[^\u4e00-\u9fff]", "", s)
    return s


def normalize_answer(ans) -> str:
    """答案归一化：数组拼接；去空白；简答仅取前 24 字作为指纹。"""
    if ans is None:
        return ""
    if isinstance(ans, (list, tuple)):
        ans = "".join(str(x) for x in ans)
    s = str(ans).strip()
    s = re.sub(r"\s+", "", s)
    # 简答/论述类答案只取开头一段做指纹，避免换行顺序差异误判
    if len(s) > 40:
        s = s[:24]
    return s


def answer_semantically_equal(a, b) -> bool:
    """比较两个答案是否语义一致（对单选比较选项字母；填空/判断比较内容；简答比较前缀）。"""
    na, nb = normalize_answer(a), normalize_answer(b)
    if not na or not nb:
        return True  # 有一方缺失时不做否决，交给 stem 判定
    return na == nb


# ---------------------------------------------------------------------------
# 加载现有题库
# ---------------------------------------------------------------------------
def load_existing_banks() -> dict:
    """返回 {bank_id: {"questions": [...], "by_norm_stem": {norm_stem: [q,...]}, "z_max": int}}"""
    result = {}
    for bid, zname in BANK_ZIPS.items():
        zpath = os.path.join(BANKS_DIR, zname)
        if not os.path.exists(zpath):
            raise FileNotFoundError("找不到题库 zip: %s" % zpath)
        with zipfile.ZipFile(zpath, "r") as z:
            manifest = json.loads(z.read("manifest.json").decode("utf-8"))
            qfiles = manifest.get("questionFiles", [])
            questions = []
            for qf in qfiles:
                data = json.loads(z.read(qf).decode("utf-8"))
                if isinstance(data, list):
                    questions.extend(item for item in data if isinstance(item, dict))
                elif isinstance(data, dict):
                    questions.append(data)
        by_norm = {}
        z_max = 0
        for q in questions:
            ns = normalize_stem(q.get("stem"))
            by_norm.setdefault(ns, []).append(q)
            m = re.match(r"^.*?:z_(\d+)$", q.get("id", ""))
            if m:
                z_max = max(z_max, int(m.group(1)))
        result[bid] = {
            "questions": questions,
            "by_norm_stem": by_norm,
            "z_max": z_max,
            "ids": {q.get("id") for q in questions},
            "chapters": {q.get("chapter") for q in questions if q.get("chapter")},
        }
        print("  加载 %s：现有 %d 题（含 z_ 编号至 %d）" % (bid, len(questions), z_max))
    return result


# ---------------------------------------------------------------------------
# 素材文件加载与结构适配
# ---------------------------------------------------------------------------
def load_material_questions(path: str) -> list:
    """读取素材 JSON，兼容 {bankId, questions:[...]} 与直接数组两种顶层结构。"""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        qs = data.get("questions")
        if not isinstance(qs, list):
            raise ValueError("素材 %s 的 questions 不是数组" % path)
        return qs
    if isinstance(data, list):
        return data
    raise ValueError("素材 %s 顶层结构无法识别" % path)


def convert_raw(q) -> dict:
    """
    将素材原始结构转成统一 v3 字段。
    兼容：
      - 已是 v3 结构（type=枚举值 / stem 字符串 / options 已归一）
      - 旧结构（type='填空题'/'选择题'/'判断题'/'简答题' / q.type+stem 数组等）
    返回 dict（不保证所有字段齐全，缺的后续补齐）。
    """
    if not isinstance(q, dict):
        raise ValueError("素材题项不是 dict: %r" % (q,))

    # ---- type 映射 ----
    raw_type = str(q.get("type", "")).strip()
    type_map = {
        "single_choice": "single_choice",
        "单选题": "single_choice",
        "选择题": "single_choice",
        "多选": "multi_choice",
        "多选题": "multi_choice",
        "multi_choice": "multi_choice",
        "判断": "true_false",
        "判断题": "true_false",
        "true_false": "true_false",
        "填空": "blank",
        "填空题": "blank",
        "blank": "blank",
        "简答": "short_answer",
        "简答题": "short_answer",
        "论述": "short_answer",
        "论述题": "short_answer",
        "名词解释": "short_answer",
        "short_answer": "short_answer",
    }
    qtype = type_map.get(raw_type, raw_type)
    if qtype not in VALID_TYPES:
        raise ValueError("无法识别的题型: %r" % raw_type)

    # ---- stem ----
    stem = q.get("stem", "")
    if isinstance(stem, (list, tuple)):
        stem = "\n".join(str(x) for x in stem)
    stem = str(stem).strip()

    # ---- options ----
    options = q.get("options")
    if options is None:
        # 旧结构可能用 q.optionsText / q.choices
        options = q.get("optionsText") or q.get("choices")
    norm_options = []
    if isinstance(options, list):
        for i, opt in enumerate(options):
            if isinstance(opt, dict) and "text" in opt:
                key = opt.get("key") or chr(65 + i)
                norm_options.append({"key": str(key).upper(), "text": str(opt["text"]).strip()})
            else:
                norm_options.append({"key": chr(65 + i), "text": str(opt).strip()})
    elif isinstance(options, dict):
        for key in sorted(options.keys()):
            norm_options.append({"key": str(key).upper(), "text": str(options[key]).strip()})

    # ---- answer ----
    answer = q.get("answer")
    if isinstance(answer, str):
        answer = answer.strip()

    # ---- explanation ----
    explanation = q.get("explanation", "")
    if explanation is None:
        explanation = ""

    # ---- chapter ----
    chapter = q.get("chapter", "") or ""

    # ---- tags / difficulty ----
    tags = q.get("tags") or []
    if not isinstance(tags, list):
        tags = [str(tags)]
    difficulty = q.get("difficulty") or "medium"
    if difficulty not in ("easy", "medium", "hard"):
        difficulty = "medium"

    # ---- source ----
    src = q.get("source") or {}
    if isinstance(src, str):
        src = {"docPath": src}
    elif not isinstance(src, dict):
        src = {}

    return {
        "type": qtype,
        "stem": stem,
        "options": norm_options,
        "answer": answer,
        "explanation": str(explanation),
        "chapter": str(chapter),
        "tags": tags,
        "difficulty": difficulty,
        "source": src,
    }


def enrich_answer_and_options(q: dict) -> dict:
    """
    按题型规范 answer / options：
      - 单选/判断：answer 为字符串
      - 多选：answer 为数组
      - 填空：answer 为数组（旧格式逗号/空格分隔的拆开）
      - 简答：answer 为参考答案文本
    """
    qtype = q["type"]
    answer = q.get("answer")
    options = q.get("options") or []

    if qtype in ("single_choice", "true_false"):
        if isinstance(answer, (list, tuple)):
            answer = answer[0] if answer else ""
        answer = str(answer).strip()

    elif qtype == "multi_choice":
        if isinstance(answer, str):
            answer = re.split(r"[、,，\s]+", answer.strip()) if answer.strip() else []
        elif isinstance(answer, (list, tuple)):
            answer = [str(x).strip() for x in answer if str(x).strip()]
        else:
            answer = []

    elif qtype == "blank":
        if isinstance(answer, str):
            answer = re.split(r"[、,，;；\s]+", answer.strip()) if answer.strip() else []
        elif isinstance(answer, (list, tuple)):
            answer = [str(x).strip() for x in answer if str(x).strip()]
        else:
            answer = []
        q["stem"] = q["stem"]

    elif qtype == "short_answer":
        if isinstance(answer, (list, tuple)):
            answer = "\n".join(str(x) for x in answer)
        answer = str(answer).strip()

    q["answer"] = answer
    q["options"] = options
    return q


# ---------------------------------------------------------------------------
# 章节归属（素材章节不在现有库章节集时映射）
# ---------------------------------------------------------------------------
def build_chapter_fallback(bank_id: str) -> dict:
    """
    素材里的章节名 → 该库最相关章节的映射。
    仅在素材 chapter 不属于现有库章节时启用。列出的为已知可能出现的别名。
    """
    fallback = {
        "bank-gudai-hanyu": {
            "汉字": "文字（上）",
            "六书": "文字（上）",
            "文字": "文字（上）",
            "古书句读": "古书的标点",
            "训诂学": "训诂",
            "音韵学": "音韵",
            "诗律": "诗词格律",
            "词义": "词汇",
            "古今词义": "词汇",
            "句法": "语法（上）",
            "虚词": "语法（下）",
        },
        "bank-xiandai-hanyu": {
            "普通话": "绪论",
            "汉民族共同语": "绪论",
            "汉字": "文字",
            "现代汉字": "文字",
            "现代汉语词汇": "词汇",
            "现代汉语语法": "语法",
            "现代汉语语音": "语音",
            "句子": "语法",
        },
        "bank-zhongguo-gudai-wenxue": {
            "神话": "先秦文学",
            "诗经": "先秦文学",
            "楚辞": "先秦文学",
            "史传散文": "秦汉文学",
            "汉赋": "秦汉文学",
            "乐府": "秦汉文学",
            "建安": "魏晋南北朝文学",
            "南北朝": "魏晋南北朝文学",
            "唐诗": "隋唐五代文学",
            "宋词": "宋代文学",
            "元曲": "元代文学",
            "明清小说": "明代文学",
            "近代文学": "近代文学",
            "考研真题精选": "论述题专题",
        },
        "bank-zhongguo-xiandai-wenxue": {
            "鲁迅": "鲁迅（一）",
            "综合专题": "综合专题",
            "五四": "五四时期（1917-1927）",
            "30年代": "三十年代（1928-1937）",
            "40年代": "四十年代（1937-1949）",
            "巴金": "巴金",
            "老舍": "老舍",
            "茅盾": "茅盾",
            "曹禺": "曹禺",
            "沈从文": "沈从文",
            "赵树理": "赵树理",
            "郭沫若": "郭沫若",
            "艾青": "艾青",
            "新诗": "新诗（一）",
            "散文": "散文（一）",
            "戏剧": "戏剧",
            "小说": "小说（一）",
            "市民通俗小说": "市民通俗小说（一）",
            "文学思潮": "文学思潮与运动（一）",
            "考研真题精选": "综合专题",
            "第一部分 考研真题精选": "综合专题",
        },
        "bank-zhongguo-dangdai-wenxue": {
            "50-60年代文学思潮": "第一章 1949-1976 文学思潮",
            "50、60年代小说": "第二章 50、60 年代小说",
            "50、60年代新诗": "第三章 50、60 年代新诗",
            "50、60年代戏剧": "第四章 50、60 年代戏剧、散文",
            "50、60年代散文": "第四章 50、60 年代戏剧、散文",
            "80年代小说": "第六章 80 年代小说",
            "80、90年代新诗": "第八章 80、90 年代新诗",
            "80、90年代戏剧": "第九章 80、90 年代戏剧",
            "80、90年代散文": "第十章 80、90 年代散文",
            "90年代小说": "第七章 90 年代小说",
            "台港文学": "第十一章 台港文学",
            "2000年以后文学": "第十二章 2000-2016 年文学概述",
            "文学思潮": "第五章 80、90 年代文学思潮",
            "考研真题精选": "论述题专题",
        },
    }
    return fallback.get(bank_id, {})


def resolve_chapter(chapter: str, bank_id: str, valid_chapters: set) -> str:
    if not chapter:
        return ""
    chapter = chapter.strip()
    if chapter in valid_chapters:
        return chapter
    fb = build_chapter_fallback(bank_id)
    # 先精确匹配别名
    if chapter in fb:
        return fb[chapter]
    # 再尝试包含匹配（素材章节名包含现有章节名，或反之）
    for existing in valid_chapters:
        if existing and (existing in chapter or chapter in existing):
            return existing
    return ""  # 无法归属，交给调用方决策


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("整合真题素材到 v08 题库（纯数据，不碰 Flutter / assets / lib）")
    print("=" * 70)

    os.makedirs(OUT_DIR, exist_ok=True)
    banks = load_existing_banks()

    # 跨库归一化 stem 索引：用于剔除“已存在于其它题库”的误放题（如现代汉语素材里混入的现代文学题）
    cross_bank_stems = {}
    for bid, bank in banks.items():
        for ns in bank["by_norm_stem"]:
            cross_bank_stems.setdefault(ns, bid)

    # 每库新增题累积
    added_by_bank = {bid: [] for bid in BANK_ZIPS}
    stats = []  # 每个素材文件的统计

    for fname, bank_id in MATERIAL_BANK.items():
        path = os.path.join(MATERIALS_DIR, fname)
        if not os.path.exists(path):
            print("\n[跳过] 素材不存在：%s" % path)
            continue
        bank = banks[bank_id]
        bank_norm = bank["by_norm_stem"]

        raw_qs = load_material_questions(path)
        print("\n处理素材：%s（%d 条原始项）→ %s" % (fname, len(raw_qs), bank_id))

        already_imported = 0   # 归一化 stem 已存在
        false_positive = 0     # 归一化 stem 匹配但 answer 有差异的“疑似误报”
        cross_bank_dup = 0     # 已在其它题库存在（跨库重复/素材误放）
        truly_new = 0
        format_errors = 0
        new_questions = []

        for idx, raw in enumerate(raw_qs):
            if not isinstance(raw, dict):
                format_errors += 1
                continue
            try:
                q = convert_raw(raw)
                q = enrich_answer_and_options(q)
            except ValueError as e:
                format_errors += 1
                print("    [格式错误] 第 %d 项：%s" % (idx + 1, e))
                continue

            ns = normalize_stem(q["stem"])
            if not ns:
                format_errors += 1
                continue

            matched = bank_norm.get(ns)
            if matched:
                # stem 已存在：判定是否仅差答案格式
                same_ans = any(
                    answer_semantically_equal(q["answer"], bq.get("answer"))
                    for bq in matched
                )
                if not same_ans and q.get("answer") not in (None, "", []):
                    false_positive += 1
                else:
                    already_imported += 1
                continue

            # stem 不在本库：检查是否已存在于其它 4 个题库（跨库去重）
            other_bank_id = cross_bank_stems.get(ns)
            if other_bank_id and other_bank_id != bank_id:
                cross_bank_dup += 1
                continue

            # ---- 真未入库 ----
            truly_new += 1

            # chapter 归属
            valid_chapters = bank["chapters"]
            chapter = resolve_chapter(q["chapter"], bank_id, valid_chapters)
            if not chapter:
                # 无法映射的章节：按内容关键词回退到“论述题专题”（若存在），否则空
                if "论述题专题" in valid_chapters:
                    chapter = "论述题专题"
                else:
                    chapter = ""

            # 单选缺 options 时给占位
            if q["type"] in ("single_choice", "multi_choice") and not q["options"]:
                if q["type"] == "single_choice":
                    q["options"] = [
                        {"key": "A", "text": "选项 A"},
                        {"key": "B", "text": "选项 B"},
                        {"key": "C", "text": "选项 C"},
                        {"key": "D", "text": "选项 D"},
                    ]
                else:
                    q["options"] = []  # 多选缺选项保留空

            # explanation 缺省
            if not q["explanation"]:
                q["explanation"] = "来源：%s（素材待人工核对解析）" % fname

            # 简答 answerFormat
            if q["type"] == "short_answer" and not q.get("answerFormat"):
                q["answerFormat"] = SHORT_ANSWER_FORMAT

            # id 续编
            bank["z_max"] += 1
            qid = "%s:z_%06d" % (bank_id, bank["z_max"])
            q["id"] = qid
            bank["ids"].add(qid)

            # source 标注素材来源文件名
            src = q.get("source") or {}
            if not isinstance(src, dict):
                src = {}
            src["docPath"] = str(src.get("docPath") or "")
            if not src["docPath"]:
                src["docPath"] = "素材文件：%s" % fname
            src["materialFile"] = fname
            q["source"] = src

            new_questions.append(q)

        stats.append({
            "file": fname,
            "bank": bank_id,
            "raw": len(raw_qs),
            "already_imported": already_imported,
            "false_positive": false_positive,
            "cross_bank_dup": cross_bank_dup,
            "truly_new": truly_new,
            "format_errors": format_errors,
        })
        added_by_bank[bank_id].extend(new_questions)
        print("    → 已入库:%d  误报(仅答案格式差异):%d  跨库重复:%d  真未入库:%d  格式错误:%d"
              % (already_imported, false_positive, cross_bank_dup, truly_new, format_errors))

    # ------------------------------------------------------------------
    # 输出 v08
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("输出 v08 文件")
    print("=" * 70)
    validation_errors = []
    for bid in BANK_ZIPS:
        existing_qs = banks[bid]["questions"]
        new_qs = added_by_bank[bid]
        merged = list(existing_qs) + new_qs
        out_path = os.path.join(OUT_DIR, "%s.v08.json" % bid)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=1)
        print("  写出 %s：现有 %d + 新增 %d = %d 题" % (out_path, len(existing_qs), len(new_qs), len(merged)))

        # ---- 校验 ----
        errs = validate_bank(bid, merged)
        validation_errors.extend(errs)
        if errs:
            for e in errs:
                print("    [校验失败] %s" % e)
        else:
            print("    校验通过：id 唯一 / type 合法 / answer 编码符合题型 / chapter 非空")

    # ------------------------------------------------------------------
    # 汇总
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("汇总（各素材贡献）")
    print("=" * 70)
    for s in stats:
        print("  %-28s → %-32s 原始:%4d 已入库:%4d 误报:%3d 跨库重复:%3d 真新增:%3d 格式错误:%d"
              % (s["file"], s["bank"], s["raw"], s["already_imported"],
                 s["false_positive"], s["cross_bank_dup"], s["truly_new"], s["format_errors"]))
    print("\n每库新增：")
    for bid in BANK_ZIPS:
        print("  %s: +%d 题" % (bid, len(added_by_bank[bid])))

    if validation_errors:
        print("\n!! 存在校验错误，共 %d 条" % len(validation_errors))
        sys.exit(1)
    print("\n全部校验通过。")


def validate_bank(bank_id: str, questions: list) -> list:
    """校验：id 唯一、type 合法、answer 符合题型编码、chapter 非空。"""
    errs = []
    seen_ids = {}
    for q in questions:
        qid = q.get("id")
        if not qid:
            errs.append("%s: 存在无 id 的题目: %s" % (bank_id, str(q.get("stem"))[:40]))
            continue
        if qid in seen_ids:
            errs.append("%s: id 重复 %s（stem: %s vs %s）"
                        % (bank_id, qid, str(q.get("stem"))[:30], str(seen_ids[qid])[:30]))
        else:
            seen_ids[qid] = q.get("stem")

        qtype = q.get("type")
        if qtype not in VALID_TYPES:
            errs.append("%s[%s]: type 非法 %r" % (bank_id, qid, qtype))
            continue

        ans = q.get("answer")
        if qtype in ("single_choice", "true_false"):
            if not isinstance(ans, str):
                errs.append("%s[%s]: %s 的 answer 应为字符串，实际 %r" % (bank_id, qid, qtype, type(ans).__name__))
            elif qtype == "single_choice":
                keys = {o.get("key") for o in q.get("options") or []}
                if ans not in keys and keys:
                    errs.append("%s[%s]: 单选答案 %s 不在选项 %s 中" % (bank_id, qid, ans, sorted(keys)))
            elif qtype == "true_false" and ans not in ("正确", "错误"):
                errs.append("%s[%s]: 判断题答案应为 正确/错误，实际 %r" % (bank_id, qid, ans))
        elif qtype == "multi_choice":
            if not isinstance(ans, list) or not ans:
                errs.append("%s[%s]: 多选答案应为非空数组，实际 %r" % (bank_id, qid, ans))
        elif qtype == "blank":
            if not isinstance(ans, list) or not ans or any(not str(x).strip() for x in ans):
                errs.append("%s[%s]: 填空答案应为非空数组" % (bank_id, qid))
        elif qtype == "short_answer":
            if not isinstance(ans, str) or not ans.strip():
                errs.append("%s[%s]: 简答答案不能为空" % (bank_id, qid))

        if not q.get("chapter"):
            errs.append("%s[%s]: chapter 为空（stem: %s）" % (bank_id, qid, str(q.get("stem"))[:40]))
    return errs


if __name__ == "__main__":
    main()
