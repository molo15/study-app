# -*- coding: utf-8 -*-
"""现代汉语 人工设计扩充 第四批：各章核心补充"""
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
    {"ch": "语音", "kw": "元音与辅音", "q": {"stem": "辅音发音时，气流在口腔中____。", "type": "blank",
        "answer": "受到阻碍", "options": [],
        "explanation": "元音发音气流不受阻碍、声带振动；辅音发音气流在口腔中受到阻碍。"}},
    {"ch": "语音", "kw": "声调（调值与调类）", "q": {"stem": "普通话的四个调类是阴平、阳平、____和去声。", "type": "blank",
        "answer": "上声", "options": [],
        "explanation": "普通话四个调类为阴平（55）、阳平（35）、上声（214）、去声（51）。"}},
    {"ch": "语音", "kw": "拼写规则", "q": {"stem": "汉语拼音的声调符号一般标在韵母的____上。", "type": "blank",
        "answer": "韵腹", "options": [],
        "explanation": "声调符号标在韵腹（主要元音）上，如“妈”mā。"}},
    {"ch": "语音", "kw": "音节结构", "q": {"stem": "一个完整的普通话音节包括声母、韵头、韵腹、韵尾和____五部分。", "type": "blank",
        "answer": "声调", "options": [],
        "explanation": "普通话音节最多由声母、韵头、韵腹、韵尾、声调五部分构成。"}},
    {"ch": "语法", "kw": "词类的划分", "q": {"stem": "根据能否充当句法成分，可以把词分为实词和____两大类。", "type": "blank",
        "answer": "虚词", "options": [],
        "explanation": "实词能充当句法成分，虚词不能单独充当句法成分。"}},
    {"ch": "语法", "kw": "句子成分", "q": {"stem": "谓语是对____加以陈述的成分。", "type": "blank",
        "answer": "主语", "options": [],
        "explanation": "主谓结构中，主语是被陈述的对象，谓语对主语加以陈述。"}},
    {"ch": "语法", "kw": "特殊句式", "q": {"stem": "“台上坐着主席团”是____句。", "type": "blank",
        "answer": "存现", "options": [],
        "explanation": "“台上坐着主席团”表示存在，是存现句。"}},
    {"ch": "语法", "kw": "复句", "q": {"stem": "“因为……所以……”连接的复句属于____复句。", "type": "blank",
        "answer": "因果", "options": [],
        "explanation": "因果复句用“因为……所以”“既然……就”等关联词，说明因果关系。"}},
    {"ch": "语法", "kw": "句类", "q": {"stem": "根据语气，句子可分为陈述句、疑问句、祈使句和____四类。", "type": "blank",
        "answer": "感叹句", "options": [],
        "explanation": "句类按语气分陈述、疑问、祈使、感叹四类。"}},
    {"ch": "语法", "kw": "短语", "q": {"stem": "“调查研究”从结构看属于____短语。", "type": "blank",
        "answer": "联合", "options": [],
        "explanation": "“调查研究”两个并列成分地位平等，是联合短语。"}},
    {"ch": "语法", "kw": "特殊句式", "q": {"stem": "“他被老师批评了”属于（　）", "type": "choice",
        "answer": "被字句", "options": ["被字句", "把字句", "连动句", "兼语句"],
        "explanation": "用介词“被”引出施事的句子是被字句，表示被动意义。"}},
    {"ch": "词汇", "kw": "合成词的结构", "q": {"stem": "“地震”的构词方式是（　）", "type": "choice",
        "answer": "主谓式", "options": ["主谓式", "动宾式", "偏正式", "补充式"],
        "explanation": "“地震”是“地”（主语）加“震”（谓语），是主谓式合成词。"}},
    {"ch": "词汇", "kw": "熟语", "q": {"stem": "“三个臭皮匠，顶个诸葛亮”属于（　）", "type": "choice",
        "answer": "谚语", "options": ["谚语", "成语", "惯用语", "歇后语"],
        "explanation": "谚语是流传民间的通俗简练的格言，这里表示人多智慧大。"}},
    {"ch": "词汇", "kw": "词", "q": {"stem": "词是最小的能够____运用的语言单位。", "type": "blank",
        "answer": "独立", "options": [],
        "explanation": "词是最小的能够独立运用的音义结合体，是造句的基本单位。"}},
    {"ch": "标点符号", "kw": "句末点号：句号、问号、叹号", "q": {"stem": "表示疑问句末尾停顿的点号是（　）", "type": "choice",
        "answer": "问号", "options": ["问号", "句号", "叹号", "分号"],
        "explanation": "问号用于疑问句、反问句末尾，表示疑问语气。"}},
    {"ch": "标点符号", "kw": "句内点号：逗号、顿号、分号、冒号", "q": {"stem": "“同志们：”这里的冒号表示____。", "type": "blank",
        "answer": "提示下文", "options": [],
        "explanation": "冒号用在称呼语后提示下文，是冒号的主要用法之一。"}},
    {"ch": "标点符号", "kw": "标号（二）：着重号、连接号、间隔号、书名号、专名号", "q": {"stem": "标示书名、篇名、报刊名的标号是（　）", "type": "choice",
        "answer": "书名号", "options": ["书名号", "引号", "括号", "连接号"],
        "explanation": "书名号《》标示书名、篇名、报刊名等。"}},
    {"ch": "文字", "kw": "文字的性质与汉字的性质", "q": {"stem": "从记录语言的方式看，汉字属于____文字。", "type": "blank",
        "answer": "表意", "options": [],
        "explanation": "汉字属于表意体系的文字，字形与意义有较直接的联系。"}},
    {"ch": "文字", "kw": "汉字的形体演变", "q": {"stem": "汉字形体演变的大致顺序是甲骨文、金文、____、隶书、楷书。", "type": "blank",
        "answer": "篆书", "options": [],
        "explanation": "汉字形体演变顺序：甲骨文→金文→篆书→隶书→楷书，另有草书行书。"}},
    {"ch": "修辞", "kw": "借代", "q": {"stem": "“红领巾们来了”中“红领巾”借指少先队员，使用的辞格是（　）", "type": "choice",
        "answer": "借代", "options": ["借代", "借喻", "比拟", "双关"],
        "explanation": "用“红领巾”这一标志代指少先队员，是借代；借喻是本体喻体都有相似关系。"}},
    {"ch": "绪论", "kw": "汉语方言与七大方言区", "q": {"stem": "汉语七大方言区中分布最广、使用人口最多的是____方言。", "type": "blank",
        "answer": "北方", "options": [],
        "explanation": "北方方言是七大方言区中分布最广、使用人口最多的方言，是普通话的基础方言。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'第四批挂载 {n} 题')
