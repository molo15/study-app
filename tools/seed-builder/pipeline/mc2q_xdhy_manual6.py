# -*- coding: utf-8 -*-
"""现代汉语 人工设计扩充 第6批：剩余薄弱点补充"""
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
    # 绪论
    {"ch": "绪论", "kw": "推广普通话的方针", "q": {"stem": "50年代初制定的推广普通话工作方针是“大力提倡、____、逐步推广”。", "type": "blank",
        "answer": "重点推行", "options": [],
        "explanation": "50年代初的推普方针是“大力提倡、重点推行、逐步推广”；新时期方针为“大力推行、积极普及、逐步提高”。"}},
    {"ch": "绪论", "kw": "普通话的定义", "q": {"stem": "普通话以北方话为____方言。", "type": "blank",
        "answer": "基础", "options": [],
        "explanation": "普通话以北京语音为标准音，以北方话为基础方言，以典范的现代白话文著作为语法规范。"}},
    {"ch": "绪论", "kw": "汉民族共同语的形成", "q": {"stem": "辛亥革命后，汉民族共同语被称为____。", "type": "blank",
        "answer": "国语", "options": [],
        "explanation": "共同语演变：雅言（先秦）→通语（汉）→官话（明清）→国语（民国）→普通话（新中国）。"}},
    {"ch": "绪论", "kw": "现代汉语的特点", "q": {"stem": "现代汉语词汇方面，____音节词占优势。", "type": "blank",
        "answer": "双", "options": [],
        "explanation": "现代汉语词汇以双音节词占优势，如“国家”“学习”等。"}},
    {"ch": "绪论", "kw": "现代汉语规范化", "q": {"stem": "现代汉语规范化的语音标准是____。", "type": "blank",
        "answer": "北京语音", "options": [],
        "explanation": "规范化三标准：语音以北京语音为标准音，词汇以北方话为基础方言，语法以典范的现代白话文著作为规范。"}},
    {"ch": "绪论", "kw": "汉语方言与七大方言区", "q": {"stem": "下列属于吴方言区的城市是（　）", "type": "choice",
        "answer": "上海", "options": ["上海", "广州", "长沙", "厦门"],
        "explanation": "吴方言通行于上海、江苏南部、浙江等地；广州属粤方言，长沙属湘方言，厦门属闽方言。"}},
    # 修辞
    {"ch": "修辞", "kw": "词语的锤炼", "q": {"stem": "词语锤炼追求的表达效果不包括（　）", "type": "choice",
        "answer": "晦涩难懂", "options": ["晦涩难懂", "准确", "鲜明", "生动"],
        "explanation": "词语锤炼追求准确、鲜明、生动的表达效果，晦涩难懂是其反面。"}},
    {"ch": "修辞", "kw": "通感", "q": {"stem": "“闻到了阳光的味道”把视觉与嗅觉沟通起来，使用的辞格是（　）", "type": "choice",
        "answer": "通感", "options": ["通感", "比喻", "夸张", "双关"],
        "explanation": "把阳光（视觉）与味道（嗅觉）沟通，是感觉移借，即通感。"}},
    {"ch": "修辞", "kw": "双关", "q": {"stem": "“我失骄杨君失柳，杨柳轻飏直上重霄九”中“杨柳”既指杨柳树又指杨开慧、柳直荀，属于（　）", "type": "choice",
        "answer": "语义双关", "options": ["语义双关", "谐音双关", "借代", "反语"],
        "explanation": "“杨柳”一词兼指两种意义，是语义双关。"}},
    {"ch": "修辞", "kw": "反复与顶真", "q": {"stem": "“竹叶烧了，还有竹枝；竹枝断了，还有竹鞭”使用的辞格是（　）", "type": "choice",
        "answer": "顶真", "options": ["顶真", "反复", "排比", "回环"],
        "explanation": "上句结尾“竹枝”作下句开头，上递下接，是顶真。"}},
    {"ch": "修辞", "kw": "反问与设问", "q": {"stem": "答案在问句之中、不需要对方回答的辞格是____。", "type": "blank",
        "answer": "反问", "options": [],
        "explanation": "反问是无疑而问、答案寓于问中，加强语气；设问是自问自答。"}},
    {"ch": "修辞", "kw": "句式的选择", "q": {"stem": "“墙上芦苇，头重脚轻根底浅”是结构整齐的____句。", "type": "blank",
        "answer": "整", "options": [],
        "explanation": "整句结构整齐、音节匀称，如对偶句、排比句；散句结构参差、活泼自然。"}},
    {"ch": "修辞", "kw": "夸张", "q": {"stem": "“飞流直下三千尺，疑是银河落九天”使用的辞格是（　）", "type": "choice",
        "answer": "夸张", "options": ["夸张", "比喻", "比拟", "借代"],
        "explanation": "“三千尺”是扩大夸张，极力写瀑布之高。"}},
    {"ch": "修辞", "kw": "对偶与对比", "q": {"stem": "“横眉冷对千夫指，俯首甘为孺子牛”上下两句结构相同、字数相等，属于（　）", "type": "choice",
        "answer": "对偶", "options": ["对偶", "对比", "排比", "回环"],
        "explanation": "两句字数相等、结构对称、意义相关，是对偶。"}},
    {"ch": "修辞", "kw": "排比", "q": {"stem": "“山朗润起来了，水涨起来了，太阳的脸红起来了”使用的辞格是（　）", "type": "choice",
        "answer": "排比", "options": ["排比", "反复", "顶真", "对偶"],
        "explanation": "三个结构相似的句子排列，增强语势，是排比。"}},
    # 文字
    {"ch": "文字", "kw": "偏旁与部首", "q": {"stem": "“休”由“亻”和“木”两个____组成。", "type": "blank",
        "answer": "偏旁", "options": [],
        "explanation": "“休”是会意字，由“亻”“木”两个偏旁组成，表示人倚树休息。"}},
    {"ch": "文字", "kw": "异体字与异读词", "q": {"stem": "下列属于异体字的一组是（　）", "type": "choice",
        "answer": "峰—峯", "options": ["峰—峯", "说—悦", "长—常", "清—晴"],
        "explanation": "“峰”与“峯”音义相同、形体不同，是异体字；其余各组音义不同。"}},
    {"ch": "文字", "kw": "汉字标准化（四定）", "q": {"stem": "汉字“四定”中，规定每个汉字的规范字形叫____。", "type": "blank",
        "answer": "定形", "options": [],
        "explanation": "汉字标准化指定量、定形、定音、定序，定形是确定标准字形。"}},
    {"ch": "文字", "kw": "笔画与笔顺", "q": {"stem": "“先横后竖、先撇后捺、从上到下、从左到右”是汉字的____规则。", "type": "blank",
        "answer": "笔顺", "options": [],
        "explanation": "笔顺是汉字书写时的先后顺序，遵循先横后竖、先撇后捺等基本规则。"}},
    {"ch": "文字", "kw": "简化字与繁体字", "q": {"stem": "“圖書館”简化作“图书馆”，其中“圖”简化为“图”主要采用____方式。", "type": "blank",
        "answer": "简化偏旁（简省笔画）", "options": [],
        "explanation": "“圖”简化为“图”是通过简化偏旁、简省笔画实现的。"}},
    # 词汇
    {"ch": "词汇", "kw": "联绵词", "q": {"stem": "“参差”的两个音节声母相同，属于____联绵词。", "type": "blank",
        "answer": "双声", "options": [],
        "explanation": "“参差”（cēn cī）声母相同，是双声联绵词；叠韵指韵母相同，如“彷徨”。"}},
    {"ch": "词汇", "kw": "词义（理性义与色彩义）", "q": {"stem": "“成果”和“后果”感情色彩不同，“成果”带有____色彩。", "type": "blank",
        "answer": "褒义", "options": [],
        "explanation": "“成果”是褒义词，“后果”多含贬义，二者感情色彩不同。"}},
    {"ch": "词汇", "kw": "义项、义素与语义场", "q": {"stem": "“打”在“打人、打水、打毛衣”中用法不同，说明“打”有多个____。", "type": "blank",
        "answer": "义项", "options": [],
        "explanation": "一个词有几个意义就分几个义项，“打”是多义词，有多个义项。"}},
    {"ch": "词汇", "kw": "基本词汇与一般词汇", "q": {"stem": "“秀才”“之乎者也”等词属于一般词汇中的____词。", "type": "blank",
        "answer": "古语", "options": [],
        "explanation": "古语词是从古代汉语中吸收的词，属于一般词汇，如“秀才”“余”等。"}},
    {"ch": "词汇", "kw": "词义的演变", "q": {"stem": "“汤”古义为“热水”，今义为“菜汤”，词义发生了____。", "type": "blank",
        "answer": "缩小", "options": [],
        "explanation": "“汤”由泛指热水缩小为指菜汤，是词义缩小；“江”由专指长江扩大为泛指河流，是扩大。"}},
    {"ch": "词汇", "kw": "词根与词缀", "q": {"stem": "“老鹰”中的“老”是____缀。", "type": "blank",
        "answer": "前", "options": [],
        "explanation": "“老鹰”的“老”不表示年龄，是前缀；“老师”“老虎”同例。"}},
    {"ch": "词汇", "kw": "语素", "q": {"stem": "“蝴蝶”是____个语素。", "type": "blank",
        "answer": "一", "options": [],
        "explanation": "“蝴蝶”虽两个音节，但“蝴”不能独立表义，整个词是一个语素，属单纯词。"}},
    # 语音
    {"ch": "语音", "kw": "《汉语拼音方案》", "q": {"stem": "汉语拼音中，y、w主要用于____声母音节开头的书写。", "type": "blank",
        "answer": "零声母", "options": [],
        "explanation": "y、w用于零声母音节开头，如“衣”yī、“乌”wū。"}},
    {"ch": "语音", "kw": "单韵母", "q": {"stem": "下列都属于单韵母的一组是（　）", "type": "choice",
        "answer": "a、o、e", "options": ["a、o、e", "ai、ei、ao", "an、en、in", "ia、ie、ua"],
        "explanation": "单韵母由一个元音充当，a、o、e、i、u、ü等是单韵母。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'第6批挂载 {n} 题')
