# -*- coding: utf-8 -*-
# 修复 update_knowledge_gudaiwenxue.py 中字符串内 ASCII 引号冲突
import re
p = r"D:\study_app\tools\seed-builder\pipeline\update_knowledge_gudaiwenxue.py"
s = open(p, encoding="utf-8").read()
# 找到所有含 ASCII 引号对的文本内容行，把其中的 "X" 替换为 "X"（中文引号）
# 规则：在一行内，字符串内部的成对 ASCII 引号（前面不是行首且不在行尾）替换
lines = s.split("\n")
fixed = 0
for i, ln in enumerate(lines):
    # 检测：行内有成对的 "..." 且行本身以 "summary"/"explanation"/"stem" 开头
    if re.search(r'^\s*"(summary|explanation|stem)"\s*:', ln):
        # 将行内除了 key 与首尾界定符之外的 "X" 替换
        # 简单策略：去掉 key 部分后的内容里，把 "X" -> \u201cX\u201d
        m = re.match(r'^(\s*"(summary|explanation|stem)"\s*:\s*)(.*)$', ln)
        head, body = m.group(1), m.group(3)
        # body 形如 "...." 或 [ ... ]
        # 替换 body 内部成对的 ASCII 引号
        newbody = re.sub(r'"([^"]*?)"', r'"\1"', body)
        if newbody != body:
            lines[i] = head + newbody
            fixed += 1
    # basicQuestions 里的 "stem"/"explanation"/"answer" 也处理
    elif re.search(r'"(stem|answer|explanation)"\s*:\s*"', ln):
        m = re.match(r'^(\s*"(stem|answer|explanation)"\s*:\s*")(.*?("\s*,?)?)$', ln)
        if m:
            head, body = m.group(1), m.group(3)
            newbody = re.sub(r'"([^"]*?)"', r'"\1"', body)
            if newbody != body:
                lines[i] = head + newbody
                fixed += 1
open(p, "w", encoding="utf-8").write("\n".join(lines))
print("fixed lines:", fixed)
