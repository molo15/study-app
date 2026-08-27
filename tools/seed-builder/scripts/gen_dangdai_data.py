# -*- coding: utf-8 -*-
"""Build final JSON for bank-zhongguo-dangdai-wenxue."""
import re, json, random
from gen_dangdai_common import *

items = json.load(open(r'out/_dangdai_items3.json', encoding='utf-8'))
raw_src = open(r'out/extract/洪子诚《中国当代文学史》.txt', encoding='utf-8').read()

random.seed(42)

# ---------------- Chapter classification ----------------
SRC_CH_MAP = {
    '第1章': 1, '第2章': 1, '第3章': 1, '第13章': 1, '第14章': 1, '第15章': 1,
    '第4章': 3, '第5章': 3,
    '第6章': 2, '第7章': 2, '第8章': 2, '第9章': 2, '第10章': 1,
    '第11章': 4, '第12章': 4,
    '第16章': 5, '第17章': 5, '第25章': 5,
    '第18章': 8, '第19章': 8, '第26章': 8,
    '第20章': 6, '第21章': 6, '第22章': 6,
    '第23章': 7, '第27章': 7, '第24章': 10,
}

def src_chapter_key(ch):
    if not ch:
        return None
    m = re.match(r'^第(\d+)章', ch)
    return f'第{m.group(1)}章' if m else None

def classify_part2(item):
    key = src_chapter_key(item['chapter'])
    if key is None:
        return 5
    return SRC_CH_MAP.get(key, 5)

# keyword rules for part1 and overrides
PART1_RULES = [
    # (regex on stem+answer, chapter)
    (r'三美|闻一多|新诗格律|九叶|艾青|朦胧诗|第三代|新民歌|骆一禾|白洋淀|《回答》|《致橡树》|《一代人》|归来|诗歌|诗人|诗派|新诗潮|女性诗歌', 8),
    (r'样板戏|三突出|第一次文代会|《在延安文艺座谈会上的讲话》|双百|《纪要》|黑八论|武训传|文革文学|潜流|手抄本|地下文学|重写文学史|人文精神|20世纪文学|两结合', 1),
    (r'茶馆|第四种剧本|绝对信号|话剧|戏剧|戏曲|老舍|曹禺|探索剧', 4),
    (r'杨绛|张中行|余秋雨|散文|杂文|随想录|学者散文|大散文', 10),
    (r'台北人|白先勇|台湾|华语|华文|海外|香港|澳门|王鼎钧|陈映真|张大春|高行健|华语语系', 11),
    (r'80后|新世纪|2000|底层写作|《兄弟》|《蛙》|秦腔', 12),
    (r'废都|黄金时代|王小波|王朔|马桥词典|新生代|女性文学|私人生活|一个人的战争|长恨歌|陈染|林白|卫慧|棉棉|90年代|人文精神', 7),
    (r'青春之歌|红旗谱|创业史|三里湾|红岩|红日|林海雪原|保卫延安|杨沫|梁斌|柳青|赵树理|山药蛋|合作化|农村|17年|十七年|红色经典', 2),
    (r'伤痕|反思|班主任|陈奂生|高晓声|刘心武|王蒙|寻根|棋王|爸爸爸|受戒|汪曾祺|红高粱|莫言|张承志|北方的河|改革|乔厂长|蒋子龙', 6),
    (r'先锋|新写实|马原|余华|格非|苏童|残雪|刘震云|池莉|方方|刘恒|一地鸡毛|烦恼人生|山上的小屋', 7),
    (r'爱美剧|语丝|张天翼|徐枕亚|玉梨魂|金粉世家|鸳鸯蝴蝶', 5),
    (r'《风景》|新历史小说', 6),
]

def classify(item):
    if item['part'] == 'part2':
        ch = classify_part2(item)
    else:
        text = (item['stem'] or '') + (item['answer'] or '')
        ch = None
        for pat, c in PART1_RULES:
            if re.search(pat, text):
                ch = c
                break
        if ch is None:
            ch = 5
    # keyword overrides
    st = (item['stem'] or '') + (item['answer'] or '')
    if re.search(r'白洋淀|天安门诗抄|四点零八分', st):
        return 8
    if re.search(r'小鲍庄|铁凝|香雪', st) and item['type'] in ('名词解释','填空题'):
        return 6
    if re.search(r'第23章', item['chapter'] or ''):
        return 7
    return ch

