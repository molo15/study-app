# -*- coding: utf-8 -*-
import json
k = json.load(open(r"D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json", encoding="utf-8"))
print("chapters:", json.dumps(k["chapters"], ensure_ascii=False, indent=1)[:800])
print("\nknowledgeCount:", k["knowledgeCount"])
# 收集所有 parent 值
parents = set()
for kp in k["knowledge"]:
    parents.add(kp.get("parent"))
print("\n所有 parent 值:", parents)
