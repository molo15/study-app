#!/usr/bin/env python3
"""
T1 题库校验 + 打包
- 校验：JSON 合法 / id 唯一且符合前缀 / chapter 非空 / 答案可验证 / source 完整 / 题型配比统计
- 打包：manifest.json(formatVersion=3, questionFiles) + questions/目录(练习/真题改编分文件) → zip
"""
import json, os, re, sys, zipfile
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # tools/seed-builder/
T1_DIR = os.path.join(BASE, 'out', 't1')
OUT_DIR = os.path.join(BASE, 'out', 'packages')

BANKS = [
    ('bank-gudai-hanyu', '考研 · 古代汉语', '0.1.0'),
    ('bank-xiandai-hanyu', '考研 · 现代汉语', '0.1.0'),
    ('bank-zhongguo-gudai-wenxue', '考研 · 中国古代文学史', '0.1.0'),
    ('bank-zhongguo-xiandai-wenxue', '考研 · 中国现代文学史', '0.1.0'),
    ('bank-zhongguo-dangdai-wenxue', '考研 · 中国当代文学史', '0.1.0'),
]

CHOICE_TYPES = {'single_choice', 'multi_choice', 'true_false'}
FREE_TYPES = {'blank', 'short_answer'}

def validate(bank_id, questions):
    errors, warns = [], []
    ids = set()
    type_counter = Counter()
    chapter_counter = Counter()
    diff_counter = Counter()
    source_kind = Counter()
    variant_counter = Counter()
    for q in questions:
        # id 唯一 + 前缀
        qid = q.get('id', '')
        if not qid.startswith(f'{bank_id}:q_'):
            errors.append(f'id 前缀错误: {qid}')
        if qid in ids:
            errors.append(f'id 重复: {qid}')
        ids.add(qid)
        # chapter
        if not q.get('chapter'):
            errors.append(f'{qid} 缺 chapter')
        else:
            chapter_counter[q['chapter']] += 1
        # type
        t = q.get('type')
        type_counter[t] += 1
        if t not in CHOICE_TYPES | FREE_TYPES:
            errors.append(f'{qid} 未知题型 {t}')
        # answer
        ans = q.get('answer')
        if t == 'true_false':
            # 判断题：答案必须为「正确/错误」，options 可空（App 端自动渲染两个选项）
            if ans not in ('正确', '错误'):
                errors.append(f'{qid} 判断题答案必须为 正确/错误: {ans}')
        elif t == 'single_choice':
            keys = {o['key'] for o in q.get('options', [])}
            if ans not in keys:
                errors.append(f'{qid} 单选答案不在 options: {ans}')
        elif t == 'multi_choice':
            keys = {o['key'] for o in q.get('options', [])}
            if not isinstance(ans, list) or not set(ans).issubset(keys):
                errors.append(f'{qid} 多选答案不合法: {ans}')
        elif t in FREE_TYPES:
            if not ans:
                errors.append(f'{qid} 缺 answer')
            if t == 'short_answer' and not q.get('answerFormat'):
                warns.append(f'{qid} 简答缺 answerFormat')
        else:
            errors.append(f'{qid} 未知题型 {t}')
        # source
        src = q.get('source', {})
        if not src.get('blockId') or not src.get('docPath'):
            errors.append(f'{qid} source 缺 blockId/docPath')
        source_kind[src.get('kind', 'exercise')] += 1
        # difficulty
        diff_counter[q.get('difficulty')] += 1
        # 变式标注（explanation 末尾）
        expl = q.get('explanation', '')
        for v in ('基础', '变式', '拓展'):
            if f'（{v}）' in expl or f'({v})' in expl:
                variant_counter[v] += 1
                break
    return {
        'errors': errors, 'warns': warns,
        'type_counter': dict(type_counter),
        'chapter_counter': dict(chapter_counter),
        'diff_counter': dict(diff_counter),
        'source_kind': dict(source_kind),
        'variant_counter': dict(variant_counter),
    }

def pack(bank_id, name, version, questions):
    """按 练习/真题改编 拆文件 + manifest(v3) → zip"""
def sanitize(name):
    """文件名安全化（章名可能含特殊字符）"""
    return re.sub(r'[\\/:*?"<>|]', '_', name)

