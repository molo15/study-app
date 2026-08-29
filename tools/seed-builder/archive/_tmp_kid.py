# -*- coding: utf-8 -*-
import json
from collections import Counter
d = json.load(open(r"D:\study_app\tools\seed-builder\out\refined\bank-zhongguo-gudai-wenxue.refined2.json", encoding="utf-8"))
# 元/清/近代 章节题的 knowledgeId
for ch in ["元代文学", "清代文学", "近代文学"]:
    qs = [q for q in d if q["chapter"] == ch]
    print(f"== {ch} ({len(qs)}题) ==")
    kids = Counter(q.get("knowledgeId") for q in qs)
    print("  knowledgeId:", dict(kids.most_common(5)))
    for q in qs[:2]:
        print("  例:", q["id"], "| kid:", q.get("knowledgeId"), "|", q["stem"][:40])
