# -*- coding: utf-8 -*-
"""P1 第二阶段：按新出题规则重出基础题。

把 5 科 knowledge.json 中每知识点下已规划的 basicQuestions（直问直答模板：
知识点直问直答 + 同域等长干扰项 + 实质解析）批量转成正式题库文件，
作为 v0.10.0 的「基础题轨」（purpose=basic），每题绑定 knowledgeId（G7）。

题型映射：choice→single_choice，blank→blank，true_false→true_false，short_answer→short_answer。
选项：answer 为正确项文本；洗牌与 answer 位置重算由打包阶段统一执行（G1），此处保持原序。

输出：out/v010/basic/<bankId>.basic.json
"""
import json, os, re

BASE = r"D:\study_app\tools\seed-builder\out"
KNOW = os.path.join(BASE, "knowledge")
OUT = os.path.join(BASE, "v010", "basic")
os.makedirs(OUT, exist_ok=True)

BANKS = [
    ("bank-xiandai-hanyu", "现代汉语"),
    ("bank-gudai-hanyu", "古代汉语"),
    ("bank-zhongguo-gudai-wenxue", "中国古代文学史"),
    ("bank-zhongguo-xiandai-wenxue", "中国现代文学史"),
    ("bank-zhongguo-dangdai-wenxue", "中国当代文学史"),
]

TYPE_MAP = {
    "choice": "single_choice",
    "blank": "blank",
    "true_false": "true_false",
    "short_answer": "short_answer",
}
KEY = "ABCD"

def to_answer(t, ans):
    if t == "single_choice":
        return ans  # 文本，打包时重算位置
    if t == "true_false":
        return "正确" if str(ans).startswith("正确") else "错误"
    if isinstance(ans, list):
        return ans
    return [str(ans)]

def build(know, bank):
    seq = 0
    qs = []
    for k in know["knowledge"]:
        kid = k["id"]
        ch = k["chapter"]
        for bq in k.get("basicQuestions", []):
            t = TYPE_MAP.get(bq.get("type"), "single_choice")
            seq += 1
            q = {
                "id": f"{bank}:kb_{seq:05d}",
                "type": t,
                "stem": bq["stem"],
                "answer": to_answer(t, bq.get("answer")),
                "explanation": bq.get("explanation", ""),
                "chapter": ch,
                "purpose": "basic",
                "knowledgeId": kid,
                "difficulty": "easy",
                "tags": [k.get("name", "")],
                "answerFormat": None,
            }
            if t == "single_choice":
                opts = bq.get("options") or []
                q["options"] = [{"key": KEY[i], "text": o} for i, o in enumerate(opts)]
                # 找到正确项 key
                ans_txt = bq.get("answer", "")
                correct_idx = next((i for i, o in enumerate(opts) if o == ans_txt), 0)
                q["answer"] = KEY[correct_idx]
            elif t == "true_false":
                q["answer"] = "正确" if str(bq.get("answer", "")).startswith("正确") else "错误"
            else:
                if isinstance(q["answer"], str):
                    q["answer"] = [q["answer"]]
            qs.append(q)
    return qs

def main():
    total = 0
    for bank, cn in BANKS:
        kp = os.path.join(KNOW, f"{cn}.knowledge.json")
        if not os.path.exists(kp):
            print(f"[{cn}] 无 knowledge.json，跳过")
            continue
        know = json.load(open(kp, encoding="utf-8"))
        qs = build(know, bank)
        out = os.path.join(OUT, f"{bank}.basic.json")
        json.dump(qs, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        total += len(qs)
        # 校验：choice 必须有 4 个同域选项、无括号注释；答案 key 存在于 options
        import collections
        bad = 0
        for q in qs:
            if q["type"] == "single_choice":
                opts = q["options"]
                if len(opts) < 4:
                    bad += 1
                if q["answer"] not in {o["key"] for o in opts}:
                    bad += 1
                if any(re.search(r"[（(]", o["text"]) for o in opts):
                    bad += 1
        print(f"[{cn}] 基础题 {len(qs)} 道 → {out}；choice 校验异常 {bad}")
    print(f"5 科合计基础题 {total} 道")

if __name__ == "__main__":
    main()
