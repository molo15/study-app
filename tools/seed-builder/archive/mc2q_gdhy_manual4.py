# -*- coding: utf-8 -*-
"""古代汉语 扩充第四批：剩余薄弱点补充"""
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
    {"ch": "绪论", "kw": "学习古代汉语的方法", "q": {"stem": "学习古代汉语应把文选、____和常用词三者结合起来。", "type": "blank",
        "answer": "通论", "options": [],
        "explanation": "王力主编《古代汉语》主张文选、通论、常用词三结合。"}},
    {"ch": "绪论", "kw": "历史观点", "q": {"stem": "“妻子”古今含义不同，说明考察词义要有____的观点。", "type": "blank",
        "answer": "历史（发展）", "options": [],
        "explanation": "古今词义有差异，要以历史发展的观点辨析，不能以今律古。"}},
    {"ch": "文字（上）", "kw": "六书说", "q": {"stem": "六书之名，最早见于东汉____的《说文解字·叙》。", "type": "blank",
        "answer": "许慎", "options": [],
        "explanation": "许慎在《说文解字·叙》中首次系统阐述六书。"}},
    {"ch": "文字（上）", "kw": "会意", "q": {"stem": "下列属于会意字的是（　）", "type": "choice",
        "answer": "休", "options": ["休", "日", "本", "江"],
        "explanation": "“休”由“人”“木”会意；“日”象形、“本”指事、“江”形声。"}},
    {"ch": "文字（上）", "kw": "转注", "q": {"stem": "转注是指（　）", "type": "choice",
        "answer": "同部首意义相通的字互相注释", "options": ["同部首意义相通的字互相注释", "借同音字表示新义", "描摹事物形状", "用符号标示抽象意义"],
        "explanation": "转注指同一部首、意义相通的字互训，如“老”“考”。"}},
    {"ch": "训诂", "kw": "古注的体例", "q": {"stem": "郑玄为《诗经》所作的注解称为“____”。", "type": "blank",
        "answer": "笺", "options": [],
        "explanation": "郑玄《毛诗笺》，“笺”是对传的补充订正。"}},
    {"ch": "训诂", "kw": "训诂的体例类型", "q": {"stem": "随文释义，逐句注解经文的训诂体例称为____。", "type": "blank",
        "answer": "随文注（传注）", "options": [],
        "explanation": "随文注是依附原文逐一解释的体例，区别于通释语义的专著。"}},
    {"ch": "语法（上）", "kw": "古汉语语法研究简况", "q": {"stem": "我国第一部系统的汉语语法著作是《____》。", "type": "blank",
        "answer": "马氏文通", "options": [],
        "explanation": "马建忠《马氏文通》（1898）是我国第一部系统的语法著作。"}},
    {"ch": "语法（上）", "kw": "名词、动词、形容词、数量词", "q": {"stem": "“参差荇菜”中“参差”是____词。", "type": "blank",
        "answer": "形容", "options": [],
        "explanation": "“参差”表示长短不齐的样子，是形容词。"}},
    {"ch": "语法（下）", "kw": "词类活用的概念与判定条件", "q": {"stem": "“沛公军霸上”中“军”是____用作动词。", "type": "blank",
        "answer": "名词", "options": [],
        "explanation": "“军”本为名词（军队），此处活用作动词，意为“驻军”。"}},
    {"ch": "工具书简介", "kw": "《康熙字典》《中华大字典》《汉语大字典》", "q": {"stem": "《康熙字典》按____部首排列汉字。", "type": "blank",
        "answer": "214", "options": [],
        "explanation": "《康熙字典》分 214 个部首，是清代官修的字典。"}},
    {"ch": "工具书简介", "kw": "字典辞书的编排体例与注音方法", "q": {"stem": "古书注音常用“某音某”的方式，称为____。", "type": "blank",
        "answer": "直音", "options": [],
        "explanation": "直音是直接用同音字注音，如“拯音整”；另有反切注音。"}},
    {"ch": "工具书简介", "kw": "训诂必读书目", "q": {"stem": "清代段玉裁所著《____》是研读《说文》的重要著作。", "type": "blank",
        "answer": "说文解字注", "options": [],
        "explanation": "段玉裁《说文解字注》是清代《说文》研究的代表作。"}},
    {"ch": "工具书简介", "kw": "词典与《辞源》《辞海》《汉语大词典》", "q": {"stem": "以解释古汉语语词为主的大型词典是《____》。", "type": "blank",
        "answer": "辞源", "options": [],
        "explanation": "《辞源》侧重古汉语语词，《辞海》兼顾百科，《汉语大词典》收词宏富。"}},
    {"ch": "古书的文体", "kw": "文体分类标准", "q": {"stem": "古人划分文体，常依据文章的____（内容与形式）。", "type": "blank",
        "answer": "内容与形式", "options": [],
        "explanation": "文体分类综合考虑内容、形式、用途等因素，如《文心雕龙》的分类。"}},
    {"ch": "古书的标点", "kw": "古书标点中的常见错误", "q": {"stem": "古书标点最常见的错误是____不当。", "type": "blank",
        "answer": "断句", "options": [],
        "explanation": "点错句读（断句错误）是古书标点最常见的错误。"}},
    {"ch": "古书的标点", "kw": "标点古文的基本方法", "q": {"stem": "标点古文应通读全篇，先____（断句）后加标点。", "type": "blank",
        "answer": "断句", "options": [],
        "explanation": "标点古文的基本方法：通读全文、理清句读、再施以标点。"}},
    {"ch": "音韵", "kw": "五音七音与清浊", "q": {"stem": "七音是在五音之外，加上半舌音和____音。", "type": "blank",
        "answer": "半齿", "options": [],
        "explanation": "五音加半舌（来母）、半齿（日母）为七音。"}},
    {"ch": "音韵", "kw": "中古声调到北京音的变化", "q": {"stem": "现代汉语普通话的四声是阴平、阳平、上声和____。", "type": "blank",
        "answer": "去声", "options": [],
        "explanation": "现代北京音四声：阴平、阳平、上声、去声，入声已消失。"}},
    {"ch": "音韵", "kw": "《韵镜》、尖音与团音", "q": {"stem": "现代普通话中，“尖音”指____声母与齐齿、撮口呼相拼的音。", "type": "blank",
        "answer": "z、c、s", "options": [],
        "explanation": "尖音是 z、c、s 与 i、ü 相拼；团音是 j、q、x 与之相拼。"}},
    {"ch": "音韵", "kw": "反切", "q": {"stem": "“东，德红切”中“德”与“东”的____相同。", "type": "blank",
        "answer": "声母", "options": [],
        "explanation": "反切上字与被切字声母相同，下字与被切字韵、调相同。"}},
    {"ch": "文字（下）", "kw": "繁简字", "q": {"stem": "“後”的简体字是____。", "type": "blank",
        "answer": "后", "options": [],
        "explanation": "“後”简化作“后”，与“皇后”之“后”同形。"}},
    {"ch": "文字（下）", "kw": "异体字", "q": {"stem": "下列属于异体字的一组是（　）", "type": "choice",
        "answer": "泪—涙", "options": ["泪—涙", "莫—暮", "说—悦", "畔—叛"],
        "explanation": "“泪—涙”音义全同而形体不同，是异体字；后三组是古今字或通假字。"}},
    {"ch": "训诂", "kw": "重要训诂著作", "q": {"stem": "王引之《经义述闻》属于____类训诂著作。", "type": "blank",
        "answer": "训诂", "options": [],
        "explanation": "《经义述闻》是清代训诂名著，考释经义词句。"}},
    {"ch": "修辞", "kw": "变文与倒置", "q": {"stem": "“甚矣，汝之不惠”将谓语置于主语前，属于____。", "type": "blank",
        "answer": "倒置（倒装）", "options": [],
        "explanation": "此句“甚矣”前置，是主谓倒置（倒装），为强调而提前。"}},
    {"ch": "修辞", "kw": "顶真与析字", "q": {"stem": "把汉字拆开来分析表意的修辞手法叫____。", "type": "blank",
        "answer": "析字", "options": [],
        "explanation": "析字是离合字形以表情达意，如“人言为信”。"}},
    {"ch": "诗词格律", "kw": "对联", "q": {"stem": "对联起源于古代的____（桃符）。", "type": "blank",
        "answer": "桃符", "options": [],
        "explanation": "对联由桃符演变而来，讲究对仗工整、平仄相谐。"}},
    {"ch": "诗词格律", "kw": "近体诗的概念、发展与分类", "q": {"stem": "超过八句的律诗称为____。", "type": "blank",
        "answer": "排律", "options": [],
        "explanation": "排律是超过八句、按律诗规则排比的近体诗。"}},
    {"ch": "音韵", "kw": "声类、字母与三十六字母", "q": {"stem": "“三十六字母”实际指中古的____个声母。", "type": "blank",
        "answer": "三十六（36）", "options": [],
        "explanation": "三十六字母是宋代人归纳的中古声母系统。"}},
    {"ch": "训诂", "kw": "训诂的体例类型", "q": {"stem": "通释语义、不随文作注的训诂专著，如《尔雅》，属于____训诂体例。", "type": "blank",
        "answer": "通释语义（专著式）", "options": [],
        "explanation": "训诂有随文注与专著两类，《尔雅》是通释语义的专著。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'古代汉语第四批挂载 {n} 题')
