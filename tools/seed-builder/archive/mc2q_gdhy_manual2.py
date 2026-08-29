# -*- coding: utf-8 -*-
"""古代汉语 扩充第二批：训诂/语法/音韵/文体/标点/格律"""
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
    # 词汇
    {"ch": "词汇", "kw": "单纯词", "q": {"stem": "“关关雎鸠”中“关关”属于____词。", "type": "blank",
        "answer": "叠音", "options": [],
        "explanation": "“关关”是叠音词（重言），模拟鸟叫声，属单纯词。"}},
    {"ch": "词汇", "kw": "词义感情色彩与轻重程度的变化", "q": {"stem": "“饥”与“饿”相比，____的词义程度更重。", "type": "blank",
        "answer": "饿", "options": [],
        "explanation": "“饥”指腹空，“饿”指饿到严重程度，二者在轻重程度上有别。"}},
    {"ch": "词汇", "kw": "词的引申义与引申方式", "q": {"stem": "“道”由“道路”引申出“道理、方法”等意义，属于词义的____。", "type": "blank",
        "answer": "引申", "options": [],
        "explanation": "由本义“道路”推演出“道理、方法”，是词义的引申。"}},
    # 语法
    {"ch": "语法（上）", "kw": "介词与连词", "q": {"stem": "“以刀杀人”中“以”是____词。", "type": "blank",
        "answer": "介", "options": [],
        "explanation": "“以刀杀人”中“以”引出工具“刀”，是介词。"}},
    {"ch": "语法（上）", "kw": "语气词、叹词、助词", "q": {"stem": "“廉颇者，赵之良将也”句末“也”表示____语气。", "type": "blank",
        "answer": "判断（陈述）", "options": [],
        "explanation": "“也”用于判断句句末，表判断、陈述语气。"}},
    {"ch": "语法（上）", "kw": "代词", "q": {"stem": "“爱其子，择师而教之”中“其”是____人称代词。", "type": "blank",
        "answer": "第三", "options": [],
        "explanation": "“其”在句中作定语，表“他的”，是第三人称代词。"}},
    {"ch": "语法（上）", "kw": "副词", "q": {"stem": "“已而之细柳军”中“已而”是表示____的副词。", "type": "blank",
        "answer": "时间", "options": [],
        "explanation": "“已而”意为“不久、随后”，是时间副词。"}},
    {"ch": "语法（上）", "kw": "固定结构与固定格式", "q": {"stem": "“如太行王屋何”中“如……何”表示____。", "type": "blank",
        "answer": "把……怎么办（奈何）", "options": [],
        "explanation": "“如……何”是固定格式，表示“把……怎么办”，如“如太行王屋何”。"}},
    # 训诂
    {"ch": "训诂", "kw": "训诂的方法", "q": {"stem": "以今语解释古语、以通语解释方言，属于____的训诂方法。", "type": "blank",
        "answer": "义训（直训）", "options": [],
        "explanation": "义训是直接解释词义，包括互训、同义为训等；声训以音求义，形训据形说义。"}},
    {"ch": "训诂", "kw": "古注的作用", "q": {"stem": "古注的主要作用之一是解释古书中的____。", "type": "blank",
        "answer": "词义", "options": [],
        "explanation": "古注的作用包括解释词义、串讲文意、说明典章制度、校勘文字等。"}},
    {"ch": "训诂", "kw": "重要训诂著作", "q": {"stem": "我国最早的解释词义的专著是《____》。", "type": "blank",
        "answer": "尔雅", "options": [],
        "explanation": "《尔雅》是我国第一部词典，也是最早解释词义的专著。"}},
    {"ch": "训诂", "kw": "古注类型（一）：传、笺、注、疏、正义", "q": {"stem": "“疏”的体例是既解释经文，又疏通解释____。", "type": "blank",
        "answer": "前人的注解", "options": [],
        "explanation": "“疏”不仅注经文，还疏通前人的传、注，如《十三经注疏》。"}},
    {"ch": "训诂", "kw": "古注术语（一）：为、曰、谓之、谓、犹、貌", "q": {"stem": "训诂术语中，用“____”“为”“谓之”来区分同义词或近义词。", "type": "blank",
        "answer": "曰", "options": [],
        "explanation": "“曰、为、谓之”常用于区分同义词或给事物下定义，如“曰”多用于辨析。"}},
    {"ch": "训诂", "kw": "古注类型（二）：章句、集解与阐发义理", "q": {"stem": "汇集各家注解于一书的注释体例称为____。", "type": "blank",
        "answer": "集解", "options": [],
        "explanation": "集解汇集各家之说，如何晏《论语集解》。"}},
    # 音韵
    {"ch": "音韵", "kw": "《切韵》《广韵》与中古音", "q": {"stem": "《切韵》是____（朝代）陆法言等人编撰的韵书。", "type": "blank",
        "answer": "隋", "options": [],
        "explanation": "《切韵》成书于隋代，是中古音的代表性韵书，《广韵》是其增订本。"}},
    {"ch": "音韵", "kw": "上古音", "q": {"stem": "研究先秦两汉时期汉语语音系统的学问称为____音学。", "type": "blank",
        "answer": "上古", "options": [],
        "explanation": "上古音研究先秦两汉语音，中古音以《切韵》《广韵》为代表。"}},
    # 修辞
    {"ch": "修辞", "kw": "借代", "q": {"stem": "“布衣”代指平民，使用的是____辞格。", "type": "blank",
        "answer": "借代", "options": [],
        "explanation": "以“布衣”（衣着特征）代指平民，是借代。"}},
    {"ch": "修辞", "kw": "起兴与比喻", "q": {"stem": "“关关雎鸠，在河之洲”在《关雎》中起____的作用。", "type": "blank",
        "answer": "起兴", "options": [],
        "explanation": "先言他物以引起所咏之词，是起兴（兴），《诗经》多用此法。"}},
    {"ch": "修辞", "kw": "起兴与比喻", "q": {"stem": "“譬如北辰，居其所而众星共之”中“北辰”是____体。", "type": "blank",
        "answer": "喻", "options": [],
        "explanation": "以“北辰”比喻君主，“北辰”是喻体。"}},
    # 古书文体
    {"ch": "古书的文体", "kw": "论辩", "q": {"stem": "“论”“辩”都属于____类文体。", "type": "blank",
        "answer": "论说（议论）", "options": [],
        "explanation": "论辩是议论说理的文体，如贾谊《过秦论》。"}},
    {"ch": "古书的文体", "kw": "序跋与书启", "q": {"stem": "写在书前的文章叫____，写在书后的叫跋。", "type": "blank",
        "answer": "序", "options": [],
        "explanation": "序（叙）在书前，跋在书后，序跋是说明著作缘起、内容等的文体。"}},
    {"ch": "古书的文体", "kw": "碑志与哀祭", "q": {"stem": "刻在墓碑上记述死者生平的文字称为____。", "type": "blank",
        "answer": "墓志铭（碑志）", "options": [],
        "explanation": "碑志是刻于碑上的文字，墓志铭记述死者生平、表达哀思。"}},
    # 古书标点
    {"ch": "古书的标点", "kw": "句读的概念", "q": {"stem": "古书断句中，“句”指语意____处的停顿。", "type": "blank",
        "answer": "完整", "options": [],
        "explanation": "“句”指语意完整之处的停顿，“读”指语意未尽而语气需停顿之处。"}},
    {"ch": "古书的标点", "kw": "句读与标点符号的异同", "q": {"stem": "与今之标点相比，古书句读____（更简略）。", "type": "blank",
        "answer": "更简略", "options": [],
        "explanation": "古书句读只有句、读两种停顿标记，远比现代标点简略。"}},
    # 诗词格律
    {"ch": "诗词格律", "kw": "近体诗的押韵", "q": {"stem": "近体诗一般只押____声韵。", "type": "blank",
        "answer": "平", "options": [],
        "explanation": "近体诗一般押平声韵，且一韵到底、不许换韵。"}},
    {"ch": "诗词格律", "kw": "平仄与拗救", "q": {"stem": "古汉语声调中，“仄”包括上、去、____三声。", "type": "blank",
        "answer": "入", "options": [],
        "explanation": "平仄相对，仄声包括上、去、入三声。"}},
    {"ch": "诗词格律", "kw": "平仄与拗救", "q": {"stem": "诗句中该用平声却用了仄声，称为____。", "type": "blank",
        "answer": "拗", "options": [],
        "explanation": "不合平仄常格叫“拗”，用变通办法补救叫“救”，合称拗救。"}},
    # 文字
    {"ch": "文字（下）", "kw": "甲骨文与金文", "q": {"stem": "甲骨文主要出土于今河南____的殷墟。", "type": "blank",
        "answer": "安阳", "options": [],
        "explanation": "甲骨文于河南安阳殷墟大量出土，是商代占卜记录文字。"}},
    {"ch": "文字（下）", "kw": "古今字", "q": {"stem": "“说”与“悦”是____字关系。", "type": "blank",
        "answer": "古今", "options": [],
        "explanation": "“说”古义有“喜悦”，后另造“悦”，二字为古今字。"}},
    {"ch": "文字（下）", "kw": "通假字", "q": {"stem": "“寡助之至，亲戚畔之”中“畔”通“____”。", "type": "blank",
        "answer": "叛", "options": [],
        "explanation": "“畔”借作“叛”，音同义通，是通假字。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'古代汉语第二批挂载 {n} 题')
