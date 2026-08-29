# -*- coding: utf-8 -*-
"""古代汉语 扩充第十三批：继续补充"""
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
    {"ch": "词汇", "kw": "词的引申义与引申方式", "q": {"stem": "“回”由“回旋”引申出“回来”，属于____引申。", "type": "blank",
        "answer": "相关", "options": [],
        "explanation": "“回”由回旋相关引申为返回、回来。"}},
    {"ch": "词汇", "kw": "词的本义", "q": {"stem": "“向”的本义是____。", "type": "blank",
        "answer": "朝北的窗户", "options": [],
        "explanation": "“向”本义为朝北的窗户（“塞向墐户”），引申为朝向、方向。"}},
    {"ch": "词汇", "kw": "词义感情色彩与轻重程度的变化", "q": {"stem": "“卑鄙”古指____，今义为品行恶劣。", "type": "blank",
        "answer": "身份低微、见识浅陋", "options": [],
        "explanation": "“卑鄙”古义是谦辞（“先帝不以臣卑鄙”），今义为贬义，感情色彩变化大。"}},
    {"ch": "词汇", "kw": "同义词辨析", "q": {"stem": "“逢”与“遇”，“遇”多指____（不期而遇）。", "type": "blank",
        "answer": "不期而遇（偶然相遇）", "options": [],
        "explanation": "“遇”多指偶然相见，“逢”多指迎接或相遇，二者有细微差别。"}},
    {"ch": "词汇", "kw": "合成词", "q": {"stem": "“瓜葛”“骨肉”这类由比喻构成的双音词，属于____（偏正）合成词。", "type": "blank",
        "answer": "偏正", "options": [],
        "explanation": "“骨肉”以偏正（像骨肉一样的关系）构成，是偏正式合成词。"}},
    {"ch": "语法（上）", "kw": "副词", "q": {"stem": "“相”在“父子相夷”中表____（相互）关系。", "type": "blank",
        "answer": "相互（彼此）", "options": [],
        "explanation": "“相”在此表互相，是副词。"}},
    {"ch": "语法（上）", "kw": "语气词、叹词、助词", "q": {"stem": "“嘻，善哉！技盖至此乎”中“嘻”是____词。", "type": "blank",
        "answer": "叹", "options": [],
        "explanation": "“嘻”表赞叹，是叹词。"}},
    {"ch": "语法（上）", "kw": "介词与连词", "q": {"stem": "“因击沛公于坐”中“因”作副词，表示____。", "type": "blank",
        "answer": "趁机（于是）", "options": [],
        "explanation": "“因”此处意为“趁机、于是”，是副词。"}},
    {"ch": "语法（下）", "kw": "名词、形容词、数词用作动词", "q": {"stem": "“六王毕，四海一”中“一”是____用作动词。", "type": "blank",
        "answer": "数词", "options": [],
        "explanation": "“一”数词活用作动词，意为“统一”。"}},
    {"ch": "语法（下）", "kw": "被动句", "q": {"stem": "“吾属今为之虏矣”中“为”表____。", "type": "blank",
        "answer": "被动", "options": [],
        "explanation": "“为”字句表被动，“为之虏”即被他俘虏。"}},
    {"ch": "文字（上）", "kw": "六书的分类学说", "q": {"stem": "六书中转注、假借属于____字法。", "type": "blank",
        "answer": "用", "options": [],
        "explanation": "转注、假借是用字法，象形、指事、会意、形声是造字法。"}},
    {"ch": "文字（下）", "kw": "汉字形体的演变", "q": {"stem": "最早发现于河南安阳殷墟的文字是____。", "type": "blank",
        "answer": "甲骨文", "options": [],
        "explanation": "甲骨文于殷墟出土，是商代文字。"}},
    {"ch": "文字（下）", "kw": "繁简字", "q": {"stem": "“医”的繁体是____。", "type": "blank",
        "answer": "醫", "options": [],
        "explanation": "“醫”简化作“医”，是繁简字。"}},
    {"ch": "音韵", "kw": "中古声调到北京音的变化", "q": {"stem": "中古全浊声母在现代北京音中多变为____（清）声母。", "type": "blank",
        "answer": "清", "options": [],
        "explanation": "“浊音清化”是中古到现代声母演变的重要规律。"}},
    {"ch": "音韵", "kw": "《韵镜》、尖音与团音", "q": {"stem": "现代普通话“j、q、x”与齐齿呼、撮口呼相拼的音是____音。", "type": "blank",
        "answer": "团", "options": [],
        "explanation": "尖团音之分：z、c、s 与 i、ü 相拼为尖音，j、q、x 相拼为团音。"}},
    {"ch": "训诂", "kw": "古注术语（二）", "q": {"stem": "“言”在古注中用于____（串讲大意）。", "type": "blank",
        "answer": "串讲句意", "options": [],
        "explanation": "“言”多用于说明句子的意思或所言之义。"}},
    {"ch": "训诂", "kw": "古注的作用", "q": {"stem": "古注除解释词义外，还注明____（读音）。", "type": "blank",
        "answer": "读音（音读）", "options": [],
        "explanation": "古注的作用包括注音、释义、串讲、说明典章制度等。"}},
    {"ch": "修辞", "kw": "顶真与析字", "q": {"stem": "“一传十，十传百”运用了____的修辞手法。", "type": "blank",
        "answer": "顶真", "options": [],
        "explanation": "前句尾“十”作下句头，上递下接，是顶真。"}},
    {"ch": "修辞", "kw": "变文与倒置", "q": {"stem": "“将军百战死，壮士十年归”中“将军”“壮士”互文，属于____。", "type": "blank",
        "answer": "互文", "options": [],
        "explanation": "将军壮士并提，互相补充，是互文。"}},
    {"ch": "古书的文体", "kw": "碑志与哀祭", "q": {"stem": "《吊屈原赋》属于____文体。", "type": "blank",
        "answer": "哀祭（吊文）", "options": [],
        "explanation": "吊文是哀祭文体，用于凭吊死者。"}},
    {"ch": "古书的文体", "kw": "论辩", "q": {"stem": "“寓言”如《庄子》中的故事，多属于____（论说/记叙）类。", "type": "blank",
        "answer": "论说（说理）", "options": [],
        "explanation": "寓言借故事说理，服务于论辩。"}},
    {"ch": "古书的标点", "kw": "标点古文的基本方法", "q": {"stem": "标点古文要善于利用____词（如夫、盖、也、矣）帮助断句。", "type": "blank",
        "answer": "虚（语气）", "options": [],
        "explanation": "虚词常是断句的标志，如句首“夫、盖”，句尾“也、矣、乎”。"}},
    {"ch": "诗词格律", "kw": "近体诗的押韵", "q": {"stem": "近体诗押韵，一般只押____（平）声韵。", "type": "blank",
        "answer": "平", "options": [],
        "explanation": "近体诗一般押平声韵，一韵到底。"}},
    {"ch": "诗词格律", "kw": "平仄与拗救", "q": {"stem": "“平平仄仄平”句第三字该平用仄，叫____。", "type": "blank",
        "answer": "拗", "options": [],
        "explanation": "该平而仄或该仄而平为拗，用变通补救为救。"}},
    {"ch": "工具书简介", "kw": "字典辞书的编排体例与注音方法", "q": {"stem": "《现代汉语词典》按____（音序）编排。", "type": "blank",
        "answer": "音序（拼音）", "options": [],
        "explanation": "现代字典辞书多按音序编排，旧字书多按部首。"}},
    {"ch": "工具书简介", "kw": "政书", "q": {"stem": "《通典》是唐代杜佑所著的____书。", "type": "blank",
        "answer": "政", "options": [],
        "explanation": "《通典》记载历代典章制度，是政书。"}},
    {"ch": "训诂", "kw": "训诂的体例类型", "q": {"stem": "《尔雅》《说文》这类通释语义的著作，属于____式训诂。", "type": "blank",
        "answer": "专著（通释）", "options": [],
        "explanation": "训诂分随文注和专著两类，《尔雅》《说文》是专著式。"}},
    {"ch": "文字（下）", "kw": "古今字与通假字的区别", "q": {"stem": "古今字的产生是由于____（本字后起），通假字则是借用。", "type": "blank",
        "answer": "为古义另造新字", "options": [],
        "explanation": "古今字是为古字的本义另造后起字，通假字是音同借用，性质不同。"}},
    {"ch": "语法（下）", "kw": "词序：宾语前置", "q": {"stem": "“子何恃而往”中“何”是____前置。", "type": "blank",
        "answer": "宾语", "options": [],
        "explanation": "疑问代词“何”作动词“恃”的宾语前置。"}},
    {"ch": "词汇", "kw": "词义的扩大、缩小、转移", "q": {"stem": "“货”古义多指____（财物），今义多指商品。", "type": "blank",
        "answer": "财物（钱财）", "options": [],
        "explanation": "“货”古指财物（“百工居肆以成其事”），今指商品，词义有演变。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'古代汉语第十三批挂载 {n} 题')
