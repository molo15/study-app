# -*- coding: utf-8 -*-
"""第一部分考研真题精选 - 填空题入库（按知识点匹配，未匹配归入科内真题精选补充点）"""
import io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PART1 = json.load(open(r'D:\study_app\tools\seed-builder\out\reports\docx题库_第一部分.json', encoding='utf-8'))

def norm(s):
    s = re.sub(r'[（）()。，、；：""“”\'  ]', '', s)
    s = re.sub(r'\[[^\]]*\]', '', s)
    s = re.sub(r'（[^）]*研）', '', s)
    return s

def entities(stem):
    return re.findall(r'《([^》]+)》', stem) + re.findall(r'[“"]([^”"]+)[”"]', stem)

def kp_text(kp):
    return kp['name'] + (kp.get('summary') or '') + ''.join(q['stem'] for q in kp.get('basicQuestions', []))

def score_kp(kp, stem):
    t = kp_text(kp)
    s = 0
    for m in entities(stem):
        if m and m in t:
            s += 3
    for kw in re.findall(r'[\u4e00-\u9fa5]{2,8}', kp['name']):
        if kw in stem:
            s += 1
    return s

JOBS = [
    ("现代文学三十年", r'D:\study_app\tools\seed-builder\out\knowledge\中国现代文学史.knowledge.json', 'k_zhen1_xdwx'),
    ("袁行霈中国文学史", r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json', 'k_zhen1_gdwx'),
    ("洪子诚当代文学史", r'D:\study_app\tools\seed-builder\out\knowledge\中国当代文学史.knowledge.json', 'k_zhen1_ddwx'),
]

for docx_name, kp_path, root_id in JOBS:
    KP = json.load(open(kp_path, encoding='utf-8'))
    qs = []
    for q in PART1[docx_name].get('填空题', []):
        ans = q['answer'].replace('|', '；').strip()
        if not ans:
            continue
        qs.append({'type': 'blank', 'stem': q['stem'], 'answer': ans, 'explanation': ' '.join(q['expl']), 'options': []})
    added = matched = merged = 0
    zhen_kp = None
    for q in qs:
        # 全库匹配
        best, best_s = None, -1
        for k in KP['knowledge']:
            s = score_kp(k, q['stem'])
            if s > best_s:
                best_s, best = s, k
        if best is not None and best_s >= 3:
            # 去重
            dup = False
            for exist in best.get('basicQuestions', []):
                if norm(exist['stem']) == norm(q['stem']):
                    dup = True
                    break
            if not dup:
                best['basicQuestions'].append(q)
                matched += 1
        else:
            if zhen_kp is None:
                zhen_kp = {"id": root_id, "name": "考研真题精选（补充）", "parent": "root", "chapter": "真题精选",
                           "hot": False, "summary": "考研真题精选补充知识点，跨章节覆盖重要考点。", "basicQuestions": []}
                KP['knowledge'].append(zhen_kp)
            zhen_kp['basicQuestions'].append(q)
            merged += 1
        added += 1
    json.dump(KP, open(kp_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{docx_name} 第一部分填空入库: 新增{added} 匹配到知识点{matched} 归入真题精选{merged}')

# 校验全部
for kp_path in [r'D:\study_app\tools\seed-builder\out\knowledge\中国现代文学史.knowledge.json',
                r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json',
                r'D:\study_app\tools\seed-builder\out\knowledge\中国当代文学史.knowledge.json']:
    KP = json.load(open(kp_path, encoding='utf-8'))
    bad = 0
    for k in KP['knowledge']:
        for q in k.get('basicQuestions', []):
            if q['type'] == 'choice' and q['answer'] not in q.get('options', []):
                bad += 1
    print('choice校验异常:', kp_path.split('\\')[-1], bad)
