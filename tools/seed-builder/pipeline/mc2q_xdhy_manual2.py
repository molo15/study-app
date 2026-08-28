# -*- coding: utf-8 -*-
"""现代汉语 人工设计扩充 第二批：文字 + 词汇薄弱点"""
import io, sys, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json'
KP = json.load(open(P, encoding='utf-8'))
def norm(s): return re.sub(r'[（）()。，、；：""“”\'  ]', '', s)
def mount(chapter, q, kw):
    kps = [k for k in KP['knowledge'] if k['chapter'] == chapter]
    best = None
    for k in kps:
        if kw and kw in k['name']:
            best = k; break
    if best is None:
        for k in kps:
            if '真题补充' in k['name']:
                best = k; break
    if best is None:
        best = {"id": "k_zhen_xdhy_" + chapter, "name": chapter + "（真题补充）", "parent": "root",
                "chapter": chapter, "hot": False, "summary": "考研真题补充知识点。", "basicQuestions": []}
        KP['knowledge'].append(best)
    for e in best.get('basicQuestions', []):
        if norm(e['stem']) == norm(q['stem']): return False
    best['basicQuestions'].append(q); return True

Q = [
    # ===== 文字 =====
    {"ch": "文字", "kw": "偏旁与部首", "q": {"stem": "部首是字典中具有____作用的偏旁。", "type": "blank",
        "answer": "归类（表意）", "options": [],
        "explanation": "部首是字典中用于归类的偏旁，一般具有表意作用，如“氵”是水的部首。"}},
    {"ch": "文字", "kw": "偏旁与部首", "q": {"stem": "“湖、河、海”的部首“氵”在表义上属于（　）", "type": "choice",
        "answer": "形旁", "options": ["形旁", "声旁", "记号", "部首偏旁兼声旁"],
        "explanation": "“氵”是形旁，表示与水有关的意义；这类字多为形声字。"}},
    {"ch": "文字", "kw": "异体字与异读词", "q": {"stem": "音义相同而形体不同的字称为____。", "type": "blank",
        "answer": "异体字", "options": [],
        "explanation": "异体字是音义完全相同、仅形体不同的字，如“峰—峯”。"}},
    {"ch": "文字", "kw": "异体字与异读词", "q": {"stem": "一个词有不止一个读音的现象称为____。", "type": "blank",
        "answer": "异读词", "options": [],
        "explanation": "异读词指一个词存在不同读音的现象，如“血”有xiě、xuè两读。"}},
    {"ch": "文字", "kw": "笔画与笔顺", "q": {"stem": "汉字的基本笔画有横、竖、撇、点、____五种。", "type": "blank",
        "answer": "折", "options": [],
        "explanation": "汉字基本笔画为横、竖、撇、点、折五种，其他笔画由它们派生。"}},
    {"ch": "文字", "kw": "笔画与笔顺", "q": {"stem": "“十”字的正确笔顺是（　）", "type": "choice",
        "answer": "先横后竖", "options": ["先横后竖", "先竖后横", "先撇后捺", "先上后下"],
        "explanation": "“十”字笔顺应先写横再写竖，遵循“先横后竖”的笔顺规则。"}},
    {"ch": "文字", "kw": "形声字", "q": {"stem": "形声字中表示读音部分的是____旁。", "type": "blank",
        "answer": "声", "options": [],
        "explanation": "形声字由形旁和声旁组成，形旁表意、声旁表音。"}},
    {"ch": "文字", "kw": "形声字", "q": {"stem": "下列属于形声字的是（　）", "type": "choice",
        "answer": "江", "options": ["江", "休", "日", "上"],
        "explanation": "“江”是形声字（氵表意、工表音）；“休”是会意字，“日”“上”是象形和指事字。"}},
    {"ch": "文字", "kw": "汉字标准化（四定）", "q": {"stem": "汉字标准化的“四定”包括定量、定形、____、定序。", "type": "blank",
        "answer": "定音", "options": [],
        "explanation": "汉字标准化指定量、定形、定音、定序四个方面。"}},
    {"ch": "文字", "kw": "简化字与繁体字", "q": {"stem": "汉字简化主要采用简化偏旁、____、草书楷化等方式。", "type": "blank",
        "answer": "同音代替", "options": [],
        "explanation": "汉字简化方式有简化偏旁、同音代替、草书楷化等。"}},
    {"ch": "文字", "kw": "独体字与合体字", "q": {"stem": "下列属于独体字的是（　）", "type": "choice",
        "answer": "日", "options": ["日", "林", "休", "明"],
        "explanation": "“日”是不能再拆分的独体字；“林”“休”“明”都是由部件构成的合体字。"}},
    {"ch": "文字", "kw": "六书", "q": {"stem": "六书中属于造字法的有象形、指事、会意和____四种。", "type": "blank",
        "answer": "形声", "options": [],
        "explanation": "六书是象形、指事、会意、形声、转注、假借，前四种是造字法，后两种是用字法。"}},
    # ===== 词汇 =====
    {"ch": "词汇", "kw": "义项、义素与语义场", "q": {"stem": "词的理性意义的分项称为____。", "type": "blank",
        "answer": "义项", "options": [],
        "explanation": "义项是词的理性意义的分项，一个词可以有几个义项。"}},
    {"ch": "词汇", "kw": "义项、义素与语义场", "q": {"stem": "同义词构成的语义关系属于（　）", "type": "choice",
        "answer": "同义聚合关系", "options": ["同义聚合关系", "反义对立关系", "上下位包含关系", "整体部分关系"],
        "explanation": "同义词在语义上构成同义聚合关系（同义场），反义词构成反义对立关系。"}},
    {"ch": "词汇", "kw": "词义（理性义与色彩义）", "q": {"stem": "词的感情色彩分为褒义、贬义和____。", "type": "blank",
        "answer": "中性", "options": [],
        "explanation": "感情色彩分褒义、贬义、中性三类。"}},
    {"ch": "词汇", "kw": "词根与词缀", "q": {"stem": "表示词的基本意义、体现词汇意义的语素是____。", "type": "blank",
        "answer": "词根", "options": [],
        "explanation": "词根是词的核心部分，表示基本词汇意义；词缀附加在词根上表示附加意义或语法意义。"}},
    {"ch": "词汇", "kw": "词根与词缀", "q": {"stem": "下列词语中“子”是词缀的是（　）", "type": "choice",
        "answer": "桌子", "options": ["桌子", "莲子", "孔子", "女子"],
        "explanation": "“桌子”的“子”是词缀（虚化后缀）；“莲子”“孔子”“女子”的“子”都有实义，是词根。"}},
    {"ch": "词汇", "kw": "单纯词与合成词", "q": {"stem": "由一个语素构成的词称为____。", "type": "blank",
        "answer": "单纯词", "options": [],
        "explanation": "单纯词由一个语素构成，如“天”“蝴蝶”“葡萄”；合成词由两个以上语素构成。"}},
    {"ch": "词汇", "kw": "单纯词与合成词", "q": {"stem": "下列属于合成词的是（　）", "type": "choice",
        "answer": "朋友", "options": ["朋友", "玻璃", "仿佛", "蜘蛛"],
        "explanation": "“朋友”由“朋”“友”两个语素构成，是合成词；其余都是双音节单纯词。"}},
    {"ch": "词汇", "kw": "基本词汇与一般词汇", "q": {"stem": "基本词汇具有稳固性、能产性和____三大特点。", "type": "blank",
        "answer": "全民常用性", "options": [],
        "explanation": "基本词汇具有稳固性、能产性、全民常用性三大特点。"}},
    {"ch": "词汇", "kw": "词义的演变", "q": {"stem": "词义演变有词义扩大、词义缩小和____三种情况。", "type": "blank",
        "answer": "词义转移", "options": [],
        "explanation": "词义演变包括扩大（如“江”由专指长江到泛指河流）、缩小、转移。"}},
    {"ch": "词汇", "kw": "语素", "q": {"stem": "语素是____的结合体。", "type": "blank",
        "answer": "音义（语音和意义）", "options": [],
        "explanation": "语素是最小的音义结合体，是构词单位。"}},
    {"ch": "词汇", "kw": "同义词与反义词", "q": {"stem": "“母亲”和“妈妈”在色彩义上的主要差别是（　）", "type": "choice",
        "answer": "语体色彩不同", "options": ["语体色彩不同", "感情色彩不同", "形象色彩不同", "理性义不同"],
        "explanation": "“母亲”是书面语，“妈妈”是口语，二者语体色彩不同。"}},
    {"ch": "词汇", "kw": "熟语", "q": {"stem": "熟语包括成语、惯用语、歇后语和____。", "type": "blank",
        "answer": "谚语", "options": [],
        "explanation": "熟语是固定的短语，包括成语、惯用语、歇后语、谚语。"}},
    {"ch": "词汇", "kw": "合成词的结构", "q": {"stem": "“汽车”的构词方式是（　）", "type": "choice",
        "answer": "偏正式", "options": ["偏正式", "并列式", "动宾式", "补充式"],
        "explanation": "“汽车”中“车”是中心语，“汽”修饰限定“车”，是偏正式（定中）合成词。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'第二批挂载 {n} 题')
