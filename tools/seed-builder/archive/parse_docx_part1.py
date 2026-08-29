# -*- coding: utf-8 -*-
"""解析三个 docx 第一部分 考研真题精选"""
import io, sys, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document

FILES = {
    "现代文学三十年": r"C:\Users\lenovo\Downloads\钱理群《中国现代文学三十年》题库1786884768.docx",
    "袁行霈中国文学史": r"C:\Users\lenovo\Downloads\袁行霈中国文学史题库1786884768.docx",
    "洪子诚当代文学史": r"C:\Users\lenovo\Downloads\洪子诚《中国当代文学史》（修订版）配套题库1786884768.docx",
}

def parse_part1(fp):
    doc = Document(fp)
    texts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    # 第一部分起点
    start = None
    for i, t in enumerate(texts):
        if re.match(r'^第一部分', t):
            start = i
            break
    if start is None:
        return {}
    # 终点：第二部分
    end = len(texts)
    for i in range(start, len(texts)):
        if re.match(r'^第二[部分编卷]', texts[i]):
            end = i
            break
    seg = texts[start:end]

    result = {}
    cur_type = None
    cur_q = None
    pending_stem = None

    def flush():
        nonlocal cur_q, pending_stem
        if cur_q is not None and cur_q['stem']:
            result.setdefault(cur_type or '其他', []).append(cur_q)
        cur_q = None
        pending_stem = None

    for t in seg:
        mt = re.match(r'^[一二三四五六七八九十]+[、.．]\s*(填空题|选择题|名词解释|简答题|论述题|判断题)', t)
        if mt:
            flush()
            cur_type = mt.group(1)
            continue
        mnum = re.match(r'^(\d+)[.、]\s*(.*)$', t)
        if mnum:
            flush()
            cur_q = {'no': int(mnum.group(1)), 'stem': mnum.group(2), 'options': [], 'answer': '', 'expl': []}
            continue
        mans = re.match(r'^【答案】[:：]?\s*(.*)$', t)
        if mans:
            if cur_q is None and pending_stem:
                cur_q = {'no': None, 'stem': pending_stem, 'options': [], 'answer': '', 'expl': []}
                pending_stem = None
            if cur_q is not None:
                cur_q['answer'] = mans.group(1).strip()
            continue
        mexp = re.match(r'^【解析】[:：]?\s*(.*)$', t)
        if mexp:
            if cur_q is not None and mexp.group(1):
                cur_q['expl'].append(mexp.group(1))
            continue
        if cur_q is not None:
            mopt = re.match(r'^([A-E])[.、]\s*(.*)$', t)
            if mopt and cur_q['options'] is not None and not cur_q['answer']:
                cur_q['options'].append((mopt.group(1), mopt.group(2)))
            elif cur_q['answer']:
                cur_q['expl'].append(t)
            else:
                cur_q['stem'] += (' ' + t if cur_q['stem'] else t)
        else:
            pending_stem = (pending_stem + ' ' + t) if pending_stem else t
    flush()
    return result

for name, fp in FILES.items():
    print('=' * 60)
    print('###', name, '第一部分')
    data = parse_part1(fp)
    from collections import Counter
    tc = Counter()
    for ty, qs in data.items():
        tc[ty] += len(qs)
    for ty, n in tc.most_common():
        print(f'  {ty}: {n}')
    print()

out = r"D:\study_app\tools\seed-builder\out\reports\docx题库_第一部分.json"
json.dump({k: parse_part1(fp) for k, fp in FILES.items()}, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('已保存:', out)
