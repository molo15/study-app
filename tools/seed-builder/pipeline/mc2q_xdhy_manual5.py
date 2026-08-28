# -*- coding: utf-8 -*-
"""现代汉语 人工设计扩充 第5批：各章补充至 5-6 题"""
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
    {"ch": "语音", "kw": "复韵母", "q": {"stem": "复韵母中韵腹位于前的，如 ai、ei、ao，属于____韵母。", "type": "blank",
        "answer": "前响", "options": [],
        "explanation": "前响复韵母前一个元音是韵腹、发音响亮，如 ai、ei、ao、ou。"}},
    {"ch": "语音", "kw": "轻声", "q": {"stem": "轻声具有____词义和词性的作用，如“东西”与“东西”。", "type": "blank",
        "answer": "区别", "options": [],
        "explanation": "轻声能区别词义和词性，如“大意（dàyì）”与“大意（dàyi）”。"}},
    {"ch": "语音", "kw": "鼻韵母", "q": {"stem": "下列全为后鼻音尾韵母的一组是（　）", "type": "choice",
        "answer": "ang、eng、ing", "options": ["ang、eng、ing", "an、en、in", "ian、uan、üan", "ai、ei、ao"],
        "explanation": "后鼻音尾韵母以-ng收尾，如 ang、eng、ing、ong。"}},
    {"ch": "语音", "kw": "四呼", "q": {"stem": "韵母中韵头或韵腹是 u 的属于____呼。", "type": "blank",
        "answer": "合口", "options": [],
        "explanation": "合口呼指韵头或韵腹是 u 的韵母，如 u、ua、uan。"}},
    {"ch": "语音", "kw": "语音四要素", "q": {"stem": "语音四要素中，与声音强弱直接相关的是____。", "type": "blank",
        "answer": "音强", "options": [],
        "explanation": "音强由声波振幅决定，与说话用力的轻重有关，与轻重音相关。"}},
    {"ch": "语音", "kw": "音素与音节", "q": {"stem": "普通话中，一个汉字一般对应一个____。", "type": "blank",
        "answer": "音节", "options": [],
        "explanation": "汉语一个汉字一般就是一个音节，如“汉”对应音节 hàn。"}},
    {"ch": "语音", "kw": "声母的发音方法", "q": {"stem": "按发音方法，b、p、d、t、g、k 都属于____音。", "type": "blank",
        "answer": "塞", "options": [],
        "explanation": "塞音发音时两个发音部位完全闭合，气流冲破阻碍迸发而出，b p d t g k 都是塞音。"}},
    {"ch": "文字", "kw": "六书", "q": {"stem": "用象征性符号或在象形字上加提示符号表示意义的造字法是____。", "type": "blank",
        "answer": "指事", "options": [],
        "explanation": "指事字用象征性符号或在象形字上添加符号表示意义，如“上”“下”“本”。"}},
    {"ch": "文字", "kw": "形声字", "q": {"stem": "“湖”的形旁是____，表示与水有关。", "type": "blank",
        "answer": "氵", "options": [],
        "explanation": "“湖”由形旁“氵”（水）和声旁“胡”组成，是形声字。"}},
    {"ch": "文字", "kw": "独体字与合体字", "q": {"stem": "由两个或两个以上部件构成的字称为____字。", "type": "blank",
        "answer": "合体", "options": [],
        "explanation": "合体字由两个或两个以上部件构成，如“明”“休”；独体字不可再分，如“日”。"}},
    {"ch": "文字", "kw": "文字的性质与汉字的性质", "q": {"stem": "汉字与拼音文字相比，字形与意义联系较直接，属于____体系。", "type": "blank",
        "answer": "表意", "options": [],
        "explanation": "汉字是表意体系的文字，字形往往能体现意义，与拼音文字不同。"}},
    {"ch": "词汇", "kw": "单纯词与合成词", "q": {"stem": "“葡萄”是____词，因为它只含一个语素。", "type": "blank",
        "answer": "单纯", "options": [],
        "explanation": "“葡萄”是一个双音节语素，不可再分，是单纯词。"}},
    {"ch": "词汇", "kw": "同义词与反义词", "q": {"stem": "“胖”与“瘦”在意义上构成____关系。", "type": "blank",
        "answer": "反义", "options": [],
        "explanation": "“胖”“瘦”意义相反或相对，构成反义关系。"}},
    {"ch": "词汇", "kw": "词", "q": {"stem": "“桌子”由____个语素构成。", "type": "blank",
        "answer": "两", "options": [],
        "explanation": "“桌子”由词根“桌”和词缀“子”两个语素构成，是合成词。"}},
    {"ch": "词汇", "kw": "熟语", "q": {"stem": "“破釜沉舟”属于熟语中的____。", "type": "blank",
        "answer": "成语", "options": [],
        "explanation": "成语是长期习用、结构定型、意义完整的固定短语，“破釜沉舟”源于历史典故。"}},
    {"ch": "语法", "kw": "虚词", "q": {"stem": "“关于”“对于”属于____词。", "type": "blank",
        "answer": "介", "options": [],
        "explanation": "“关于”“对于”是介词，常与名词性成分组成介词短语。"}},
    {"ch": "语法", "kw": "句类", "q": {"stem": "“请把门关上！”从语气看属于____句。", "type": "blank",
        "answer": "祈使", "options": [],
        "explanation": "表示请求、命令、劝阻等语气的句子是祈使句。"}},
    {"ch": "语法", "kw": "复句", "q": {"stem": "“不是……而是……”连接的是____复句。", "type": "blank",
        "answer": "并列", "options": [],
        "explanation": "“不是……而是……”表示并列的两种情况，是并列复句。"}},
    {"ch": "语法", "kw": "语法的性质与语法单位", "q": {"stem": "语法的三大性质是抽象性、稳固性和____。", "type": "blank",
        "answer": "民族性", "options": [],
        "explanation": "语法具有抽象性、稳固性、民族性三大性质。"}},
    {"ch": "修辞", "kw": "借代", "q": {"stem": "借代中，借体与本体之间是____关系。", "type": "blank",
        "answer": "相关", "options": [],
        "explanation": "借代借与本体相关的事物代替本体，如用“红领巾”代少先队员；借喻则基于相似关系。"}},
    {"ch": "修辞", "kw": "其他辞格", "q": {"stem": "正话反说、用反义的话表达本意的辞格称为____。", "type": "blank",
        "answer": "反语", "options": [],
        "explanation": "反语是正话反说，如“你真聪明”（讽刺时），有讽刺、幽默的表达效果。"}},
    {"ch": "修辞", "kw": "比喻", "q": {"stem": "“共产党像太阳”中“共产党”是____，太阳是喻体。", "type": "blank",
        "answer": "本体", "options": [],
        "explanation": "比喻由本体、喻体、喻词构成，被比的事物是本体，用来打比方的是喻体。"}},
    {"ch": "标点符号", "kw": "句末点号：句号、问号、叹号", "q": {"stem": "“多美的景色啊！”句末应使用（　）", "type": "choice",
        "answer": "叹号", "options": ["叹号", "句号", "问号", "分号"],
        "explanation": "感叹句末尾用叹号，表达强烈的感情。"}},
    {"ch": "标点符号", "kw": "句内点号：逗号、顿号、分号、冒号", "q": {"stem": "分号主要用于____之间的停顿。", "type": "blank",
        "answer": "并列分句", "options": [],
        "explanation": "分号表示复句内并列分句之间的停顿，比逗号长、比句号短。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'第5批挂载 {n} 题')
