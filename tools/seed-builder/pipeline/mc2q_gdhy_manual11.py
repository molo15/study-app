# -*- coding: utf-8 -*-
"""古代汉语 扩充第十一批：继续补充各章考点"""
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
    {"ch": "词汇", "kw": "词义感情色彩与轻重程度的变化", "q": {"stem": "“谤”在古汉语中常表示____。", "type": "blank",
        "answer": "议论批评（公开指责）", "options": [],
        "explanation": "“谤”古义为公开议论指责，今义偏重诽谤。"}},
    {"ch": "词汇", "kw": "词的本义", "q": {"stem": "“引”的本义是____。", "type": "blank",
        "answer": "开弓", "options": [],
        "explanation": "“引”本义为开弓（“君子引而不发”），引申为拉、引、引导。"}},
    {"ch": "词汇", "kw": "词的引申义与引申方式", "q": {"stem": "“发”由“放箭”引申为“出发、发生”，属于____引申。", "type": "blank",
        "answer": "相关", "options": [],
        "explanation": "“发”由放箭（弓发）相关引申为出发等义。"}},
    {"ch": "词汇", "kw": "单纯词", "q": {"stem": "“布衣”“妻子”在先秦汉语中通常是____个词。", "type": "blank",
        "answer": "两", "options": [],
        "explanation": "“布衣”指布做的衣服（代平民），“妻子”指妻和子，各是两个词。"}},
    {"ch": "词汇", "kw": "合成词", "q": {"stem": "“敬畏”由两个意义相近的语素构成，是____合成词。", "type": "blank",
        "answer": "并列（联合）", "options": [],
        "explanation": "“敬”“畏”义近并列，构成并列式合成词。"}},
    {"ch": "语法（上）", "kw": "代词", "q": {"stem": "“尔、汝、若”属于____人称代词。", "type": "blank",
        "answer": "第二", "options": [],
        "explanation": "“尔、汝、若、而、乃”是第二人称代词。"}},
    {"ch": "语法（上）", "kw": "副词", "q": {"stem": "“毋”“勿”常用于____语气。", "type": "blank",
        "answer": "禁止（不要）", "options": [],
        "explanation": "“毋、勿”表禁止、劝阻，意为“不要”。"}},
    {"ch": "语法（上）", "kw": "语气词、叹词、助词", "q": {"stem": "“子非三闾大夫与”中“与”表____语气。", "type": "blank",
        "answer": "疑问（测度）", "options": [],
        "explanation": "“与（欤）”表疑问或测度语气。"}},
    {"ch": "语法（上）", "kw": "介词与连词", "q": {"stem": "“以五月五日生”中“以”引介____。", "type": "blank",
        "answer": "时间", "options": [],
        "explanation": "“以”在此介引时间，意为“在”。"}},
    {"ch": "语法（上）", "kw": "语气词、叹词、助词", "q": {"stem": "“耳”是“而已”的____词。", "type": "blank",
        "answer": "合音（兼）", "options": [],
        "explanation": "“耳”合“而已”二音，兼有限止语气。"}},
    {"ch": "语法（下）", "kw": "判断句", "q": {"stem": "“南阳刘子骥，高尚士也”是____句。", "type": "blank",
        "answer": "判断", "options": [],
        "explanation": "“……，……也”是判断句格式。"}},
    {"ch": "语法（下）", "kw": "使动用法", "q": {"stem": "“齐威王欲将孙膑”中“将”是____用法。", "type": "blank",
        "answer": "使动", "options": [],
        "explanation": "“将孙膑”即使孙膑为将，是使动用法。"}},
    {"ch": "语法（下）", "kw": "意动用法", "q": {"stem": "“吾从而师之”中“师”是____用法。", "type": "blank",
        "answer": "意动", "options": [],
        "explanation": "“师之”即以他为师，名词意动用法。"}},
    {"ch": "语法（下）", "kw": "名词作状语", "q": {"stem": "“乃丹书帛曰”中“丹”作状语，意为____。", "type": "blank",
        "answer": "用朱砂", "options": [],
        "explanation": "“丹”名词作状语，表示“用朱砂”。"}},
    {"ch": "语法（下）", "kw": "词序：宾语前置", "q": {"stem": "“唯弈秋之为听”中“弈秋”是____前置。", "type": "blank",
        "answer": "宾语", "options": [],
        "explanation": "用“之”复指，宾语“弈秋”前置。"}},
    {"ch": "文字（上）", "kw": "象形与指事", "q": {"stem": "“人、口、手”等描摹人体器官形状，都是____字。", "type": "blank",
        "answer": "象形", "options": [],
        "explanation": "象形字描摹事物的形状。"}},
    {"ch": "文字（上）", "kw": "象形与指事", "q": {"stem": "“朱”在“木”中加一点标示赤心，属于____字。", "type": "blank",
        "answer": "指事", "options": [],
        "explanation": "“朱”在木上加指示符号标示赤心木，是指事字。"}},
    {"ch": "文字（上）", "kw": "会意", "q": {"stem": "“信”由“人”“言”会意，表示____。", "type": "blank",
        "answer": "人言要真实可信", "options": [],
        "explanation": "“信”以“人言”会意为言语真实、诚信。"}},
    {"ch": "文字（上）", "kw": "形声", "q": {"stem": "“裹”字中表音的“果”是____旁。", "type": "blank",
        "answer": "声", "options": [],
        "explanation": "“裹”从衣果声，“果”是声旁。"}},
    {"ch": "文字（下）", "kw": "古今字", "q": {"stem": "“解”与“懈”是____字关系。", "type": "blank",
        "answer": "古今", "options": [],
        "explanation": "“解”古有“松懈”义，后作“懈”，是古今字。"}},
    {"ch": "音韵", "kw": "声类、字母与三十六字母", "q": {"stem": "三十六字母中“影”母属于____音。", "type": "blank",
        "answer": "喉", "options": [],
        "explanation": "“影晓匣喻”是喉音。"}},
    {"ch": "音韵", "kw": "《切韵》《广韵》与中古音", "q": {"stem": "《中原音韵》主要反映____（朝代）的语音系统。", "type": "blank",
        "answer": "元", "options": [],
        "explanation": "《中原音韵》是元代周德清所著，反映元代北方语音。"}},
    {"ch": "音韵", "kw": "上古音", "q": {"stem": "清代古音学的开创者是____（顾炎武）。", "type": "blank",
        "answer": "顾炎武", "options": [],
        "explanation": "顾炎武《音学五书》开创清代古音学研究。"}},
    {"ch": "训诂", "kw": "古注术语（一）", "q": {"stem": "“曰、为、谓之”常用于____。", "type": "blank",
        "answer": "辨析同义词或下定义", "options": [],
        "explanation": "这三个术语常用来辨析同义词、给事物下定义。"}},
    {"ch": "训诂", "kw": "重要训诂著作", "q": {"stem": "西汉扬雄所著《____》记载了汉代各地方言。", "type": "blank",
        "answer": "方言", "options": [],
        "explanation": "扬雄《方言》是第一部方言词汇专著。"}},
    {"ch": "修辞", "kw": "借代", "q": {"stem": "“干戈”代指____。", "type": "blank",
        "answer": "战争", "options": [],
        "explanation": "以兵器“干戈”代指战争，是借代。"}},
    {"ch": "修辞", "kw": "夸张与引用", "q": {"stem": "“《传》曰：‘刑不上大夫。’”属于____的修辞手法。", "type": "blank",
        "answer": "引用", "options": [],
        "explanation": "引用《传》文佐证观点，是引用。"}},
    {"ch": "古书的文体", "kw": "论辩", "q": {"stem": "“驳议”是臣下反驳他人主张的____文体。", "type": "blank",
        "answer": "论说（议论）", "options": [],
        "explanation": "驳议是论说文体，用于驳斥不当之议。"}},
    {"ch": "古书的文体", "kw": "序跋与书启", "q": {"stem": "《报任安书》属于____文体。", "type": "blank",
        "answer": "书启（书信）", "options": [],
        "explanation": "“书”是书信，属书启类文体。"}},
    {"ch": "古书的标点", "kw": "标点古文的基本方法", "q": {"stem": "标点古文，首先要____全文，理解大意。", "type": "blank",
        "answer": "通读", "options": [],
        "explanation": "标点古文的基本步骤：通读全文、理解文意、再断句加标点。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'古代汉语第十一批挂载 {n} 题')
