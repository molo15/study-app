# -*- coding: utf-8 -*-
"""通用章节准备：从 materials.json 抽素材 + 从 v08 拆存量题，供逐章审查/生成。

用法：python scripts/prep_bank.py <bank_key> [--workdir out/vXX]

bank_key 映射（materials 文件名 / v08 文件名 / 章节清单）在 BANK_CONFIG 中。
输出：
  {workdir}/materials/<章>.txt   笔记素材（h 标题 → ## 行，正文 [blockId] 前缀）
  {workdir}/existing/<章>.json   存量题拆分（含 论述题专题）
"""
import argparse
import json
import os
import re
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # tools/seed-builder

# bank_key: (materials文件基名, v08文件基名, 素材章清单, 存量章清单)
BANK_CONFIG = {
    'zhongguo-dangdai-wenxue': {
        'mat': 'bank-中国当代文学史.materials.json',
        'v08': 'bank-zhongguo-dangdai-wenxue.v08.json',
        'mat_chapters': [
            '第一章 1949-1976 文学思潮', '第二章 50、60 年代小说',
            '第三章 50、60 年代新诗', '第四章 50、60 年代戏剧、散文',
            '第五章 80、90 年代文学思潮', '第六章 80 年代小说',
            '第七章 90 年代小说', '第八章 80、90 年代新诗',
            '第九章 80、90 年代戏剧', '第十章 80、90 年代散文',
            '第十一章 台港文学', '第十二章 2000-2016 年文学概述',
        ],
        'nav_chapters': ['上编 十七年文学（1949-1976）', '中编 新时期文学（1978-1999）',
                         '下编 台港文学与世纪之交', '中国当代文学史'],
    },
    'zhongguo-xiandai-wenxue': {
        'mat': 'bank-中国现代文学史.materials.json',
        'v08': 'bank-zhongguo-xiandai-wenxue.v08.json',
        # 素材章：小说（一）=五四小说、（二）=三十小说、（三）=四十小说，思潮/新诗/散文同理
        'mat_chapters': [
            '文学思潮与运动（一）', '文学思潮与运动（二）', '文学思潮与运动（三）',
            '小说（一）', '小说（二）', '小说（三）',
            '新诗（一）', '新诗（二）', '新诗（三）',
            '散文（一）', '散文（二）', '散文（三）',
            '戏剧', '戏剧（二）', '戏剧（三）',
            '鲁迅（一）', '鲁迅（二）', '巴金', '老舍', '茅盾', '沈从文',
            '曹禺', '赵树理', '郭沫若', '艾青',
            '市民通俗小说（一）', '市民通俗小说（二）', '智识阶层形象谱系',
        ],
        # 存量章：三个时期大章 + 碎片章（碎片章与素材章对齐）
        'existing_chapters': [
            '五四时期（1917-1927）', '三十年代（1928-1937）', '四十年代（1937-1949）',
            '文学思潮与运动（一）', '文学思潮与运动（二）', '文学思潮与运动（三）',
            '小说（一）', '小说（二）', '小说（三）',
            '新诗（一）', '新诗（二）', '新诗（三）',
            '散文（一）', '散文（二）', '散文（三）',
            '戏剧', '戏剧（二）', '戏剧（三）',
            '鲁迅（一）', '鲁迅（二）', '巴金', '老舍', '茅盾', '沈从文',
            '曹禺', '赵树理', '郭沫若', '艾青',
            '市民通俗小说（一）', '综合专题',
        ],
        'nav_chapters': ['中国现代文学史'],
    },
    'zhongguo-gudai-wenxue': {
        'mat': 'bank-中国古代文学史.materials.json',
        'v08': 'bank-zhongguo-gudai-wenxue.v08.json',
        # 素材章：6 个有素材的真实章节；元代/清代/近代素材无（存量题来自外部题库，审查重点把关）
        'mat_chapters': [
            '先秦文学', '秦汉文学', '魏晋南北朝文学',
            '隋唐五代文学', '宋代文学', '明代文学',
        ],
        'existing_chapters': [
            '先秦文学', '秦汉文学', '魏晋南北朝文学',
            '隋唐五代文学', '宋代文学', '明代文学',
            '元代文学', '清代文学', '近代文学',
        ],
        'nav_chapters': ['上编 先秦两汉文学', '中编 魏晋隋唐文学', '中国古代文学史'],
    },
    'gudai-hanyu': {
        'mat': 'bank-古代汉语.materials.json',
        'v08': 'bank-gudai-hanyu.v08.json',
        # 素材章：13 个（胡安顺体系）
        'mat_chapters': [
            '修辞', '古书的文体', '古书的标点', '工具书简介',
            '文字（上）', '文字（下）', '绪论', '训诂', '词汇',
            '诗词格律', '语法（上）', '语法（下）', '音韵',
        ],
        'existing_chapters': [
            '修辞', '古书的文体', '古书的标点', '工具书简介',
            '文字（上）', '文字（下）', '绪论', '训诂', '词汇',
            '诗词格律', '语法（上）', '语法（下）', '音韵',
        ],
        'nav_chapters': ['上编 基础知识', '下编 音韵训诂与格律', '中编 语言文字学', '古代汉语'],
    },
}


