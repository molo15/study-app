# -*- coding: utf-8 -*-
"""分析题库 JSON：题型分布 / 答案位置 / 等价答案 / 重复题干 / 抽样"""
import json, os, re
from collections import Counter, defaultdict

BASE = r"D:\study_app\tools\seed-builder\out"
FILES = {
    "古代汉语": os.path.join(BASE, "v09gudaihanyu", "bank-gudai-hanyu.v09.json"),
    "现代汉语": os.path.join(BASE, "v09", "bank-xiandai-hanyu.v09.json"),
    "中国古代文学史": os.path.join(BASE, "v09gudaiwenxue", "bank-zhongguo-gudai-wenxue.v09.json"),
    "中国现代文学史": os.path.join(BASE, "v09xiandaiwenxue", "bank-zhongguo-xiandai-wenxue.v09.json"),
    "中国当代文学史": os.path.join(BASE, "v09dangdai", "bank-zhongguo-dangdai-wenxue.v09.json"),
}

def norm(s):
    if not s: return ""
    return re.sub(r"[\s，。、；：？！,.!?;:'\"“”‘’（）()\[\]【】—…·《》〈〉<>\-]+", "", str(s))

for name, path in FILES.items():
    if not os.path.exists(path):
        print(f"!! {name}: 文件不存在 {path}")
        continue
    data = json.load(open(path, encoding="utf-8"))
    print(f"\n{'='*60}\n【{name}】 总题数: {len(data)}")

    # 题型分布
    types = Counter(q.get("type") for q in data)
    print("题型分布:", dict(types))

    # 答案位置分布（仅单选，看答案是否总是第一个选项）
    pos_counter = Counter()
    no_options = 0
    multi_with_variants = 0
    for q in data:
        if q.get("type") == "single_choice":
            opts = q.get("options") or []
            ans = q.get("answer")
            if not opts:
                no_options += 1
                continue
            keys = [o.get("key") for o in opts]
            # 答案可能是 "A" 或 ["A"]
            ans_set = ans if isinstance(ans, list) else [ans]
            # 取答案在选项中的下标
            if ans_set and ans_set[0] in keys:
                pos_counter[keys.index(ans_set[0])] += 1
        # 等价答案统计
        if q.get("answerVariants"):
            multi_with_variants += 1

    # 字母标注
    labels = {0:"A",1:"B",2:"C",3:"D",4:"E"}
    pos_str = ", ".join(f"{labels.get(i,f'#{i}')}={c}" for i,c in sorted(pos_counter.items()))
    print(f"单选答案位置分布: {pos_str}  (无选项题:{no_options})")
    if pos_counter:
        first = pos_counter.get(0, 0)
        total = sum(pos_counter.values())
        print(f"  → 答案是首个选项(A)的比例: {first}/{total} = {first/total*100:.1f}%")
    print(f"含 answerVariants(等价答案) 的题数: {multi_with_variants}")

    # 重复题干检测（归一化后完全相同的题干）
    seen = defaultdict(list)
    for i, q in enumerate(data):
        seen[norm(q.get("stem"))].append(i)
    dups = {k: v for k, v in seen.items() if len(v) > 1}
    print(f"完全重复题干组数: {len(dups)}，涉及题目数: {sum(len(v) for v in dups.values())}")
    if dups:
        for k, v in list(dups.items())[:3]:
            print(f"  例: idx={v} stem={data[v[0]]['stem'][:50]}")

    # 抽样：前2道 + 含 answerVariants 的1道
    print("— 抽样题目 —")
    for q in data[:2]:
        print(f"  [{q.get('type')}] {q.get('stem','')[:60]}")
        print(f"      options={[(o.get('key'),o.get('text','')[:20]) for o in (q.get('options') or [])][:4]}")
        print(f"      answer={q.get('answer')}")
    for q in data:
        if q.get("answerVariants"):
            print(f"  [含等价答案 {q.get('type')}] {q.get('stem','')[:50]}")
            print(f"      answerVariants={q.get('answerVariants')[:3]}")
            break
