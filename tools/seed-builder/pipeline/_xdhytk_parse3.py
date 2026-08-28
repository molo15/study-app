# -*- coding: utf-8 -*-
"""v3 通用解析：按答案区关键字定位，提取单选+填空"""
import io, sys, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SPLIT = r'D:\study_app\tools\seed-builder\out\xiandai-tiku-split'
CHAPTERS = ['绪论', '语音', '文字', '词汇', '语法', '修辞']

def load(path):
    with open(path, encoding='utf-8') as f:
        return f.read()

def find_answer_start(text):
    """定位答案区起点：取所有答案标志中最早出现的位置"""
    pos = [i for kw in ['答案略', '答案参见教材', '（答案略'] if (i := text.find(kw)) >= 0]
    return min(pos) if pos else -1

def split_q(block):
    items = []
    parts = re.split(r'(?=\n\s*\d{1,3}[\.．、])', block)
    for p in parts:
        m = re.match(r'\s*(\d{1,3})[\.．、]\s*(.*)', p, re.S)
        if m:
            items.append({'num': int(m.group(1)), 'body': m.group(2)})
    return items

def parse_options(body):
    opts = {}
    m_all = re.findall(r'([A-E])\s*[\.、．]?\s*([^\nA-E]{1,40})', body)
    for letter, txt in m_all:
        if letter not in opts:
            opts[letter] = re.sub(r'^[\.、．、\s]+|[、，。；;]+$', '', txt).strip()
    # 题干：去掉选项区（第一个 独立 A-E 选项 之前）
    stem = body
    m = re.search(r'\s*[A-E]\s*[\.、．]?\s*\S', body)
    if m:
        stem = body[:m.start()]
    stem = re.sub(r'[\s　]+', ' ', stem).strip(' 　')
    stem = re.sub(r'[_—＿]+$', '', stem).strip()
    return stem, opts

def parse_letter_ans(block):
    ans = {}
    for m in re.finditer(r'(\d{1,3})\s*[\.、．]\s*([A-E])', block):
        ans.setdefault(int(m.group(1)), m.group(2))
    return ans

def parse_num_ans(block):
    ans = {}
    for m in re.finditer(r'(\d{1,3})[\.．、]\s*(.+?)(?=\n\s*\d{1,3}[\.．、]|\n\s*[一二三四五六]|$)', block, re.S):
        ans[int(m.group(1))] = m.group(2).strip()
    return ans

for fn in CHAPTERS:
    text = load(os.path.join(SPLIT, fn + '.txt'))
    apos = find_answer_start(text)
    q_part = text[:apos] if apos > 0 else text
    a_part = text[apos:] if apos > 0 else ''
    # 单选
    cm = list(re.finditer(r'[一二三四五六七八]*、*单项选择题', q_part))
    qs = []
    if cm:
        seg_q = q_part[cm[0].start():]
        seg_q = re.split(r'\n\s*[一二三四五六]、', seg_q)[0]  # 到下一个题型标题
        items = split_q(seg_q)
        # 答案：在 a_part 里找单项选择段（任意标题）
        am = re.search(r'[一二三四五六七八]*、*单项选择题(.*)', a_part, re.S)
        ans_map = parse_letter_ans(am.group(1)) if am else {}
        if fn == '语法':
            print('DBG cm=', len(cm), 'items=', len(items), 'ans=', len(ans_map))
        for it in items:
            if it['num'] in ans_map:
                stem, opts = parse_options(it['body'])
                if len(opts) >= 4 and stem:
                    qs.append({'num': it['num'], 'stem': stem, 'options': [opts.get(l, '') for l in 'ABCD'],
                               'ans': ans_map[it['num']]})
    # 填空
    bm = list(re.finditer(r'填空题', q_part))
    blanks = []
    if bm:
        seg_b = q_part[bm[0].start():]
        # 到下一个题型标题（排除"填空"本身）
        seg_b = re.split(r'\n\s*[一二三四五六]、[^\n]*?(?<!填空)', seg_b)[0]
        items = split_q(seg_b)
        bm2 = re.search(r'填空题\s*\n(.*)', a_part, re.S)
        bans = parse_num_ans(bm2.group(1)) if bm2 else {}
        for it in items:
            if it['num'] in bans:
                stem = re.sub(r'[\s　]+', ' ', it['body']).strip()
                blanks.append({'num': it['num'], 'stem': stem, 'ans': bans[it['num']]})
    print(f'{fn}: 单选 {len(qs)}, 填空 {len(blanks)}')
    # 抽样
    for q in qs[:2]:
        print('   ', q['num'], q['stem'][:24], '|', q['ans'], '|', q['options'][:2])
