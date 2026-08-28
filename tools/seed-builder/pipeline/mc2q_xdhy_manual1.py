# -*- coding: utf-8 -*-
"""现代汉语 人工设计扩充 第一批：绪论 + 语音薄弱点"""
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
    # ===== 绪论 =====
    {"ch": "绪论", "kw": "现代汉语的定义", "q": {"stem": "狭义的“现代汉语”指的是（　）", "type": "choice",
        "answer": "现代汉民族共同语", "options": ["现代汉民族共同语", "各地方言的总称", "古代汉语的延续", "普通话与方言的合称"],
        "explanation": "狭义的现代汉语指现代汉民族共同语（普通话），广义的还兼指现代汉语的各种方言。"}},
    {"ch": "绪论", "kw": "现代汉语的定义", "q": {"stem": "现代汉语的地域分支是（　）", "type": "choice",
        "answer": "方言", "options": ["方言", "次方言", "土语", "亲属语言"],
        "explanation": "方言是现代汉语的地域分支，共同语是在方言基础上形成的。"}},
    {"ch": "绪论", "kw": "普通话的定义", "q": {"stem": "普通话以北京语音为____，以北方话为基础方言。", "type": "blank",
        "answer": "标准音", "options": [],
        "explanation": "普通话的定义：以北京语音为标准音，以北方话为基础方言，以典范的现代白话文著作为语法规范。"}},
    {"ch": "绪论", "kw": "汉语方言与七大方言区", "q": {"stem": "下列不属于汉语七大方言区的是（　）", "type": "choice",
        "answer": "晋方言", "options": ["晋方言", "吴方言", "闽方言", "粤方言"],
        "explanation": "汉语七大方言区是北方方言、吴、湘、赣、客家、闽、粤；晋方言不在传统七区之列。"}},
    {"ch": "绪论", "kw": "汉民族共同语的形成", "q": {"stem": "汉族早在先秦时代就存在古代民族共同语，春秋时代称为____。", "type": "blank",
        "answer": "雅言", "options": [],
        "explanation": "先秦共同语称“雅言”，汉代称“通语”，明清称“官话”，辛亥革命后称“国语”，新中国成立后称“普通话”。"}},
    {"ch": "绪论", "kw": "现代汉语的特点", "q": {"stem": "现代汉语语法方面的主要特点是（　）", "type": "choice",
        "answer": "缺乏严格意义的形态变化", "options": ["缺乏严格意义的形态变化", "有丰富的词形变化", "主要靠词尾变化表语法意义", "语序和虚词作用不大"],
        "explanation": "现代汉语缺乏严格意义的形态变化，主要靠语序和虚词表达语法意义。"}},
    {"ch": "绪论", "kw": "现代汉语规范化", "q": {"stem": "普通话以典范的现代____著作为语法规范。", "type": "blank",
        "answer": "白话文", "options": [],
        "explanation": "普通话规范三标准：语音以北京语音为标准音，词汇以北方话为基础方言，语法以典范的现代白话文著作为规范。"}},
    {"ch": "绪论", "kw": "推广普通话的方针", "q": {"stem": "新时期推广普通话的工作方针是（　）", "type": "choice",
        "answer": "大力推行、积极普及、逐步提高", "options": ["大力推行、积极普及、逐步提高", "大力提倡、重点推行、逐步普及", "重点推行、积极普及", "普及为主、兼顾规范"],
        "explanation": "新时期推普方针是“大力推行、积极普及、逐步提高”。"}},
    # ===== 语音 =====
    {"ch": "语音", "kw": "声母的数量", "q": {"stem": "普通话共有____个辅音声母。", "type": "blank",
        "answer": "21", "options": [],
        "explanation": "普通话有21个辅音声母，另有零声母。"}},
    {"ch": "语音", "kw": "声母的数量", "q": {"stem": "下列全为舌尖前音声母的一组是（　）", "type": "choice",
        "answer": "z、c、s", "options": ["z、c、s", "zh、ch、sh", "j、q、x", "b、p、m"],
        "explanation": "舌尖前音是z、c、s；zh、ch、sh是舌尖后音；j、q、x是舌面音。"}},
    {"ch": "语音", "kw": "鼻韵母", "q": {"stem": "普通话鼻韵母分为前鼻音尾韵母和____两大类。", "type": "blank",
        "answer": "后鼻音尾韵母", "options": [],
        "explanation": "鼻韵母按韵尾分前鼻音尾（-n）和后鼻音尾（-ng）两类。"}},
    {"ch": "语音", "kw": "鼻韵母", "q": {"stem": "下列属于前鼻音尾韵母的是（　）", "type": "choice",
        "answer": "an、en、in", "options": ["an、en、in", "ang、eng、ing", "ong、iong", "a、o、e"],
        "explanation": "前鼻音尾韵母以-n收尾，如an、en、in；ang、eng、ing是后鼻音尾韵母。"}},
    {"ch": "语音", "kw": "单韵母", "q": {"stem": "普通话单韵母共有____个。", "type": "blank",
        "answer": "10", "options": [],
        "explanation": "普通话单韵母共10个，包括舌面元音7个、舌尖元音2个、卷舌元音1个。"}},
    {"ch": "语音", "kw": "复韵母", "q": {"stem": "复韵母按韵腹的位置分为前响、____、中响三类。", "type": "blank",
        "answer": "后响", "options": [],
        "explanation": "复韵母分前响、后响、中响三类，如ai是前响、ia是后响、iao是中响。"}},
    {"ch": "语音", "kw": "四呼", "q": {"stem": "韵母中韵头或韵腹是i的属于____呼。", "type": "blank",
        "answer": "齐齿", "options": [],
        "explanation": "四呼：开口呼（无韵头、韵腹非i/u/ü）、齐齿呼（i或i开头）、合口呼（u或u开头）、撮口呼（ü或ü开头）。"}},
    {"ch": "语音", "kw": "四呼", "q": {"stem": "下列属于撮口呼韵母的一组是（　）", "type": "choice",
        "answer": "ü、üe、üan", "options": ["ü、üe、üan", "i、ia、ian", "u、ua、uan", "a、o、e"],
        "explanation": "撮口呼韵母以ü或ü开头，如ü、üe、üan、ün。"}},
    {"ch": "语音", "kw": "轻声", "q": {"stem": "轻声在物理上的变化主要表现为音强变弱、音长____。", "type": "blank",
        "answer": "变短", "options": [],
        "explanation": "轻声的音高不固定，音强变弱、音长变短、音色也发生变化。"}},
    {"ch": "语音", "kw": "儿化", "q": {"stem": "儿化的主要作用不包括（　）", "type": "choice",
        "answer": "表示庄重严肃", "options": ["表示庄重严肃", "区别词义", "区别词性", "表示细小、喜爱的感情色彩"],
        "explanation": "儿化能区别词义、词性，并表示细小、亲切、喜爱的感情色彩，没有“庄重严肃”的作用。"}},
    {"ch": "语音", "kw": "变调", "q": {"stem": "两个上声相连，前一个上声的调值一般变为____。", "type": "blank",
        "answer": "阳平（35）", "options": [],
        "explanation": "两个上声相连，前一个上声变读为阳平，调值由214变为35。"}},
    {"ch": "语音", "kw": "《汉语拼音方案》", "q": {"stem": "《汉语拼音方案》由字母表、声母表、韵母表、____和隔音符号五部分组成。", "type": "blank",
        "answer": "声调符号", "options": [],
        "explanation": "《汉语拼音方案》包括字母表、声母表、韵母表、声调符号、隔音符号五部分。"}},
    {"ch": "语音", "kw": "语音四要素", "q": {"stem": "声调的高低升降主要决定于语音四要素中的____。", "type": "blank",
        "answer": "音高", "options": [],
        "explanation": "音高决定声调的高低升降，音色区别不同音素，音强与轻重音有关，音长与语速有关。"}},
    {"ch": "语音", "kw": "音素与音节", "q": {"stem": "最小的语音单位是（　）", "type": "choice",
        "answer": "音素", "options": ["音素", "音节", "音位", "音强"],
        "explanation": "音素是最小的语音单位，音节是听觉上自然感到的最基本的语音结构单位。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'第一批挂载 {n} 题')
