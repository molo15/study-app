# -*- coding: utf-8 -*-
"""修复古代汉语 choice 题「answer 与 options 不匹配」的历史遗留问题。
打包时 answer 错配会静默指向第一个选项（答案错题隐患），必须修。
"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = r"D:\study_app\tools\seed-builder\out\knowledge\古代汉语.knowledge.json"

# 手工特例（子串匹配无法处理）：answer → 应为选项文本
MANUAL = {
    "由褒义变为贬义": "由褒变贬",
    "名词作状语，表比喻": "名词作状语表比喻",
}

def fix():
    d = json.load(open(PATH, encoding="utf-8"))
    fixed, remaining = [], []
    for k in d["knowledge"]:
        for q in k.get("basicQuestions", []):
            if q["type"] != "choice":
                continue
            opts = q.get("options", [])
            ans = q.get("answer", "")
            if ans in opts:
                continue  # 正常
            # 尝试修复
            new = MANUAL.get(ans)
            if new is None:
                # 子串匹配：选项是 answer 的子串，或 answer 是选项的子串
                for o in opts:
                    if o and o in ans:
                        new = o; break
                if new is None:
                    for o in opts:
                        if ans and ans in o:
                            new = o; break
            if new and new in opts:
                fixed.append((k["id"], ans, new, q["stem"][:30]))
                q["answer"] = new
            else:
                remaining.append((k["id"], ans, q["stem"][:30]))
    json.dump(d, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"已修复 {len(fixed)} 题：")
    for kid, old, new, stem in fixed:
        print(f"  [{kid}] {stem}…  {old!r} → {new!r}")
    print()
    print(f"无法自动修复 {len(remaining)} 题：")
    for kid, ans, stem in remaining:
        print(f"  [{kid}] {stem}… answer={ans!r}")

if __name__ == "__main__":
    fix()
