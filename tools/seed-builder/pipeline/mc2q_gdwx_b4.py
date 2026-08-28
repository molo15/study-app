# -*- coding: utf-8 -*-
"""古代文学史 名词解释→基础题 第四批（第一部分考研真题精选中的古代名词解释）"""
import io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json'
KP = json.load(open(P, encoding='utf-8'))

def norm(s):
    return re.sub(r'[（）()。，、；：""“”\'  ]', '', s)

def kp_text(k):
    return k['name'] + (k.get('summary') or '') + ''.join(q['stem'] for q in k.get('basicQuestions', []))

def mount(chapter, q, match_kw):
    kps = [k for k in KP['knowledge'] if k['chapter'] == chapter]
    best = None
    for k in kps:
        if match_kw and match_kw in kp_text(k):
            best = k
            break
    if best is None:
        for k in kps:
            if '真题补充' in k['name']:
                best = k
                break
    if best is None:
        best = {"id": "k_zhen_gdwx_" + chapter, "name": chapter + "（真题补充）",
                "parent": "root", "chapter": chapter, "hot": False,
                "summary": "考研真题补充知识点，覆盖该章重要考点。", "basicQuestions": []}
        KP['knowledge'].append(best)
    for e in best.get('basicQuestions', []):
        if norm(e['stem']) == norm(q['stem']):
            return
    best['basicQuestions'].append(q)

