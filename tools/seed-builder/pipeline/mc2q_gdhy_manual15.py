# -*- coding: utf-8 -*-
"""古代汉语 扩充第十五批：收官"""
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
    {"ch": "词汇", "kw": "词的本义", "q": {"stem": "“发”的本义是____。", "type": "blank",
        "answer": "放箭（发射）", "options": [],
        "explanation": "“发”本义为把箭射出去，引申为出发、发生。"}},
    {"ch": "词汇", "kw": "词义的扩大、缩小、转移", "q": {"stem": "“金”古义指____（金属），今义多指黄金。", "type": "blank",
        "answer": "金属（总称）", "options": [],
        "explanation": "“金”古义泛指金属（“金就砺则利”），今义缩小为黄金。"}},
    {"ch": "词汇", "kw": "同义词辨析", "q": {"stem": "“亡”与“逃”，“亡”古义常指____。", "type": "blank",
        "answer": "逃跑（出奔）", "options": [],
        "explanation": "“亡”古义为逃跑、出走（“今亡亦死”），后指死亡。"}},
    {"ch": "语法（上）", "kw": "副词", "q": {"stem": "“窃为大王不取也”中“窃”是表示____的副词（谦敬）。", "type": "blank",
        "answer": "谦敬（私下）", "options": [],
        "explanation": "“窃”作表谦副词，意为“私下里”。"}},
    {"ch": "语法（上）", "kw": "语气词、叹词、助词", "q": {"stem": "“此中人语云：‘不足为外人道也。’”中“也”表____语气。", "type": "blank",
        "answer": "肯定（陈述）", "options": [],
        "explanation": "“也”表陈述、肯定的语气。"}},
    {"ch": "语法（下）", "kw": "使动用法", "q": {"stem": "“诸侯恐惧，会盟而谋弱秦”中“弱”是____用法。", "type": "blank",
        "answer": "使动", "options": [],
        "explanation": "“弱秦”即使秦弱，形容词使动用法。"}},
    {"ch": "语法（下）", "kw": "意动用法", "q": {"stem": "“粪土当年万户侯”中“粪土”是____用法。", "type": "blank",
        "answer": "意动", "options": [],
        "explanation": "“粪土当年万户侯”即以万户侯为粪土，名词意动用法。"}},
    {"ch": "文字（上）", "kw": "六书说", "q": {"stem": "六书概念最早完整见于《____》。", "type": "blank",
        "answer": "说文解字", "options": [],
        "explanation": "许慎《说文解字·叙》最早系统说明六书。"}},
    {"ch": "文字（上）", "kw": "形声", "q": {"stem": "“期”字中表音的“其”是____旁。", "type": "blank",
        "answer": "声", "options": [],
        "explanation": "“期”从月其声，“其”是声旁。"}},
    {"ch": "文字（下）", "kw": "异体字", "q": {"stem": "“睹”与“覩”是____字。", "type": "blank",
        "answer": "异体", "options": [],
        "explanation": "“睹”“覩”音义全同而形体不同，是异体字。"}},
    {"ch": "音韵", "kw": "阴声韵、阳声韵、入声韵", "q": {"stem": "“之、鱼、侯”等以元音收尾的韵是____声韵。", "type": "blank",
        "answer": "阴", "options": [],
        "explanation": "以元音收尾的韵是阴声韵。"}},
    {"ch": "音韵", "kw": "《切韵》《广韵》与中古音", "q": {"stem": "《切韵》成书于____（朝代）。", "type": "blank",
        "answer": "隋", "options": [],
        "explanation": "《切韵》为隋代陆法言等所撰。"}},
    {"ch": "训诂", "kw": "古注类型（一）", "q": {"stem": "“注”与“传”相比，“注”更侧重____（解词释句）。", "type": "blank",
        "answer": "解词释句", "options": [],
        "explanation": "“传”重在传述经义，“注”重在解释词句。"}},
    {"ch": "修辞", "kw": "起兴与比喻", "q": {"stem": "“桃之夭夭，灼灼其华”在《桃夭》中起____作用。", "type": "blank",
        "answer": "起兴", "options": [],
        "explanation": "以桃花起兴，引出对女子的赞美。"}},
    {"ch": "古书的文体", "kw": "论辩", "q": {"stem": "《孟子》中“王顾左右而言他”的对话属于____文体（语录体）。", "type": "blank",
        "answer": "论辩（语录）", "options": [],
        "explanation": "先秦诸子散文多语录体，记录论辩对话。"}},
    {"ch": "古书的标点", "kw": "句读与标点符号的异同", "q": {"stem": "与古书句读相比，现代标点能更精细地表示____（语气/句类）。", "type": "blank",
        "answer": "语气和句类", "options": [],
        "explanation": "现代标点可标示疑问、感叹等语气，古书句读不能。"}},
    {"ch": "诗词格律", "kw": "近体诗的押韵", "q": {"stem": "近体诗一般押____（平）声韵且一韵到底。", "type": "blank",
        "answer": "平", "options": [],
        "explanation": "近体诗押平声韵，一韵到底，不许换韵。"}},
    {"ch": "工具书简介", "kw": "类书", "q": {"stem": "《艺文类聚》属于____书。", "type": "blank",
        "answer": "类", "options": [],
        "explanation": "《艺文类聚》按类编纂，是类书。"}},
    {"ch": "工具书简介", "kw": "词典与《辞源》《辞海》《汉语大词典》", "q": {"stem": "《汉语大词典》共收词约____（37万）条。", "type": "blank",
        "answer": "37万", "options": [],
        "explanation": "《汉语大词典》是我国规模最大的汉语词典之一，收词37万余条。"}},
    {"ch": "语法（下）", "kw": "判断句", "q": {"stem": "“是天时不如地利也”中“是”作____。", "type": "blank",
        "answer": "主语", "options": [],
        "explanation": "“是”在此为指示代词作主语，意为“这”。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'古代汉语第十五批挂载 {n} 题')
