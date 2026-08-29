# -*- coding: utf-8 -*-
"""当代文学史 扩充第六批：继续扩充"""
import io, sys, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'D:\study_app\tools\seed-builder\out\knowledge\中国当代文学史.knowledge.json'
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
        best = {"id": "k_zhen_ddwx_" + chapter, "name": chapter + "（真题补充）", "parent": "root",
                "chapter": chapter, "hot": False, "summary": "考研真题补充知识点。", "basicQuestions": []}
        KP['knowledge'].append(best)
    for e in best.get('basicQuestions', []):
        if norm(e['stem']) == norm(q['stem']): return False
    best['basicQuestions'].append(q); return True

Q = [
    {"ch": "小说（80年代）", "kw": "余华的小说创作", "q": {"stem": "余华的先锋小说代表作是《____》。", "type": "blank",
        "answer": "现实一种", "options": [],
        "explanation": "《现实一种》《河边的错误》等是余华先锋时期的代表作。"}},
    {"ch": "小说（80年代）", "kw": "余华的小说创作", "q": {"stem": "《许三观卖血记》写____为养家屡次卖血。", "type": "blank",
        "answer": "许三观", "options": [],
        "explanation": "《许三观卖血记》写许三观以卖血支撑家庭的一生。"}},
    {"ch": "小说（80年代）", "kw": "王蒙的意识流小说", "q": {"stem": "王蒙《组织部来了个年轻人》的主人公是____。", "type": "blank",
        "answer": "林震", "options": [],
        "explanation": "林震是《组织部来了个年轻人》中的青年干部。"}},
    {"ch": "小说（80年代）", "kw": "陆文夫的小说", "q": {"stem": "陆文夫《小巷深处》写____（苏州）巷陌人生。", "type": "blank",
        "answer": "苏州", "options": [],
        "explanation": "陆文夫多写苏州小巷人物，被誉为“小巷文学”。"}},
    {"ch": "小说（80年代）", "kw": "高晓声的乡土小说", "q": {"stem": "《陈奂生上城》中的陈奂生是____形象。", "type": "blank",
        "answer": "农民", "options": [],
        "explanation": "陈奂生是高晓声塑造的改革开放初期农民形象。"}},
    {"ch": "小说（90年代）", "kw": "新现实主义小说", "q": {"stem": "新现实主义小说又称“____”小说。", "type": "blank",
        "answer": "现实主义冲击波", "options": [],
        "explanation": "90年代谈歌等的新现实主义小说被称为“现实主义冲击波”。"}},
    {"ch": "小说（90年代）", "kw": "新生代小说", "q": {"stem": "新生代小说多写____（日常/边缘）经验。", "type": "blank",
        "answer": "日常琐碎与边缘", "options": [],
        "explanation": "新生代小说回避宏大叙事，聚焦日常与边缘经验。"}},
    {"ch": "小说（90年代）", "kw": "王小波的小说", "q": {"stem": "王小波的“时代三部曲”是《黄金时代》《白银时代》和《____》。", "type": "blank",
        "answer": "青铜时代", "options": [],
        "explanation": "“时代三部曲”含《黄金时代》《白银时代》《青铜时代》。"}},
    {"ch": "小说（90年代）", "kw": "贾平凹的小说", "q": {"stem": "贾平凹《废都》写____（西安）文化人生活。", "type": "blank",
        "answer": "西安", "options": [],
        "explanation": "《废都》以西安（西京）为背景，写文化人的精神困境。"}},
    {"ch": "小说（90年代）", "kw": "王安忆《小鲍庄》", "q": {"stem": "王安忆《小鲍庄》属于____（寻根）文学。", "type": "blank",
        "answer": "寻根", "options": [],
        "explanation": "《小鲍庄》写仁义庄的伦理道德，是寻根文学代表作。"}},
    {"ch": "新诗（50-60年代）", "kw": "政治抒情诗", "q": {"stem": "政治抒情诗的特点是____（抒情）与政治结合。", "type": "blank",
        "answer": "政治激情（豪迈抒情）", "options": [],
        "explanation": "政治抒情诗以澎湃的抒情表达政治激情，如郭小川、贺敬之之作。"}},
    {"ch": "新诗（50-60年代）", "kw": "郭小川的诗歌创作", "q": {"stem": "郭小川后期代表作有《____》（甘蔗林—青纱帐）。", "type": "blank",
        "answer": "甘蔗林—青纱帐", "options": [],
        "explanation": "《甘蔗林—青纱帐》是郭小川后期的代表作。"}},
    {"ch": "新诗（80-90年代）", "kw": "“归来”诗人", "q": {"stem": "艾青新时期代表作是《____》（光的赞歌）。", "type": "blank",
        "answer": "光的赞歌", "options": [],
        "explanation": "艾青《光的赞歌》是其“归来”后的代表作。"}},
    {"ch": "新诗（80-90年代）", "kw": "顾城的诗歌", "q": {"stem": "“黑夜给了我黑色的眼睛”出自顾城《____》。", "type": "blank",
        "answer": "一代人", "options": [],
        "explanation": "《一代人》是顾城代表作，“黑夜给了我黑色的眼睛，我却用它寻找光明”。"}},
    {"ch": "新诗（80-90年代）", "kw": "北岛的诗歌", "q": {"stem": "北岛是“____”（今天派）诗群代表。", "type": "blank",
        "answer": "今天", "options": [],
        "explanation": "北岛是《今天》杂志核心人物，朦胧诗（今天派）代表。"}},
    {"ch": "台港文学", "kw": "白先勇的小说", "q": {"stem": "白先勇小说多写____（今昔/怀旧）之感。", "type": "blank",
        "answer": "今昔对照与怀旧", "options": [],
        "explanation": "白先勇擅写繁华与没落的对照，寄寓今昔之感。"}},
    {"ch": "台港文学", "kw": "余光中的散文", "q": {"stem": "余光中散文善于运用____（古典）语言。", "type": "blank",
        "answer": "古典（文言）", "options": [],
        "explanation": "余光中散文熔古典与现代于一炉，语言典雅。"}},
    {"ch": "台港文学", "kw": "金庸小说的文化底蕴与现代意识", "q": {"stem": "金庸小说《天龙八部》中的主角之一是____。", "type": "blank",
        "answer": "乔峰（萧峰）", "options": [],
        "explanation": "《天龙八部》以乔峰、段誉、虚竹为主线。"}},
    {"ch": "2000-2016年文学", "kw": "莫言的魔幻现实主义", "q": {"stem": "莫言《蛙》关注____（生育/计划生育）主题。", "type": "blank",
        "answer": "生育（计划生育）", "options": [],
        "explanation": "《蛙》以乡村妇产科医生“姑姑”的视角写计划生育史。"}},
    {"ch": "2000-2016年文学", "kw": "莫言《红高粱》", "q": {"stem": "《红高粱》中“我奶奶”是____。", "type": "blank",
        "answer": "戴凤莲（九儿）", "options": [],
        "explanation": "“我奶奶”戴凤莲（九儿）是《红高粱》中敢爱敢恨的女性。"}},
    {"ch": "2000-2016年文学", "kw": "打工文学与底层写作", "q": {"stem": "打工文学写的是____（进城务工）者的生活。", "type": "blank",
        "answer": "进城务工（底层）", "options": [],
        "explanation": "打工文学以进城务工者的生存为题材。"}},
    {"ch": "散文（80-90年代）", "kw": "悲悼散文", "q": {"stem": "巴金《怀念萧珊》是____（悲悼）散文。", "type": "blank",
        "answer": "悲悼（悼亡）", "options": [],
        "explanation": "《怀念萧珊》悼念亡妻，是悲悼散文名篇。"}},
    {"ch": "散文（80-90年代）", "kw": "女性散文", "q": {"stem": "女性散文以____（女性）视角书写经验。", "type": "blank",
        "answer": "女性", "options": [],
        "explanation": "女性散文以女性视角写性别经验与心灵世界。"}},
    {"ch": "散文（80-90年代）", "kw": "跨文体散文", "q": {"stem": "跨文体散文融合小说、____、评论等因素。", "type": "blank",
        "answer": "诗歌", "options": [],
        "explanation": "跨文体散文打破文体界限，融合小说、诗歌、评论等手法。"}},
    {"ch": "戏剧（80-90年代）", "kw": "戏剧观讨论与探索戏剧", "q": {"stem": "80年代探索戏剧借鉴了____（西方现代派）手法。", "type": "blank",
        "answer": "西方现代派（象征、荒诞）", "options": [],
        "explanation": "探索戏剧借鉴西方象征主义、荒诞派等现代手法革新舞台。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "潜在写作（地下文学）", "q": {"stem": "“文革”地下文学代表有“____”（白洋淀）诗群。", "type": "blank",
        "answer": "白洋淀", "options": [],
        "explanation": "白洋淀诗群是“文革”时期重要的地下诗歌群体。"}},
    {"ch": "文学思潮（80-90年代）", "kw": "文学主体性讨论", "q": {"stem": "文学主体性讨论强调作家与文学的____（主体）地位。", "type": "blank",
        "answer": "主体", "options": [],
        "explanation": "文学主体性讨论主张尊重文学创作的主体性，反对机械反映论。"}},
    {"ch": "文学思潮（80-90年代）", "kw": "“方法年”“观念年”与“三论”", "q": {"stem": "80年代文学批评的“方法年”引入了____（新方法）。", "type": "blank",
        "answer": "系统论、信息论等新方法", "options": [],
        "explanation": "“方法年”把系统论、信息论等自然科学方法引入文学批评。"}},
    {"ch": "戏剧散文（50-60年代）", "kw": "秦牧的散文", "q": {"stem": "秦牧散文《土地》是____（抒情）散文名篇。", "type": "blank",
        "answer": "抒情（咏物）", "options": [],
        "explanation": "《土地》借土地抒爱国之情，是秦牧散文名篇。"}},
    {"ch": "戏剧散文（50-60年代）", "kw": "刘白羽的散文", "q": {"stem": "刘白羽散文风格____（雄浑壮阔）。", "type": "blank",
        "answer": "雄浑壮阔", "options": [],
        "explanation": "刘白羽散文以雄浑壮阔的气势著称，如《长江三日》。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'当代第六批挂载 {n} 题')