for it in items:
    it['chapter_num'] = classify(it)
    it['doc_chapter'] = (it['chapter'] or '').strip() or '考研真题精选'
    it['school_year'] = extract_school_year(it['stem'])

# ---------------- helpers ----------------
def school_anno(it):
    sy = it['school_year']
    return f"（{sy}）" if sy else ""

def join_exp(it, extra=''):
    sy = it['school_year']
    base = ''
    if it['analysis']:
        base = re.sub(r'\s+', '', it['analysis'])
        if len(base) > 400:
            base = base[:400] + '……'
    if extra:
        base = (base + '；' if base else '') + extra
    if sy:
        base = (f"（{sy}）" + base) if base else f"（{sy}）"
    return base

def clean_stem_for_q(it):
    s = it['stem']
    s = re.sub(r'\[[^\]]*?(?:大学|学院|人大)[^\]]*研\]', '', s)
    s = re.sub(r'（[^）]*?(?:大学|学院|人大)[^）]*研）', '', s)
    s = re.sub(r'（\d+\s*字以上）', '', s)
    s = re.sub(r'^\s*[\d]+[\.、、]\s*', '', s)
    return s.strip()

def bullets(analysis):
    """Extract bullet point strings from analysis text."""
    out = []
    for line in (analysis or '').split('\n'):
        s = re.sub(r'^\s*[①②③④⑤⑥⑦⑧⑨⑩]+\s*', '', line).strip()
        if s and len(s) >= 4:
            out.append(re.sub(r'\s+', '', s))
    return out

# topic label from stem (strip trailing question words)
def topic_label(it, maxlen=26):
    s = clean_stem_for_q(it)
    s = re.sub(r'^(简述|简答|简评|简析|论述|分析|试析|试论|谈谈|结合|比较|概述|略述|如何看待|怎样评价)[\.\s]*', '', s)
    s = re.sub(r'[？?。]$', '', s)
    return s[:maxlen]

# global bullet pool for distractors
GLOBAL_BULLETS = []
for it in items:
    GLOBAL_BULLETS.extend(bullets(it['analysis']))
GLOBAL_BULLETS = [b for b in GLOBAL_BULLETS if 6 <= len(b) <= 40]
GLOBAL_BULLETS = list(dict.fromkeys(GLOBAL_BULLETS))

def pick_distractor(exclude_terms, n=1, pool=None):
    pool = pool or GLOBAL_BULLETS
    cand = [b for b in pool if b not in exclude_terms]
    if len(cand) < n:
        return ['以讽刺调侃的语言揭示社会现实中的矛盾'] * n
    return random.sample(cand, n)

questions = []
q_index = 1

def add(qtype, stem, answer, options=None, explanation="", chapter=None,
        tags=None, difficulty="medium", ans_fmt=None, doc_path="洪子诚当代文学史题库.docx"):
    global q_index
    q = {
        "id": qid(q_index),
        "type": qtype,
        "stem": stem,
        "options": options or [],
        "answer": answer,
        "explanation": explanation,
        "answerFormat": ans_fmt or ANS_FORMAT[qtype],
        "chapter": CH_NAMES[chapter] if chapter else CH_NAMES[5],
        "tags": ["文学史题库", "当代文学"] + [t for t in (tags or []) if t not in ("文学史题库", "当代文学")],
        "difficulty": difficulty,
        "source": {"blockId": "", "docPath": doc_path},
    }
    questions.append(q)
    q_index += 1
    return q

def shuffle_options(correct_text, distractor_texts, stem, explanation, chapter, tags, difficulty, doc_path):
    opts = [('A', correct_text)] + [(chr(ord('B')+i), t) for i, t in enumerate(distractor_texts)]
    random.shuffle(opts)
    key = [k for k, t in opts if t == correct_text][0]
    opts_sorted = sorted(opts, key=lambda x: x[0])
    add('single_choice', stem, key, [{'key': k, 'text': t} for k, t in opts_sorted],
        explanation=explanation, chapter=chapter, tags=tags, difficulty=difficulty, doc_path=doc_path)

print("helpers ready, global bullets:", len(GLOBAL_BULLETS))
json.dump({}, open(r'out/_dummy.json','w'))
