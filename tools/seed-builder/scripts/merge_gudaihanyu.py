# -*- coding: utf-8 -*-
"""古代汉语合并脚本 - 将 dispositions 和 draft 合并到 v08 库

输入：
  out/v08/bank-gudai-hanyu.v08.json          存量全量题
  out/v09gudaihanyu/dispositions/<章>.json   审查处置
  out/v09gudaihanyu/draft/基础-<章>.json      基础题
  out/v09gudaihanyu/draft/测试-<章>.json      测试题
  out/papers/papers.json                       模拟卷
输出：
  out/v09gudaihanyu/bank-gudai-hanyu.v09.json  合并后全量题
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V08 = os.path.join(BASE, 'out', 'v08', 'bank-gudai-hanyu.v08.json')
DISP_DIR = os.path.join(BASE, 'out', 'v09gudaihanyu', 'dispositions')
DRAFT_DIR = os.path.join(BASE, 'out', 'v09gudaihanyu', 'draft')
OUT = os.path.join(BASE, 'out', 'v09gudaihanyu', 'bank-gudai-hanyu.v09.json')
PAPERS = os.path.join(BASE, 'out', 'papers', 'papers.json')

CHAPTERS = [
    '绪论', '文字（上）', '文字（下）', '词汇', '语法（上）', '语法（下）',
    '古书的文体', '古书的标点', '工具书简介', '修辞', '训诂', '诗词格律', '音韵'
]
TYPE_MAP = {
    'single_choice': 'single_choice', 'multi_choice': 'multi_choice',
    'true_false': 'true_false', 'blank': 'blank', 'short_answer': 'short_answer',
}
PAPER_BANK_KEY = 'gudai-hanyu'


def load_dispositions():
    """读取全部处置文件，返回 {qid: {action, ...}}"""
    result = {}
    for fname in os.listdir(DISP_DIR):
        if not fname.endswith('.json'):
            continue
        path = os.path.join(DISP_DIR, fname)
        data = json.load(open(path, encoding='utf-8'))
        for qid, disp in data.items():
            if qid.startswith('_'):
                continue
            result[qid] = disp
    return result


def load_draft():
    """读取阶段C生成的draft文件，返回 {qid: question_json}"""
    result = {}
    if not os.path.isdir(DRAFT_DIR):
        return result
    for fname in os.listdir(DRAFT_DIR):
        if not fname.endswith('.json'):
            continue
        data = json.load(open(os.path.join(DRAFT_DIR, fname), encoding='utf-8'))
        for q in data:
            if isinstance(q, dict) and q.get('id'):
                result[q['id']] = q
    return result


def assign_new_ids(draft, existing_ids):
    """为新增题分配 b_/c_ 序号"""
    mapping = {}
    basic_seq = 1
    test_seq = 1
    for qid, q in draft.items():
        if qid in existing_ids:
            continue
        purpose = q.get('purpose')
        if purpose == 'basic':
            while f'bank-gudai-hanyu:b_{basic_seq:06d}' in existing_ids:
                basic_seq += 1
            new_id = f'bank-gudai-hanyu:b_{basic_seq:06d}'
            basic_seq += 1
        elif purpose == 'test':
            while f'bank-gudai-hanyu:c_{test_seq:06d}' in existing_ids:
                test_seq += 1
            new_id = f'bank-gudai-hanyu:c_{test_seq:06d}'
            test_seq += 1
        else:
            print(f'!! 新增题缺 purpose: {qid}')
            continue
        mapping[qid] = new_id
        existing_ids.add(new_id)
    return mapping


def validate(questions):
    errors = []
    seen = set()
    for q in questions:
        qid = q.get('id', '')
        if qid in seen:
            errors.append(f'id 重复: {qid}')
        seen.add(qid)
        t = q.get('type')
        if t not in TYPE_MAP:
            errors.append(f'{qid} 未知题型: {t}')
        if q.get('chapter') not in CHAPTERS:
            errors.append(f'{qid} chapter 不在章节内: {q.get("chapter")}')
        # 新题(b_/c_)允许无blockId，只要source不为空
        if not q.get('source'):
            errors.append(f'{qid} 缺 source')
        ans = q.get('answer')
        if t == 'true_false' and ans not in ('正确', '错误'):
            errors.append(f'{qid} 判断题 answer 非法: {ans}')
        if t == 'single_choice':
            keys = {o.get('key') for o in q.get('options', [])}
            if ans not in keys:
                errors.append(f'{qid} 单选 answer 不在选项内: {ans}')
        if t == 'multi_choice':
            keys = {o.get('key') for o in q.get('options', [])}
            if not isinstance(ans, list) or not set(ans).issubset(keys):
                errors.append(f'{qid} 多选 answer 非法: {ans}')
        if t == 'blank' and not ans:
            errors.append(f'{qid} 填空 answer 为空')
        if t == 'short_answer' and not ans:
            errors.append(f'{qid} 简答 answer 为空')
        p = q.get('purpose')
        if p not in ('basic', 'test'):
            errors.append(f'{qid} purpose 非法: {p}')
        av = q.get('answerVariants')
        if av is not None:
            if not isinstance(av, list) or not all(isinstance(g, list) and g for g in av):
                errors.append(f'{qid} answerVariants 格式非法: {av}')
    return errors


def normalize_variants(questions):
    """归一化 answerVariants"""
    for q in questions:
        av = q.get('answerVariants')
        if not av:
            continue
        groups = []
        for g in av:
            if not isinstance(g, list):
                continue
            items = []
            for item in g:
                if not isinstance(item, str):
                    continue
                if '=' in item:
                    for part in item.split('='):
                        part = part.strip()
                        if part:
                            items.append(part)
                elif item.strip():
                    items.append(item.strip())
            if items:
                groups.append(items)
        q['answerVariants'] = groups if groups else []
    return questions


def main():
    print("=== 古代汉语合并 ===")
    print(f"读取 v08 库: {V08}")
    all_qs = json.load(open(V08, encoding='utf-8'))
    print(f"  存量题: {len(all_qs)} 题")

    print(f"读取处置文件: {DISP_DIR}")
    dispositions = load_dispositions()
    print(f"  处置: {len(dispositions)} 题")

    print(f"读取 draft 文件: {DRAFT_DIR}")
    draft = load_draft()
    print(f"  draft: {len(draft)} 题")

    kept = []
    missing_disp = []
    missing_rewrite = []

    for q in all_qs:
        qid = q['id']
        disp = dispositions.get(qid)
        if disp is None:
            missing_disp.append(qid)
            continue
        action = disp.get('action')
        if action == 'delete':
            continue
        if action == 'rewrite':
            rewritten = draft.get(qid)
            if rewritten is None:
                missing_rewrite.append(qid)
                continue
            q = rewritten
            q['id'] = qid
        else:
            q = dict(q)
            q['purpose'] = 'basic' if action == 'keep_basic' else 'test'
            sc = disp.get('suggestedChapter')
            if sc and sc in CHAPTERS:
                q['chapter'] = sc
            elif q.get('chapter') == '论述题专题':
                missing_disp.append(f'{qid}(论述题专题未归章)')
                continue
            av = disp.get('answerVariants')
            if av:
                q['answerVariants'] = av
        kept.append(q)

    if missing_disp:
        print(f'!! 缺处置记录的题: {len(missing_disp)}')
        for qid in missing_disp[:10]:
            print('   ', qid)
    if missing_rewrite:
        print(f'!! 标 rewrite 但 draft 中无改写版的题: {len(missing_rewrite)}')
        for qid in missing_rewrite:
            print('   ', qid)

    existing_ids = {q['id'] for q in all_qs}
    id_map = assign_new_ids(draft, existing_ids)
    added = 0
    for temp_id, q in draft.items():
        if temp_id in existing_ids:
            continue
        new_id = id_map.get(temp_id)
        if new_id is None:
            continue
        q = dict(q)
        q['id'] = new_id
        if q.get('chapter') not in CHAPTERS or q.get('purpose') not in ('basic', 'test'):
            print(f'!! 新增题缺 chapter/purpose: {temp_id}')
            continue
        kept.append(q)
        added += 1

    kept = normalize_variants(kept)

    errors = validate(kept)
    if errors:
        print(f'!! 校验失败 {len(errors)} 条（前 30 条）：')
        for e in errors[:30]:
            print('   ', e)
        sys.exit(1)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(kept, f, ensure_ascii=False, indent=1)

    from collections import Counter
    ch = Counter(q['chapter'] for q in kept)
    pur = Counter(q['purpose'] for q in kept)
    tp = Counter(q['type'] for q in kept)
    print(f'合并完成：总 {len(kept)} 题（新增 {added}），原 {len(all_qs)} 中保留 {len(kept) - added}')
    print('  章节:', dict(ch))
    print('  purpose:', dict(pur))
    print('  题型:', dict(tp))


if __name__ == '__main__':
    main()
