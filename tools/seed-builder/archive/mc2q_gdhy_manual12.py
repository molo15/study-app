# -*- coding: utf-8 -*-
"""古代汉语 扩充第十二批：混合选择题型"""
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
    {"ch": "词汇", "kw": "词义的扩大、缩小、转移", "q": {"stem": "下列属于词义扩大的是（　）", "type": "choice",
        "answer": "河（由专指黄河到泛指河流）", "options": ["河（由专指黄河到泛指河流）", "汤（由热水到菜汤）", "涕（由眼泪到鼻涕）", "走（由跑到行走）"],
        "explanation": "“河”由专指黄河扩大为泛指河流，是词义扩大；其余为缩小或转移。"}},
    {"ch": "词汇", "kw": "词义的扩大、缩小、转移", "q": {"stem": "“狱”在古汉语中常指____。", "type": "blank",
        "answer": "案件（官司）", "options": [],
        "explanation": "“狱”古义为案件（“小大之狱，虽不能察”），今义为监狱。"}},
    {"ch": "词汇", "kw": "词义的扩大、缩小、转移", "q": {"stem": "“涕”的古义是____。", "type": "blank",
        "answer": "眼泪", "options": [],
        "explanation": "“涕”古义为眼泪（“泣涕涟涟”），今义为鼻涕。"}},
    {"ch": "词汇", "kw": "词义感情色彩与轻重程度的变化", "q": {"stem": "“贼”在古汉语中常指____。", "type": "blank",
        "answer": "害（杀害、残害）", "options": [],
        "explanation": "“贼”古义指杀害、残害（“贼仁者谓之贼”），后指盗贼。"}},
    {"ch": "词汇", "kw": "单纯词：单音词、叠音词、联绵词、外来词", "q": {"stem": "下列属于叠韵联绵词的是（　）", "type": "choice",
        "answer": "逍遥", "options": ["逍遥", "参差", "忐忑", "仿佛"],
        "explanation": "“逍遥”（xiāo yáo）叠韵；参差、忐忑、仿佛是双声联绵词。"}},
    {"ch": "语法（下）", "kw": "使动用法", "q": {"stem": "“春风又绿江南岸”中“绿”的活用类型是（　）", "type": "choice",
        "answer": "形容词使动", "options": ["形容词使动", "形容词意动", "名词作状语", "名词用作动词"],
        "explanation": "“绿江南岸”即使江南岸变绿，是形容词使动用法。"}},
    {"ch": "语法（下）", "kw": "意动用法", "q": {"stem": "“渔人甚异之”中“异”的活用类型是（　）", "type": "choice",
        "answer": "形容词意动", "options": ["形容词意动", "形容词使动", "名词作状语", "动词使动"],
        "explanation": "“异之”即以之为异，是形容词意动用法。"}},
    {"ch": "语法（上）", "kw": "代词", "q": {"stem": "“公与之乘”中“之”是（　）", "type": "choice",
        "answer": "第三人称代词", "options": ["第三人称代词", "第一人称代词", "指示代词", "语气助词"],
        "explanation": "“之”在此指代曹刿，是第三人称代词。"}},
    {"ch": "语法（下）", "kw": "词序：宾语前置", "q": {"stem": "“大王来何操”中“何”是（　）", "type": "choice",
        "answer": "宾语前置", "options": ["宾语前置", "主语", "状语", "补语"],
        "explanation": "疑问代词“何”作动词“操”的宾语而前置。"}},
    {"ch": "语法（下）", "kw": "被动句", "q": {"stem": "“身死人手，为天下笑”中“为”表示（　）", "type": "choice",
        "answer": "被动", "options": ["被动", "主动", "使动", "判断"],
        "explanation": "“为”字句表被动，“为天下笑”即被天下人耻笑。"}},
    {"ch": "文字（上）", "kw": "形声", "q": {"stem": "下列全是形声字的一组是（　）", "type": "choice",
        "answer": "江、河、湖、海", "options": ["江、河、湖、海", "日、月、山、水", "休、武、从、采", "上、下、本、末"],
        "explanation": "“江河湖海”都是形声字；其余分别是象形、会意、指事字。"}},
    {"ch": "文字（上）", "kw": "六书说", "q": {"stem": "“武”字按六书属于（　）", "type": "choice",
        "answer": "会意", "options": ["会意", "象形", "指事", "形声"],
        "explanation": "“武”由“止”“戈”会意，是会意字。"}},
    {"ch": "文字（上）", "kw": "象形与指事", "q": {"stem": "“上”“下”二字按六书属于（　）", "type": "choice",
        "answer": "指事", "options": ["指事", "象形", "会意", "形声"],
        "explanation": "“上”“下”用指示符号标示方位，是指事字。"}},
    {"ch": "文字（上）", "kw": "象形与指事", "q": {"stem": "“本”“末”都是在“木”上加指示符号，属于（　）", "type": "choice",
        "answer": "指事字", "options": ["指事字", "象形字", "会意字", "形声字"],
        "explanation": "“本”“末”以符号标示树根、树梢，是指事字。"}},
    {"ch": "音韵", "kw": "阴声韵、阳声韵、入声韵", "q": {"stem": "“东”“阳”等以鼻音收尾，属于（　）", "type": "choice",
        "answer": "阳声韵", "options": ["阳声韵", "阴声韵", "入声韵", "无韵尾"],
        "explanation": "以鼻音（-m、-n、-ng）收尾的是阳声韵。"}},
    {"ch": "音韵", "kw": "反切", "q": {"stem": "“练，郎甸切”中“郎”提供被切字的（　）", "type": "choice",
        "answer": "声母", "options": ["声母", "韵母", "声调", "韵母和声调"],
        "explanation": "反切上字取声，“郎”与“练”声母相同。"}},
    {"ch": "训诂", "kw": "字典与《说文解字》", "q": {"stem": "《说文解字》的作者是（　）", "type": "choice",
        "answer": "许慎", "options": ["许慎", "段玉裁", "扬雄", "王引之"],
        "explanation": "许慎著《说文解字》，是东汉文字学家。"}},
    {"ch": "训诂", "kw": "古注类型（一）：传、笺、注、疏、正义", "q": {"stem": "“笺”这一注释体例，最初用于（　）", "type": "choice",
        "answer": "郑玄注《诗经》", "options": ["郑玄注《诗经》", "孔颖达疏《五经》", "何晏注《论语》", "郭璞注《尔雅》"],
        "explanation": "郑玄作《毛诗笺》，“笺”是对毛传的补充订正。"}},
    {"ch": "修辞", "kw": "借代", "q": {"stem": "“黄发垂髫，并怡然自乐”中“黄发”“垂髫”用的是（　）", "type": "choice",
        "answer": "借代", "options": ["借代", "比喻", "借喻", "双关"],
        "explanation": "以老人儿童的体征特征代指老人儿童，是借代。"}},
    {"ch": "修辞", "kw": "起兴与比喻", "q": {"stem": "“大珠小珠落玉盘”描写琵琶声，用的是（　）", "type": "choice",
        "answer": "比喻", "options": ["比喻", "借代", "夸张", "双关"],
        "explanation": "把琵琶声比作珠落玉盘之声，是比喻。"}},
    {"ch": "古书的文体", "kw": "奏议与诏令", "q": {"stem": "《出师表》属于（　）文体", "type": "choice",
        "answer": "奏议", "options": ["奏议", "诏令", "序跋", "传状"],
        "explanation": "“表”是臣下上奏君主的奏议文体。"}},
    {"ch": "古书的文体", "kw": "杂记", "q": {"stem": "《岳阳楼记》属于（　）文体", "type": "choice",
        "answer": "杂记", "options": ["杂记", "论辩", "箴铭", "碑志"],
        "explanation": "《岳阳楼记》记楼抒情，属杂记类。"}},
    {"ch": "古书的标点", "kw": "句读的概念", "q": {"stem": "“句读之不知”中“句读”指的是（　）", "type": "choice",
        "answer": "断句（句读）", "options": ["断句（句读）", "标点符号", "朗读节奏", "词义解释"],
        "explanation": "句读指古书断句，“句”为语意完整处，“读”为语气停顿处。"}},
    {"ch": "诗词格律", "kw": "律诗的结构", "q": {"stem": "律诗四联中，第____联是“颔联”。", "type": "choice",
        "answer": "二", "options": ["二", "一", "三", "四"],
        "explanation": "律诗四联依次为首联、颔联、颈联、尾联，颔联是第二联。"}},
    {"ch": "诗词格律", "kw": "平仄与拗救", "q": {"stem": "近体诗“平仄”中的“平”包括（　）", "type": "choice",
        "answer": "阴平和阳平", "options": ["阴平和阳平", "阴平和上声", "去声和入声", "上声和去声"],
        "explanation": "平声包括阴平、阳平，仄声包括上、去、入三声。"}},
    {"ch": "工具书简介", "kw": "词典与《辞源》《辞海》《汉语大词典》", "q": {"stem": "《辞源》侧重收录（　）", "type": "choice",
        "answer": "古汉语语词", "options": ["古汉语语词", "现代白话词", "百科词条", "方言词"],
        "explanation": "《辞源》以解释古汉语语词为主，兼顾古代文化知识。"}},
    {"ch": "工具书简介", "kw": "虚词类词典", "q": {"stem": "《经传释词》的作者是（　）", "type": "choice",
        "answer": "王引之", "options": ["王引之", "段玉裁", "许慎", "马建忠"],
        "explanation": "《经传释词》是清代王引之所著，专释虚词。"}},
    {"ch": "诗词格律", "kw": "对仗", "q": {"stem": "“无边落木萧萧下，不尽长江滚滚来”中“萧萧”是（　）", "type": "choice",
        "answer": "叠音词", "options": ["叠音词", "联绵词", "合成词", "外来词"],
        "explanation": "“萧萧”是模拟声音的叠音词（拟声），与“滚滚”相对。"}},
    {"ch": "词汇", "kw": "单纯词", "q": {"stem": "古汉语中“衣”指上衣，“裳”指（　）", "type": "choice",
        "answer": "下衣（裙子）", "options": ["下衣（裙子）", "帽子", "鞋子", "外衣"],
        "explanation": "“衣”是上衣，“裳”是下衣（裙），古汉语中常为两个词。"}},
    {"ch": "训诂", "kw": "重要训诂著作", "q": {"stem": "“尔雅”中“尔”意为（　）", "type": "choice",
        "answer": "近（接近）", "options": ["近（接近）", "你", "远", "多"],
        "explanation": "“尔”通“迩”，意为近；“雅”指雅言、标准语。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'古代汉语第十二批挂载 {n} 题')
