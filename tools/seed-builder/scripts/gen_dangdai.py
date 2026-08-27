# -*- coding: utf-8 -*-
"""Generate bank-zhongguo-dangdai-wenxue JSON (final budgeted version)."""
import re, json, random, sys
sys.path.insert(0, r'D:\study_app\tools\seed-builder\scripts')

from dangdai_curated_a import CURATED as CA
from dangdai_curated_b import CURATED as CB
CURATED = {}
CURATED.update(CA)
CURATED.update(CB)

BANK_ID = "bank-zhongguo-dangdai-wenxue"
CH_NAMES = {
    1: "第一章 1949-1976 文学思潮",
    2: "第二章 50、60 年代小说",
    3: "第三章 50、60 年代新诗",
    4: "第四章 50、60 年代戏剧、散文",
    5: "第五章 80、90 年代文学思潮",
    6: "第六章 80 年代小说",
    7: "第七章 90 年代小说",
    8: "第八章 80、90 年代新诗",
    9: "第九章 80、90 年代戏剧",
    10: "第十章 80、90 年代散文",
    11: "第十一章 台港文学",
    12: "第十二章 2000-2016 年文学概述",
}
ANS_FORMAT = {
    "single_choice": "单选：从所给选项中选出唯一正确答案",
    "multi_choice": "多选：选出所有符合题意的选项",
    "blank": "填空：在横线处填出正确答案（多个空按顺序填写）",
    "short_answer": "简答/论述：分要点作答，先摆结论再给依据",
    "true_false": "判断：判断下列说法的正误（正确或错误）",
}

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
PART1_RULES = [
    (r'三美|闻一多|新诗格律|九叶|艾青|朦胧诗|第三代|新民歌|骆一禾|白洋淀|《回答》|《致橡树》|《一代人》|归来|诗歌|诗人|诗派|新诗潮|女性诗歌', 8),
    (r'样板戏|三突出|第一次文代会|《在延安文艺座谈会上的讲话》|双百|《纪要》|黑八论|武训传|文革文学|潜流|手抄本|地下文学|重写文学史|人文精神|20世纪文学|两结合', 1),
    (r'茶馆|第四种剧本|话剧|戏剧|戏曲|老舍|曹禺', 4),
    (r'绝对信号|探索剧|高行健', 9),
    (r'杨绛|张中行|余秋雨|散文|杂文|随想录|学者散文|大散文', 10),
    (r'台北人|白先勇|台湾|华语|华文|海外|香港|澳门|王鼎钧|陈映真|张大春|高行健|华语语系', 11),
    (r'80后|新世纪|2000|底层写作|《兄弟》|《蛙》|秦腔', 12),
    (r'废都|黄金时代|王小波|王朔|马桥词典|新生代|女性文学|私人生活|一个人的战争|长恨歌|陈染|林白|卫慧|棉棉|90年代', 7),
    (r'青春之歌|红旗谱|创业史|三里湾|红岩|红日|林海雪原|保卫延安|杨沫|梁斌|柳青|赵树理|山药蛋|合作化|农村|17年|十七年|红色经典', 2),
    (r'伤痕|反思|班主任|陈奂生|高晓声|刘心武|王蒙|寻根|棋王|爸爸爸|受戒|汪曾祺|红高粱|莫言|张承志|北方的河|改革|乔厂长|蒋子龙', 6),
    (r'先锋|新写实|马原|余华|格非|苏童|残雪|刘震云|池莉|方方|刘恒|一地鸡毛|烦恼人生|山上的小屋', 7),
    (r'爱美剧|语丝|张天翼|徐枕亚|玉梨魂|金粉世家|鸳鸯蝴蝶', 5),
    (r'《风景》|新历史小说', 6),
]

def src_key(ch):
    if not ch:
        return None
    m = re.match(r'^第(\d+)章', ch)
    return f'第{m.group(1)}章' if m else None

def classify(item):
    if item['part'] == 'part2':
        key = src_key(item['chapter'])
        return SRC_CH_MAP.get(key, 5)
    text = (item['stem'] or '') + (item['answer'] or '')
    for pat, c in PART1_RULES:
        if re.search(pat, text):
            return c
    return 5

