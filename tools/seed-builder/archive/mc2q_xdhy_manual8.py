# -*- coding: utf-8 -*-
"""现代汉语 人工设计扩充 第8批"""
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
    {"ch": "语音", "kw": "声母的数量", "q": {"stem": "普通话中属于舌尖中音的一组声母是（　）", "type": "choice",
        "answer": "d、t、n、l", "options": ["d、t、n、l", "z、c、s", "zh、ch、sh", "b、p、m、f"],
        "explanation": "舌尖中音有 d、t、n、l，舌尖接触上齿龈发音。"}},
    {"ch": "语音", "kw": "单韵母", "q": {"stem": "普通话单韵母中，唯一的卷舌元音是____。", "type": "blank",
        "answer": "er", "options": [],
        "explanation": "er 是卷舌元音，属单韵母，如“儿”“耳”的韵母。"}},
    {"ch": "语音", "kw": "变调", "q": {"stem": "上声在阴平、阳平、去声前变读为____（21）。", "type": "blank",
        "answer": "半上", "options": [],
        "explanation": "上声在非上声前读半上（21），如“首都”“海洋”；两上相连前一上读阳平（35）。"}},
    {"ch": "语音", "kw": "韵母的构成与分类", "q": {"stem": "韵母中必不可少、发音最响亮的成分是____。", "type": "blank",
        "answer": "韵腹", "options": [],
        "explanation": "韵腹是韵母的核心，发音最响亮，一个韵母可以没有韵头和韵尾，但必须有韵腹。"}},
    {"ch": "语音", "kw": "儿化", "q": {"stem": "“花儿”中“儿”在发音上（　）", "type": "choice",
        "answer": "与前一个音节融合成卷舌韵母", "options": ["与前一个音节融合成卷舌韵母", "读成独立音节", "读轻声", "不发音"],
        "explanation": "儿化时“儿”与前一音节的韵母融合成一个卷舌韵母，不读独立音节。"}},
    {"ch": "文字", "kw": "文字的性质与汉字的性质", "q": {"stem": "汉字是记录____的书写符号系统。", "type": "blank",
        "answer": "汉语", "options": [],
        "explanation": "文字是记录语言的书写符号系统，汉字是记录汉语的书写符号系统。"}},
    {"ch": "文字", "kw": "六书", "q": {"stem": "“武”字由“止”“戈”组成，表示制止战争，属于六书中的（　）", "type": "choice",
        "answer": "会意", "options": ["会意", "象形", "指事", "形声"],
        "explanation": "“武”由两个表意偏旁组合表示新的意义，是会意字。"}},
    {"ch": "文字", "kw": "形声字", "q": {"stem": "“湖”字中，表示读音的“胡”位于____。", "type": "blank",
        "answer": "右（右边）", "options": [],
        "explanation": "“湖”形旁“氵”在左、声旁“胡”在右，是左形右声的形声字。"}},
    {"ch": "文字", "kw": "独体字与合体字", "q": {"stem": "“田”字不可再拆分为更小的部件，属于____字。", "type": "blank",
        "answer": "独体", "options": [],
        "explanation": "“田”是象形字，整体一个部件，是独体字。"}},
    {"ch": "词汇", "kw": "联绵词", "q": {"stem": "下列属于联绵词的是（　）", "type": "choice",
        "answer": "妯娌", "options": ["妯娌", "国家", "人民", "花朵"],
        "explanation": "“妯娌”是双声联绵词；“国家”是并列合成词，其余也是合成词。"}},
    {"ch": "词汇", "kw": "词义（理性义与色彩义）", "q": {"stem": "“逝世”与“死了”在色彩义上的差别主要是（　）", "type": "choice",
        "answer": "语体色彩和感情色彩不同", "options": ["语体色彩和感情色彩不同", "理性义不同", "形象色彩不同", "没有差别"],
        "explanation": "“逝世”庄重、表敬重，“死了”直白，二者语体色彩和感情色彩不同。"}},
    {"ch": "词汇", "kw": "语素", "q": {"stem": "“咖啡”是一个音译外来词，由____个语素构成。", "type": "blank",
        "answer": "一", "options": [],
        "explanation": "“咖啡”整体是一个音译语素，不可再分。"}},
    {"ch": "词汇", "kw": "熟语", "q": {"stem": "“碰钉子”“开夜车”属于熟语中的____。", "type": "blank",
        "answer": "惯用语", "options": [],
        "explanation": "惯用语是口语中惯用的固定短语，如“碰钉子”“开后门”。"}},
    {"ch": "语法", "kw": "实词", "q": {"stem": "下列词中属于实词的是（　）", "type": "choice",
        "answer": "奔跑", "options": ["奔跑", "的", "和", "吗"],
        "explanation": "“奔跑”是动词，能充当谓语，是实词；“的、和、吗”是虚词。"}},
    {"ch": "语法", "kw": "短语", "q": {"stem": "“非常漂亮”中“非常”修饰“漂亮”，属于____短语。", "type": "blank",
        "answer": "偏正（状中）", "options": [],
        "explanation": "“非常漂亮”是状语+中心语，属于偏正短语中的状中短语。"}},
    {"ch": "语法", "kw": "句子成分", "q": {"stem": "“我买了一本书”中“一本书”在句中充当____。", "type": "blank",
        "answer": "宾语", "options": [],
        "explanation": "“一本书”是动词“买”支配的对象，充当宾语。"}},
    {"ch": "语法", "kw": "特殊句式", "q": {"stem": "“这本书我看过”的主语是____。", "type": "blank",
        "answer": "这本书（全句主语）", "options": [],
        "explanation": "“这本书”是全句主语，“我看过”是谓语（主谓谓语部分），属主谓谓语句。"}},
    {"ch": "修辞", "kw": "比喻", "q": {"stem": "“他像老虎一样凶猛”中“像”是喻词，属于（　）", "type": "choice",
        "answer": "明喻", "options": ["明喻", "暗喻", "借喻", "博喻"],
        "explanation": "本体、喻体、喻词都出现且用“像”等连接，是明喻。"}},
    {"ch": "修辞", "kw": "借代", "q": {"stem": "“巾帼不让须眉”中“巾帼”代指女性、“须眉”代指男性，属于（　）", "type": "choice",
        "answer": "借代", "options": ["借代", "借喻", "比拟", "双关"],
        "explanation": "以“巾帼”这一服饰特征代指女性，是借代。"}},
    {"ch": "修辞", "kw": "比拟", "q": {"stem": "“群山在呼唤”把群山当作人来写，属于（　）", "type": "choice",
        "answer": "拟人", "options": ["拟人", "拟物", "比喻", "夸张"],
        "explanation": "赋予“群山”人的动作“呼唤”，是拟人。"}},
    {"ch": "标点符号", "kw": "标号（一）：引号、括号、破折号、省略号", "q": {"stem": "标示文中引用部分的标号是（　）", "type": "choice",
        "answer": "引号", "options": ["引号", "括号", "破折号", "书名号"],
        "explanation": "引号标示引用、强调或特殊含义，如“他说‘你好’”。"}},
    {"ch": "绪论", "kw": "现代汉语的定义", "q": {"stem": "广义的现代汉语除现代汉民族共同语外，还包括现代汉民族的____。", "type": "blank",
        "answer": "方言", "options": [],
        "explanation": "广义的现代汉语兼指共同语和各方言；狭义的指现代汉民族共同语（普通话）。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'第8批挂载 {n} 题')
