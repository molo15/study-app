# -*- coding: utf-8 -*-
"""古代汉语 扩充第一批：绪论/文字/词汇/语法/音韵/训诂/格律 薄弱点"""
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
    # 绪论
    {"ch": "绪论", "kw": "古代汉语的定义", "q": {"stem": "古代汉语是____汉语，指古代汉民族所使用的语言。", "type": "blank",
        "answer": "古代汉民族使用的", "options": [],
        "explanation": "古代汉语指古代汉民族使用的语言，与现代汉语相对，通常以先秦两汉口语为基础形成的书面语为研究对象。"}},
    {"ch": "绪论", "kw": "王力", "q": {"stem": "王力先生认为学习古代汉语应以____为主。", "type": "blank",
        "answer": "词汇", "options": [],
        "explanation": "王力在《古代汉语》中指出，学习古代汉语的重点在词汇，语音、语法次之。"}},
    # 文字
    {"ch": "文字（上）", "kw": "象形与指事", "q": {"stem": "用简单的线条描摹事物形状以表意的造字法是____。", "type": "blank",
        "answer": "象形", "options": [],
        "explanation": "象形字描摹事物的形状，如“日”“月”“山”；指事字用符号标示抽象意义，如“上”“下”。"}},
    {"ch": "文字（上）", "kw": "象形与指事", "q": {"stem": "下列属于指事字的是（　）", "type": "choice",
        "answer": "本", "options": ["本", "日", "山", "马"],
        "explanation": "“本”在“木”下加一横标示树根之所在，是指事字；“日”“山”“马”是象形字。"}},
    {"ch": "文字（上）", "kw": "形声", "q": {"stem": "下列属于形声字的是（　）", "type": "choice",
        "answer": "江", "options": ["江", "从", "休", "武"],
        "explanation": "“江”由形旁“氵”和声旁“工”构成，是形声字；“从”“休”“武”是会意字。"}},
    {"ch": "文字（下）", "kw": "古今字", "q": {"stem": "“莫”本义为日落，后写作“暮”，二者构成____字关系。", "type": "blank",
        "answer": "古今", "options": [],
        "explanation": "“莫”是古字，“暮”是为其本义另造的后起字，二者是古今字。"}},
    {"ch": "文字（下）", "kw": "通假字", "q": {"stem": "“甚矣，汝之不惠”中“惠”通“慧”，属于____字。", "type": "blank",
        "answer": "通假", "options": [],
        "explanation": "“惠”与“慧”音同义通，用“惠”代替“慧”，是通假字。"}},
    {"ch": "文字（下）", "kw": "小篆与隶变", "q": {"stem": "汉字由小篆演变为隶书的变化过程称为____。", "type": "blank",
        "answer": "隶变", "options": [],
        "explanation": "隶变使汉字由圆转的线条变为方折的笔画，是汉字形体演变中的关键一环。"}},
    {"ch": "文字（下）", "kw": "汉字形体的演变", "q": {"stem": "汉字形体演变的大致顺序是甲骨文、金文、____、隶书、楷书。", "type": "blank",
        "answer": "小篆", "options": [],
        "explanation": "汉字形体演变：甲骨文→金文→小篆→隶书→楷书。"}},
    {"ch": "文字（下）", "kw": "甲骨文与金文", "q": {"stem": "刻写在龟甲兽骨上的殷商文字称为____。", "type": "blank",
        "answer": "甲骨文", "options": [],
        "explanation": "甲骨文是刻在龟甲兽骨上的文字，主要用于占卜，是迄今发现的最早的成熟汉字。"}},
    # 词汇
    {"ch": "词汇", "kw": "单纯词", "q": {"stem": "古代汉语中，____音节词占绝大多数。", "type": "blank",
        "answer": "单", "options": [],
        "explanation": "古代汉语以单音词为主，一个字通常就是一个词，与现代汉语双音词化不同。"}},
    {"ch": "词汇", "kw": "同义词辨析", "q": {"stem": "“疾”与“病”同表疾病，但“病”程度更____。", "type": "blank",
        "answer": "重", "options": [],
        "explanation": "“疾”是轻病，“病”是重病，二者在词义轻重上有别，是同义词辨析的常见例。"}},
    {"ch": "词汇", "kw": "词义感情色彩与轻重程度的变化", "q": {"stem": "“爪牙”由“得力助手”变为“帮凶”，是词义____的变化。", "type": "blank",
        "answer": "感情色彩", "options": [],
        "explanation": "“爪牙”由中性褒义变为贬义，是感情色彩的变化。"}},
    {"ch": "词汇", "kw": "词义的扩大、缩小、转移", "q": {"stem": "“江”由专指长江扩大为泛指一切河流，属于词义____。", "type": "blank",
        "answer": "扩大", "options": [],
        "explanation": "“江”词义由专指扩大为泛指，是词义扩大。"}},
    {"ch": "词汇", "kw": "词的引申义与引申方式", "q": {"stem": "“节”由“竹节”引申出“节操、礼节”等意义，称为词的____义。", "type": "blank",
        "answer": "引申", "options": [],
        "explanation": "由本义推演出来的意义是引申义，“节”由竹节引申指节操、礼节。"}},
    {"ch": "词汇", "kw": "词的本义", "q": {"stem": "探求词的本义，主要依据____中的用例和字形分析。", "type": "blank",
        "answer": "古代文献", "options": [],
        "explanation": "探求本义主要从古代文献的用例和字形的结构两方面入手。"}},
    {"ch": "词汇", "kw": "合成词", "q": {"stem": "“妻子”在先秦汉语中通常指“妻子和子女”，是____个词。", "type": "blank",
        "answer": "两", "options": [],
        "explanation": "“妻子”在先秦是两个词（并列短语），指妻子和子女；现代汉语是合成词。"}},
    # 语法
    {"ch": "语法（上）", "kw": "代词", "q": {"stem": "“吾、余、予”属于____人称代词。", "type": "blank",
        "answer": "第一", "options": [],
        "explanation": "“吾、余、予、我”是第一人称代词，“尔、汝、若”是第二人称代词。"}},
    {"ch": "语法（上）", "kw": "兼词", "q": {"stem": "“投诸渤海之尾”中“诸”兼有“之”“于”二词，是____词。", "type": "blank",
        "answer": "兼", "options": [],
        "explanation": "“诸”兼有代词“之”和介词“于”（或语气词“乎”）的用法，是兼词。"}},
    {"ch": "语法（下）", "kw": "使动用法", "q": {"stem": "“项伯杀人，臣活之”中“活”是____用法。", "type": "blank",
        "answer": "使动", "options": [],
        "explanation": "“活之”即“使之活”，“活”是动词的使动用法。"}},
    {"ch": "语法（下）", "kw": "意动用法", "q": {"stem": "“孔子登东山而小鲁”中“小”是____用法。", "type": "blank",
        "answer": "意动", "options": [],
        "explanation": "“小鲁”即“以鲁为小”，形容词“小”是意动用法。"}},
    {"ch": "语法（下）", "kw": "名词作状语", "q": {"stem": "“箕畚运于渤海之尾”中“箕畚”是名词作____。", "type": "blank",
        "answer": "状语", "options": [],
        "explanation": "“箕畚”原为名词，此处作状语，表示“用箕畚”。"}},
    {"ch": "语法（下）", "kw": "判断句", "q": {"stem": "“廉颇者，赵之良将也”是古代汉语的____句。", "type": "blank",
        "answer": "判断", "options": [],
        "explanation": "“……者，……也”是古代汉语判断句的典型格式。"}},
    {"ch": "语法（下）", "kw": "宾语前置", "q": {"stem": "“何罪之有”中“何罪”是____前置。", "type": "blank",
        "answer": "宾语", "options": [],
        "explanation": "“何罪之有”即“有何罪”，疑问代词“何”作宾语前置，用“之”复指。"}},
    {"ch": "语法（下）", "kw": "被动句", "q": {"stem": "“信而见疑，忠而被谤”中“见”“被”表____。", "type": "blank",
        "answer": "被动", "options": [],
        "explanation": "“见”“被”是表被动的标志，此句是被动句。"}},
    {"ch": "语法（下）", "kw": "名词、形容词、数词用作动词", "q": {"stem": "“假舟楫者，非能水也”中“水”是名词用作____。", "type": "blank",
        "answer": "动词", "options": [],
        "explanation": "“水”此处活用作动词，意为“游泳”，是名词用作动词。"}},
    # 音韵
    {"ch": "音韵", "kw": "声类、字母与三十六字母", "q": {"stem": "传统音韵学中，表示声母的术语称为____。", "type": "blank",
        "answer": "字母", "options": [],
        "explanation": "传统音韵学以“字母”表示声母，如“三十六字母”。"}},
    {"ch": "音韵", "kw": "阴声韵、阳声韵、入声韵", "q": {"stem": "以元音收尾的韵称为____声韵。", "type": "blank",
        "answer": "阴", "options": [],
        "explanation": "以元音收尾是阴声韵，以鼻音收尾是阳声韵，以塞音收尾是入声韵。"}},
    # 训诂
    {"ch": "训诂", "kw": "训诂的概念", "q": {"stem": "“训”指解释词义，“诂”亦指解释古语，二者合称____。", "type": "blank",
        "answer": "训诂", "options": [],
        "explanation": "训诂即解释古书词义的工作，训诂学是研究古代文献语言的学科。"}},
    # 诗词格律
    {"ch": "诗词格律", "kw": "律诗的结构", "q": {"stem": "律诗八句分为四联，依次是首联、颔联、____、尾联。", "type": "blank",
        "answer": "颈联", "options": [],
        "explanation": "律诗四联：首联、颔联、颈联、尾联。"}},
    {"ch": "诗词格律", "kw": "对仗", "q": {"stem": "律诗一般要求颔联和____两联对仗。", "type": "blank",
        "answer": "颈联", "options": [],
        "explanation": "律诗中间两联（颔联、颈联）一般要求对仗。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'古代汉语第一批挂载 {n} 题')
