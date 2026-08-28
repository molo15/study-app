# -*- coding: utf-8 -*-
"""解析现代汉语试题库全部章节：单选+填空（题干区+答案区）"""
import io, sys, re, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SPLIT = r'D:\study_app\tools\seed-builder\out\xiandai-tiku-split'
CHAPTER_CN = {'绪论': '绪论', '语音': '语音', '文字': '文字', '词汇': '词汇', '语法': '语法', '修辞': '修辞'}

def load(path):
    with open(path, encoding='utf-8') as f:
        return f.read()

def split_q(block):
    """把题干区文本按 编号. 切块，返回 [{num, body}]"""
    items = []
    # 以 行首 数字. 开头
    parts = re.split(r'(?=\n\s*\d{1,3}\.)', block)
    for p in parts:
        m = re.match(r'\s*(\d{1,3})\.\s*(.*)', p, re.S)
        if m:
            items.append({'num': int(m.group(1)), 'body': m.group(2)})
    return items

def parse_options(body):
    """从题干体提取 A-D 选项，返回 (stem, {A:..,D:..})"""
    opts = {}
    # 匹配 A.xxx B.xxx ... 允许换行
    letters = 'ABCDEF'
    m_all = re.findall(r'([A-EＡ-Ｅ])[\.、．]\s*([^A-EＡ-Ｅ\n]{1,50})', body)
    if m_all:
        for letter, txt in m_all:
            if letter in 'ABCDE' and letter not in opts:
                opts[letter] = re.sub(r'[\s　]+', '', txt).strip(' 　，,。；;')
    # 题干 = 去掉选项后的剩余
    stem = re.split(r'\s*[A-E][\.、．]\s*', body)[0]
    stem = re.sub(r'[\s　]+', ' ', stem).strip(' 　')
    stem = re.sub(r'[_—＿]+$', '', stem).strip()
    return stem, opts

def parse_answers(block):
    """答案区：连续 '1.A 2.D ...'"""
    ans = {}
    for m in re.finditer(r'(\d{1,3})\s*\.?\s*([A-EＡ-Ｅ])', block):
        n = int(m.group(1))
        if 1 <= n <= 200:
            ans.setdefault(n, m.group(2).upper().replace('Ａ', 'A'))
    return ans

def parse_blank_ans(block):
    """填空答案区：'1.答案' 编号列表"""
    ans = {}
    for m in re.finditer(r'(\d{1,3})\.\s*(.+?)(?=\n\s*\d{1,3}\.|\n\s*[一二三四五]|$)', block, re.S):
        ans[int(m.group(1))] = m.group(2).strip()
    return ans

def parse_blank_q(block):
    """填空题干区：编号+题干"""
    return split_q(block)

for fn, ch in CHAPTER_CN.items():
    text = load(os.path.join(SPLIT, fn + '.txt'))
    # 题干区与答案区：找到两处"二、单项选择题"等
    choice_head_pos = [m.start() for m in re.finditer(r'二、单项选择题', text)]
    multi_head_pos = [m.start() for m in re.finditer(r'三、多项选择题', text)]
    blank_head_pos = [m.start() for m in re.finditer(r'二、填空题', text)]
    # 单选题干区
    choice_q = ''
    if len(choice_head_pos) >= 1:
        end = multi_head_pos[0] if multi_head_pos else len(text)
        choice_q = text[choice_head_pos[0]:end]
    # 单选答案区（第二个 二、单项选择题）
    choice_a = ''
    if len(choice_head_pos) >= 2:
        end = multi_head_pos[1] if len(multi_head_pos) >= 2 else len(text)
        choice_a = text[choice_head_pos[1]:end]
    # 填空答案区（第二个 二、填空题）
    blank_a = ''
    if len(blank_head_pos) >= 2:
        end = choice_head_pos[1] if len(choice_head_pos) >= 2 else len(text)
        blank_a = text[blank_head_pos[1]:end]

    q_items = split_q(choice_q)
    ans_map = parse_answers(choice_a)
    qs = []
    for it in q_items:
        if it['num'] in ans_map:
            stem, opts = parse_options(it['body'])
            if len(opts) >= 4 and stem:
                qs.append({'num': it['num'], 'stem': stem, 'options': [opts.get(l, '') for l in 'ABCD'],
                           'ans': ans_map[it['num']]})
    # 填空（题干区在"二、填空题"到"二、单项选择题"之间）
    blank_q_items = split_q(text[blank_head_pos[0]:choice_head_pos[0]]) if blank_head_pos and choice_head_pos else []
    blank_ans = parse_blank_ans(blank_a)
    blanks = []
    for it in blank_q_items:
        if it['num'] in blank_ans:
            stem = re.sub(r'[\s　]+', ' ', it['body']).strip()
            blanks.append({'num': it['num'], 'stem': stem, 'ans': blank_ans[it['num']]})
    print(f'{fn}章: 单选可解析 {len(qs)}/{len(q_items)}, 填空 {len(blanks)}/{len(blank_q_items)}')