def clean_stem(s):
    s = re.sub(r'\[[^\]]*?(?:大学|学院|人大)[^\]]*研\]', '', s)
    s = re.sub(r'（[^）]*?(?:大学|学院|人大)[^）]*研）', '', s)
    s = re.sub(r'（\d+\s*字以上）', '', s)
    s = re.sub(r'^\s*[\d]+[\.、、]\s*', '', s)
    s = re.sub(r'^相关试题[:：]\s*', '', s)
    s = s.replace('\t', '＿').replace('\u3000', '＿')
    return s.strip()

def school_year(s):
    m = re.search(r'\[([^\]]*?(?:大学|学院|人大)[^\]]*研)\]', s)
    if m:
        return m.group(1)
    m = re.search(r'（([^）]*?(?:大学|学院|人大)[^）]*研)）', s)
    return m.group(1) if m else ""

def sentences(text, lo=8, hi=46):
    text = re.sub(r'[①-⑩]\s*', '。', text or '')
    out = []
    for p in re.split(r'[；;。！？]', text):
        p = re.sub(r'\s+', '', p)
        if lo <= len(p) <= hi and not p.startswith('【'):
            out.append(p)
    return out

def build_pool(items):
    pool = []
    for it in items:
        txt = (it['answer'] or '') + '。' + (it['analysis'] or '')
        pool.extend(sentences(txt))
    return list(dict.fromkeys(pool))

def condense(s, n=42):
    s = re.sub(r'\s+', '', s or '')
    return s if len(s) <= n else s[:n] + '…'

items = json.load(open(r'D:\study_app\tools\seed-builder\out\_dangdai_items3.json', encoding='utf-8'))
POOL = build_pool(items)
random.seed(7)

questions = []
idx = 0

def emit(qtype, stem, answer, options=None, explanation="", chapter=5, tags=None,
          difficulty="medium", ans_fmt=None, block=""):
    global idx
    idx += 1
    questions.append({
        "id": f"{BANK_ID}:t_{idx:06d}",
        "type": qtype,
        "stem": stem,
        "options": options or [],
        "answer": answer,
        "explanation": explanation,
        "answerFormat": ans_fmt or ANS_FORMAT[qtype],
        "chapter": CH_NAMES[chapter],
        "tags": ["文学史题库", "当代文学"] + [t for t in (tags or []) if t not in ("文学史题库", "当代文学")],
        "difficulty": difficulty,
        "source": {"blockId": block, "docPath": f"洪子诚当代文学史题库.docx（章节：{CH_NAMES[chapter]}）"},
    })

def distractors(exclude, n=3, lo=10, hi=46):
    cand = [p for p in POOL if p not in exclude and lo <= len(p) <= hi]
    random.shuffle(cand)
    return cand[:n]

def short_answer_from(it):
    txt = re.sub(r'\s+', '', it['analysis'] or it['answer'] or '')
    if not txt:
        return None
    parts = re.split(r'(?<=。)(?=[①②③④⑤⑥⑦⑧⑨⑩])|(?=[①②③④⑤⑥⑦⑧⑨⑩])', txt)
    buf = ""
    pts = []
    for p in parts:
        if re.match(r'^[①②③④⑤⑥⑦⑧⑨⑩]', p):
            if buf:
                pts.append(buf)
            buf = p
        else:
            buf += p
    if buf:
        pts.append(buf)
    if len(pts) == 1:
        pts = sentences(pts[0], lo=6, hi=80)
    return '；'.join(pts[:6]) if pts else condense(txt, 60)

def has_bullets(it):
    return bool(re.search(r'[①②③④⑤⑥⑦⑧⑨⑩]', it['analysis'] or it['answer'] or ''))

# ---------------- budget planning ----------------
# classify all items
for it in items:
    it['ch'] = classify(it)
    # keyword overrides
    text = (it['stem'] or '') + (it['answer'] or '')
    if re.search(r'探索剧|绝对信号|高行健|实验戏剧', text):
        it['ch'] = 9
    if re.search(r'《茶馆》|第四种剧本|龙须沟', text) and it['type'] == '填空题':
        it['ch'] = 4
    it['sy'] = school_year(it['stem'])

n_select = 0
n_blank = 0
n_noun = 0
n_short = 0
n_essay = 0
for it in items:
    t = it['type']
    if t == '选择题':
        n_select += 1
    elif t == '填空题':
        n_blank += 1
    elif t == '名词解释':
        n_noun += 1
    elif t == '简答题':
        n_short += 1
    else:
        n_essay += 1

