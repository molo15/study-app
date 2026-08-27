# -*- coding: utf-8 -*-
"""修复 draft JSON 中字符串值内未转义的半角双引号（替换为中文引号）。

背景：生成 agent 在 explanation/stem 中使用半角 " 标注引文，导致 JSON 解析失败。
状态机：只在字符串值内部处理；半角引号成对替换为“”。
"""
import sys
import json


def fix_file(path: str) -> int:
    content = open(path, encoding='utf-8').read()
    out = []
    in_str = False
    escaped = False
    quote_open = False
    replaced = 0
    for ch in content:
        if in_str:
            if escaped:
                out.append(ch)
                escaped = False
                continue
            if ch == '\\':
                out.append(ch)
                escaped = True
                continue
            if ch == '"':
                out.append('“' if not quote_open else '”')
                quote_open = not quote_open
                replaced += 1
                continue
            out.append(ch)
            continue
        if ch == '"':
            in_str = True
            quote_open = True
            out.append(ch)
            continue
        out.append(ch)

    fixed = ''.join(out)
    data = json.loads(fixed)  # 解析失败则抛异常，不写文件
    with open(path, 'w', encoding='utf-8') as f:
        f.write(fixed)
    return replaced, len(data)


if __name__ == '__main__':
    for p in sys.argv[1:]:
        try:
            n, total = fix_file(p)
            print(f'{p}: 修复 {n} 处引号，共 {total} 题')
        except Exception as e:
            print(f'{p}: 失败 {e}')
