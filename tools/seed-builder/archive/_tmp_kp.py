# -*- coding: utf-8 -*-
import json
from collections import defaultdict
k = json.load(open(r"D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json", encoding="utf-8"))["knowledge"]
by_ch = defaultdict(list)
for kp in k:
    by_ch[kp["chapter"]].append(kp)
for ch in sorted(by_ch):
    print(f"== {ch} ({len(by_ch[ch])}知识点) ==")
    for kp in by_ch[ch]:
        print(f"   {kp['id']} | {kp['name']} | hot={kp.get('hot')}")
