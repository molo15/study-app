# -*- coding: utf-8 -*-
import json
from collections import defaultdict, Counter

q = json.load(open(r"D:\study_app\tools\seed-builder\out\extract\袁行霈题库.parsed.json", encoding="utf-8"))
print("=== 袁行霈题库 每编 填空题(带解析) ===")
by_ch = defaultdict(list)
for x in q:
    by_ch[x["chapter"]].append(x)
for ch in sorted(by_ch, key=lambda c: c):
    qs = by_ch[ch]
    bk = [x for x in qs if x["type"] == "填空题"]
    bk_an = [x for x in bk if x["analysis"]]
    print(f"  {ch}: 总{len(qs)} | 填空{len(bk)} 带解析{len(bk_an)}")
noch = [x for x in q if not x["chapter"]]
bk = [x for x in noch if x["type"] == "填空题"]
bk_an = sum(1 for x in bk if x["analysis"])
print(f"  (考研真题精选): 总{len(noch)} | 填空{len(bk)} 带解析{bk_an}")
print()
d = json.load(open(r"D:\study_app\tools\seed-builder\out\refined\bank-zhongguo-gudai-wenxue.refined2.json", encoding="utf-8"))
print("=== 古文史每章当前题量 ===")
cc = Counter(q2["chapter"] for q2 in d)
cc_b = Counter(q2["chapter"] for q2 in d if q2.get("purpose") == "basic")
for ch in sorted(cc):
    print(f"  {ch}: 总{cc[ch]} 基础{cc_b[ch]}")