def extract_materials(cfg, workdir):
    src = os.path.join(BASE, 'out', cfg['mat'])
    out_dir = os.path.join(workdir, 'materials')
    os.makedirs(out_dir, exist_ok=True)
    data = json.load(open(src, encoding='utf-8'))
    mats = data['materials']
    buckets = {ch: [] for ch in cfg['mat_chapters']}
    skipped = 0
    for m in mats:
        ch = m.get('chapter', '')
        if ch in cfg['nav_chapters']:
            skipped += 1
            continue
        if ch not in buckets:
            continue
        buckets[ch].append(m)
    total = 0
    for ch in cfg['mat_chapters']:
        items = buckets[ch]
        lines = [f'# 章节素材：{ch}（{len(items)} 条笔记块）', '']
        for m in items:
            block_id = m.get('blockId', '')
            t = m.get('type', '')
            content = (m.get('content') or '').strip()
            if not content:
                continue
            if t == 'h':
                lines.append(f'## [{block_id}] {content}')
            else:
                lines.append(f'[{block_id}] {content}')
            lines.append('')
        out_path = os.path.join(out_dir, f'{ch}.txt')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        total += len(items)
        print(f'  素材 {ch}: {len(items)} 条 -> {out_path}')
    print(f'  导航块跳过: {skipped}，合计写入: {total}')


def split_existing(cfg, workdir):
    src = os.path.join(BASE, 'out', 'v08', cfg['v08'])
    out_dir = os.path.join(workdir, 'existing')
    os.makedirs(out_dir, exist_ok=True)
    qs = json.load(open(src, encoding='utf-8'))
    chapters = cfg['existing_chapters'] + ['论述题专题']
    buckets = {ch: [] for ch in chapters}
    unknown = []
    for q in qs:
        ch = q.get('chapter', '')
        if ch in buckets:
            buckets[ch].append(q)
        else:
            unknown.append((ch, q.get('id')))
    for ch in chapters:
        out_path = os.path.join(out_dir, f'{ch}.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(buckets[ch], f, ensure_ascii=False, indent=1)
        print(f'  存量 {ch}: {len(buckets[ch])}')
    if unknown:
        print('  未知章节:', unknown)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bank_key', choices=list(BANK_CONFIG.keys()))
    ap.add_argument('--workdir', default=None, help='工作目录')
    args = ap.parse_args()
    cfg = BANK_CONFIG[args.bank_key]
    workdir = args.workdir or os.path.join(BASE, 'out', f'v09{args.bank_key.replace("zhongguo-", "").replace("-", "")}')
    os.makedirs(workdir, exist_ok=True)
    print(f'== 准备：{args.bank_key}，workdir={workdir}')
    extract_materials(cfg, workdir)
    print('---')
    split_existing(cfg, workdir)


if __name__ == '__main__':
    main()
