# -*- coding: utf-8 -*-
"""现代文学史：docx 客观题入库 v2
- 填空题 → blank（|转；）；选择题 → choice（答案转文本）
- 去重：题干规范化比较
- 匹配知识点：书名号 + 知识点名实体词 + 题实体词双向匹配
- 未匹配 → 归入章节"XX（真题补充）"汇总知识点（每章最多1个）
"""
import io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DOCX = json.load(open(r'D:\study_app\tools\seed-builder\out\reports\docx题库_解析.json', encoding='utf-8'))
KP = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国现代文学史.knowledge.json', encoding='utf-8'))

MAP = {
    "第1章 文学思潮与运动（一）": "文学思潮与运动（一）",
    "第2章 鲁迅（一）": "鲁迅（一）",
    "第3章 小说（一）": "小说（一）",
    "第4章 通俗小说（一）": "市民通俗小说（一）",
    "第5章 郭沫若": "郭沫若",
    "第6章 新诗（一）": "新诗（一）",
    "第7章 散文（一）": "散文（一）",
    "第8章 戏剧（一）": "戏剧",
    "第9章 文学思潮与运动（二）": "文学思潮与运动（二）",
    "第10章 茅 盾": "茅盾",
    "第11章 老 舍": "老舍",
    "第12章 巴 金": "巴金",
    "第13章 沈从文": "沈从文",
    "第14章 小说（二）": "小说（二）",
    "第15章 通俗小说（二）": "市民通俗小说（二）",
    "第16章 新诗（二）": "新诗（二）",
    "第17章 鲁迅（二）": "鲁迅（二）",
    "第18章 散文（二）": "散文（二）",
    "第19章 曹 禺": "曹禺",
    "第20章 戏剧（二）": "戏剧（二）",
    "第21章 文学思潮与运动（三）": "文学思潮与运动（三）",
    "第22章 赵树理": "赵树理",
    "第23章 小说（三）": "小说（三）",
    "第24章 通俗小说（三）": "市民通俗小说（二）",
    "第25章 艾 青": "艾青",
    "第26章 新诗（三）": "新诗（三）",
    "第27章 散文（三）": "散文（三）",
    "第28章 戏剧（三）": "戏剧（三）",
    "第29章 台湾文学": "台湾文学",
}

def norm(s):
    s = re.sub(r'[（）()。，、；：""“”\'  ]', '', s)
    s = re.sub(r'\[[^\]]*\]', '', s)
    s = re.sub(r'（[^）]*研）', '', s)
    return s

def kp_text(kp):
    return kp['name'] + (kp.get('summary') or '') + ''.join(q['stem'] for q in kp.get('basicQuestions', []))

def entities(stem):
    """提取题干实体：书名号、引号内、标点分隔词"""
    out = re.findall(r'《([^》]+)》', stem)
    out += re.findall(r'[“"]([^”"]+)[”"]', stem)
    return out

def score_kp(kp, stem):
    t = kp_text(kp)
    s = 0
    for m in entities(stem):
        if m and m in t:
            s += 3
    # 知识点名称片段
    for kw in re.findall(r'[\u4e00-\u9fa5]{2,8}', kp['name']):
        if kw in stem:
            s += 1
    return s

by_chap = {}
for k in KP['knowledge']:
    by_chap.setdefault(k['chapter'], []).append(k)

added = skipped = merged = 0
for docx_ch, target_ch in MAP.items():
    types = DOCX['现代文学三十年'].get(docx_ch, {})
    qs = []
    for q in types.get('填空题', []):
        ans = q['answer'].replace('|', '；').strip()
        if not ans:
            continue
        qs.append({'type': 'blank', 'stem': q['stem'], 'answer': ans, 'explanation': q['expl'], 'options': []})
    for q in types.get('选择题', []):
        if q['answer'] in 'ABCDE' and len(q['answer']) == 1 and q['options']:
            idx = ord(q['answer']) - ord('A')
            if idx < len(q['options']):
                ans = q['options'][idx][1]
            else:
                continue
            qs.append({'type': 'choice', 'stem': q['stem'], 'answer': ans, 'explanation': q['expl'],
                       'options': [o[1] for o in q['options']]})
        else:
            continue

    kps = by_chap.get(target_ch, [])
    # 每章真题补充点（懒创建）
    zhen_kp = None
    for q in qs:
        ns = norm(q['stem'])
        dup = False
        for k in kps:
            for exist in k.get('basicQuestions', []):
                e = norm(exist['stem'])
                if e == ns or (len(ns) >= 6 and ns in e):
                    dup = True
                    break
            if dup:
                break
        if dup:
            skipped += 1
            continue
        best, best_s = None, -1
        for k in kps:
            s = score_kp(k, q['stem'])
            if s > best_s:
                best_s, best = s, k
        if best is not None and best_s >= 2:
            best['basicQuestions'].append(q)
        else:
            if zhen_kp is None:
                zhen_kp = {"id": f"k_xdwx_zhen_{target_ch.replace('（','').replace('）','')}",
                           "name": f"{target_ch}（真题补充）", "parent": "k_xdwx_xd", "chapter": target_ch,
                           "hot": False, "summary": "考研真题补充知识点，覆盖该章重要考点。", "basicQuestions": []}
                KP['knowledge'].append(zhen_kp)
                kps.append(zhen_kp)
            zhen_kp['basicQuestions'].append(q)
            merged += 1
        added += 1

json.dump(KP, open(r'D:\study_app\tools\seed-builder\out\knowledge\中国现代文学史.knowledge.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'现代文学史入库: 新增{added} 跳过重复{skipped} 归入真题补充点{merged}')

# 校验
bad = []
for k in KP['knowledge']:
    for q in k.get('basicQuestions', []):
        if q['type'] == 'choice':
            if len(q.get('options', [])) != 4:
                bad.append(f"{k['id']} 选项数: {q['stem'][:18]}")
            if q['answer'] not in q.get('options', []):
                bad.append(f"{k['id']} 错配: {q['stem'][:22]}")
print('choice 校验异常:', len(bad))
for b in bad[:20]:
    print('  ', b)