# short_answer budget = 15% of total
target_total = 360
sa_budget = int(target_total * 0.15) - 2  # 52, leave headroom for essay 'sa' subs
# decide which 简答 become short_answer: prefer bullet-structured ones
short_items = [i for i, it in enumerate(items) if it['type'] == '简答题']
short_items_sorted = sorted(short_items, key=lambda i: (0 if has_bullets(items[i]) else 1, -len(items[i]['analysis'] or '')))
sa_ids = set(short_items_sorted[:sa_budget])

# essays: part1 essays get 2 questions each; part2 essays get 1 each (curated use first sub, uncurated auto 1)
# compute essay split list
def essay_subs(i, it):
    if i in CURATED:
        subs = CURATED[i]
        return subs[:2]
    return None  # auto

# ---------------- process ----------------
def process(item, i):
    ch = item['ch']
    sy = item['sy']
    sy_note = f"（{sy}）" if sy else ""
    blk = f"源题{i}"
    typ = item['type']

    # 选择题
    if typ == '选择题':
        opts = [o.strip() for o in item['options'] if o.strip()]
        ans = item['answer'].strip()
        if len(opts) >= 2 and len(ans) == 1:
            ana = re.sub(r'\s+', '', item['analysis'] or '')
            exp = sy_note + (condense(ana, 200) if ana else condense(item['answer'], 80))
            emit('single_choice', clean_stem(item['stem']), ans.upper(),
                 [{'key': chr(ord('A')+k), 'text': v} for k, v in enumerate(opts)],
                 explanation=exp, chapter=ch, difficulty='easy', block=blk)
        return

    # 填空题
    if typ == '填空题':
        stem = clean_stem(item['stem'])
        ans_parts = [a.strip() for a in re.split(r'[|｜]', item['answer']) if a.strip()]
        ana = re.sub(r'\s+', '', item['analysis'] or '')
        exp = sy_note + (condense(ana, 200) if ana else condense(item['answer'], 80))
        if len(ans_parts) == 1 and ans_parts[0] and not re.search(r'＿', stem):
            fact = ans_parts[0]
            ds = distractors([fact], n=3, lo=2, hi=14)
            opts = [fact] + ds
            random.shuffle(opts)
            key = chr(ord('A') + opts.index(fact))
            emit('single_choice', f"题干空缺处应填入的内容是？（{condense(stem, 26)}）", key,
                 [{'key': chr(ord('A')+k), 'text': v} for k, v in enumerate(opts)],
                 explanation=exp, chapter=ch, difficulty='easy', block=blk)
        else:
            emit('blank', stem, ans_parts, explanation=exp, chapter=ch, difficulty='easy', block=blk)
        return

    # 名词解释 -> single_choice
    if typ == '名词解释':
        topic = condense(clean_stem(item['stem']) or item['answer'], 22)
        facts = sentences(item['answer'] + '。' + (item['analysis'] or ''), lo=12, hi=42)
        if not facts:
            facts = [condense(item['answer'], 30)]
        correct = facts[0]
        opts = [correct] + distractors([correct], n=3, lo=10, hi=46)
        random.shuffle(opts)
        key = chr(ord('A') + opts.index(correct))
        ana = re.sub(r'\s+', '', item['analysis'] or '')
        exp = sy_note + (condense(ana, 200) if ana else condense(item['answer'], 80))
        emit('single_choice', f"关于“{topic}”，下列说法正确的一项是？", key,
             [{'key': chr(ord('A')+k), 'text': v} for k, v in enumerate(opts)],
             explanation=exp, chapter=ch, difficulty='medium', block=blk)
        return

    # 简答题
    if typ == '简答题':
        ana = re.sub(r'\s+', '', item['analysis'] or '')
        exp_base = (condense(ana, 200) if ana else condense(item['answer'], 80))
        if i in CURATED:
            # keep the strongest single sub-question per curated short-answer item to control volume
            for sub in CURATED[i][:1]:
                t = sub['t']
                sexp = sub.get('exp', '')
                if sy and sy not in sexp:
                    sexp = sexp + sy_note if sexp else sy_note
                if not sexp:
                    sexp = exp_base
                if t == 'sc':
                    ans_letter = sub['ans'] if isinstance(sub['ans'], str) else chr(ord('A') + sub['ans'])
                    emit('single_choice', sub['stem'], ans_letter,
                         [{'key': chr(ord('A')+k), 'text': v} for k, v in enumerate(sub['opts'])],
                         explanation=sexp, chapter=ch, difficulty='medium', block=blk)
                elif t == 'blank':
                    emit('blank', sub['stem'], sub['ans'], explanation=sexp, chapter=ch,
                         difficulty='easy', block=blk)
                elif t == 'tf':
                    emit('true_false', sub['stem'], sub['ans'], explanation=sexp, chapter=ch,
                         difficulty='medium', block=blk)
                elif t == 'sa':
                    emit('short_answer', sub['stem'], sub['ans'], explanation=sexp, chapter=ch,
                         difficulty='hard', block=blk)
            return
        exp = sy_note + exp_base if sy else exp_base
        if i in sa_ids:
            # short_answer (要点化)
            sa = short_answer_from(item) or condense(item['answer'], 60)
            emit('short_answer', clean_stem(item['stem']), sa, explanation=exp,
                 chapter=ch, difficulty='hard', block=blk)
        else:
            facts = sentences(item['answer'] + '。' + ana, lo=14, hi=46)
            correct = facts[0] if facts else condense(item['answer'], 26)
            opts = [correct] + distractors([correct], n=3, lo=12, hi=46)
            random.shuffle(opts)
            key = chr(ord('A') + opts.index(correct))
            emit('single_choice', f"关于“{condense(item['stem'], 22)}”，下列说法正确的一项是？", key,
                 [{'key': chr(ord('A')+k), 'text': v} for k, v in enumerate(opts)],
                 explanation=exp, chapter=ch, difficulty='medium', block=blk)
        return

    # 论述/作品分析
    subs = essay_subs(i, item)
    ana = re.sub(r'\s+', '', item['analysis'] or '')
    exp_base = (condense(ana, 200) if ana else condense(item['answer'], 80))
    exp = sy_note + exp_base if sy else exp_base
    if subs is not None:
        # part1 curated essays can yield 2 sub-questions; part2 yield 1
        maxsubs = 2 if item['part'] == 'part1' else 1
        for sub in subs[:maxsubs]:
            t = sub['t']
            sexp = sub.get('exp', '')
            if sy and sy not in sexp:
                sexp = sexp + sy_note if sexp else sy_note
            if not sexp:
                sexp = exp_base
            if t == 'sc':
                ans_letter = sub['ans'] if isinstance(sub['ans'], str) else chr(ord('A') + sub['ans'])
                emit('single_choice', sub['stem'], ans_letter,
                     [{'key': chr(ord('A')+k), 'text': v} for k, v in enumerate(sub['opts'])],
                     explanation=sexp, chapter=ch, difficulty='medium', block=blk)
            elif t == 'blank':
                emit('blank', sub['stem'], sub['ans'], explanation=sexp, chapter=ch,
                     difficulty='easy', block=blk)
            elif t == 'tf':
                emit('true_false', sub['stem'], sub['ans'], explanation=sexp, chapter=ch,
                     difficulty='medium', block=blk)
            elif t == 'sa':
                emit('short_answer', sub['stem'], sub['ans'], explanation=sexp, chapter=ch,
                     difficulty='hard', block=blk)
        return
    # auto
    topic = condense(clean_stem(item['stem']), 20)
    facts = sentences(ana or item['answer'], lo=14, hi=46)
    f = facts[0] if facts else condense(item['answer'], 30)
    opts = [f] + distractors([f], n=3, lo=12, hi=46)
    random.shuffle(opts)
    key = chr(ord('A') + opts.index(f))
    emit('single_choice', f"关于“{topic}”，下列说法正确的一项是？", key,
         [{'key': chr(ord('A')+k), 'text': v} for k, v in enumerate(opts)],
         explanation=exp, chapter=ch, difficulty='medium', block=blk)

for i, it in enumerate(items):
    process(it, i)

from collections import Counter
print("generated:", len(questions))
print(Counter(q['type'] for q in questions))
sa_n = sum(1 for q in questions if q['type'] == 'short_answer')
print("short_answer share: %.1f%%" % (100.0 * sa_n / len(questions)))
print(Counter(q['chapter'] for q in questions))
json.dump({"bankId": BANK_ID, "questions": questions},
          open(r'D:\study_app\tools\seed-builder\out\zhenti\wenxue-dangdai-tiku.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print("saved")
