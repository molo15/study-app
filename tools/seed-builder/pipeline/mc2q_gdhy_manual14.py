# -*- coding: utf-8 -*-
"""古代汉语 扩充第十四批：冲刺补充"""
import io, sys, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'D:\study_app\tools\seed-builder\out\knowledge\古代汉语.knowledge.json'
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
        best = {"id": "k_zhen_gdhy_" + chapter, "name": chapter + "（真题补充）", "parent": "root",
                "chapter": chapter, "hot": False, "summary": "考研真题补充知识点。", "basicQuestions": []}
        KP['knowledge'].append(best)
    for e in best.get('basicQuestions', []):
        if norm(e['stem']) == norm(q['stem']): return False
    best['basicQuestions'].append(q); return True

Q = [
    {"ch": "词汇", "kw": "词的本义", "q": {"stem": "“汤”的本义是____。", "type": "blank",
        "answer": "热水", "options": [],
        "explanation": "“汤”本义为热水（“赴汤蹈火”），今义为菜汤。"}},
    {"ch": "词汇", "kw": "词的引申义与引申方式", "q": {"stem": "“引”由“开弓”引申为“拉长、延长”，属于____引申。", "type": "blank",
        "answer": "相关", "options": [],
        "explanation": "“引”由开弓相关引申为拉、引等义。"}},
    {"ch": "词汇", "kw": "词义感情色彩与轻重程度的变化", "q": {"stem": "“爪牙”古指____（得力助手），今指帮凶。", "type": "blank",
        "answer": "得力助手（武臣）", "options": [],
        "explanation": "“爪牙”由中性词变为贬义词，是感情色彩的变化。"}},
    {"ch": "词汇", "kw": "同义词辨析", "q": {"stem": "“执”与“持”，____更强调抓住不放。", "type": "blank",
        "answer": "执", "options": [],
        "explanation": "“执”强调执持不放，“持”重在拿着，二者在侧重上有别。"}},
    {"ch": "词汇", "kw": "合成词", "q": {"stem": "“城池”“门户”由两个意义相关语素构成，属于____合成词。", "type": "blank",
        "answer": "并列（联合）", "options": [],
        "explanation": "“城池”即城与池，“门户”即门与户，是并列式。"}},
    {"ch": "语法（上）", "kw": "副词", "q": {"stem": "“能”“可”在“非能水也”中是____动词（助动词）。", "type": "blank",
        "answer": "能愿（助）", "options": [],
        "explanation": "“能”是能愿动词（助动词），表能力。"}},
    {"ch": "语法（上）", "kw": "语气词、叹词、助词", "q": {"stem": "“呜呼”是表示____的叹词。", "type": "blank",
        "answer": "感叹（叹息）", "options": [],
        "explanation": "“呜呼”表感叹、叹息，是叹词。"}},
    {"ch": "语法（上）", "kw": "介词与连词", "q": {"stem": "“青，取之于蓝”中“于”引介____。", "type": "blank",
        "answer": "处所（来源）", "options": [],
        "explanation": "“于蓝”介引处所、来源。"}},
    {"ch": "语法（下）", "kw": "名词、形容词、数词用作动词", "q": {"stem": "“老吾老以及人之老”中第一个“老”是____活用。", "type": "blank",
        "answer": "形容词用作动词（尊老）", "options": [],
        "explanation": "“老吾老”中前“老”作动词，意为“尊敬、赡养”。"}},
    {"ch": "语法（下）", "kw": "被动句", "q": {"stem": "“戍卒叫，函谷举”中“举”表____（被动）。", "type": "blank",
        "answer": "被动（被攻占）", "options": [],
        "explanation": "“函谷举”即函谷关被攻占，是意念上的被动。"}},
    {"ch": "文字（上）", "kw": "象形与指事", "q": {"stem": "“瓜”描摹瓜形，是____字。", "type": "blank",
        "answer": "象形", "options": [],
        "explanation": "“瓜”象瓜实之形，是象形字。"}},
    {"ch": "文字（上）", "kw": "会意", "q": {"stem": "“明”由“日”“月”会意，表示____。", "type": "blank",
        "answer": "明亮（光明）", "options": [],
        "explanation": "“明”以日月相映会意为光明，是会意字。"}},
    {"ch": "文字（上）", "kw": "形声", "q": {"stem": "“柄”字中表音的“丙”是____旁。", "type": "blank",
        "answer": "声", "options": [],
        "explanation": "“柄”从木丙声，“丙”是声旁。"}},
    {"ch": "文字（下）", "kw": "古今字", "q": {"stem": "“要”与“腰”是____字关系。", "type": "blank",
        "answer": "古今", "options": [],
        "explanation": "“要”本义为腰，后加“月”作“腰”，是古今字。"}},
    {"ch": "文字（下）", "kw": "通假字", "q": {"stem": "“召有司案图”中“案”通“____”。", "type": "blank",
        "answer": "按", "options": [],
        "explanation": "“案”通“按”，意为察看，是通假字。"}},
    {"ch": "音韵", "kw": "声类、字母与三十六字母", "q": {"stem": "三十六字母中“端透定泥”属于____音。", "type": "blank",
        "answer": "舌（舌头）", "options": [],
        "explanation": "端透定泥是舌头音（舌音）。"}},
    {"ch": "音韵", "kw": "反切", "q": {"stem": "反切注音中，“切”表示____（拼合）。", "type": "blank",
        "answer": "拼合（两字相拼）", "options": [],
        "explanation": "“反”“切”都是拼音之意，即两字相拼注音。"}},
    {"ch": "音韵", "kw": "上古音", "q": {"stem": "研究上古声母，有“古无____（轻唇）音”之说。", "type": "blank",
        "answer": "轻唇", "options": [],
        "explanation": "清代学者提出“古无轻唇音”“古无舌上音”等上古声母规律。"}},
    {"ch": "训诂", "kw": "古注术语（一）", "q": {"stem": "“谓”常用于____（指具体含义）。", "type": "blank",
        "answer": "说明具体所指", "options": [],
        "explanation": "“谓”多用来解释句中词语的具体所指，如“王谓诸侯”。"}},
    {"ch": "训诂", "kw": "训诂的方法", "q": {"stem": "“互训”指用____（同义词）互相解释。", "type": "blank",
        "answer": "同义词", "options": [],
        "explanation": "互训用意义相同的词互相注释，如“老，考也”。"}},
    {"ch": "修辞", "kw": "借代", "q": {"stem": "“烽火”代指____（战争）。", "type": "blank",
        "answer": "战争（战乱）", "options": [],
        "explanation": "以“烽火”这一战争信号代指战争，是借代。"}},
    {"ch": "修辞", "kw": "委婉", "q": {"stem": "“先帝创业未半而中道崩殂”中“崩殂”委婉指____。", "type": "blank",
        "answer": "皇帝去世", "options": [],
        "explanation": "“崩殂”是帝王之死的委婉说法。"}},
    {"ch": "古书的文体", "kw": "序跋与书启", "q": {"stem": "写在书前的文字称为____。", "type": "blank",
        "answer": "序（叙）", "options": [],
        "explanation": "序在书前，跋在书后。"}},
    {"ch": "古书的文体", "kw": "奏议与诏令", "q": {"stem": "“疏”如《谏太宗十思疏》，是臣下上奏的____文体。", "type": "blank",
        "answer": "奏议", "options": [],
        "explanation": "“疏”是臣下分条陈述的奏议文体。"}},
    {"ch": "古书的标点", "kw": "古书标点中的常见错误", "q": {"stem": "“使子路反见之”若断为“使子路反/见之”，属于____错误。", "type": "blank",
        "answer": "断句（句读）", "options": [],
        "explanation": "断句不当导致文意变化，是句读错误。"}},
    {"ch": "诗词格律", "kw": "对仗", "q": {"stem": "律诗要求____联和颈联必须对仗。", "type": "blank",
        "answer": "颔", "options": [],
        "explanation": "律诗中间两联（颔联、颈联）要求对仗。"}},
    {"ch": "诗词格律", "kw": "近体诗的概念、发展与分类", "q": {"stem": "绝句每首____句。", "type": "blank",
        "answer": "四", "options": [],
        "explanation": "绝句四句，律诗八句，都是近体诗。"}},
    {"ch": "工具书简介", "kw": "字典与《说文解字》", "q": {"stem": "《说文解字》是一部分析____的字典。", "type": "blank",
        "answer": "字形（本义）", "options": [],
        "explanation": "《说文》从字形分析入手说明字的本义。"}},
    {"ch": "工具书简介", "kw": "训诂必读书目", "q": {"stem": "《说文解字》清代“四大家”之一是____（王筠）。", "type": "blank",
        "answer": "王筠", "options": [],
        "explanation": "清代《说文》四大家：段玉裁、桂馥、王筠、朱骏声。"}},
    {"ch": "词汇", "kw": "词义的扩大、缩小、转移", "q": {"stem": "“瓦”古指____（陶器总称），今专指屋瓦。", "type": "blank",
        "answer": "陶器（土器）", "options": [],
        "explanation": "“瓦”古义泛指陶器，今义缩小为屋瓦。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'古代汉语第十四批挂载 {n} 题')
