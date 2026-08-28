# -*- coding: utf-8 -*-
"""现代汉语 人工设计扩充 第7批"""
import io, sys, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json'
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
        best = {"id": "k_zhen_xdhy_" + chapter, "name": chapter + "（真题补充）", "parent": "root",
                "chapter": chapter, "hot": False, "summary": "考研真题补充知识点。", "basicQuestions": []}
        KP['knowledge'].append(best)
    for e in best.get('basicQuestions', []):
        if norm(e['stem']) == norm(q['stem']): return False
    best['basicQuestions'].append(q); return True

Q = [
    {"ch": "绪论", "kw": "推广普通话的方针", "q": {"stem": "新时期推广普通话的方针是“大力推行、积极普及、____”。", "type": "blank",
        "answer": "逐步提高", "options": [],
        "explanation": "新时期推普方针是“大力推行、积极普及、逐步提高”。"}},
    {"ch": "绪论", "kw": "普通话的定义", "q": {"stem": "普通话的语法规范是（　）", "type": "choice",
        "answer": "典范的现代白话文著作", "options": ["典范的现代白话文著作", "现代汉语词典", "古代白话文著作", "各地方言语法"],
        "explanation": "普通话以典范的现代白话文著作为语法规范。"}},
    {"ch": "语音", "kw": "语调与语流音变", "q": {"stem": "句子中的停顿、重音和句调合称为____。", "type": "blank",
        "answer": "语调", "options": [],
        "explanation": "语调包括停顿、重音、句调，与句子语气和表达密切相关。"}},
    {"ch": "语音", "kw": "儿化", "q": {"stem": "“盖儿”中“儿化”使“盖”由动词变为名词，说明儿化有____作用。", "type": "blank",
        "answer": "区别词性", "options": [],
        "explanation": "“盖（动词）—盖儿（名词）”，儿化有区别词性、词义的作用。"}},
    {"ch": "语音", "kw": "声母的数量", "q": {"stem": "普通话的辅音声母中，浊音有 m、n、l、____四个。", "type": "blank",
        "answer": "r", "options": [],
        "explanation": "普通话浊声母有 m、n、l、r 四个，其余都是清音。"}},
    {"ch": "语音", "kw": "《汉语拼音方案》", "q": {"stem": "《汉语拼音方案》中，a、o、e开头的零声母音节与前一音节相连时要用____符号隔开。", "type": "blank",
        "answer": "隔音", "options": [],
        "explanation": "隔音符号（’）用于 a、o、e 开头的零声母音节与前一音节相连时，如“皮袄”pí’ǎo。"}},
    {"ch": "语音", "kw": "复韵母", "q": {"stem": "ia、ie、ua、uo 等韵腹在后的复韵母属于____响复韵母。", "type": "blank",
        "answer": "后", "options": [],
        "explanation": "后响复韵母韵腹在后、发音响亮，如 ia、ie、ua、uo。"}},
    {"ch": "语音", "kw": "鼻韵母", "q": {"stem": "前鼻音尾韵母的韵尾是____。", "type": "blank",
        "answer": "-n", "options": [],
        "explanation": "前鼻音尾韵母以舌尖鼻音-n收尾，如 an、en、in、un。"}},
    {"ch": "文字", "kw": "偏旁与部首", "q": {"stem": "“的”字的部首是（　）", "type": "choice",
        "answer": "白", "options": ["白", "勺", "丿", "日"],
        "explanation": "“的”的部首是“白”，字典中按部首查字。"}},
    {"ch": "文字", "kw": "异体字与异读词", "q": {"stem": "“泪”与“涙”音义完全相同、形体不同，二者是____字。", "type": "blank",
        "answer": "异体", "options": [],
        "explanation": "“泪”和“涙”音义相同而形体不同，是异体字。"}},
    {"ch": "文字", "kw": "汉字标准化（四定）", "q": {"stem": "汉字标准化中，确定现代汉语用字数量的工作叫____。", "type": "blank",
        "answer": "定量", "options": [],
        "explanation": "汉字标准化四定：定量、定形、定音、定序。"}},
    {"ch": "文字", "kw": "笔画与笔顺", "q": {"stem": "“我”字的第一笔是（　）", "type": "choice",
        "answer": "撇", "options": ["撇", "横", "竖钩", "点"],
        "explanation": "“我”的笔顺是撇、横、竖钩、提、斜钩、撇、点，第一笔是撇。"}},
    {"ch": "文字", "kw": "简化字与繁体字", "q": {"stem": "“後”简化为“后”采用的是____代替法。", "type": "blank",
        "answer": "同音", "options": [],
        "explanation": "“後”“后”音同，用笔画少的“后”代替“後”，是同音代替。"}},
    {"ch": "词汇", "kw": "联绵词", "q": {"stem": "“彷徨”的两个音节韵母相同，属于____联绵词。", "type": "blank",
        "answer": "叠韵", "options": [],
        "explanation": "“彷徨”韵母相同，是叠韵联绵词；“参差”是双声联绵词。"}},
    {"ch": "词汇", "kw": "词义（理性义与色彩义）", "q": {"stem": "“壮丽”“雄伟”多用于书面语，带有____语体色彩。", "type": "blank",
        "answer": "书面", "options": [],
        "explanation": "词义色彩包括感情色彩、语体色彩、形象色彩，“壮丽”偏书面语体。"}},
    {"ch": "词汇", "kw": "义项、义素与语义场", "q": {"stem": "“木”有“树木”“木头”等多个意义，是一个____义词。", "type": "blank",
        "answer": "多", "options": [],
        "explanation": "有几个义项的词是多义词，“木”兼有“树木”“木头”等义项。"}},
    {"ch": "词汇", "kw": "基本词汇与一般词汇", "q": {"stem": "基本词汇具有____性、能产性和全民常用性。", "type": "blank",
        "answer": "稳固", "options": [],
        "explanation": "基本词汇三大特点：稳固性、能产性、全民常用性。"}},
    {"ch": "词汇", "kw": "词义的演变", "q": {"stem": "“爪牙”古义为“得力助手”，今义为“帮凶”，词义发生了____。", "type": "blank",
        "answer": "转移", "options": [],
        "explanation": "“爪牙”由中性词变为贬义词，词义由所指对象转移，是词义转移。"}},
    {"ch": "词汇", "kw": "词根与词缀", "q": {"stem": "“花儿”中的“儿”是____缀。", "type": "blank",
        "answer": "后", "options": [],
        "explanation": "“儿”附加在“花”后，是后缀（词缀），使词带上细小、喜爱的色彩。"}},
    {"ch": "词汇", "kw": "语素", "q": {"stem": "“巧克力”是____个语素。", "type": "blank",
        "answer": "一", "options": [],
        "explanation": "“巧克力”是音译外来词，整体一个语素。"}},
    {"ch": "修辞", "kw": "比拟", "q": {"stem": "把人当作物来描写，或把甲物当作乙物来描写，称为____。", "type": "blank",
        "answer": "拟物", "options": [],
        "explanation": "比拟分拟人（把物当人）和拟物（把人当物、把甲物当乙物）。"}},
    {"ch": "修辞", "kw": "词语的锤炼", "q": {"stem": "词语锤炼一般从意义和____两方面入手。", "type": "blank",
        "answer": "声音", "options": [],
        "explanation": "词语锤炼从意义（准确鲜明）和声音（和谐动听）两方面入手。"}},
    {"ch": "修辞", "kw": "通感", "q": {"stem": "“甜美的歌声”把听觉与____觉沟通起来。", "type": "blank",
        "answer": "味", "options": [],
        "explanation": "“甜美”本用于味觉，此处形容歌声，是感觉移借的通感。"}},
    {"ch": "修辞", "kw": "双关", "q": {"stem": "“旗杆上插鸡毛——好大的掸（胆）子”利用“掸”与“胆”同音，是____双关。", "type": "blank",
        "answer": "谐音", "options": [],
        "explanation": "“掸”谐“胆”，音同义不同，是谐音双关。"}},
    {"ch": "修辞", "kw": "反复与顶真", "q": {"stem": "“沉默呵，沉默呵！不在沉默中爆发，就在沉默中灭亡”中“沉默”反复出现，属于（　）", "type": "choice",
        "answer": "连续反复", "options": ["连续反复", "间隔反复", "顶真", "排比"],
        "explanation": "“沉默呵，沉默呵”连续重复，是连续反复。"}},
    {"ch": "修辞", "kw": "反问与设问", "q": {"stem": "“谁是我们最可爱的人呢？我们的部队、我们的战士……”先问后答，使用了（　）", "type": "choice",
        "answer": "设问", "options": ["设问", "反问", "疑问句", "双关"],
        "explanation": "自问自答以引起注意，是设问。"}},
    {"ch": "修辞", "kw": "夸张", "q": {"stem": "“未饮心先醉”属于（　）", "type": "choice",
        "answer": "超前夸张", "options": ["超前夸张", "扩大夸张", "缩小夸张", "借代"],
        "explanation": "“未饮”却“先醉”，把后出现的事说成先出现，是超前夸张。"}},
    {"ch": "修辞", "kw": "对偶与对比", "q": {"stem": "对偶从内容上看，可分为正对、反对和____。", "type": "blank",
        "answer": "串对（流水对）", "options": [],
        "explanation": "对偶按内容分正对、反对、串对（流水对），按结构分严对、宽对。"}},
    {"ch": "标点符号", "kw": "标号（一）：引号、括号、破折号、省略号", "q": {"stem": "标示语意转折、解释说明或声音延长的标号是（　）", "type": "choice",
        "answer": "破折号", "options": ["破折号", "省略号", "括号", "引号"],
        "explanation": "破折号标示解释说明、语意转折、声音延长等。"}},
    {"ch": "标点符号", "kw": "标点符号的性质与分类", "q": {"stem": "标号的作用是标示词语的____和作用。", "type": "blank",
        "answer": "性质", "options": [],
        "explanation": "点号表停顿和语气，标号标示词语的性质和作用。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'第7批挂载 {n} 题')
