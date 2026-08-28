# -*- coding: utf-8 -*-
"""古代汉语 扩充第十批：继续补充各章考点"""
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
    {"ch": "词汇", "kw": "词的引申义与引申方式", "q": {"stem": "“绝”由“断”引申出“极、非常”，属于词义的____。", "type": "blank",
        "answer": "引申", "options": [],
        "explanation": "“绝”由本义“断”引申为“极、非常”，是引申义。"}},
    {"ch": "词汇", "kw": "词的本义", "q": {"stem": "“信”的本义是____。", "type": "blank",
        "answer": "言语真实", "options": [],
        "explanation": "“信”本义为言语真实，引申为信用、相信。"}},
    {"ch": "词汇", "kw": "词义的扩大、缩小、转移", "q": {"stem": "“河”古专指____，今泛指一切河流。", "type": "blank",
        "answer": "黄河", "options": [],
        "explanation": "“河”古专指黄河（“河内凶”），今泛指河流，是词义扩大。"}},
    {"ch": "词汇", "kw": "合成词", "q": {"stem": "“干戈”本指两种兵器，并列代指战争，是____合成词。", "type": "blank",
        "answer": "并列（联合）", "options": [],
        "explanation": "“干戈”由“干”（盾）、“戈”（矛）并列构成。"}},
    {"ch": "词汇", "kw": "同义词辨析", "q": {"stem": "“恭”与“敬”相比，“恭”偏重____方面。", "type": "blank",
        "answer": "外貌（态度）", "options": [],
        "explanation": "“恭”偏重外在态度，“敬”偏重内心，二者在侧重上有别。"}},
    {"ch": "语法（上）", "kw": "代词", "q": {"stem": "“某”“或”是不定代词，表示____。", "type": "blank",
        "answer": "不确定的人或事物（虚指）", "options": [],
        "explanation": "“某”“或”表虚指，指不确定的人或事物。"}},
    {"ch": "语法（上）", "kw": "副词", "q": {"stem": "“村中闻有此人，咸来问讯”中“咸”表示____。", "type": "blank",
        "answer": "都（全）", "options": [],
        "explanation": "“咸”是范围副词，意为“都、全”。"}},
    {"ch": "语法（上）", "kw": "语气词、叹词、助词", "q": {"stem": "“直不过百步耳”中“耳”表示____语气。", "type": "blank",
        "answer": "限止（罢了）", "options": [],
        "explanation": "“耳”表限止语气，相当于“罢了”。"}},
    {"ch": "语法（上）", "kw": "介词与连词", "q": {"stem": "“先生且休矣”中“且”作副词，表示____。", "type": "blank",
        "answer": "暂且", "options": [],
        "explanation": "“且”此处为副词，意为“暂且、姑且”。"}},
    {"ch": "语法（上）", "kw": "介词与连词", "q": {"stem": "“自三峡七百里中”中“自”引介____。", "type": "blank",
        "answer": "处所（从）", "options": [],
        "explanation": "“自”在此引介处所，相当于“从”。"}},
    {"ch": "语法（下）", "kw": "判断句", "q": {"stem": "“是吾剑之所从坠”中“是”在句中作____。", "type": "blank",
        "answer": "主语", "options": [],
        "explanation": "“是”在此是代词作主语，意为“这里”，不是判断词。"}},
    {"ch": "语法（下）", "kw": "使动用法", "q": {"stem": "“饮余马于咸池”中“饮”是____用法。", "type": "blank",
        "answer": "使动", "options": [],
        "explanation": "“饮余马”即使我的马饮水，是使动用法。"}},
    {"ch": "语法（下）", "kw": "意动用法", "q": {"stem": "“成以其小，劣之”中“劣”是____用法。", "type": "blank",
        "answer": "意动", "options": [],
        "explanation": "“劣之”即以之为劣，是意动用法。"}},
    {"ch": "语法（下）", "kw": "名词作状语", "q": {"stem": "“日扳仲永环谒于邑人”中“日”作状语，意为____。", "type": "blank",
        "answer": "每天", "options": [],
        "explanation": "“日”名词作状语，表时间频率“每天”。"}},
    {"ch": "语法（下）", "kw": "词序：宾语前置", "q": {"stem": "“古之人不余欺也”中“余”是____前置。", "type": "blank",
        "answer": "宾语", "options": [],
        "explanation": "否定句中代词“余”作宾语前置，即“不欺余”。"}},
    {"ch": "文字（上）", "kw": "象形与指事", "q": {"stem": "“牛”“羊”突出头部角形以区别，属于____字。", "type": "blank",
        "answer": "象形", "options": [],
        "explanation": "“牛”“羊”描摹牛、羊头形，是象形字。"}},
    {"ch": "文字（上）", "kw": "象形与指事", "q": {"stem": "“亦”是“腋”的本字，在“大”旁加两点标示腋部，属于____字。", "type": "blank",
        "answer": "指事", "options": [],
        "explanation": "“亦”以符号标示腋下部位，是指事字。"}},
    {"ch": "文字（上）", "kw": "会意", "q": {"stem": "“及”由“人”“又”会意，本义表示____。", "type": "blank",
        "answer": "追上（赶及）", "options": [],
        "explanation": "“及”像手及人，会意为“追上、达到”。"}},
    {"ch": "文字（上）", "kw": "形声", "q": {"stem": "“胫”字中表音的“圣”是____旁。", "type": "blank",
        "answer": "声", "options": [],
        "explanation": "“胫”从肉（月）圣声，“圣”是声旁。"}},
    {"ch": "文字（下）", "kw": "古今字", "q": {"stem": "“景”与“影”是____字关系。", "type": "blank",
        "answer": "古今", "options": [],
        "explanation": "“景”古有“阴影”义（“天下云集响应，赢粮而景从”），后加“彡”作“影”，是古今字。"}},
    {"ch": "音韵", "kw": "声类、字母与三十六字母", "q": {"stem": "三十六字母中“来”母属于七音中的____。", "type": "blank",
        "answer": "半舌", "options": [],
        "explanation": "五音加半舌（来母）、半齿（日母）为七音。"}},
    {"ch": "音韵", "kw": "反切", "q": {"stem": "反切注音法产生于____末。", "type": "blank",
        "answer": "东汉", "options": [],
        "explanation": "反切萌生于东汉，成熟于魏晋。"}},
    {"ch": "音韵", "kw": "《切韵》《广韵》与中古音", "q": {"stem": "《广韵》的前身是隋代陆法言等编的《____》。", "type": "blank",
        "answer": "切韵", "options": [],
        "explanation": "《切韵》成书于隋，是《广韵》的前身。"}},
    {"ch": "训诂", "kw": "古注术语（二）：之言、言、读为、读如", "q": {"stem": "“读如”在古注中多用于____。", "type": "blank",
        "answer": "注音", "options": [],
        "explanation": "“读如、读若”多用于注音；“读为”多说明通假。"}},
    {"ch": "训诂", "kw": "古注类型（一）：传、笺、注、疏、正义", "q": {"stem": "“疏”又称“____”。", "type": "blank",
        "answer": "正义", "options": [],
        "explanation": "“疏”（正义）既解释经文，又疏通前人的传注。"}},
    {"ch": "修辞", "kw": "借代", "q": {"stem": "“丝竹”代指____。", "type": "blank",
        "answer": "音乐", "options": [],
        "explanation": "以乐器材料“丝竹”代指音乐，是借代。"}},
    {"ch": "修辞", "kw": "委婉", "q": {"stem": "“老臣病足，曾不能疾走，不得见久矣，窃自恕，而恐太后玉体之有所郄也”中“有所郄”委婉指____。", "type": "blank",
        "answer": "身体欠安（生病）", "options": [],
        "explanation": "“有所郄”婉言身体不适，是委婉表达。"}},
    {"ch": "古书的文体", "kw": "碑志与哀祭", "q": {"stem": "《祭十二郎文》属于____文体。", "type": "blank",
        "answer": "哀祭", "options": [],
        "explanation": "哀祭文用于悼念死者，如祭文、吊文。"}},
    {"ch": "古书的文体", "kw": "杂记", "q": {"stem": "《小石潭记》属于____文体。", "type": "blank",
        "answer": "杂记（游记）", "options": [],
        "explanation": "《小石潭记》记游写景，属杂记中的游记。"}},
    {"ch": "古书的标点", "kw": "古书标点中的常见错误", "q": {"stem": "把“以”误属下句或属上句，属于标点中的____错误。", "type": "blank",
        "answer": "断句", "options": [],
        "explanation": "断句（句读）不当是古书标点最常见的错误。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'古代汉语第十批挂载 {n} 题')
