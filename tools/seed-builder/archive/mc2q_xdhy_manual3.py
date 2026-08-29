# -*- coding: utf-8 -*-
"""现代汉语 人工设计扩充 第三批：修辞 + 标点 + 语法薄弱点"""
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
    # ===== 修辞 =====
    {"ch": "修辞", "kw": "其他辞格", "q": {"stem": "把用于甲事物的词语顺势拈来用于乙事物的辞格称为____。", "type": "blank",
        "answer": "拈连", "options": [],
        "explanation": "拈连是把适用于甲事物的词语顺势移用到乙事物，如“线缝住了嘴，也缝住了歌声”。"}},
    {"ch": "修辞", "kw": "其他辞格", "q": {"stem": "仿照现成词语临时创造新词的辞格称为____。", "type": "blank",
        "answer": "仿词", "options": [],
        "explanation": "仿词是仿照现成词语临时造词，如仿“公理”造“婆理”。"}},
    {"ch": "修辞", "kw": "其他辞格", "q": {"stem": "前后词语回环往复、形式颠倒的辞格称为____。", "type": "blank",
        "answer": "回环", "options": [],
        "explanation": "回环是前后语句词语回环往复，如“人人为我，我为人人”。"}},
    {"ch": "修辞", "kw": "反复与顶真", "q": {"stem": "后一句的开头重复前一句结尾的词语、上递下接的辞格称为____。", "type": "blank",
        "answer": "顶真", "options": [],
        "explanation": "顶真又称顶针，上句结尾的词语作下句的开头，如“竹叶烧了，还有竹枝”。"}},
    {"ch": "修辞", "kw": "反复与顶真", "q": {"stem": "“盼望着，盼望着，东风来了，春天的脚步近了”使用的辞格是（　）", "type": "choice",
        "answer": "反复", "options": ["反复", "排比", "顶真", "夸张"],
        "explanation": "“盼望着”连续出现是反复，用以突出强调急切的心情。"}},
    {"ch": "修辞", "kw": "词语的锤炼", "q": {"stem": "词语的锤炼一般从____和声音两方面入手。", "type": "blank",
        "answer": "意义", "options": [],
        "explanation": "词语锤炼从意义和声音两方面入手，意义要准确鲜明，声音要和谐动听。"}},
    {"ch": "修辞", "kw": "通感", "q": {"stem": "把视觉、听觉、嗅觉等不同感觉沟通起来的辞格称为____。", "type": "blank",
        "answer": "通感", "options": [],
        "explanation": "通感是感觉的移借，如“歌声甜润”，把听觉与味觉沟通起来。"}},
    {"ch": "修辞", "kw": "双关", "q": {"stem": "“东边日出西边雨，道是无晴却有晴”中“晴”谐“情”，使用的辞格是（　）", "type": "choice",
        "answer": "谐音双关", "options": ["谐音双关", "语义双关", "借代", "反语"],
        "explanation": "“晴”谐音“情”，一语双关，是谐音双关。"}},
    {"ch": "修辞", "kw": "反问与设问", "q": {"stem": "无疑而问、自问自答以引起注意的辞格称为____。", "type": "blank",
        "answer": "设问", "options": [],
        "explanation": "设问是自问自答，反问是答案在问中；设问重在引起注意，反问重在加强语气。"}},
    {"ch": "修辞", "kw": "句式的选择", "q": {"stem": "从结构长短看，句子可以分为长句和____。", "type": "blank",
        "answer": "短句", "options": [],
        "explanation": "长句结构复杂、表意严密，短句结构简单、明快有力，二者各有表达效果。"}},
    {"ch": "修辞", "kw": "夸张", "q": {"stem": "故意言过其实、对事物进行扩大或缩小描写的辞格称为____。", "type": "blank",
        "answer": "夸张", "options": [],
        "explanation": "夸张分扩大夸张、缩小夸张、超前夸张，如“白发三千丈”。"}},
    {"ch": "修辞", "kw": "对偶与对比", "q": {"stem": "“两个黄鹂鸣翠柳，一行白鹭上青天”使用的辞格是（　）", "type": "choice",
        "answer": "对偶", "options": ["对偶", "对比", "排比", "比喻"],
        "explanation": "上下两句结构相同、字数相等、意义相关，是对偶。"}},
    {"ch": "修辞", "kw": "排比", "q": {"stem": "排比是把____个或三个以上结构相同或相似、语气一致的语句排列起来。", "type": "blank",
        "answer": "三", "options": [],
        "explanation": "排比一般由三个或三个以上结构相同或相似、语气一致的语句构成。"}},
    {"ch": "修辞", "kw": "比拟", "q": {"stem": "“太阳公公露出了笑脸”使用的辞格是（　）", "type": "choice",
        "answer": "拟人", "options": ["拟人", "拟物", "比喻", "借代"],
        "explanation": "把太阳当成人来写，赋予它以人的情态，是拟人。"}},
    # ===== 标点 =====
    {"ch": "标点符号", "kw": "标点符号的性质与分类", "q": {"stem": "标点符号分为____和标号两大类。", "type": "blank",
        "answer": "点号", "options": [],
        "explanation": "点号表示停顿和语气，标号标示词语的性质和作用。"}},
    {"ch": "标点符号", "kw": "易混淆标点的辨析", "q": {"stem": "表示句子内部并列词语之间的停顿应使用（　）", "type": "choice",
        "answer": "顿号", "options": ["顿号", "逗号", "分号", "冒号"],
        "explanation": "顿号表示并列词语之间的停顿，逗号表示句子内部一般性停顿。"}},
    # ===== 语法 =====
    {"ch": "语法", "kw": "虚词", "q": {"stem": "介词、连词、助词、语气词等属于____。", "type": "blank",
        "answer": "虚词", "options": [],
        "explanation": "虚词不能单独充当句法成分，包括介词、连词、助词、语气词、叹词、拟声词。"}},
    {"ch": "语法", "kw": "语法的性质与语法单位", "q": {"stem": "语法单位包括语素、词、____、句子四级。", "type": "blank",
        "answer": "短语", "options": [],
        "explanation": "语法单位是语素、词、短语、句子四级，由小到大。"}},
    {"ch": "语法", "kw": "语法的性质与语法单位", "q": {"stem": "最小的能够独立运用的语言单位是（　）", "type": "choice",
        "answer": "词", "options": ["词", "语素", "短语", "句子"],
        "explanation": "词是最小的能够独立运用的音义结合体；语素是最小的音义结合体但不能独立运用。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'第三批挂载 {n} 题')
