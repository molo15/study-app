# -*- coding: utf-8 -*-
"""P1a: 导出解析问题题单（missing / lazy / too_short），供逐条重写解析。"""
import json, os, re

SAN = r"D:\study_app\tools\seed-builder\out\sanitized"
FILES = {
    "古代汉语": os.path.join(SAN, "古代汉语.sanitized.json"),
    "现代汉语": os.path.join(SAN, "现代汉语.sanitized.json"),
    "中国古代文学史": os.path.join(SAN, "中国古代文学史.sanitized.json"),
    "中国现代文学史": os.path.join(SAN, "中国现代文学史.sanitized.json"),
    "中国当代文学史": os.path.join(SAN, "中国当代文学史.sanitized.json"),
}
OUT = os.path.join(SAN, "fixlist_explanation")
os.makedirs(OUT, exist_ok=True)

LAZY_RE = re.compile(r"^(见原文|见教材|见参考|参考答案见|参考解析|同解析|略[。]?|见上|见下|见解析|。?)$")

def problem_type(q):
    e = (q.get("explanation") or "").strip()
    if not e:
        return "missing"
    if LAZY_RE.match(e):
        return "lazy"
    min_len = 40 if q.get("type") == "short_answer" else 20
    if len(e) < min_len:
        return "too_short"
    return None

total = 0
for name, path in FILES.items():
    data = json.load(open(path, encoding="utf-8"))
    problems = [q for q in data if problem_type(q)]
    total += len(problems)
    lines = [f"# {name} 解析问题题单（{len(problems)} 条）", ""]
    by_type = {}
    for q in problems:
        t = problem_type(q)
        by_type.setdefault(t, []).append(q)
    for t in ["missing", "lazy", "too_short"]:
        qs = by_type.get(t, [])
        if not qs:
            continue
        lines.append(f"## {t}（{len(qs)} 条）")
        for q in qs:
            e = (q.get("explanation") or "").strip()[:80]
            src = (q.get("source") or {}).get("blockId", "")
            lines.append(
                f"- id=`{q['id']}` | {q.get('type')} | 难:{q.get('difficulty','')}\n"
                f"  题干: {q.get('stem','')}\n"
                f"  答案: {json.dumps(q.get('answer'), ensure_ascii=False)}\n"
                f"  现解析: {e}\n"
                f"  素材: {src}"
            )
        lines.append("")
    fname = os.path.join(OUT, f"fixlist_{name}.md")
    open(fname, "w", encoding="utf-8").write("\n".join(lines))
    print(f"{name}: {len(problems)} 条 (missing={len(by_type.get('missing',[]))}, lazy={len(by_type.get('lazy',[]))}, too_short={len(by_type.get('too_short',[]))}) -> {fname}")

print(f"\n合计解析问题: {total} 条")
