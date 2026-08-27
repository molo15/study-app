#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_papers.py — 模拟卷组卷脚本（纯数据工具，不触碰 Flutter/打包）

用题库题池生成 5 张真题风格模拟卷：
  古代汉语        40 题 / 60 分钟
  现代汉语        50 题 / 75 分钟
  中国古代文学史  45 题 / 70 分钟
  中国现代文学史  42 题 / 65 分钟
  中国当代文学史  40 题 / 60 分钟

规则：
  1. 题池优先读取 out/v08/{bank_id}.v08.json（数组形式、v3 字段），否则回退读取
     app/assets/banks/{bank_id}-v0.7.0.zip（manifest.json 的 questionFiles 每章一个 json）。
  2. 排除 chapter=='论述题专题' 的题参与客观题/简答题池；论述题（short_answer 且
     answerFormat 含「论述」）单独成池，论述题配额从该池抽取。
     ※ v0.7.0 实测：全部论述题集中在「论述题专题」章（各章 short_answer 均无论述题），
       故该章仅作为论述题来源，不参与其余题型抽样。
  3. 客观题（单选/多选/判断/填空）在前，按 题型 + 难度（易→中→难）排序；简答/论述在后。
  4. 每卷按题型分层随机抽样，seed 固定（seed + bank_id 哈希）保证可复现；
     章节覆盖用「按 chapter 分桶轮转取」尽量分散。
  5. 某题型配额超过可用题数时自动降配额，缺口补到有富余的客观题型，并打印告警。
  6. 输出 { "papers": [ {bankId, name, durationMin, questionIds:[...]}, ... ] }。
     组卷脚本不生成 paper id（`{bank_id}:paper_01` 由打包侧生成）。

用法：
  python src/build_papers.py [--dir DIR] [--seed 42] [--out out/papers/papers.json]