# ---- 编分组配置（manifest.chapters 两级：group → chapters，按学科标准） ----
def chapter_groups(bank_id, chapters):
    """返回 [{'group':..,'chapters':[..]}, ..]；未归组章节放「其他」"""
    def xiandai_wenxue(ch):
        if ch.startswith('五四'): return '五四时期（1917-1927）'
        if ch.startswith('三十'): return '三十年代（1928-1937）'
        if ch.startswith('四十'): return '四十年代（1937-1949）'
        return '综合专题'
    def dangdai_wenxue(ch):
        pre = ch[:2]
        if pre in ('第一','第二','第三','第四'): return '上编 十七年文学（1949-1976）'
        if pre in ('第五','第六','第七','第八','第九','第十'): return '中编 新时期文学（1978-1999）'
        return '下编 台港文学与世纪之交'
    MAPS = {
        'bank-gudai-hanyu': lambda c: '上编 基础知识' if c in ('修辞','古书的标点','工具书简介') else (
            '中编 语言文字学' if c.startswith(('文字','词汇','语法')) else '下编 音韵训诂与格律'),
        'bank-xiandai-hanyu': lambda c: '上编 语音与文字' if c in ('绪论','语音','文字') else (
            '中编 词汇与语法' if c in ('词汇','语法') else '下编 修辞'),
        'bank-zhongguo-gudai-wenxue': lambda c: '上编 先秦两汉文学' if c in ('先秦文学','秦汉文学') else (
            '中编 魏晋隋唐文学' if c in ('魏晋南北朝文学','隋唐五代文学') else '下编 宋元明清文学'),
        'bank-zhongguo-xiandai-wenxue': xiandai_wenxue,
        'bank-zhongguo-dangdai-wenxue': dangdai_wenxue,
    }
    fn = MAPS.get(bank_id, lambda c: '全部')
    groups = {}
    for ch in chapters:
        groups.setdefault(fn(ch), []).append(ch)
    return [{'group': g, 'chapters': sorted(v)} for g, v in sorted(groups.items())]

def split_by_chapter(items):
    """按完整章名精确分组——一章一个文件（用户要求：一章一章分开生成）"""
    groups = {}
    for q in items:
        ch = q['chapter']
        groups.setdefault(ch, []).append(q)
    return groups

def pack(bank_id, name, version, questions):
    """按章节拆文件 + manifest(v3) → zip（题库统一：每章一个文件，无类别前缀）"""
    os.makedirs(OUT_DIR, exist_ok=True)
    zip_path = os.path.join(OUT_DIR, f'{bank_id}-v{version}.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        manifest = {
            'formatVersion': 3,
            'bankId': bank_id,
            'name': name,
            'version': version,
            'generatedAt': '2026-08-16T12:00:00+08:00',
            'chapters': chapter_groups(bank_id, sorted({q['chapter'] for q in questions})),
            'questionFiles': [],
            'mockPapers': [],
        }
        # questions/ 目录：每章一个文件 <章>.json（真题/课后题/练习统一并入对应章）
        for ch, qs in split_by_chapter(questions).items():
            fname = f'questions/{sanitize(ch)}.json'
            zf.writestr(fname, json.dumps(qs, ensure_ascii=False, indent=2))
            manifest['questionFiles'].append(fname)
        zf.writestr('manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2))
    return zip_path, len(questions), 0

def main():
    os.makedirs(T1_DIR, exist_ok=True)
    print('=' * 60)
    total = 0
    for bank_id, name, version in BANKS:
        t1 = os.path.join(T1_DIR, f'{bank_id}.t1.json')
        if not os.path.exists(t1):
            print(f'!! 缺失: {t1}')
            continue
        data = json.load(open(t1, encoding='utf-8'))
        questions = data.get('questions', [])
        total += len(questions)
        r = validate(bank_id, questions)
        print(f'\n【{name}】{len(questions)} 题')
        print(f'  题型: {r["type_counter"]}')
        print(f'  难度: {r["diff_counter"]}')
        print(f'  来源: {r["source_kind"]}')
        print(f'  变式: {r["variant_counter"]}')
        print(f'  章节: {len(r["chapter_counter"])} 章')
        if r['errors']:
            print(f'  ❌ 错误 {len(r["errors"])} 条: {r["errors"][:5]}')
        if r['warns']:
            print(f'  ⚠️ 警告 {len(r["warns"])} 条: {r["warns"][:5]}')
        if not r['errors']:
            zip_path, n_ex, n_zt = pack(bank_id, name, version, questions)
            print(f'  ✅ 打包成功: {zip_path}（练习 {n_ex} + 真题改编 {n_zt}）')
    print(f'\n总计: {total} 题')

if __name__ == '__main__':
    main()
