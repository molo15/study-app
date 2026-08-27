# -*- coding: utf-8 -*-
"""抽取现代汉语 6 章笔记素材为文本文件，供逐章审查/生成 agent 阅读。

输入：out/bank-现代汉语.materials.json（materials 数组，每元素含 chapter/type/content/markdown/blockId/docPath）
输出：out/v09/materials/<章>.txt —— h 标题块转为 markdown 标题行，p 正文块原样输出；
      行首标注 [blockId] 便于生成题时回填 source。
排除：chapter 为编级组名/“现代汉语”的目录导航块（无正文内容）。
"""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # tools/seed-builder
SRC = os.path.join(BASE, 'out', 'bank-现代汉语.materials.json')
OUT_DIR = os.path.join(BASE, 'out', 'v09', 'materials')

CHAPTERS = ['绪论', '语音', '文字', '词汇', '语法', '修辞']
NAV_CHAPTERS = {'上编 语音与文字', '中编 词汇与语法', '下编 修辞', '现代汉语'}


def heading_level(markdown: str) -> str:
    """materials 的 h 块 markdown 形如 '## 三、汉字的特点 ★★...'，还原标题层级。"""
    md = (markdown or '').strip()
    if md.startswith('#'):
        return md
    return md


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    data = json.load(open(SRC, encoding='utf-8'))
    mats = data['materials']

    buckets = {ch: [] for ch in CHAPTERS}
    skipped = 0
    for m in mats:
        ch = m.get('chapter', '')
        if ch in NAV_CHAPTERS:
            skipped += 1
            continue
        if ch not in buckets:
            continue  # 非 6 章范围（不应存在）
        buckets[ch].append(m)

    total = 0
    for ch in CHAPTERS:
        items = buckets[ch]
        lines = [f'# 章节素材：{ch}（{len(items)} 条笔记块）', '']
        for m in items:
            block_id = m.get('blockId', '')
            doc_path = m.get('docPath', '')
            t = m.get('type', '')
            content = (m.get('content') or '').strip()
            if not content:
                continue
            if t == 'h':
                lines.append(f'## [{block_id}] {content}')
            else:
                lines.append(f'[{block_id}] {content}')
            lines.append('')
        out_path = os.path.join(OUT_DIR, f'{ch}.txt')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        total += len(items)
        print(f'{ch}: {len(items)} 条 -> {out_path}')

    print(f'导航块跳过: {skipped}，合计写入: {total}')


if __name__ == '__main__':
    main()
