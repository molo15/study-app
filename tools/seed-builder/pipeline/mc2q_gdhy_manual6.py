# -*- coding: utf-8 -*-
"""古代汉语 扩充第六批：语法/音韵/训诂/词汇深层考点"""
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
    {"ch": "文字（下）", "kw": "小篆与隶变", "q": {"stem": "隶变之后，汉字的圆转线条变成了____。", "type": "blank",
        "answer": "方折笔画", "options": [],
        "explanation": "隶变使汉字由线条变为笔画，由圆转变为方折，是汉字形体演变的里程碑。"}},
    {"ch": "文字（下）", "kw": "汉字形体的演变", "q": {"stem": "楷书也叫____书。", "type": "blank",
        "answer": "真（正）", "options": [],
        "explanation": "楷书又称真书、正书，是现行通用的标准字体。"}},
    {"ch": "文字（下）", "kw": "甲骨文与金文", "q": {"stem": "甲骨文多用刀契刻，故又称____文。", "type": "blank",
        "answer": "契", "options": [],
        "explanation": "甲骨文因契刻于龟甲兽骨，也称契文、卜辞。"}},
    {"ch": "文字（上）", "kw": "六书的分类学说", "q": {"stem": "象形、指事是____体字，会意、形声是合体字。", "type": "blank",
        "answer": "独", "options": [],
        "explanation": "象形、指事为独体字，会意、形声为合体字。"}},
    {"ch": "文字（上）", "kw": "形声", "q": {"stem": "“闻”字中表示读音的“门”是____旁。", "type": "blank",
        "answer": "声", "options": [],
        "explanation": "“闻”从耳门声，“门”是声旁。"}},
    {"ch": "词汇", "kw": "词的引申义与引申方式", "q": {"stem": "“兵”由“兵器”引申出“士兵、军队”，属于____引申。", "type": "blank",
        "answer": "相关（连锁）", "options": [],
        "explanation": "由本义到引申义有相关、相因等方式，“兵”由兵器到持兵器的人。"}},
    {"ch": "词汇", "kw": "词义感情色彩与轻重程度的变化", "q": {"stem": "“诛”由“责备”引申为“杀戮”，词义程度____。", "type": "blank",
        "answer": "加重", "options": [],
        "explanation": "“诛”由轻责备到重杀戮，词义由轻变重。"}},
    {"ch": "词汇", "kw": "单纯词", "q": {"stem": "古汉语“虽”与现代“虽然”不同，它是____音节词。", "type": "blank",
        "answer": "单", "options": [],
        "explanation": "古汉语以单音词为主，“虽”是一个单音节词。"}},
    {"ch": "词汇", "kw": "单纯词", "q": {"stem": "“窈窕”“辗转”属于____词。", "type": "blank",
        "answer": "联绵", "options": [],
        "explanation": "“窈窕”“辗转”是双声叠韵联绵词，不可拆分。"}},
    {"ch": "词汇", "kw": "单纯词", "q": {"stem": "“葡萄”“石榴”是汉代以来的____词。", "type": "blank",
        "answer": "外来", "options": [],
        "explanation": "“葡萄”“石榴”是音译外来词。"}},
    {"ch": "语法（上）", "kw": "兼词", "q": {"stem": "“积土成山，风雨兴焉”中“焉”兼有“于”“之”的作用，是____词。", "type": "blank",
        "answer": "兼", "options": [],
        "explanation": "“焉”兼有介词“于”和代词“之”的作用，是兼词。"}},
    {"ch": "语法（上）", "kw": "代词", "q": {"stem": "“或以为死，或以为亡”中“或”表示____。", "type": "blank",
        "answer": "有的人（虚指）", "options": [],
        "explanation": "“或”在此是虚指代词，表示“有的人”。"}},
    {"ch": "语法（上）", "kw": "副词", "q": {"stem": "“岂若吾乡邻之旦旦有是哉”中“岂”表示____语气。", "type": "blank",
        "answer": "反问", "options": [],
        "explanation": "“岂”是表反问的语气副词，意为“难道”。"}},
    {"ch": "语法（上）", "kw": "介词与连词", "q": {"stem": "“战于长勺”中“于”引出____。", "type": "blank",
        "answer": "处所（地点）", "options": [],
        "explanation": "“于长勺”介引处所，是介词“于”的用法之一。"}},
    {"ch": "语法（上）", "kw": "介词与连词", "q": {"stem": "“学而时习之”中“而”连接两个动作，表示____关系。", "type": "blank",
        "answer": "顺承", "options": [],
        "explanation": "“而”连接“学”“习之”，表顺承（承接）关系。"}},
    {"ch": "语法（下）", "kw": "使动用法", "q": {"stem": "“苦其心志，劳其筋骨”中“苦”“劳”都是____用法。", "type": "blank",
        "answer": "使动", "options": [],
        "explanation": "“苦其心志”即使其心志苦，是形容词使动用法。"}},
    {"ch": "语法（下）", "kw": "意动用法", "q": {"stem": "“不耻下问”中“耻”是____用法。", "type": "blank",
        "answer": "意动", "options": [],
        "explanation": "“不耻下问”即以向不如自己的人请教为耻，“耻”是意动用法。"}},
    {"ch": "语法（下）", "kw": "名词作状语", "q": {"stem": "“岁征民间”中“岁”作状语，表示____。", "type": "blank",
        "answer": "每年（时间）", "options": [],
        "explanation": "“岁”名词作状语，表时间频率“每年”。"}},
    {"ch": "语法（下）", "kw": "词序：宾语前置", "q": {"stem": "“莫我肯顾”是____句中的宾语前置。", "type": "blank",
        "answer": "否定", "options": [],
        "explanation": "否定句中代词作宾语一般前置，“莫我肯顾”即“莫肯顾我”。"}},
    {"ch": "语法（下）", "kw": "被动句", "q": {"stem": "“不拘于时”中“于”引出施动者，表示____。", "type": "blank",
        "answer": "被动", "options": [],
        "explanation": "“于”字句表被动，“不拘于时”即不被时俗拘束。"}},
    {"ch": "音韵", "kw": "反切", "q": {"stem": "“工，古红切”中“红”提供被切字的____。", "type": "blank",
        "answer": "韵母和声调", "options": [],
        "explanation": "反切下字取韵与调，“红”与“工”同韵同调。"}},
    {"ch": "音韵", "kw": "《切韵》《广韵》与中古音", "q": {"stem": "《广韵》共分____个韵部。", "type": "blank",
        "answer": "206", "options": [],
        "explanation": "《广韵》分206韵，是中古音韵系统的代表。"}},
    {"ch": "音韵", "kw": "上古音", "q": {"stem": "研究上古音的重要材料是《诗经》的____。", "type": "blank",
        "answer": "用韵（押韵）", "options": [],
        "explanation": "《诗经》用韵是考求上古音的重要依据，另可参谐声系统。"}},
    {"ch": "训诂", "kw": "古注术语（一）", "q": {"stem": "训诂术语“犹”表示用词解释、意义____。", "type": "blank",
        "answer": "相通（相近）", "options": [],
        "explanation": "“犹”表示二者意义可以相通，如“如，犹‘乃’也”。"}},
    {"ch": "训诂", "kw": "训诂的概念", "q": {"stem": "“诂”侧重解释____（古语），《说文》云“训，说教也”。", "type": "blank",
        "answer": "古语（古代语言）", "options": [],
        "explanation": "训诂即解释古书语言，包括训、诂两类解释方式。"}},
    {"ch": "训诂", "kw": "重要训诂著作", "q": {"stem": "《尔雅》十九篇中，首篇为____篇。", "type": "blank",
        "answer": "释诂", "options": [],
        "explanation": "《尔雅》以《释诂》《释言》《释训》等篇解释古语词。"}},
    {"ch": "修辞", "kw": "委婉", "q": {"stem": "“一旦山陵崩，长安君何以自托于赵”中“山陵崩”委婉指____。", "type": "blank",
        "answer": "帝王（太后）去世", "options": [],
        "explanation": "“山陵崩”是讳言尊长者死亡的委婉语。"}},
    {"ch": "修辞", "kw": "排比", "q": {"stem": "“骐骥一跃，不能十步；驽马十驾，功在不舍”运用了____的修辞手法。", "type": "blank",
        "answer": "对偶", "options": [],
        "explanation": "两两相对、字数结构相当，是对偶。"}},
    {"ch": "古书的文体", "kw": "奏议与诏令", "q": {"stem": "君主向下发布的文书称为____。", "type": "blank",
        "answer": "诏令", "options": [],
        "explanation": "诏令是皇帝发布的公文，如诏、令、制、诰。"}},
    {"ch": "古书的文体", "kw": "箴铭与颂赞", "q": {"stem": "用于歌颂功德、赞美人物的文体称为____。", "type": "blank",
        "answer": "颂赞", "options": [],
        "explanation": "颂赞用于褒美功德，如《文心雕龙》所论颂赞体。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'古代汉语第六批挂载 {n} 题')
