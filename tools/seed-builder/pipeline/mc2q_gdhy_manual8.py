# -*- coding: utf-8 -*-
"""古代汉语 扩充第八批：深层考点继续补充"""
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
    {"ch": "词汇", "kw": "词义的扩大、缩小、转移", "q": {"stem": "“走”古义为____，今义为行走。", "type": "blank",
        "answer": "跑", "options": [],
        "explanation": "“走”词义由“跑”转移为“行走”，是词义转移。"}},
    {"ch": "词汇", "kw": "词的引申义与引申方式", "q": {"stem": "“道”由“道路”引申出“道理”，是由具体到抽象的____引申。", "type": "blank",
        "answer": "比喻", "options": [],
        "explanation": "“道”由道路喻指道理，是比喻引申。"}},
    {"ch": "词汇", "kw": "词的本义", "q": {"stem": "“鄙”的本义是____。", "type": "blank",
        "answer": "边邑（边远地方）", "options": [],
        "explanation": "“鄙”本义为边邑，引申为鄙陋、粗俗。"}},
    {"ch": "词汇", "kw": "单纯词", "q": {"stem": "“衣裳”在古汉语中通常指____。", "type": "blank",
        "answer": "上衣和下裳（两个词）", "options": [],
        "explanation": "“衣”是上衣，“裳”是下衣，古汉语中常是两个词。"}},
    {"ch": "词汇", "kw": "单纯词", "q": {"stem": "“徘徊”“彷徨”属于____联绵词。", "type": "blank",
        "answer": "叠韵", "options": [],
        "explanation": "“徘徊”（huái）“彷徨”（huáng）韵母相同，是叠韵联绵词。"}},
    {"ch": "语法（上）", "kw": "代词", "q": {"stem": "“彼君子兮”中“彼”是____指代词。", "type": "blank",
        "answer": "远", "options": [],
        "explanation": "“彼”表远指，“此”表近指。"}},
    {"ch": "语法（上）", "kw": "副词", "q": {"stem": "“水波稍稍平”中“稍稍”是____副词。", "type": "blank",
        "answer": "时间（逐渐）", "options": [],
        "explanation": "“稍稍”表逐渐，是时间副词。"}},
    {"ch": "语法（上）", "kw": "语气词、叹词、助词", "q": {"stem": "“学而时习之，不亦说乎”中“乎”表示____语气。", "type": "blank",
        "answer": "反问", "options": [],
        "explanation": "“不亦……乎”是反问句式，“乎”加强反问语气。"}},
    {"ch": "语法（上）", "kw": "介词与连词", "q": {"stem": "“然则北通巫峡，南极潇湘”中“然则”表示____。", "type": "blank",
        "answer": "顺承（那么）", "options": [],
        "explanation": "“然则”意为“既然如此，那么”，表顺承推论。"}},
    {"ch": "语法（上）", "kw": "兼词", "q": {"stem": "“投诸渤海之尾”中“诸”兼有“之”“____”二词。", "type": "blank",
        "answer": "于", "options": [],
        "explanation": "“诸”=“之于”，兼有代词“之”和介词“于”。"}},
    {"ch": "语法（下）", "kw": "判断句", "q": {"stem": "“此必是豫让也”中“是”在句中表示____。", "type": "blank",
        "answer": "判断", "options": [],
        "explanation": "“是”作判断词，相当于现代汉语的“是”。"}},
    {"ch": "语法（下）", "kw": "意动用法", "q": {"stem": "“侣鱼虾而友麋鹿”中“侣”“友”是____用法。", "type": "blank",
        "answer": "意动", "options": [],
        "explanation": "“侣鱼虾”即以鱼虾为伴侣，名词意动用法。"}},
    {"ch": "语法（下）", "kw": "使动用法", "q": {"stem": "“既来之，则安之”中“来”“安”是____用法。", "type": "blank",
        "answer": "使动", "options": [],
        "explanation": "“来之”即使之来，“安之”即使之安，是使动用法。"}},
    {"ch": "语法（下）", "kw": "名词作状语", "q": {"stem": "“其一犬坐于前”中“犬”作____。", "type": "blank",
        "answer": "状语", "options": [],
        "explanation": "“犬坐”即“像狗一样蹲坐”，“犬”是名词作状语，表比喻。"}},
    {"ch": "语法（下）", "kw": "词序：宾语前置", "q": {"stem": "“微斯人，吾谁与归”中“谁”是____前置。", "type": "blank",
        "answer": "介词宾语", "options": [],
        "explanation": "疑问代词“谁”作介词“与”的宾语而前置。"}},
    {"ch": "文字（上）", "kw": "六书说", "q": {"stem": "“从”由两个“人”前后相随组成，是____字。", "type": "blank",
        "answer": "会意", "options": [],
        "explanation": "“从”两“人”相从，会意字。"}},
    {"ch": "文字（上）", "kw": "形声", "q": {"stem": "“梅”字中表示意义的“木”是____旁。", "type": "blank",
        "answer": "形", "options": [],
        "explanation": "“梅”从木每声，“木”是形旁，“每”是声旁。"}},
    {"ch": "文字（下）", "kw": "古今字", "q": {"stem": "“内”与“纳”是____字关系。", "type": "blank",
        "answer": "古今", "options": [],
        "explanation": "“内”古有“纳”义，后加形旁作“纳”，是古今字。"}},
    {"ch": "文字（下）", "kw": "通假字", "q": {"stem": "“愿伯具言臣之不敢倍德也”中“倍”通“____”。", "type": "blank",
        "answer": "背", "options": [],
        "explanation": "“倍”通“背”，意为违背，是通假字。"}},
    {"ch": "文字（下）", "kw": "小篆与隶变", "q": {"stem": "隶书是____（朝代）通行的字体。", "type": "blank",
        "answer": "汉", "options": [],
        "explanation": "隶书在汉代定型通行，故称“汉隶”。"}},
    {"ch": "音韵", "kw": "声类、字母与三十六字母", "q": {"stem": "“精、清、从、心、邪”在三十六字母中属于____音。", "type": "blank",
        "answer": "齿", "options": [],
        "explanation": "精清从心邪是齿头音（齿音）。"}},
    {"ch": "音韵", "kw": "反切", "q": {"stem": "“母，莫厚切”中“厚”与被切字“母”的____相同。", "type": "blank",
        "answer": "韵母和声调", "options": [],
        "explanation": "反切下字取韵与调，“厚”与“母”同韵同调。"}},
    {"ch": "音韵", "kw": "上古音", "q": {"stem": "宋人“叶韵”说，是把后人的读音强加于____。", "type": "blank",
        "answer": "古诗（上古音）", "options": [],
        "explanation": "“叶韵”误以为古诗可按当时口语改读，混淆了古今音变。"}},
    {"ch": "训诂", "kw": "古注术语（二）", "q": {"stem": "“之言”常用于____训释。", "type": "blank",
        "answer": "声训（推源）", "options": [],
        "explanation": "“之言”多用于声训推源，如“祗之言是（正确）也”。"}},
    {"ch": "训诂", "kw": "古注类型（二）", "q": {"stem": "“集注”的体例是汇集____。", "type": "blank",
        "answer": "各家注解", "options": [],
        "explanation": "集注、集解汇集多家注解，如《论语集注》。"}},
    {"ch": "修辞", "kw": "夸张与引用", "q": {"stem": "“《诗》云：‘他人有心，予忖度之。’”属于____的修辞手法。", "type": "blank",
        "answer": "引用", "options": [],
        "explanation": "引用《诗经》语句来增强说服力，是引用。"}},
    {"ch": "修辞", "kw": "借代", "q": {"stem": "“丹青”代指____。", "type": "blank",
        "answer": "绘画", "options": [],
        "explanation": "以颜料“丹青”代指绘画艺术，是借代。"}},
    {"ch": "古书的文体", "kw": "序跋与书启", "q": {"stem": "《兰亭集序》属于____文体。", "type": "blank",
        "answer": "序跋（序）", "options": [],
        "explanation": "《兰亭集序》是诗文集的序，属序跋类。"}},
    {"ch": "古书的文体", "kw": "论辩", "q": {"stem": "贾谊《过秦论》的“论”是____文体。", "type": "blank",
        "answer": "议论（论说）", "options": [],
        "explanation": "“论”是议论说理文体，如《过秦论》《六国论》。"}},
    {"ch": "古书的标点", "kw": "句读的概念", "q": {"stem": "“今/天下三分”与“今天/下三分”的差别，属于____。", "type": "blank",
        "answer": "断句（句读）", "options": [],
        "explanation": "断句位置不同导致意义不同，是句读（断句）问题。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'古代汉语第八批挂载 {n} 题')
