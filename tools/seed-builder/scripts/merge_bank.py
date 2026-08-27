# -*- coding: utf-8 -*-
"""通用 v0.9.0 合并：存量题（按审查处置归类）+ 新生成基础/测试题 → 题库 v09 JSON。

用法：python scripts/merge_bank.py <bank_key>

bank_key 配置见 BANK_CONFIG（materials 文件名 / v08 文件名 / 章节清单 / 工作目录 / 模拟卷 bankId）。
逻辑与 merge_v09.py 一致：keep/rewrite/delete、论述题专题归章、answerVariants 合并与归一化、
docPath 回填、新增题统一分配 b_/c_ id、mockPaper 被删引用用同章同题型替代。
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # tools/seed-builder
PAPERS = os.path.join(BASE, 'out', 'papers', 'papers.json')

BANK_CONFIG = {
    'zhongguo-xiandai-wenxue': {
        'bank_id': 'bank-zhongguo-xiandai-wenxue',
        'paper_bank_id': 'bank-zhongguo-xiandai-wenxue',
        'v08': os.path.join(BASE, 'out', 'v08', 'bank-zhongguo-xiandai-wenxue.v08.json'),
        'materials': os.path.join(BASE, 'out', 'bank-中国现代文学史.materials.json'),
        'workdir': os.path.join(BASE, 'out', 'v09xiandaiwenxue'),
        'chapters': [
            # 拆归后目标章节 = 素材章体系（细章）
            '文学思潮与运动（一）', '文学思潮与运动（二）', '文学思潮与运动（三）',
            '小说（一）', '小说（二）', '小说（三）',
            '新诗（一）', '新诗（二）', '新诗（三）',
            '散文（一）', '散文（二）', '散文（三）',
            '戏剧', '戏剧（二）', '戏剧（三）',
            '鲁迅（一）', '鲁迅（二）', '巴金', '老舍', '茅盾', '沈从文',
            '曹禺', '赵树理', '郭沫若', '艾青',
            '市民通俗小说（一）', '市民通俗小说（二）', '智识阶层形象谱系',
            '综合专题',
        ],
    },
    'zhongguo-gudai-wenxue': {
        'bank_id': 'bank-zhongguo-gudai-wenxue',
        'paper_bank_id': 'bank-zhongguo-gudai-wenxue',
        'v08': os.path.join(BASE, 'out', 'v08', 'bank-zhongguo-gudai-wenxue.v08.json'),
        'materials': os.path.join(BASE, 'out', 'bank-中国古代文学史.materials.json'),
        'workdir': os.path.join(BASE, 'out', 'v09gudaiwenxue'),
        'chapters': [
            '先秦文学', '秦汉文学', '魏晋南北朝文学', '隋唐五代文学',
            '宋代文学', '明代文学', '元代文学', '清代文学', '近代文学',
        ],
        'allow_textbook_source': True,  # 元代/清代/近代无素材，允许 source.blockId='textbook-standard' 占位
    },
    'gudai-hanyu': {
        'bank_id': 'bank-gudai-hanyu',
        'paper_bank_id': 'bank-gudai-hanyu',
        'v08': os.path.join(BASE, 'out', 'v08', 'bank-gudai-hanyu.v08.json'),
        'materials': os.path.join(BASE, 'out', 'bank-古代汉语.materials.json'),
        'workdir': os.path.join(BASE, 'out', 'v09gudaihanyu'),
        'chapters': [
            '修辞', '古书的文体', '古书的标点', '工具书简介',
            '文字（上）', '文字（下）', '绪论', '训诂', '词汇',
            '诗词格律', '语法（上）', '语法（下）', '音韵',
        ],
        'allow_textbook_source': False,
    },
}

TYPE_MAP = {
    'single_choice': 'single_choice', 'multi_choice': 'multi_choice',
    'true_false': 'true_false', 'blank': 'blank', 'short_answer': 'short_answer',
}


def load_dispositions(disp_dir):
    result = {}
    for fname in os.listdir(disp_dir):
        if not fname.endswith('.json'):
            continue
        data = json.load(open(os.path.join(disp_dir, fname), encoding='utf-8'))
        for qid, disp in data.items():
            if qid.startswith('_'):
                continue
            result[qid] = disp
    return result


def load_draft(draft_dir):
    result = {}
    if not os.path.isdir(draft_dir):
        return result
    for fname in os.listdir(draft_dir):
        if not fname.endswith('.json'):
            continue
        data = json.load(open(os.path.join(draft_dir, fname), encoding='utf-8'))
        for q in data:
            if isinstance(q, dict) and q.get('id'):
                result[q['id']] = q
    return result


def assign_new_ids(draft, existing_ids):
    mapping = {}
    basic_seq = 1
    test_seq = 1
    for qid, q in draft.items():
        if qid in existing_ids:
            continue
        purpose = q.get('purpose')
        if purpose == 'basic':
            while f'{BANK_ID}:b_{basic_seq:06d}' in existing_ids:
                basic_seq += 1
            new_id = f'{BANK_ID}:b_{basic_seq:06d}'
            basic_seq += 1
        elif purpose == 'test':
            while f'{BANK_ID}:c_{test_seq:06d}' in existing_ids:
                test_seq += 1
            new_id = f'{BANK_ID}:c_{test_seq:06d}'
            test_seq += 1
        else:
            print(f'!! 新增题缺 purpose: {qid}')
            continue
        mapping[qid] = new_id
        existing_ids.add(new_id)
    return mapping


def normalize_variants(questions):
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


def fill_docpath(questions, materials_path):
    if not os.path.exists(materials_path):
        return questions
    data = json.load(open(materials_path, encoding='utf-8'))
    block_map = {m['blockId']: m.get('docPath', '') for m in data['materials']}
    for q in questions:
        src = q.get('source') or {}
        if not src.get('docPath') and src.get('blockId') in block_map:
            q['source'] = {**src, 'docPath': block_map[src['blockId']]}
    return questions


def validate(questions, chapters, allow_textbook_source=False):
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
        if q.get('chapter') not in chapters:
            errors.append(f'{qid} chapter 不在章节内: {q.get("chapter")}')
        if not q.get('source', {}).get('blockId'):
            errors.append(f'{qid} 缺 source.blockId')
        if not q.get('source', {}).get('docPath'):
            if not (allow_textbook_source and q.get('source', {}).get('blockId') == 'textbook-standard'):
                errors.append(f'{qid} 缺 source.docPath')
        ans = q.get('answer')
        if t == 'true_false' and ans not in ('正确', '错误'):
            errors.append(f'{qid} 判断 answer 非法: {ans}')
        if t == 'single_choice':
            keys = {o.get('key') for o in q.get('options', [])}
            if ans not in keys:
                errors.append(f'{qid} 单选 answer 不在选项: {ans}')
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


def fix_papers(questions, paper_bank_id, v08_path):
    if not os.path.exists(PAPERS):
        print('  papers.json 不存在，跳过 mockPaper 修复')
        return
    papers_data = json.load(open(PAPERS, encoding='utf-8'))
    all_v08 = json.load(open(v08_path, encoding='utf-8'))
    v08_meta = {q['id']: q for q in all_v08}

    kept_ids = {q['id'] for q in questions}
    by_ch_type = {}
    for q in questions:
        by_ch_type.setdefault((q['chapter'], q['type']), []).append(q['id'])

    replaced = []
    for paper in papers_data.get('papers', []):
        if paper.get('bankId') != paper_bank_id:
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
                ch = None
            pool = by_ch_type.get((ch, t), []) if ch else []
            if not pool:
                pool = [id_ for (c, tt), id_list in by_ch_type.items()
                        if tt == t and id_list for id_ in id_list]
            alt = next((i for i in pool if i not in used_in_paper), None)
            if alt is None and pool:
                alt = pool[0]
            if alt:
                new_ids.append(alt)
                used_in_paper.add(alt)
                replaced.append((qid, alt))
            else:
                new_ids.append(qid)
        paper['questionIds'] = new_ids

    if replaced:
        with open(PAPERS, 'w', encoding='utf-8') as f:
            json.dump(papers_data, f, ensure_ascii=False, indent=2)
        print(f'  mockPaper 已修复 {len(replaced)} 处引用：')
        for old, new in replaced[:15]:
            print(f'    {old} → {new}')
    else:
        print('  mockPaper 无需修复（无被删题引用）')


def main(bank_key):
    global BANK_ID
    cfg = BANK_CONFIG[bank_key]
    BANK_ID = cfg['bank_id']
    chapters = cfg['chapters']
    workdir = cfg['workdir']
    disp_dir = os.path.join(workdir, 'dispositions')
    draft_dir = os.path.join(workdir, 'draft')
    out_path = os.path.join(workdir, f'{BANK_ID}.v09.json')

    all_qs = json.load(open(cfg['v08'], encoding='utf-8'))
    dispositions = load_dispositions(disp_dir)
    draft = load_draft(draft_dir)

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
            if sc and sc in chapters:
                q['chapter'] = sc
            elif q.get('chapter') == '论述题专题':
                missing_disp.append(f'{qid}(论述题专题未归章)')
                continue
            av = disp.get('answerVariants')
            if av:
                q['answerVariants'] = av
        kept.append(q)

    if missing_disp:
        print('!! 缺处置记录的题（不会入库）:', len(missing_disp))
        for qid in missing_disp[:20]:
            print('   ', qid)
    if missing_rewrite:
        print('!! 标 rewrite 但 draft 无改写版的题（不会入库）:', len(missing_rewrite))
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
        if q.get('chapter') not in chapters or q.get('purpose') not in ('basic', 'test'):
            print(f'!! 新增题缺 chapter/purpose 归位: {temp_id}')
            continue
        kept.append(q)
        added += 1

    kept = normalize_variants(kept)
    kept = fill_docpath(kept, cfg['materials'])

    errors = validate(kept, chapters, cfg.get('allow_textbook_source', False))
    if errors:
        print(f'!! 校验失败 {len(errors)} 条（前 30 条）：')
        for e in errors[:30]:
            print('   ', e)
        sys.exit(1)

    fix_papers(kept, cfg['paper_bank_id'], cfg['v08'])

    os.makedirs(workdir, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
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
    main(sys.argv[1])
