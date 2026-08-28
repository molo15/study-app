# -*- coding: utf-8 -*-
"""古代汉语 扩充第七批：零散考点补充"""
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
    {"ch": "词汇", "kw": "词义的扩大、缩小、转移", "q": {"stem": "“菜”由“蔬菜”扩大为泛指“菜肴”，属于词义____。", "type": "blank",
        "answer": "扩大", "options": [],
        "explanation": "“菜”由专指蔬菜扩大为泛指菜肴，是词义扩大。"}},
    {"ch": "词汇", "kw": "词的本义", "q": {"stem": "“字”的本义是____。", "type": "blank",
        "answer": "生孩子", "options": [],
        "explanation": "“字”本义为生孩子（“女子贞不字”），引申为文字。"}},
    {"ch": "词汇", "kw": "词的引申义与引申方式", "q": {"stem": "“信”由“言语真实”引申出“信用、相信”，属于____引申。", "type": "blank",
        "answer": "相因", "options": [],
        "explanation": "“信”由“言语真实”因相关而引申为信用、相信，是相因引申。"}},
    {"ch": "词汇", "kw": "合成词", "q": {"stem": "“奔走”“停止”这类由意义相同相近的语素构成的词是____合成词。", "type": "blank",
        "answer": "并列（联合）", "options": [],
        "explanation": "由意义相同相近的语素并列构成的是并列式合成词。"}},
    {"ch": "词汇", "kw": "词义感情色彩与轻重程度的变化", "q": {"stem": "“恨”在古汉语中常表示____。", "type": "blank",
        "answer": "遗憾", "options": [],
        "explanation": "“恨”古义为遗憾（“此恨绵绵无绝期”），今义为怨恨。"}},
    {"ch": "语法（上）", "kw": "代词", "q": {"stem": "“其孰能讥之乎”中“其”表示____语气。", "type": "blank",
        "answer": "反问", "options": [],
        "explanation": "“其”在句中加强反问语气，意为“难道”。"}},
    {"ch": "语法（上）", "kw": "兼词", "q": {"stem": "“盍各言尔志”中“盍”是“何不”的____词。", "type": "blank",
        "answer": "兼", "options": [],
        "explanation": "“盍”兼有“何”“不”二字之义，是兼词。"}},
    {"ch": "语法（上）", "kw": "副词", "q": {"stem": "“亟请于武公”中“亟”表示____。", "type": "blank",
        "answer": "屡次（多次）", "options": [],
        "explanation": "“亟”作副词，表示屡次、多次。"}},
    {"ch": "语法（上）", "kw": "语气词、叹词、助词", "q": {"stem": "“吾知所以距子矣”中“矣”表示____语气。", "type": "blank",
        "answer": "已然（陈述、变化）", "options": [],
        "explanation": "“矣”表已然或将然的变化语气，相当于“了”。"}},
    {"ch": "语法（上）", "kw": "介词与连词", "q": {"stem": "“虽我之死，有子存焉”中“虽”表示____。", "type": "blank",
        "answer": "让步（即使）", "options": [],
        "explanation": "“虽”在古汉语常表让步，相当于“即使”。"}},
    {"ch": "语法（下）", "kw": "判断句", "q": {"stem": "“此则岳阳楼之大观也”中“则”起____作用。", "type": "blank",
        "answer": "帮助判断", "options": [],
        "explanation": "“则”在判断句中表确认，帮助构成判断。"}},
    {"ch": "语法（下）", "kw": "使动用法", "q": {"stem": "“富国强兵”中“富”“强”是____用法。", "type": "blank",
        "answer": "使动", "options": [],
        "explanation": "“富国强兵”即使国家富足、军队强大，是使动用法。"}},
    {"ch": "语法（下）", "kw": "名词、形容词、数词用作动词", "q": {"stem": "“左右欲刃相如”中“刃”是____活用。", "type": "blank",
        "answer": "名词用作动词", "options": [],
        "explanation": "“刃”本为名词（刀），此处活用作动词，意为“用刀杀”。"}},
    {"ch": "语法（下）", "kw": "词序：宾语前置", "q": {"stem": "“何以战”中“何”是____前置。", "type": "blank",
        "answer": "介词宾语", "options": [],
        "explanation": "疑问代词“何”作介词“以”的宾语而前置，即“以何战”。"}},
    {"ch": "语法（下）", "kw": "被动句", "q": {"stem": "“见笑于大方之家”中“见……于”配合表示____。", "type": "blank",
        "answer": "被动", "options": [],
        "explanation": "“见”与“于”配合构成被动句，即“被大方之家耻笑”。"}},
    {"ch": "文字（上）", "kw": "象形与指事", "q": {"stem": "“一”“二”“三”用抽象符号表示数目，属于____字。", "type": "blank",
        "answer": "指事", "options": [],
        "explanation": "用纯符号标示抽象概念，是指事字。"}},
    {"ch": "文字（下）", "kw": "古今字", "q": {"stem": "“益”与“溢”是____字关系。", "type": "blank",
        "answer": "古今", "options": [],
        "explanation": "“益”本义为水满溢出，后加“氵”作“溢”，是古今字。"}},
    {"ch": "文字（下）", "kw": "通假字", "q": {"stem": "“离骚”中“离”通“罹”，表____义。", "type": "blank",
        "answer": "遭受（遭遇）", "options": [],
        "explanation": "“离”通“罹”，意为遭遇忧愁，是通假字。"}},
    {"ch": "文字（下）", "kw": "异体字", "q": {"stem": "“峰”与“峯”音义相同、结构不同，属于____字。", "type": "blank",
        "answer": "异体", "options": [],
        "explanation": "“峰”“峯”是一对异体字。"}},
    {"ch": "音韵", "kw": "阴声韵、阳声韵、入声韵", "q": {"stem": "以塞音（-p、-t、-k）收尾的韵称为____声韵。", "type": "blank",
        "answer": "入", "options": [],
        "explanation": "入声韵以塞音收尾，是古汉语韵类之一。"}},
    {"ch": "音韵", "kw": "声类、字母与三十六字母", "q": {"stem": "“见、溪、群、疑”在三十六字母中属于____音。", "type": "blank",
        "answer": "牙", "options": [],
        "explanation": "见溪群疑是牙音（舌根音），属五音中的牙音。"}},
    {"ch": "音韵", "kw": "《切韵》《广韵》与中古音", "q": {"stem": "《广韵》编定于____（朝代）。", "type": "blank",
        "answer": "宋", "options": [],
        "explanation": "《广韵》全称《大宋重修广韵》，编定于北宋。"}},
    {"ch": "训诂", "kw": "古注术语（二）：之言、言、读为、读如", "q": {"stem": "“读为”“读若”常用于____。", "type": "blank",
        "answer": "注明音读或说明通假", "options": [],
        "explanation": "“读为”多说明通假，“读若”多注音，是古注常用术语。"}},
    {"ch": "训诂", "kw": "古注类型（二）：章句、集解与阐发义理", "q": {"stem": "“章句”是分章析句的____体例。", "type": "blank",
        "answer": "注解", "options": [],
        "explanation": "章句体例除解词外还分章析句串讲，如赵岐《孟子章句》。"}},
    {"ch": "训诂", "kw": "重要训诂著作", "q": {"stem": "汉代刘熙所著《____》是著名的声训专著。", "type": "blank",
        "answer": "释名", "options": [],
        "explanation": "《释名》以声训方式推求事物得名之由。"}},
    {"ch": "修辞", "kw": "借代", "q": {"stem": "“红颜”代指____。", "type": "blank",
        "answer": "青年女子", "options": [],
        "explanation": "以“红颜”的容貌特征代指青年女子，是借代。"}},
    {"ch": "修辞", "kw": "夸张与引用", "q": {"stem": "“白发三千丈”极力夸大，使用了____的修辞手法。", "type": "blank",
        "answer": "夸张", "options": [],
        "explanation": "“三千丈”是扩大夸张，极言白发之长。"}},
    {"ch": "古书的文体", "kw": "论辩", "q": {"stem": "韩愈《原毁》中“原”是____类文体。", "type": "blank",
        "answer": "论说（推原）", "options": [],
        "explanation": "“原”是推究本原的论说文，如《原毁》《原道》。"}},
    {"ch": "古书的文体", "kw": "杂记", "q": {"stem": "《桃花源记》属于____文体。", "type": "blank",
        "answer": "杂记", "options": [],
        "explanation": "《桃花源记》记述虚构之境，属杂记类。"}},
    {"ch": "古书的标点", "kw": "句读的概念", "q": {"stem": "“民可使由之不可使知之”如何断句，历来有分歧，属于____问题。", "type": "blank",
        "answer": "句读", "options": [],
        "explanation": "对同一段文字断句不同，意义便不同，这是句读问题的典型例。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'古代汉语第七批挂载 {n} 题')
