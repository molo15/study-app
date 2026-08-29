# -*- coding: utf-8 -*-
"""古代汉语 扩充第三批：文字/音韵/文体/工具书/修辞"""
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
    # 文字
    {"ch": "文字（上）", "kw": "会意", "q": {"stem": "“休”由“人”“木”组合表示人倚树休息，属于____字。", "type": "blank",
        "answer": "会意", "options": [],
        "explanation": "会意字由两个以上表意偏旁组合表示新义，“休”是会意字。"}},
    {"ch": "文字（上）", "kw": "六书的分类学说", "q": {"stem": "六书中，象形、指事、会意、形声属于____字法。", "type": "blank",
        "answer": "造", "options": [],
        "explanation": "六书分造字法和用字法，前四种是造字法，转注、假借是用字法。"}},
    {"ch": "文字（上）", "kw": "转注", "q": {"stem": "“老”与“考”同部、意义相通而互训，属于六书中的____。", "type": "blank",
        "answer": "转注", "options": [],
        "explanation": "转注指同一部首、意义相通的字互相注释，如“老”“考”互训。"}},
    {"ch": "文字（上）", "kw": "假借", "q": {"stem": "“难”本指一种鸟，借用为“困难”之“难”，属于六书中的____。", "type": "blank",
        "answer": "假借", "options": [],
        "explanation": "假借是本无其字而借用同音字表示新义，属用字法。"}},
    {"ch": "文字（下）", "kw": "古今字与通假字的区别", "q": {"stem": "古今字中，古字与后起字有____关系；通假字则是临时借用音同字。", "type": "blank",
        "answer": "先后（本字与后起字）", "options": [],
        "explanation": "古今字是先后造字的关系，通假字是音同义通的临时借用，二者有区别。"}},
    {"ch": "文字（下）", "kw": "异体字", "q": {"stem": "“泪”与“涙”音义全同而形体不同，属于____字。", "type": "blank",
        "answer": "异体", "options": [],
        "explanation": "异体字是音义完全相同、形体不同的字。"}},
    {"ch": "文字（下）", "kw": "繁简字", "q": {"stem": "“學習”的简体是____。", "type": "blank",
        "answer": "学习", "options": [],
        "explanation": "“學習”简化作“学习”，是繁简字关系。"}},
    # 绪论
    {"ch": "绪论", "kw": "历史观点", "q": {"stem": "阅读古书要注意古今词义的____差异，不能以今律古。", "type": "blank",
        "answer": "时代", "options": [],
        "explanation": "古今词义有时代差异，要以历史发展的观点看待古义。"}},
    {"ch": "绪论", "kw": "古代汉语的教学内容", "q": {"stem": "王力主编《古代汉语》的教学内容包括文选、____和常用词三部分。", "type": "blank",
        "answer": "通论", "options": [],
        "explanation": "王力《古代汉语》以文选、通论、常用词三结合为体例。"}},
    {"ch": "绪论", "kw": "古代汉语课的性质与学习意义", "q": {"stem": "古代汉语课是一门____课，为阅读古书提供工具。", "type": "blank",
        "answer": "工具", "options": [],
        "explanation": "古代汉语课具有工具课性质，重在培养阅读古书的能力。"}},
    # 词汇
    {"ch": "词汇", "kw": "词汇的发展", "q": {"stem": "汉语词汇由以单音词为主，逐步发展为以____词为主。", "type": "blank",
        "answer": "双音", "options": [],
        "explanation": "汉语词汇发展的趋势是由单音词向双音词转化。"}},
    # 诗词格律
    {"ch": "诗词格律", "kw": "对联", "q": {"stem": "对联要求上下联字数相等、____相对、平仄相谐。", "type": "blank",
        "answer": "词性", "options": [],
        "explanation": "对联要求上下联字数相等、词性相对、结构相应、平仄相谐。"}},
    {"ch": "诗词格律", "kw": "近体诗的概念、发展与分类", "q": {"stem": "近体诗可分为律诗和____两大类。", "type": "blank",
        "answer": "绝句", "options": [],
        "explanation": "近体诗分绝句（四句）和律诗（八句）两类。"}},
    # 语法
    {"ch": "语法（下）", "kw": "词类活用的概念与判定条件", "q": {"stem": "判断词类活用，主要看词的____功能是否临时改变。", "type": "blank",
        "answer": "语法", "options": [],
        "explanation": "词类活用是某类词在句中临时改变其基本语法功能的现象。"}},
    # 音韵
    {"ch": "音韵", "kw": "反切", "q": {"stem": "反切注音时，上字取____，下字取韵母和声调。", "type": "blank",
        "answer": "声母", "options": [],
        "explanation": "反切是两字相拼注音，上字取声、下字取韵和调。"}},
    {"ch": "音韵", "kw": "音韵学基本概念", "q": {"stem": "音韵学是研究汉语____的学科。", "type": "blank",
        "answer": "语音（古今语音系统）", "options": [],
        "explanation": "音韵学研究汉语语音的结构、演变与规律。"}},
    {"ch": "音韵", "kw": "五音七音与清浊", "q": {"stem": "传统音韵学按发音部位分为唇、舌、____、牙、喉五音。", "type": "blank",
        "answer": "齿", "options": [],
        "explanation": "五音是唇、舌、齿、牙、喉，加半舌、半齿为七音。"}},
    {"ch": "音韵", "kw": "韵母结构：韵头、韵腹、韵尾", "q": {"stem": "传统音韵学把韵母分为韵头、____、韵尾三部分。", "type": "blank",
        "answer": "韵腹", "options": [],
        "explanation": "韵母由韵头、韵腹、韵尾构成，韵腹是核心。"}},
    {"ch": "音韵", "kw": "中古声调到北京音的变化", "q": {"stem": "中古入声韵在现代北京音中已____。", "type": "blank",
        "answer": "消失（派入四声）", "options": [],
        "explanation": "现代北京音无入声，中古入声字分别派入阴平、阳平、上声、去声。"}},
    {"ch": "音韵", "kw": "《韵镜》、尖音与团音", "q": {"stem": "《韵镜》是现存最早的____图。", "type": "blank",
        "answer": "等韵", "options": [],
        "explanation": "《韵镜》是现存最早的等韵图，表现声韵调的配合关系。"}},
    # 修辞
    {"ch": "修辞", "kw": "互文与并提", "q": {"stem": "“秦时明月汉时关”中“秦”“汉”互补，用的是____。", "type": "blank",
        "answer": "互文", "options": [],
        "explanation": "互文指上下文意义相互补充，合在一起才完整，如“秦时明月汉时关”应解为秦汉时的明月与关。"}},
    {"ch": "修辞", "kw": "委婉", "q": {"stem": "“驾崩”是天子之死的____说法。", "type": "blank",
        "answer": "委婉（讳饰）", "options": [],
        "explanation": "委婉是避免直说、用含蓄的话表达，如“驾崩”讳言帝王之死。"}},
    {"ch": "修辞", "kw": "顶真与析字", "q": {"stem": "“忽闻海上有仙山，山在虚无缥缈间”中“山”上递下接，用的是____。", "type": "blank",
        "answer": "顶真", "options": [],
        "explanation": "前句结尾“仙山”之“山”作下句开头，是顶真。"}},
    {"ch": "修辞", "kw": "排比", "q": {"stem": "三个或三个以上结构相似、语气一致的语句排列，称为____。", "type": "blank",
        "answer": "排比", "options": [],
        "explanation": "排比由结构相同或相似、语气一致的语句排列而成，增强语势。"}},
    {"ch": "修辞", "kw": "变文与倒置", "q": {"stem": "为避免重复而变换词语表达同一意义，称为____。", "type": "blank",
        "answer": "变文", "options": [],
        "explanation": "变文是在上下文中变换用词以避免重复，如“陟罚臧否，不宜异同”中“臧否”与“异同”。"}},
    # 古书文体
    {"ch": "古书的文体", "kw": "奏议与诏令", "q": {"stem": "臣下向君主进言陈事的文书称为____。", "type": "blank",
        "answer": "奏议", "options": [],
        "explanation": "奏议是臣下上书君主的文体，如奏、议、表、疏。"}},
    {"ch": "古书的文体", "kw": "杂记", "q": {"stem": "记述山川景物、风土人情的文体称为____。", "type": "blank",
        "answer": "杂记", "options": [],
        "explanation": "杂记记述山水游记、杂事见闻，如柳宗元《小石潭记》。"}},
    {"ch": "古书的文体", "kw": "传状", "q": {"stem": "记述人物生平事迹的文体称为____。", "type": "blank",
        "answer": "传状（传记）", "options": [],
        "explanation": "传状是记述人物生平的文体，如《五柳先生传》。"}},
    {"ch": "古书的文体", "kw": "箴铭与颂赞", "q": {"stem": "用于规劝告诫、自我警戒的文体称为____。", "type": "blank",
        "answer": "箴铭", "options": [],
        "explanation": "箴铭用于规诫，如韩愈《五箴》。"}},
    # 工具书
    {"ch": "工具书简介", "kw": "字典与《说文解字》", "q": {"stem": "《说文解字》的作者是东汉的____。", "type": "blank",
        "answer": "许慎", "options": [],
        "explanation": "许慎著《说文解字》，按部首编排，是第一部系统分析汉字字形的字书。"}},
    {"ch": "工具书简介", "kw": "虚词类词典", "q": {"stem": "解释古汉语虚词的专著有《经传释词》和《____》。", "type": "blank",
        "answer": "词诠", "options": [],
        "explanation": "《词诠》（杨树达）是解释虚词的专著，与《经传释词》同为虚词词典。"}},
    {"ch": "工具书简介", "kw": "类书", "q": {"stem": "分类汇编古代资料的书籍称为____。", "type": "blank",
        "answer": "类书", "options": [],
        "explanation": "类书按类汇集材料，如《艺文类聚》《太平御览》。"}},
    {"ch": "工具书简介", "kw": "政书", "q": {"stem": "专门记载历代典章制度的书籍称为____。", "type": "blank",
        "answer": "政书", "options": [],
        "explanation": "政书记载典章制度，如《通典》《文献通考》。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'古代汉语第三批挂载 {n} 题')
