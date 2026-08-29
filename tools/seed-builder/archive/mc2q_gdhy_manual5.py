# -*- coding: utf-8 -*-
"""古代汉语 扩充第五批：深化各章核心考点"""
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
    {"ch": "文字（上）", "kw": "象形与指事", "q": {"stem": "下列全属于象形字的一组是（　）", "type": "choice",
        "answer": "日、月、山、水", "options": ["日、月、山、水", "上、下、本、末", "休、武、从、采", "江、河、湖、海"],
        "explanation": "“日、月、山、水”描摹事物形状，是象形字；第二组指事，第三组会意，第四组形声。"}},
    {"ch": "文字（上）", "kw": "象形与指事", "q": {"stem": "在象形字上加指示符号标示部位的字，如“刃”，属于____字。", "type": "blank",
        "answer": "指事", "options": [],
        "explanation": "“刃”在“刀”上加一点标示刀刃所在，是指事字。"}},
    {"ch": "文字（上）", "kw": "形声", "q": {"stem": "形声字中表示读音的部分称为____。", "type": "blank",
        "answer": "声旁（声符）", "options": [],
        "explanation": "形声字由形旁表义、声旁表音构成，声旁表音。"}},
    {"ch": "文字（下）", "kw": "古今字", "q": {"stem": "“反”与“返”是____字关系。", "type": "blank",
        "answer": "古今", "options": [],
        "explanation": "“反”古义有返回，后加“辶”作“返”，二字为古今字。"}},
    {"ch": "文字（下）", "kw": "通假字", "q": {"stem": "“蚤”通“早”，属于____字。", "type": "blank",
        "answer": "通假", "options": [],
        "explanation": "“蚤”借作“早”，音同义通，是通假字。"}},
    {"ch": "词汇", "kw": "词的本义", "q": {"stem": "“兵”的本义是____。", "type": "blank",
        "answer": "兵器", "options": [],
        "explanation": "“兵”本义为兵器，引申为士兵、军队。"}},
    {"ch": "词汇", "kw": "词义的扩大、缩小、转移", "q": {"stem": "“汤”由“热水”缩小为“菜汤”，属于词义____。", "type": "blank",
        "answer": "缩小", "options": [],
        "explanation": "“汤”由热水（如“赴汤蹈火”）缩小为菜汤，是词义缩小。"}},
    {"ch": "词汇", "kw": "词义的扩大、缩小、转移", "q": {"stem": "“涕”由“眼泪”转为“鼻涕”，属于词义____。", "type": "blank",
        "answer": "转移", "options": [],
        "explanation": "“涕”古今义所指转移，由眼泪转为鼻涕，是词义转移。"}},
    {"ch": "词汇", "kw": "单纯词：单音词、叠音词、联绵词、外来词", "q": {"stem": "“参差”“仿佛”属于____词。", "type": "blank",
        "answer": "联绵", "options": [],
        "explanation": "联绵词是两音节连缀成义、不可拆分的单纯词，如“参差”“仿佛”。"}},
    {"ch": "词汇", "kw": "同义词辨析", "q": {"stem": "“宫”与“室”、“疾”与“病”都属于____。", "type": "blank",
        "answer": "同义词", "options": [],
        "explanation": "这些词意义相近，在范围、轻重、色彩上有差别，属同义词。"}},
    {"ch": "语法（下）", "kw": "使动用法", "q": {"stem": "“春风又绿江南岸”中“绿”是____用法。", "type": "blank",
        "answer": "使动", "options": [],
        "explanation": "“绿江南岸”即“使江南岸变绿”，形容词“绿”为使动用法。"}},
    {"ch": "语法（下）", "kw": "意动用法", "q": {"stem": "“渔人甚异之”中“异”是____用法。", "type": "blank",
        "answer": "意动", "options": [],
        "explanation": "“异之”即“以之为异”，形容词“异”是意动用法。"}},
    {"ch": "语法（下）", "kw": "词序：宾语前置", "q": {"stem": "“唯利是图”中“利”是____前置。", "type": "blank",
        "answer": "宾语", "options": [],
        "explanation": "“唯利是图”即“唯图利”，用“是”复指前置宾语“利”。"}},
    {"ch": "语法（下）", "kw": "被动句", "q": {"stem": "“为天下笑”中“为”表示____。", "type": "blank",
        "answer": "被动", "options": [],
        "explanation": "“为”字句是古代汉语被动句的典型句式，“为天下笑”即被天下人耻笑。"}},
    {"ch": "语法（下）", "kw": "名词作状语", "q": {"stem": "“卒廷见相如”中“廷”是名词作____。", "type": "blank",
        "answer": "状语", "options": [],
        "explanation": "“廷”作状语，表示“在朝廷上”。"}},
    {"ch": "语法（下）", "kw": "判断句", "q": {"stem": "“刘备，天下枭雄”是____标志的判断句。", "type": "blank",
        "answer": "无（省略“者”“也”）", "options": [],
        "explanation": "此句不用“者”“也”等标志，是依靠语序直接表示的判断句。"}},
    {"ch": "音韵", "kw": "阴声韵、阳声韵、入声韵", "q": {"stem": "以鼻音收尾的韵称为____声韵。", "type": "blank",
        "answer": "阳", "options": [],
        "explanation": "以元音收尾是阴声韵，以鼻音（-m/-n/-ŋ）收尾是阳声韵，以塞音收尾是入声韵。"}},
    {"ch": "音韵", "kw": "《切韵》《广韵》与中古音", "q": {"stem": "《广韵》是《____》的增订本。", "type": "blank",
        "answer": "切韵", "options": [],
        "explanation": "《广韵》全称《大宋重修广韵》，增订《切韵》而成。"}},
    {"ch": "音韵", "kw": "声类、字母与三十六字母", "q": {"stem": "“帮、滂、并、明”在三十六字母中属于____音。", "type": "blank",
        "answer": "唇", "options": [],
        "explanation": "帮滂并明是双唇音（唇音），是三十六字母的唇音类。"}},
    {"ch": "训诂", "kw": "古注术语（一）", "q": {"stem": "训诂术语中，“谓之”常用于给事物____。", "type": "blank",
        "answer": "下定义", "options": [],
        "explanation": "“谓之、曰、为”用于下定义或辨析同义词。"}},
    {"ch": "训诂", "kw": "训诂的方法", "q": {"stem": "用读音相同或相近的字来解释词义，称为____训。", "type": "blank",
        "answer": "声", "options": [],
        "explanation": "声训以音求义，如“天，颠也”；形训据形说义；义训直陈词义。"}},
    {"ch": "训诂", "kw": "训诂的方法", "q": {"stem": "根据字形结构分析词义的方法，称为____训。", "type": "blank",
        "answer": "形", "options": [],
        "explanation": "形训据字形说义，如《说文》“武，止戈为武”。"}},
    {"ch": "修辞", "kw": "借代", "q": {"stem": "“黄发垂髫”代指老人和小孩，用的是____。", "type": "blank",
        "answer": "借代", "options": [],
        "explanation": "以“黄发”“垂髫”的体征特征代指老人儿童，是借代。"}},
    {"ch": "修辞", "kw": "起兴与比喻", "q": {"stem": "“君者，舟也”中本体“君”与喻体“舟”同时出现，是____喻。", "type": "blank",
        "answer": "暗", "options": [],
        "explanation": "用“者……也”联系本体喻体，是暗喻（隐喻）。"}},
    {"ch": "修辞", "kw": "互文与并提", "q": {"stem": "“东市买骏马，西市买鞍鞯”应合看为“到东西市买骏马鞍鞯”，属于____。", "type": "blank",
        "answer": "互文", "options": [],
        "explanation": "“东市”“西市”互补，合起来才完整，是互文。"}},
    {"ch": "古书的文体", "kw": "奏议与诏令", "q": {"stem": "“表”如诸葛亮《出师表》，属于____文体。", "type": "blank",
        "answer": "奏议（表）", "options": [],
        "explanation": "“表”是臣下向君主陈情的奏议文体。"}},
    {"ch": "古书的文体", "kw": "序跋与书启", "q": {"stem": "写在书后的文字称为____。", "type": "blank",
        "answer": "跋", "options": [],
        "explanation": "序在书前，跋在书后，序跋说明著作缘起、旨趣。"}},
    {"ch": "古书的文体", "kw": "传状", "q": {"stem": "《五柳先生传》属于____文体。", "type": "blank",
        "answer": "传状（传记）", "options": [],
        "explanation": "《五柳先生传》以传记体写人，属传状类文体。"}},
    {"ch": "古书的标点", "kw": "句读的概念", "q": {"stem": "古书断句中，“读”指语意未尽而语气需要____之处。", "type": "blank",
        "answer": "停顿", "options": [],
        "explanation": "“句”是语意完整处，“读”是语意未尽而需停顿处。"}},
    {"ch": "诗词格律", "kw": "近体诗的押韵", "q": {"stem": "近体诗一般隔句押韵，即____句押韵。", "type": "blank",
        "answer": "偶（双数）", "options": [],
        "explanation": "近体诗一般偶数句押韵，首句可入韵可不入韵。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'古代汉语第五批挂载 {n} 题')
