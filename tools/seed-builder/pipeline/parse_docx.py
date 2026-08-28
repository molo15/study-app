# -*- coding: utf-8 -*-
"""解析三个 docx 题库为结构化 JSON（鲁棒版，支持无编号主观题）"""
import io, sys, os, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document

FILES = {
    "现代文学三十年": r"C:\Users\lenovo\Downloads\钱理群《中国现代文学三十年》题库1786884768.docx",
    "袁行霈中国文学史": r"C:\Users\lenovo\Downloads\袁行霈中国文学史题库1786884768.docx",
    "洪子诚当代文学史": r"C:\Users\lenovo\Downloads\洪子诚《中国当代文学史》（修订版）配套题库1786884768.docx",
}

TYPE_HEAD_RE = re.compile(r'^(填空题|选择题|名词解释|简答题|简答与论述|论述题|判断题|综合题)$')
CHAPTER_RE = re.compile(r'^(第[一二三四五六七八九十百\d]+[章编])\s+(.+)$|^(第一编|第二编|第三编|第四编|第五编|第六编|第七编|第八编|第九编|上编|中编|下编)\s+(.+)$')

def parse_docx(fp):
    doc = Document(fp)
    texts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    result = {}
    cur_chapter = None
    cur_type = None
    cur_q = None
    in_answer = False   # 已出现【答案】
    in_expl = False     # 已出现【解析】
    pending_stem = None  # 主观题无编号时暂存的题干

    def flush():
        nonlocal cur_q, in_answer, in_expl, pending_stem
        if cur_q is not None:
            # 去掉空解析，合并
            q = cur_q
            q['expl'] = ' '.join(x for x in q.get('expl', []) if x).strip()
            q['stem'] = q['stem'].strip()
            if q['stem'] and cur_chapter and cur_type:
                result.setdefault(cur_chapter, {}).setdefault(cur_type, []).append(q)
        cur_q = None
        in_answer = False
        in_expl = False
        pending_stem = None

    in_part2 = False
    for t in texts:
        if not in_part2:
            if re.match(r'^第二[部分编卷]', t) or '章节题库' in t:
                in_part2 = True
                flush()
            continue

        # 章节标题
        mch = CHAPTER_RE.match(t)
        if mch:
            flush()
            cur_chapter = t
            cur_type = None
            continue

        # 题型标题
        if TYPE_HEAD_RE.match(t):
            flush()
            cur_type = t
            continue

        # 数字编号题目
        mnum = re.match(r'^(\d+)[.、]\s*(.*)$', t)
        if mnum and cur_chapter is not None:
            flush()
            cur_q = {'no': int(mnum.group(1)), 'stem': mnum.group(2).strip(), 'options': [], 'answer': '', 'expl': []}
            in_answer = False
            continue

        # 【答案】
        mans = re.match(r'^【答案】[:：]?\s*(.*)$', t)
        if mans:
            if cur_q is None:
                # 主观题无编号：上一段 pending_stem 为题干
                if pending_stem:
                    cur_q = {'no': None, 'stem': pending_stem, 'options': [], 'answer': '', 'expl': []}
                    pending_stem = None
                else:
                    # 无题干（异常），跳过
                    continue
            cur_q['answer'] = mans.group(1).strip()
            in_answer = True
            in_expl = False
            continue

        # 【解析】
        mexp = re.match(r'^【解析】[:：]?\s*(.*)$', t)
        if mexp:
            if cur_q is None:
                continue
            in_expl = True
            if mexp.group(1):
                cur_q['expl'].append(mexp.group(1))
            continue

        # 普通段落
        if cur_q is not None:
            # 选择题选项
            mopt = re.match(r'^([A-E])[.、]\s*(.*)$', t)
            if mopt and not in_answer and cur_type == '选择题':
                cur_q['options'].append((mopt.group(1), mopt.group(2).strip()))
            elif in_answer or in_expl:
                # 解析/答案续行
                cur_q['expl'].append(t)
            else:
                # 题干续行
                cur_q['stem'] += (' ' + t if cur_q['stem'] else t)
        else:
            # 无当前题：可能是主观题题干（无编号），暂存
            if cur_chapter and cur_type and not pending_stem:
                pending_stem = t
            elif pending_stem:
                pending_stem += (' ' + t)
    flush()
    return result

all_data = {}
from collections import Counter
for name, fp in FILES.items():
    print(f'解析 {name} ...', flush=True)
    data = parse_docx(fp)
    all_data[name] = data
    print(f'  章节数: {len(data)}')
    tc = Counter()
    for ch, types in data.items():
        for ty, qs in types.items():
            tc[ty] += len(qs)
    total = sum(tc.values())
    print(f'  题目总数: {total}')
    for ty, n in tc.most_common():
        print(f'    {ty}: {n}')
    print()

out = r"D:\study_app\tools\seed-builder\out\reports\docx题库_解析.json"
json.dump(all_data, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('已保存:', out)