"""

import argparse
import json
import random
import zipfile
import zlib
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent          # tools/seed-builder
APP_ASSETS_BANKS = Path(r'D:/study_app/app/assets/banks')
DEFAULT_V08_DIR = PROJECT_ROOT / 'out' / 'v08'

# ---------------------------------------------------------------------------
# 卷定义（客观题为主、论述题 ≤15%、每卷至少 1 道论述题）
# ---------------------------------------------------------------------------
PAPER_DEFS = [
    {
        'bank_id': 'bank-gudai-hanyu',
        'short_name': '古代汉语',
        'duration_min': 60,
        'quotas': {'single_choice': 14, 'multi_choice': 4, 'true_false': 6,
                   'blank': 10, 'short_answer': 4, 'essay': 2},
    },
    {
        'bank_id': 'bank-xiandai-hanyu',
        'short_name': '现代汉语',
        'duration_min': 75,
        'quotas': {'single_choice': 18, 'multi_choice': 5, 'true_false': 8,
                   'blank': 12, 'short_answer': 5, 'essay': 2},
    },
    {
        'bank_id': 'bank-zhongguo-gudai-wenxue',
        'short_name': '中国古代文学史',
        'duration_min': 70,
        'quotas': {'single_choice': 16, 'multi_choice': 4, 'true_false': 6,
                   'blank': 12, 'short_answer': 4, 'essay': 3},
    },
    {
        'bank_id': 'bank-zhongguo-xiandai-wenxue',
        'short_name': '中国现代文学史',
        'duration_min': 65,
        'quotas': {'single_choice': 16, 'multi_choice': 3, 'true_false': 5,
                   'blank': 10, 'short_answer': 5, 'essay': 3},
    },
    {
        'bank_id': 'bank-zhongguo-dangdai-wenxue',
        'short_name': '中国当代文学史',
        'duration_min': 60,
        'quotas': {'single_choice': 16, 'multi_choice': 3, 'true_false': 4,
                   'blank': 10, 'short_answer': 4, 'essay': 3},
    },
]

# 输出顺序：客观题在前，简答/论述在后；同题型内按难度 易→中→难 排序
TYPE_ORDER = ['single_choice', 'multi_choice', 'true_false', 'blank',
              'short_answer', 'essay']
OBJECTIVE_TYPES = ['single_choice', 'multi_choice', 'true_false', 'blank']
TYPE_LABEL = {
    'single_choice': '单选', 'multi_choice': '多选', 'true_false': '判断',
    'blank': '填空', 'short_answer': '简答', 'essay': '论述',
}
DIFF_RANK = {'easy': 0, 'medium': 1, 'hard': 2}
DIFF_LABEL = {0: '易', 1: '中', 2: '难'}


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------
def stable_hash(s: str) -> int:
    """稳定非负哈希，用于种子里掺入 bank 维度，保证可复现且不同库序列不同。"""
    return zlib.crc32(s.encode('utf-8'))


def is_essay(q: dict) -> bool:
    """论述型题：short_answer 且 answerFormat 含「论述」。"""
    return q.get('type') == 'short_answer' and '论述' in (q.get('answerFormat') or '')


def qtype_of(q: dict) -> str:
    t = q.get('type')
    if t == 'short_answer':
        return 'essay' if is_essay(q) else 'short_answer'
    return t


def find_bank_source(bank_id: str, dirs, assets_banks):
    """找题库源文件，返回 (path, kind)。kind ∈ {'v08','zip'}。"""
    for d in dirs:
        d = Path(d)
        if not d.is_dir():
            continue
        v08 = d / f'{bank_id}.v08.json'
        if v08.exists():
            return v08, 'v08'
        zips = sorted(d.glob(f'{bank_id}-*.zip'))
        if zips:
            return zips[-1], 'zip'
    if assets_banks is not None:
        zips = sorted(assets_banks.glob(f'{bank_id}-*.zip'))
        if zips:
            return zips[-1], 'zip'
    return None, None


def load_bank(bank_id: str, dirs, assets_banks):
    """加载某库全部题目，返回 (bank_name, questions)。"""
    src, kind = find_bank_source(bank_id, dirs, assets_banks)
    if src is None:
        return None, []
    if kind == 'v08':
        data = json.loads(src.read_text('utf-8'))
        manifest = {}
        if isinstance(data, dict):
            manifest = data
            data = data.get('questions', data.get('items', []))
        if not isinstance(data, list):
            raise ValueError(f'{src}: v08 题目应为数组，实际 {type(data)}')
        return manifest.get('name', ''), data
    # zip 回退：manifest.questionFiles 每章一个 json
    with zipfile.ZipFile(src) as z:
        manifest = json.loads(z.read('manifest.json'))
        questions = []
        for f in manifest.get('questionFiles', []):
            questions.extend(json.loads(z.read(f)))
    return manifest.get('name', ''), questions


def bucket_by_chapter(pool, used_ids):
    """pool: [{chapter, id, ...}] → {chapter: [q,...]}，剔除已用 id 并打乱桶内顺序。"""
    buckets = defaultdict(list)
    for q in pool:
        if q['id'] in used_ids:
            continue
        buckets[q.get('chapter') or '未分类'].append(q)
    return buckets


def round_robin_sample(rng, buckets, need):
    """按 chapter 分桶轮转取，尽量分散章节覆盖。"""
    chosen = []
    chapters = [c for c, lst in buckets.items() if lst]
    rng.shuffle(chapters)
    while need > 0 and chapters:
        still = []
        for c in chapters:
            if need <= 0:
                break
            chosen.append(buckets[c].pop())
            need -= 1
            if buckets[c]:
                still.append(c)
        chapters = still
    return chosen


def adjust_quotas(bank_id, quotas, availability, warnings):
    """配额超过可用题数 → 降配额，缺口补到有富余的客观题型。返回调整后配额。"""
    adjusted = dict(quotas)
    for t in TYPE_ORDER:
        quota = adjusted.get(t, 0)
        avail = availability.get(t, 0)
        if quota <= avail:
            continue
        deficit = quota - avail
        adjusted[t] = avail
        # 选一个有富余的客观题型（排除自身）补缺口
        best, best_surplus = None, -1
        for ot in OBJECTIVE_TYPES:
            if ot == t:
                continue
            surplus = availability.get(ot, 0) - adjusted.get(ot, 0)
            if surplus > best_surplus:
                best, best_surplus = ot, surplus
        if best is not None and best_surplus > 0:
            add = min(deficit, best_surplus)
            adjusted[best] += add
            warnings.append(
                f'[{bank_id}] {TYPE_LABEL[t]}({t}) 配额 {quota} > 可用 {avail}，'
                f'降为 {avail}；缺口 {deficit} 补到 {TYPE_LABEL[best]}({best}) +{add}')
        else:
            warnings.append(
                f'[{bank_id}] {TYPE_LABEL[t]}({t}) 配额 {quota} > 可用 {avail}，'
                f'且无富余客观题型可补，该卷实际题数将少于配额')
    return adjusted


def sample_paper(rng, pool_by_type, quotas, warnings, bank_id):
    """按题型分层抽样（chapter 分桶轮转），返回 {qtype: [q,...]}。"""
    used_ids = set()
    picked = defaultdict(list)
    for t in TYPE_ORDER:
        quota = quotas.get(t, 0)
        if quota <= 0:
            continue
        buckets = bucket_by_chapter(pool_by_type.get(t, []), used_ids)
        for lst in buckets.values():
            rng.shuffle(lst)
        qs = round_robin_sample(rng, buckets, quota)
        if len(qs) < quota:
            warnings.append(
                f'[{bank_id}] {TYPE_LABEL[t]}({t}) 实际取到 {len(qs)} < 配额 {quota}，'
                f'该卷题数不足')
        for q in qs:
            picked[t].append(q)
            used_ids.add(q['id'])
    return picked


def ordered_question_ids(picked):
    """客观题在前（题型内 易→中→难），简答/论述在后。"""
    ordered = []
    for t in TYPE_ORDER:
        bucket = list(picked.get(t, []))
        bucket.sort(key=lambda q: DIFF_RANK.get(q.get('difficulty'), 1))
        ordered.extend(q['id'] for q in bucket)
    return ordered


def type_stats(picked):
    return {t: len(picked.get(t, [])) for t in TYPE_ORDER}


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description='模拟卷组卷脚本（5 张卷）')
    parser.add_argument('--dir', default=None,
                        help='题库目录（含 {bank_id}.v08.json 或 {bank_id}-*.zip）。'
                             '默认自动探测 out/v08 优先，回退 app/assets/banks')
    parser.add_argument('--seed', type=int, default=42, help='随机种子，默认 42')
    parser.add_argument('--out', default=None,
                        help='输出 json 路径，默认 out/papers/papers.json（相对脚本工程根）')
    args = parser.parse_args()

    if args.dir:
        dirs = [Path(args.dir)]
    else:
        dirs = [DEFAULT_V08_DIR]
    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = PROJECT_ROOT / out_path
    else:
        out_path = PROJECT_ROOT / 'out' / 'papers' / 'papers.json'

    print(f'[build_papers] seed={args.seed}  搜索目录: {[str(d) for d in dirs]}')
    print(f'[build_papers] 回退目录: {APP_ASSETS_BANKS}')
    print('=' * 78)

    warnings = []
    papers = []
    ok = True

    for defn in PAPER_DEFS:
        bank_id = defn['bank_id']
        bank_name, questions = load_bank(bank_id, dirs, APP_ASSETS_BANKS)
        if bank_name is None:
            print(f'\n!! [{bank_id}] 未找到题库源（v08 或 zip），跳过该卷')
            ok = False
            continue

        # 建池：论述题单独成池；论述题专题章其余内容一律排除
        pool_by_type = defaultdict(list)
        excluded = 0
        for q in questions:
            if q.get('chapter') == '论述题专题' and not is_essay(q):
                excluded += 1
                continue
            pool_by_type[qtype_of(q)].append(q)

        availability = {t: len(pool_by_type.get(t, [])) for t in TYPE_ORDER}

        print(f'\n=== {defn["short_name"]} [{bank_id}]  '
              f'来源: {bank_name or "v08"}  题目总数 {len(questions)}  '
              f'(排除专题章非论述 {excluded})')
        print('    题池:', ', '.join(f'{TYPE_LABEL[t]}={availability[t]}'
                                     for t in TYPE_ORDER))

        quotas = adjust_quotas(bank_id, defn['quotas'], availability, warnings)
        rng = random.Random(args.seed + stable_hash(bank_id))
        picked = sample_paper(rng, pool_by_type, quotas, warnings, bank_id)

        qids = ordered_question_ids(picked)
        paper = {
            'bankId': bank_id,
            'name': f'{defn["short_name"]}模拟卷一',
            'durationMin': defn['duration_min'],
            'questionIds': qids,
        }
        papers.append(paper)

        # ---- 校验 ----
        total = len(qids)
        expect = sum(quotas.values())
        stats = type_stats(picked)
        # 用全库 id->题 映射做存在性校验
        all_ids = {q['id'] for q in questions}
        missing = [qid for qid in qids if qid not in all_ids]
        dups = len(qids) - len(set(qids))

        chap_counts = Counter()
        id2q = {q['id']: q for q in questions}
        for qid in qids:
            chap_counts[id2q[qid].get('chapter', '?')] += 1

        flags = []
        if total != expect:
            flags.append(f'题数 {total} != 配额 {expect}')
            ok = False
        if missing:
            flags.append(f'存在题池外 id {len(missing)} 个')
            ok = False
        if dups:
            flags.append(f'卷内重复 id {dups} 个')
            ok = False
        if stats.get('essay', 0) < 1:
            flags.append('论述题不足 1 道')
            ok = False

        print(f'    卷内题数: {total}（配额 {expect}）  覆盖章节: {len(chap_counts)} 个')
        print('    题型分布:', ', '.join(
            f'{TYPE_LABEL[t]}={stats[t]}' for t in TYPE_ORDER if stats[t] > 0))
        print('    难度分布:', ', '.join(
            f'难={DIFF_LABEL[r]}:{n}' for r, n in
            sorted(Counter(DIFF_RANK.get(id2q[i].get('difficulty'), 1)
                           for i in qids).items())))
        print('    章节分布:', ', '.join(f'{c}×{n}' for c, n in
                                        sorted(chap_counts.items(), key=lambda kv: -kv[1])))
        if flags:
            ok = False
            print('    !! 校验告警:', '; '.join(flags))

    # ---- 输出 ----
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps({'papers': papers}, ensure_ascii=False, indent=2),
        encoding='utf-8')
    print('\n' + '=' * 78)
    print(f'[build_papers] 已写出 {len(papers)} 张卷 → {out_path}')

    if warnings:
        print('\n--- 配额告警 ---')
        for w in warnings:
            print('  ', w)
    if not ok:
        print('\n[build_papers] ⚠ 存在校验未通过项，请人工核查')
        sys.exit(1)
    print('[build_papers] 校验全部通过 ✅')


if __name__ == '__main__':
    main()
