# -*- coding: utf-8 -*-
import json
k = json.load(open(r"D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json", encoding="utf-8"))
print("knowledge.json 顶层 keys:", list(k.keys()))
kps = k["knowledge"]
print("节点数:", len(kps))
# 打印一个完整节点
print("\n=== 节点完整字段示例 ===")
print(json.dumps(kps[0], ensure_ascii=False, indent=1))
print("\n=== 所有顶层 parent 节点 ===")
for kp in kps:
    if not kp.get("parent"):
        print(f"  {kp['id']} | {kp['name']}")
