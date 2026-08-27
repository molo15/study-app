# -*- coding: utf-8 -*-
"""论述题专题 v0.7.0 打包：
- 加载 app/assets/banks/*v0.6.0.zip（线上真源）
- 每个 bank：
   1) 按规则把「论述型/论述型简答」移入 chapter=论述题专题（不删题，只改 chapter + answerFormat）
   2) 文学史三科并入 out/lunshu/<bank>.json 的真题论述题
- 重打包 v0.7.0：一章一文件 + manifest（chapters 分组末尾追加 论述题专题）+ 数据完整性校验
- 输出到 out/packages/v07/ 并复制到 app/assets/banks/
"""
import json
import os
import re
import shutil
import sys
import zipfile
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # tools/seed-builder
SRC_DIR = os.path.join('app', 'assets', 'banks')
OUT_DIR = os.path.join(BASE, 'out', 'packages', 'v07')
LUNSHU_DIR = os.path.join(BASE, 'out', 'lunshu')

VERSION = '0.7.0'

LUNSHU_CHAPTER = '论述题专题'
LUNSHU_FORMAT = '论述题：分条作答，先摆论点再给论据，结合具体例证论证充分。'

# 各 bank 移入规则（short_answer 才可能论述型）
# 返回 True 表示该题应移入论述题专题
def move_rule(bank_id, q):
    if q.get('type') != 'short_answer':
        return False
    stem = str(q.get('stem', ''))
    fmt = str(q.get('answerFormat', '') or '')
    if bank_id in ('bank-zhongguo-gudai-wenxue', 'bank-zhongguo-dangdai-wenxue'):
        # 文学史：answerFormat 已标注「论述」的归专题
        return '论述' in fmt
    if bank_id == 'bank-zhongguo-xiandai-wenxue':
        # 现代文学史：非「名词解释」的简答均为论述型
        return not stem.startswith('名词解释')
    if bank_id == 'bank-gudai-hanyu':
        # 古代汉语：排除名解/翻译/断句/标点/平仄实操/默写/长文断句
        if stem.startswith(('名词解释', '解释名词', '请翻译', '请为下列文字', '翻译', '标点翻译',
                            '默写', '给《', '标出', '写出', '曾子', '昔者', '（仅限',
                            '(1)', '晋文公')):
            return False
        return True
    if bank_id == 'bank-xiandai-hanyu':
        if stem.startswith(('分析下面', '符号法', '多重复句', '对比下列', '请分析下列')):
            return False
        if stem in ('辅音', '韵母', '双拼法', '塞擦音', '音素与音位', '实词', '复句',
                    '生成语法', '语素', '词', '义素分析法', '指事字', '金文',
                    '现代汉民族共同语（名词解释）', '方言区（名词解释）'):
            return False
        if '（名词解释）' in stem:
            return False
        return True
    return False


def load_bank(bank_id, version):
    """从 src zip 读取全部题目与 manifest。"""
    path = os.path.join(SRC_DIR, f'{bank_id}-v{version}.zip')
    zf = zipfile.ZipFile(path)
    man = json.loads(zf.read('manifest.json'))
    questions = []
    for fn in man['questionFiles']:
        questions.extend(json.loads(zf.read(fn)))
    return man, questions


def sanitize(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name)


