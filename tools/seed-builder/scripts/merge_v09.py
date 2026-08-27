# -*- coding: utf-8 -*-
"""v0.9.0 合并：存量题（按审查处置归类）+ 新生成基础/测试题 → 现代汉语 v09 题库 JSON。

输入：
  out/v08/bank-xiandai-hanyu.v08.json          存量全量题（1054）
  out/v09/dispositions/<章>.json               6 章 + 论述题专题 的审查处置（含 _gaps）
  out/v09/draft/基础-<章>.json / 测试-<章>.json  阶段 C 生成 agent 的新题/改写题
  out/papers/papers.json                       模拟卷（含 questionIds，需修复被删引用）
输出：
  out/v09/bank-xiandai-hanyu.v09.json          合并后全量题（chapter 归入 6 章，purpose 归类）
处理规则：
  - keep_basic → 保留原题，purpose=basic；keep_test → purpose=test
  - rewrite   → 从 draft 文件中按原 id 找改写版（生成 agent 产出，自带 purpose）；找不到则报错退出
  - delete    → 移除
  - 论述题专题 → 按 suggestedChapter 归入真实章节（若 delete/rewrite 同样适用）
  - dispositions 中的 answerVariants 合并进题
  - mockPaper 中被删/归并的 questionIds 用同章同题型替代题补齐
校验：id 唯一、type 合法、answer 编码、chapter 命中 6 章、source 完整、purpose 合法。
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # tools/seed-builder
V08 = os.path.join(BASE, 'out', 'v08', 'bank-xiandai-hanyu.v08.json')
MATERIALS = os.path.join(BASE, 'out', 'bank-现代汉语.materials.json')
DISP_DIR = os.path.join(BASE, 'out', 'v09', 'dispositions')
DRAFT_DIR = os.path.join(BASE, 'out', 'v09', 'draft')
OUT = os.path.join(BASE, 'out', 'v09', 'bank-xiandai-hanyu.v09.json')
PAPERS = os.path.join(BASE, 'out', 'papers', 'papers.json')

CHAPTERS = ['绪论', '语音', '文字', '词汇', '语法', '修辞']
TYPE_MAP = {
    'single_choice': 'single_choice', 'multi_choice': 'multi_choice',
    'true_false': 'true_false', 'blank': 'blank', 'short_answer': 'short_answer',
}

# 现代汉语模拟卷（papers.json 中 bank 键与 bankId 的映射）
PAPER_BANK_KEY = 'xiandai-hanyu'


def load_dispositions():
    """读取全部处置文件（含论述题专题），返回 {qid: {action, suggestedChapter, answerVariants, rewriteSuggestion}}。"""
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
    """读取阶段 C 生成的 draft 文件，返回 {qid: question_json}。

    改写题：draft 中 id 与存量题一致（含 bank-xiandai-hanyu: 前缀且在 v08 中）→ 替换。
    新增题：draft 中 id 为临时 id（生成 agent 用，如 "temp:绪论:1"）→ 在 main 中统一重分配 b_/c_ 序号。
    """
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
    """为 draft 中的新增题（id 不在存量）统一分配 b_/c_ 序号，避免并行生成时的 id 冲突。

    返回 {临时id: 正式id} 映射。
    """
    mapping = {}
    basic_seq = 1
    test_seq = 1
    for qid, q in draft.items():
        if qid in existing_ids:
            continue  # 改写题保留原 id
        purpose = q.get('purpose')
        if purpose == 'basic':
            while f'bank-xiandai-hanyu:b_{basic_seq:06d}' in existing_ids:
                basic_seq += 1
            new_id = f'bank-xiandai-hanyu:b_{basic_seq:06d}'
            basic_seq += 1
        elif purpose == 'test':
            while f'bank-xiandai-hanyu:c_{test_seq:06d}' in existing_ids:
                test_seq += 1
            new_id = f'bank-xiandai-hanyu:c_{test_seq:06d}'
            test_seq += 1
        else:
            print(f'!! 新增题缺 purpose（不分配 id）: {qid}')
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
            errors.append(f'{qid} chapter 不在 6 章内: {q.get("chapter")}')
        if not q.get('source', {}).get('blockId'):
            errors.append(f'{qid} 缺 source.blockId')
        if not q.get('source', {}).get('docPath'):
            errors.append(f'{qid} 缺 source.docPath')
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
    """归一化 answerVariants：审查 agent 可能写成扁平数组 ['A','B']（契约要求分组嵌套 [['A','B']]），
    统一为分组嵌套；元素中的 '=' 分隔（如 '音色=音质'）拆成同组两个等价词。"""
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


def fill_docpath(questions):
    """新题 source 缺 docPath 时，从 materials.json 按 blockId 回填。"""
    if not os.path.exists(MATERIALS):
        return questions
    data = json.load(open(MATERIALS, encoding='utf-8'))
    block_map = {m['blockId']: m.get('docPath', '') for m in data['materials']}
    for q in questions:
        src = q.get('source') or {}
        if not src.get('docPath') and src.get('blockId') in block_map:
            q['source'] = {**src, 'docPath': block_map[src['blockId']]}
    return questions


def main():
    all_qs = json.load(open(V08, encoding='utf-8'))
    dispositions = load_dispositions()
    draft = load_draft()

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
            q = rewritten  # 改写版（生成 agent 已带 purpose/chapter）
            q['id'] = qid  # 确保改写题保留原 id
        else:
            q = dict(q)
            q['purpose'] = 'basic' if action == 'keep_basic' else 'test'
            # 归章：论述题专题按 suggestedChapter 归入真实章节
            sc = disp.get('suggestedChapter')
            if sc and sc in CHAPTERS:
                q['chapter'] = sc
            elif q.get('chapter') == '论述题专题':
                missing_disp.append(f'{qid}(论述题专题未归章)')
                continue
            # 合并审查建议的等价答案
            av = disp.get('answerVariants')
            if av:
                q['answerVariants'] = av
        kept.append(q)

    if missing_disp:
        print('!! 缺处置记录的题（不会入库）:', len(missing_disp))
        for qid in missing_disp[:20]:
            print('   ', qid)
    if missing_rewrite:
        print('!! 标 rewrite 但 draft 中无改写版的题（不会入库）:', len(missing_rewrite))
        for qid in missing_rewrite:
            print('   ', qid)

    # 新增题：统一分配 b_/c_ id
    existing_ids = {q['id'] for q in all_qs}
    id_map = assign_new_ids(draft, existing_ids)
    added = 0
    for temp_id, q in draft.items():
        if temp_id in existing_ids:
            continue  # 改写题已处理
        new_id = id_map.get(temp_id)
        if new_id is None:
            continue
        q = dict(q)
        q['id'] = new_id
        if q.get('chapter') not in CHAPTERS or q.get('purpose') not in ('basic', 'test'):
            print(f'!! 新增题缺 chapter/purpose 归位: {temp_id}')
            continue
        kept.append(q)
        added += 1

    kept = normalize_variants(kept)
    kept = fill_docpath(kept)

    errors = validate(kept)
    if errors:
        print(f'!! 校验失败 {len(errors)} 条（前 30 条）：')
        for e in errors[:30]:
            print('   ', e)
        sys.exit(1)

    # mockPaper 修复：被删/归并的 questionIds 用同章同题型替代题补齐
    fix_papers(kept)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(kept, f, ensure_ascii=False, indent=1)

    from collections import Counter
    ch = Counter(q['chapter'] for q in kept)
    pur = Counter(q['purpose'] for q in kept)
    tp = Counter(q['type'] for q in kept)
    print(f'合并完成：总 {len(kept)} 题（新增 {added}），原 1054 中保留 {len(kept) - added}')
    print('  章节:', dict(ch))
    print('  purpose:', dict(pur))
    print('  题型:', dict(tp))


def fix_papers(questions):
    """papers.json 中现代汉语模拟卷的被删题引用，用同章同题型替代题补齐。

    被删题的原章节/题型从 v08 全量题反查（v08 中保留 chapter 字段，含论述题专题），
    替代题在保留+新增题池中按 (chapter, type) 优先、放宽到同组同题型选取。
    """
    if not os.path.exists(PAPERS):
        print('  papers.json 不存在，跳过 mockPaper 修复')
        return
    papers_data = json.load(open(PAPERS, encoding='utf-8'))
    all_v08 = json.load(open(V08, encoding='utf-8'))
    v08_meta = {q['id']: q for q in all_v08}

    kept_ids = {q['id'] for q in questions}
    by_ch_type = {}
    for q in questions:
        by_ch_type.setdefault((q['chapter'], q['type']), []).append(q['id'])

    replaced = []
    for paper in papers_data.get('papers', []):
        if paper.get('bankId') != 'bank-xiandai-hanyu':
            continue
        new_ids = []
        used_in_paper = set(paper.get('questionIds', []))
        for qid in paper.get('questionIds', []):
            if qid in kept_ids:
                new_ids.append(qid)
                continue
            meta = v08_meta.get(qid, {})
            ch = meta.get('chapter')
            t = meta.get('type')
            if ch == '论述题专题':
                ch = None  # 伪章节，按题型放宽
            pool = by_ch_type.get((ch, t), []) if ch else []
            if not pool:
                # 放宽：同题型任意章节
                pool = [i for (c, tt), ids in by_ch_type.items()
                        if tt == t and ids]
            # 优先选未被本卷用过的替代题，避免卷内重复
            alt = next((i for i in pool if i not in used_in_paper), None)
            if alt is None and pool:
                alt = pool[0]
            if alt:
                new_ids.append(alt)
                used_in_paper.add(alt)
                replaced.append((qid, alt))
            else:
                new_ids.append(qid)  # 保守：无替代则保留原 id（导入时软归档）
        paper['questionIds'] = new_ids

    if replaced:
        with open(PAPERS, 'w', encoding='utf-8') as f:
            json.dump(papers_data, f, ensure_ascii=False, indent=2)
        print(f'  mockPaper 已修复 {len(replaced)} 处引用（原题 → 替代题）：')
        for old, new in replaced[:15]:
            print(f'    {old} → {new}')
    else:
        print('  mockPaper 无需修复（无被删题引用）')


if __name__ == '__main__':
    main()
