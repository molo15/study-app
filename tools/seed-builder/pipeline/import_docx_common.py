# -*- coding: utf-8 -*-
"""通用 docx 客观题入库（古代文学史、当代文学史）"""
import io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DOCX = json.load(open(r'D:\study_app\tools\seed-builder\out\reports\docx题库_解析.json', encoding='utf-8'))

def norm(s):
    s = re.sub(r'[（）()。，、；：""“”\'  ]', '', s)
    s = re.sub(r'\[[^\]]*\]', '', s)
    s = re.sub(r'（[^）]*研）', '', s)
    return s

def kp_text(kp):
    return kp['name'] + (kp.get('summary') or '') + ''.join(q['stem'] for q in kp.get('basicQuestions', []))

def entities(stem):
    return re.findall(r'《([^》]+)》', stem) + re.findall(r'[“"]([^”"]+)[”"]', stem)

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

def import_subject(subject, docx_name, kp_path, maps):
    KP = json.load(open(kp_path, encoding='utf-8'))
    by_chap = {}
    for k in KP['knowledge']:
        by_chap.setdefault(k['chapter'], []).append(k)

    added = skipped = merged = 0
    for docx_ch, target_ch in maps.items():
        types = DOCX[docx_name].get(docx_ch, {})
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
                    zhen_kp = {"id": f"k_zhen_{subject}_{target_ch.replace('（','').replace('）','')}",
                               "name": f"{target_ch}（真题补充）", "parent": "root", "chapter": target_ch,
                               "hot": False, "summary": "考研真题补充知识点，覆盖该章重要考点。", "basicQuestions": []}
                    KP['knowledge'].append(zhen_kp)
                    kps.append(zhen_kp)
                zhen_kp['basicQuestions'].append(q)
                merged += 1
            added += 1

    json.dump(KP, open(kp_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    bad = []
    for k in KP['knowledge']:
        for q in k.get('basicQuestions', []):
            if q['type'] == 'choice':
                if len(q.get('options', [])) != 4:
                    bad.append(f"{k['id']} 选项数: {q['stem'][:18]}")
                if q['answer'] not in q.get('options', []):
                    bad.append(f"{k['id']} 错配: {q['stem'][:22]}")
    print(f'{subject} 入库: 新增{added} 跳过重复{skipped} 归入真题补充点{merged} | choice校验异常{len(bad)}')
    for b in bad[:15]:
        print('  ', b)

# 古代文学史映射
GD_MAP = {
    "第一编 先秦文学": "先秦文学",
    "第二编 秦汉文学": "秦汉文学",
    "第三编 魏晋南北朝文学": "魏晋南北朝文学",
    "第四编 隋唐五代文学": "隋唐五代文学",
    "第五编 宋代文学": "宋代文学",
    "第六编 元代文学": "元代文学",
    "第七编 明代文学": "明代文学",
    "第八编 清代文学": "清代文学",
    "第九编 近代文学": "近代文学",
}
import_subject("古代文学史", "袁行霈中国文学史",
               r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json', GD_MAP)

# 当代文学史映射
DD_MAP = {
    "第1章 文学的“转折”": "文学思潮（1949-1976）",
    "第2章 文学环境与文学规范": "文学思潮（1949-1976）",
    "第3章 矛盾和冲突": "文学思潮（1949-1976）",
    "第4章 隐失的诗人和诗派": "新诗（50-60年代）",
    "第5章 诗歌体式和诗歌事件": "新诗（50-60年代）",
    "第6章 小说的题材和形态": "小说（50-60年代）",
    "第7章 农村题材小说": "小说（50-60年代）",
    "第8章 对历史的叙述": "小说（50-60年代）",
    "第9章 当代的“通俗小说”": "小说（50-60年代）",
    "第10章 在主流之外": "文学思潮（1949-1976）",
    "第11章 散 文": "戏剧散文（50-60年代）",
    "第12章 话 剧": "戏剧散文（50-60年代）",
    "第13章 走向“文革文学”": "文学思潮（1949-1976）",
    "第14章 重新构造“经典”": "文学思潮（1949-1976）",
    "第15章 分裂的文学世界": "文学思潮（1949-1976）",
    "第16章 文学“新时期”的想象": "文学思潮（80-90年代）",
    "第17章 80年代文学概况": "文学思潮（80-90年代）",
    "第18章 “归来者”的诗": "新诗（80-90年代）",
    "第19章 新诗潮": "新诗（80-90年代）",
    "第20章 历史创伤的记忆": "小说（80年代）",
    "第21章 80年代中后期的小说（一）": "小说（80年代）",
    "第22章 80年代中后期的小说（二）": "小说（80年代）",
    "第23章 女作家的小说": "小说（90年代）",
    "第24章 散 文": "散文（80-90年代）",
    "第25章 90年代的文学状况": "文学思潮（80-90年代）",
    "第26章 90年代的诗": "新诗（80-90年代）",
    "第27章 90年代的小说": "小说（90年代）",
}
import_subject("当代文学史", "洪子诚当代文学史",
               r'D:\study_app\tools\seed-builder\out\knowledge\中国当代文学史.knowledge.json', DD_MAP)
