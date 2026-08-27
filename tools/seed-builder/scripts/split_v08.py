# -*- coding: utf-8 -*-
"""把 v08 现代汉语全量题按章拆出，供逐章审查 agent 使用。

输入：out/v08/bank-xiandai-hanyu.v08.json（1054 题）
输出：out/v09/existing/<章>.json —— 6 个真实章节 + 论述题专题.json（46 题，待审查拆归）
说明：只按 chapter 字段拆分，不动题目内容；论述题专题的拆归由审查阶段判定后
      由 merge_v09.py 执行（通过 reports 中的建议 chapter 字段）。
"""
import json
import os
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # tools/seed-builder
SRC = os.path.join(BASE, 'out', 'v08', 'bank-xiandai-hanyu.v08.json')
OUT_DIR = os.path.join(BASE, 'out', 'v09', 'existing')

CHAPTERS = ['绪论', '语音', '文字', '词汇', '语法', '修辞', '论述题专题']


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    qs = json.load(open(SRC, encoding='utf-8'))

    buckets = {ch: [] for ch in CHAPTERS}
    unknown = []
    for q in qs:
        ch = q.get('chapter', '')
        if ch in buckets:
            buckets[ch].append(q)
        else:
            unknown.append((ch, q.get('id')))

    summary = []
    for ch in CHAPTERS:
        out_path = os.path.join(OUT_DIR, f'{ch}.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(buckets[ch], f, ensure_ascii=False, indent=1)
        summary.append((ch, len(buckets[ch])))

    print('章节拆分结果：')
    for ch, n in summary:
        print(f'  {ch}: {n}')
    if unknown:
        print('未知章节（需处理）:')
        for ch, qid in unknown:
            print(f'  {ch} | {qid}')


if __name__ == '__main__':
    main()
