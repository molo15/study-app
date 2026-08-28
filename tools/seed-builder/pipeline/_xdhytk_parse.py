# -*- coding: utf-8 -*-
"""从现代汉语试题库解析单选/填空，先预览语音章"""
import io, sys, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load(path):
    with open(path, encoding='utf-8') as f:
        return f.read()

def parse_choice_section(text):
    """从文档中解析单选：题干块序列 + 答案字母"""
    # 找"二、单项选择题"到"三、多项选择题"之间
    m = re.search(r'二、单项选择.*?(?=三、多项选择|四、判断|$)', text, re.S)
    if not m:
        return [], []
    body = m.group(0)
    # 题干块：以 数字. 开头（但排除答案区如 "1.A 2.D"）
    # 先分离答案区：形如 "1.A 2.D 3.C ..." 的连续编号
    ans_m = re.search(r'((?:\d{1,3}\.[A-ZＡ-Ｚ][\.\s]*){10,})', body)
    answer_map = {}
    if ans_m:
        for n, a in re.findall(r'(\d{1,3})\.([A-ZＡ-Ｚ])', ans_m.group(0)):
            answer_map[int(n)] = a.upper()
        body = body.replace(ans_m.group(0), '')
    # 题干块序列
    blocks = re.split(r'(?=\n\s*\d{1,3}\.)', body)
    items = []
    for b in blocks:
        mnum = re.match(r'\s*(\d{1,3})\.\s*(.*)', b, re.S)
        if not mnum:
            continue
        num = int(mnum.group(1))
        rest = mnum.group(2)
        # 提取选项
        opts = {}
        for letter in 'ABCD':
            om = re.search(letter + r'[\.、]\s*([^A-D]{1,60}?)(?=\s*[A-D][\.、]|$)', rest, re.S)
            if om:
                opts[letter] = re.sub(r'[\s　]+', '', om.group(1)).strip()
        # 题干 = 去掉选项部分
        stem = re.split(r'\s*[A-D][\.、]\s*[^A-D]{1,60}', rest)[0]
        stem = re.sub(r'[\s　]+', ' ', stem).strip(' 　.-')
        if not stem:
            continue
        items.append({'num': num, 'stem': stem, 'options': opts,
                      'ans': answer_map.get(num)})
    return items, answer_map

def parse_blank(text):
    """解析填空题：题干块 + 答案"""
    m = re.search(r'二、填空题：(.*?)(?=二、单项选择题|三、)', text, re.S)
    if not m:
        return []
    body = m.group(0)
    # 答案区在 二、单项选择 之前
    ans_m = re.search(r'((?:\d{1,3}\.|\d{1,3}\s+)[^\n]{0,80}\n?){5,}', body)
    # 简化：答案区是"一、"结束后、"二、单项"前的编号列表
    # 找答案编号
    answer_map = {}
    for mm in re.finditer(r'(\d{1,3})\.\s*(.+?)(?=\n\s*\d{1,3}\.|\n\s*二、单项|$)', body, re.S):
        answer_map[int(mm.group(1))] = mm.group(2).strip()
    return answer_map

if __name__ == '__main__':
    text = load(r'D:\study_app\tools\seed-builder\out\xiandai-tiku-split\语音.txt')
    items, ansmap = parse_choice_section(text)
    print(f'语音章单选解析 {len(items)} 道，其中带答案 {sum(1 for i in items if i["ans"])}')
    for it in items[:8]:
        print(it['num'], it['stem'][:30], '|', it['ans'], '|', {k: v[:12] for k, v in it['options'].items()})
    print('---填空答案预览---')
    bm = parse_blank(text)
    for k in sorted(list(bm.keys()))[:6]:
        print(k, bm[k][:40])