Q = [
    {"ch": "隋唐五代文学", "mk": "杜甫", "q": {"stem": "“沉郁顿挫”是对____诗歌风格的集中概括。", "type": "blank",
        "answer": "杜甫", "explanation": "沉郁顿挫是对杜甫诗歌风格特征的集中概括，指感情深沉浓郁、顿挫有致。",
        "options": []}},
    {"ch": "宋代文学", "mk": "豪放", "q": {"stem": "“以诗为词”是宋人对____词艺术特色的概括。", "type": "blank",
        "answer": "苏轼", "explanation": "“以诗为词”是宋人对苏轼词艺术特色的概括，他以诗法入词，扩大了词的表现功能。",
        "options": []}},
    {"ch": "秦汉文学", "mk": "史记", "q": {"stem": "下列不属于《史记》五种体例的是（　）", "type": "choice",
        "answer": "辞赋", "explanation": "《史记》五种体例为本纪、表、书、世家、列传；辞赋是汉代文体，不在其列。",
        "options": ["辞赋", "本纪", "表", "列传"]}},
    {"ch": "隋唐五代文学", "mk": "韩孟", "q": {"stem": "“大历诗风”是指唐代大历至贞元年间活跃于诗坛上的____的诗风。", "type": "blank",
        "answer": "大历十才子", "explanation": "大历诗风指大历至贞元年间诗坛风气，以“大历十才子”等为代表，风格清雅平淡。",
        "options": []}},
    {"ch": "明代文学", "mk": "诗文流派", "q": {"stem": "明代后期的“公安派”以“三袁”为代表，核心主张是（　）", "type": "choice",
        "answer": "独抒性灵，不拘格套", "explanation": "公安派以袁宗道、袁宏道、袁中道“三袁”为代表，主张“独抒性灵，不拘格套”。",
        "options": ["独抒性灵，不拘格套", "文必秦汉，诗必盛唐", "格调至上，温柔敦厚", "宗经征圣，载道明理"]}},
    {"ch": "清代文学", "mk": "桐城", "q": {"stem": "清代延续最长、影响最大的散文流派“桐城派”的代表人物是____、刘大櫆、姚鼐。", "type": "blank",
        "answer": "方苞", "explanation": "桐城派是清代延续最长、影响最大的散文流派，代表人物为方苞、刘大櫆、姚鼐。",
        "options": []}},
    {"ch": "秦汉文学", "mk": "真题补充", "q": {"stem": "东汉历史散文《吴越春秋》主要记述的是（　）", "type": "choice",
        "answer": "吴越两国的兴亡历史", "explanation": "《吴越春秋》是成书于东汉的历史散文，主要记述吴越两国的兴亡历史。",
        "options": ["吴越两国的兴亡历史", "西汉的建立过程", "战国策士的游说活动", "春秋诸侯的争霸战争"]}},
    {"ch": "魏晋南北朝文学", "mk": "正始", "q": {"stem": "“正始之音”指正始时期诗人的风尚言论，其代表人物是____、阮籍等。", "type": "blank",
        "answer": "嵇康", "explanation": "正始之音指正始时期诗人的风尚言论，代表诗人为嵇康、阮籍等竹林名士。",
        "options": []}},
    {"ch": "宋代文学", "mk": "辛弃疾", "q": {"stem": "“以文为词”是____倡导的词学观点。", "type": "blank",
        "answer": "辛弃疾", "explanation": "“以文为词”是辛弃疾倡导的词学观点，他把散文手法融入词中，扩大了词的表现力。",
        "options": []}},
    {"ch": "清代文学", "mk": "聊斋", "q": {"stem": "鲁迅评价《聊斋志异》的艺术特点是“用传奇法而以____”。", "type": "blank",
        "answer": "志怪", "explanation": "“用传奇法而以志怪”是鲁迅对《聊斋志异》艺术特点的概括。",
        "options": []}},
    {"ch": "秦汉文学", "mk": "乐府", "q": {"stem": "掌管音乐的官署“乐府”最早设立于____时期。", "type": "blank",
        "answer": "汉武帝", "explanation": "乐府本是掌管音乐的机关名称，最早设立于汉武帝时期，负责采集民间歌谣。",
        "options": []}},
    {"ch": "近代文学", "mk": "梁启超", "q": {"stem": "“诗界革命”是近代文学史上的诗歌改良运动，其代表诗人是____。", "type": "blank",
        "answer": "黄遵宪", "explanation": "诗界革命是近代诗歌改良运动，黄遵宪是其代表诗人，主张“我手写吾口”。",
        "options": []}},
    {"ch": "先秦文学", "mk": "楚辞", "q": {"stem": "“庄骚”是《庄子》和《____》的合称。", "type": "blank",
        "answer": "楚辞", "explanation": "庄骚是《庄子》与《楚辞》的合称，语出唐代韩愈之文。",
        "options": []}},
    {"ch": "隋唐五代文学", "mk": "花间", "q": {"stem": "敦煌石室中发现的曲子词总集《____》是现存最早的民间词集。", "type": "blank",
        "answer": "云谣集杂曲子", "explanation": "《云谣集杂曲子》是敦煌石室所发现的曲子词总集，对研究词的起源有重要价值。",
        "options": []}},
    {"ch": "明代文学", "mk": "诗文流派", "q": {"stem": "明代嘉靖年间的散文流派“唐宋派”代表人物有王慎中、唐顺之和____。", "type": "blank",
        "answer": "归有光", "explanation": "唐宋派是明代嘉靖年间散文流派，代表人物王慎中、唐顺之、归有光、茅坤。",
        "options": []}},
    {"ch": "清代文学", "mk": "聊斋", "q": {"stem": "笔记小说集《阅微草堂笔记》的作者是（　）", "type": "choice",
        "answer": "纪昀", "explanation": "《阅微草堂笔记》是清代学者纪昀（纪晓岚）所著的笔记小说集。",
        "options": ["纪昀", "蒲松龄", "袁枚", "李渔"]}},
    {"ch": "先秦文学", "mk": "尚书", "q": {"stem": "我国第一部历史散文集是《____》。", "type": "blank",
        "answer": "尚书", "explanation": "《尚书》是我国第一部历史散文集，包括《虞书》《夏书》《商书》《周书》。",
        "options": []}},
    {"ch": "元代文学", "mk": "散曲", "q": {"stem": "散曲中的“套数”是由宋、金时期的____发展而来的连贯成套的曲子。", "type": "choice",
        "answer": "诸宫调", "explanation": "套数是连贯成套的曲子，由宋金时期的诸宫调发展而来，又称散套。",
        "options": ["诸宫调", "变文", "话本", "杂剧"]}},
    {"ch": "魏晋南北朝文学", "mk": "宫体", "q": {"stem": "“宫体诗”是指以南朝____为太子时的东宫为中心的诗歌。", "type": "choice",
        "answer": "梁简文帝（萧纲）", "explanation": "宫体诗以南朝梁简文帝萧纲为太子时的东宫为中心，风格轻艳。",
        "options": ["梁简文帝（萧纲）", "梁武帝（萧衍）", "陈后主（陈叔宝）", "宋文帝（刘义隆）"]}},
    {"ch": "隋唐五代文学", "mk": "变文", "q": {"stem": "唐传奇是在前代____和史传文学的基础上发展起来的文言短篇小说。", "type": "choice",
        "answer": "志怪小说", "explanation": "唐传奇在前代志怪小说和史传文学的基础上发展而来，标志着文言短篇小说的成熟。",
        "options": ["志怪小说", "话本", "变文", "杂剧"]}},
]

n = 0
for it in Q:
    mount(it['ch'], it['q'], it['mk'])
    n += 1

json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('第四批挂载', n, '题')