def pack_bank(bank_id, name, questions):
    """一章一文件 + manifest(v3)，分组末尾追加论述题专题。"""
    chapters_sorted = sorted({q['chapter'] for q in questions})
    groups = [{'group': '全部', 'chapters': chapters_sorted}] if len(chapters_sorted) <= 1 else None
    # 从现有章节自动按「编」归类（沿用 pack_t1 的分组函数）
    groups = chapter_groups_auto(bank_id, chapters_sorted)
    # 末尾追加论述题专题分组
    if LUNSHU_CHAPTER in chapters_sorted and not any(
            LUNSHU_CHAPTER in g['chapters'] for g in groups):
        groups.append({'group': LUNSHU_CHAPTER, 'chapters': [LUNSHU_CHAPTER]})
    manifest = {
        'formatVersion': 3,
        'bankId': bank_id,
        'name': name,
        'version': VERSION,
        'generatedAt': '2026-08-17T12:00:00+08:00',
        'chapters': groups,
        'questionFiles': [],
        'mockPapers': [],
    }
    by_chapter = {}
    for q in questions:
        by_chapter.setdefault(q['chapter'], []).append(q)
    os.makedirs(OUT_DIR, exist_ok=True)
    zip_path = os.path.join(OUT_DIR, f'{bank_id}-v{VERSION}.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for ch in sorted(by_chapter):
            fname = f'questions/{sanitize(ch)}.json'
            zf.writestr(fname, json.dumps(by_chapter[ch], ensure_ascii=False, indent=2))
            manifest['questionFiles'].append(fname)
        zf.writestr('manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2))
    return zip_path


def chapter_groups_auto(bank_id, chapters):
    """沿用 pack_t1 的分组逻辑，保证与原 v0.6.0 分组一致。"""
    def xiandai_wenxue(ch):
        if ch.startswith('五四'): return '五四时期（1917-1927）'
        if ch.startswith('三十'): return '三十年代（1928-1937）'
        if ch.startswith('四十'): return '四十年代（1937-1949）'
        return '综合专题'
    def dangdai_wenxue(ch):
        pre = ch[:2]
        if pre in ('第一', '第二', '第三', '第四'): return '上编 十七年文学（1949-1976）'
        if pre in ('第五', '第六', '第七', '第八', '第九', '第十'): return '中编 新时期文学（1978-1999）'
        return '下编 台港文学与世纪之交'
    MAPS = {
        'bank-gudai-hanyu': lambda c: '上编 基础知识' if c in ('修辞', '古书的标点', '工具书简介') else (
            '中编 语言文字学' if c.startswith(('文字', '词汇', '语法')) else '下编 音韵训诂与格律'),
        'bank-xiandai-hanyu': lambda c: '上编 语音与文字' if c in ('绪论', '语音', '文字') else (
            '中编 词汇与语法' if c in ('词汇', '语法') else '下编 修辞'),
        'bank-zhongguo-gudai-wenxue': lambda c: '上编 先秦两汉文学' if c in ('先秦文学', '秦汉文学') else (
            '中编 魏晋隋唐文学' if c in ('魏晋南北朝文学', '隋唐五代文学') else '下编 宋元明清文学'),
        'bank-zhongguo-xiandai-wenxue': xiandai_wenxue,
        'bank-zhongguo-dangdai-wenxue': dangdai_wenxue,
    }
    fn = MAPS.get(bank_id, lambda c: '全部')
    groups = {}
    for ch in chapters:
        g = LUNSHU_CHAPTER if ch == LUNSHU_CHAPTER else fn(ch)
        groups.setdefault(g, []).append(ch)
    return [{'group': g, 'chapters': sorted(v)} for g, v in sorted(groups.items())]


def validate(bank_id, questions):
    errors = []
    ids = set()
    for q in questions:
        qid = q.get('id', '')
        if qid in ids:
            errors.append(f'id 重复: {qid}')
        ids.add(qid)
        t = q.get('type')
        ans = q.get('answer')
        if t == 'true_false' and ans not in ('正确', '错误'):
            errors.append(f'{qid} 判断答案: {ans}')
        elif t == 'single_choice':
            keys = {o['key'] for o in q.get('options', [])}
            if ans not in keys:
                errors.append(f'{qid} 单选答案: {ans}')
        elif t == 'multi_choice':
            keys = {o['key'] for o in q.get('options', [])}
            if not isinstance(ans, list) or not set(ans).issubset(keys):
                errors.append(f'{qid} 多选答案: {ans}')
        elif t in ('blank', 'short_answer'):
            if not ans:
                errors.append(f'{qid} 缺 answer')
    return errors


BANKS = [
    ('bank-gudai-hanyu', '考研 · 古代汉语'),
    ('bank-xiandai-hanyu', '考研 · 现代汉语'),
    ('bank-zhongguo-gudai-wenxue', '考研 · 中国古代文学史'),
    ('bank-zhongguo-xiandai-wenxue', '考研 · 中国现代文学史'),
    ('bank-zhongguo-dangdai-wenxue', '考研 · 中国当代文学史'),
]


def main():
    total_new = 0
    for bank_id, name in BANKS:
        man, questions = load_bank(bank_id, '0.6.0')
        moved = 0
        for q in questions:
            if move_rule(bank_id, q):
                q['chapter'] = LUNSHU_CHAPTER
                q['answerFormat'] = LUNSHU_FORMAT
                moved += 1
        # 并入真题论述题（文学史）
        lun_path = os.path.join(LUNSHU_DIR, bank_id + '.json')
        added = 0
        if os.path.exists(lun_path):
            added_qs = json.load(open(lun_path, encoding='utf-8'))
            existing_ids = {q['id'] for q in questions}
            for q in added_qs:
                if q['id'] in existing_ids:
                    continue
                questions.append(q)
                added += 1
                existing_ids.add(q['id'])
        total_new += added
        # 校验 + 打包
        errs = validate(bank_id, questions)
        lun_cnt = sum(1 for q in questions if q['chapter'] == LUNSHU_CHAPTER)
        print(f'【{name}】总 {len(questions)} 题 | 移入专题 {moved} | 新增真题论述题 {added} | 专题共 {lun_cnt} 题')
        if errs:
            print(f'   ❌ 校验错误 {len(errs)}: {errs[:5]}')
        else:
            zip_path = pack_bank(bank_id, name, questions)
            print(f'   ✅ v0.7.0: {zip_path}')
    print(f'\n新增真题论述题合计: {total_new}')


if __name__ == '__main__':
    main()
