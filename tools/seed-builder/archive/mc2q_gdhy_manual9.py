# -*- coding: utf-8 -*-
"""古代汉语 扩充第九批：继续补充各章考点"""
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
    {"ch": "词汇", "kw": "词义的扩大、缩小、转移", "q": {"stem": "“烈士”古义指____，今义指为正义牺牲的人。", "type": "blank",
        "answer": "有抱负、有操守的人", "options": [],
        "explanation": "“烈士”词义由“有抱负的人”转移为“为正义牺牲的人”。"}},
    {"ch": "词汇", "kw": "词的引申义与引申方式", "q": {"stem": "“朝”由“早晨”引申出“朝见、朝廷”，属于____引申。", "type": "blank",
        "answer": "相关", "options": [],
        "explanation": "“朝”由早晨（臣子早晨朝见）相关引申为朝见、朝廷。"}},
    {"ch": "词汇", "kw": "词的本义", "q": {"stem": "“斤”的本义是____。", "type": "blank",
        "answer": "斧头", "options": [],
        "explanation": "“斤”本义为斧头（“斧斤以时入山林”），引申为重量单位。"}},
    {"ch": "词汇", "kw": "合成词", "q": {"stem": "“社稷”由“社”（土神）“稷”（谷神）并列构成，是____合成词。", "type": "blank",
        "answer": "并列（联合）", "options": [],
        "explanation": "“社稷”两词义并列，共同代指国家，是并列式合成词。"}},
    {"ch": "词汇", "kw": "同义词辨析", "q": {"stem": "“杀”用于杀一般对象，“弑”专用于____。", "type": "blank",
        "answer": "下杀上（臣杀君、子杀父）", "options": [],
        "explanation": "“弑”指地位低者杀死地位高者，是“杀”与“弑”的区别。"}},
    {"ch": "语法（上）", "kw": "代词", "q": {"stem": "“谁、孰、何”都是____代词。", "type": "blank",
        "answer": "疑问", "options": [],
        "explanation": "“谁、孰、何、安”等是疑问代词。"}},
    {"ch": "语法（上）", "kw": "副词", "q": {"stem": "“臣未尝闻也”中“未尝”表示____。", "type": "blank",
        "answer": "未曾（从来没有）", "options": [],
        "explanation": "“未尝”是表否定的时间副词，意为“未曾、从来没有”。"}},
    {"ch": "语法（上）", "kw": "语气词、叹词、助词", "q": {"stem": "“燕雀安知鸿鹄之志哉”中“哉”表示____语气。", "type": "blank",
        "answer": "感叹", "options": [],
        "explanation": "“哉”常表感叹、反问语气。"}},
    {"ch": "语法（上）", "kw": "介词与连词", "q": {"stem": "“为天下人谋永福”中“为”引介____。", "type": "blank",
        "answer": "对象（目的）", "options": [],
        "explanation": "“为”在此介引动作的对象，是介词。"}},
    {"ch": "语法（上）", "kw": "兼词", "q": {"stem": "“盖各言尔志”中的“盖”即“盍”，是“何不”的____词。", "type": "blank",
        "answer": "兼", "options": [],
        "explanation": "“盍（盖）”兼有“何”“不”之义，是兼词。"}},
    {"ch": "语法（下）", "kw": "判断句", "q": {"stem": "“陈胜者，阳城人也”是典型的____句。", "type": "blank",
        "answer": "判断", "options": [],
        "explanation": "“……者，……也”是古代汉语判断句的典型格式。"}},
    {"ch": "语法（下）", "kw": "使动用法", "q": {"stem": "“舞幽壑之潜蛟”中“舞”是____用法。", "type": "blank",
        "answer": "使动", "options": [],
        "explanation": "“舞幽壑之潜蛟”即使潜蛟舞动，是使动用法。"}},
    {"ch": "语法（下）", "kw": "意动用法", "q": {"stem": "“吾妻之美我者，私我也”中“美”是____用法。", "type": "blank",
        "answer": "意动", "options": [],
        "explanation": "“美我”即“以我为美”，形容词意动用法。"}},
    {"ch": "语法（下）", "kw": "名词作状语", "q": {"stem": "“而乡邻之生日蹙”中“日”作状语，意为____。", "type": "blank",
        "answer": "一天天地", "options": [],
        "explanation": "“日”名词作状语，表时间频率“一天天地”。"}},
    {"ch": "语法（下）", "kw": "词序：宾语前置", "q": {"stem": "“惟陈言之务去”中“陈言”是____前置。", "type": "blank",
        "answer": "宾语", "options": [],
        "explanation": "用“之”复指，将宾语“陈言”前置。"}},
    {"ch": "文字（上）", "kw": "象形与指事", "q": {"stem": "“口”是象形字，描摹____的形状。", "type": "blank",
        "answer": "嘴（口）", "options": [],
        "explanation": "“口”象嘴之形，是象形字。"}},
    {"ch": "文字（上）", "kw": "象形与指事", "q": {"stem": "“甘”在“口”中加一点标示所含之物，属于____字。", "type": "blank",
        "answer": "指事", "options": [],
        "explanation": "“甘”在口内加点指所含甘美之物，是指事字。"}},
    {"ch": "文字（上）", "kw": "会意", "q": {"stem": "“初”由“衣”“刀”会意，表示____。", "type": "blank",
        "answer": "裁衣之始", "options": [],
        "explanation": "“初”以“裁衣之始”会意为“开始”，是会意字。"}},
    {"ch": "文字（上）", "kw": "形声", "q": {"stem": "“娶”字中表音的“取”是____旁。", "type": "blank",
        "answer": "声", "options": [],
        "explanation": "“娶”从女取声，“取”是声旁。"}},
    {"ch": "文字（下）", "kw": "古今字", "q": {"stem": "“责”与“债”是____字关系。", "type": "blank",
        "answer": "古今", "options": [],
        "explanation": "“责”古有“债务”义，后加“亻”作“债”，是古今字。"}},
    {"ch": "音韵", "kw": "阴声韵、阳声韵、入声韵", "q": {"stem": "“东、阳、侵”等以鼻音收尾的韵是____声韵。", "type": "blank",
        "answer": "阳", "options": [],
        "explanation": "以 -m、-n、-ng 鼻音收尾的是阳声韵。"}},
    {"ch": "音韵", "kw": "反切", "q": {"stem": "“旦，得按切”中“得”与被切字“旦”的____相同。", "type": "blank",
        "answer": "声母", "options": [],
        "explanation": "反切上字取声，“得”与“旦”声母相同。"}},
    {"ch": "音韵", "kw": "中古声调到北京音的变化", "q": {"stem": "中古“浊上变去”指的是____的变化。", "type": "blank",
        "answer": "声调", "options": [],
        "explanation": "“浊上变去”指中古全浊上声字到现代读为去声，是声调演变。"}},
    {"ch": "训诂", "kw": "古注术语（一）：为、曰、谓之、谓、犹、貌", "q": {"stem": "训诂术语“貌”用于描写人或事物的____。", "type": "blank",
        "answer": "性状（情状）", "options": [],
        "explanation": "“貌”常用于描写形容词性的状态，如“肃然，敬貌”。"}},
    {"ch": "训诂", "kw": "字典与《说文解字》", "q": {"stem": "《说文解字》首创按____编排汉字的方法。", "type": "blank",
        "answer": "部首", "options": [],
        "explanation": "许慎把 9353 个字按 540 个部首归类，首创部首编排法。"}},
    {"ch": "训诂", "kw": "字典与《说文解字》", "q": {"stem": "《说文解字》共分____个部首。", "type": "blank",
        "answer": "540", "options": [],
        "explanation": "《说文》分 540 部首，是中国第一部字典。"}},
    {"ch": "修辞", "kw": "起兴与比喻", "q": {"stem": "“如切如磋，如琢如磨”用“如”作喻词，是____喻。", "type": "blank",
        "answer": "明", "options": [],
        "explanation": "用“如”直接连接本体喻体，是明喻。"}},
    {"ch": "修辞", "kw": "夸张与引用", "q": {"stem": "“力拔山兮气盖世”极力夸大，使用了____。", "type": "blank",
        "answer": "夸张", "options": [],
        "explanation": "“力拔山”夸大力量之强，是夸张。"}},
    {"ch": "古书的文体", "kw": "碑志与哀祭", "q": {"stem": "《柳子厚墓志铭》属于____文体。", "type": "blank",
        "answer": "碑志（墓志铭）", "options": [],
        "explanation": "墓志铭记述死者生平、寄予哀思，属碑志类。"}},
    {"ch": "古书的文体", "kw": "序跋与书启", "q": {"stem": "“启”是臣民上呈君主的____类文体。", "type": "blank",
        "answer": "书启", "options": [],
        "explanation": "“启”为书函、上陈之文体，属书启类。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'古代汉语第九批挂载 {n} 题')
