# -*- coding: utf-8 -*-
"""当代文学史 扩充第三批：思潮/戏剧/新诗50/小说50"""
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
    {"ch": "新诗（50-60年代）", "kw": "政治抒情诗", "q": {"stem": "政治抒情诗的代表诗人有郭小川和____。", "type": "blank",
        "answer": "贺敬之", "options": [],
        "explanation": "郭小川、贺敬之是政治抒情诗的代表诗人。"}},
    {"ch": "新诗（50-60年代）", "kw": "郭小川的诗歌创作", "q": {"stem": "郭小川的政治抒情诗代表作是《____》。", "type": "blank",
        "answer": "致青年公民", "options": [],
        "explanation": "郭小川《致青年公民》等以其昂扬的鼓点式语言著称。"}},
    {"ch": "新诗（50-60年代）", "kw": "贺敬之的诗歌创作", "q": {"stem": "贺敬之《回延安》采用____民歌形式。", "type": "blank",
        "answer": "信天游", "options": [],
        "explanation": "《回延安》以陕北信天游形式写对延安的深情。"}},
    {"ch": "新诗（50-60年代）", "kw": "“大我”与“小我”", "q": {"stem": "50年代诗歌主张以“____”（大我）消融个人抒情。", "type": "blank",
        "answer": "大我（集体）", "options": [],
        "explanation": "当时强调抒写集体、时代的“大我”，淡化个人的“小我”。"}},
    {"ch": "小说（50-60年代）", "kw": "山药蛋派", "q": {"stem": "“山药蛋派”的代表作家是____。", "type": "blank",
        "answer": "赵树理", "options": [],
        "explanation": "以赵树理为代表的“山药蛋派”写农村生活，语言通俗。"}},
    {"ch": "小说（50-60年代）", "kw": "赵树理《三里湾》", "q": {"stem": "赵树理《三里湾》反映____运动。", "type": "blank",
        "answer": "农业合作化", "options": [],
        "explanation": "《三里湾》写农业合作化中农村的变革与人物。"}},
    {"ch": "小说（50-60年代）", "kw": "革命历史小说的两种书写方式", "q": {"stem": "“三红一创”中的“三红”指《红岩》《红日》和《____》。", "type": "blank",
        "answer": "红旗谱", "options": [],
        "explanation": "“三红一创”即《红岩》《红日》《红旗谱》《创业史》，是十七年小说代表作。"}},
    {"ch": "小说（50-60年代）", "kw": "茹志鹃的小说创作", "q": {"stem": "茹志鹃《百合花》写____之间的深情。", "type": "blank",
        "answer": "军民（通讯员与媳妇）", "options": [],
        "explanation": "《百合花》以“我”、通讯员、新媳妇的关系写军民鱼水情。"}},
    {"ch": "小说（50-60年代）", "kw": "王蒙《组织部来了个年轻人》", "q": {"stem": "王蒙《组织部来了个年轻人》的主人公是____。", "type": "blank",
        "answer": "林震", "options": [],
        "explanation": "小说写青年林震在组织部的理想与困惑，是“干预生活”之作。"}},
    {"ch": "小说（50-60年代）", "kw": "“双百”调整期的小说创作", "q": {"stem": "“双百”调整期出现了“____”（干预生活）的创作。", "type": "blank",
        "answer": "干预生活", "options": [],
        "explanation": "“双百”期间出现“干预生活”“写真实”的小说，如《组织部来了个年轻人》。"}},
    {"ch": "小说（50-60年代）", "kw": "柳青《创业史》", "q": {"stem": "柳青《创业史》的主人公是____。", "type": "blank",
        "answer": "梁生宝", "options": [],
        "explanation": "《创业史》写梁生宝带领农民走合作化道路，是“一创”代表作。"}},
    {"ch": "小说（50-60年代）", "kw": "梁斌《红旗谱》", "q": {"stem": "梁斌《红旗谱》写____一家三代人的革命斗争。", "type": "blank",
        "answer": "朱老忠", "options": [],
        "explanation": "《红旗谱》写朱老忠一家三代与地主的斗争，是革命历史小说代表作。"}},
    {"ch": "小说（50-60年代）", "kw": "杨沫《青春之歌》", "q": {"stem": "杨沫《青春之歌》的女主人公是____。", "type": "blank",
        "answer": "林道静", "options": [],
        "explanation": "《青春之歌》写林道静从个人反抗走向革命道路的成长历程。"}},
    {"ch": "戏剧（80-90年代）", "kw": "戏剧观讨论与探索戏剧", "q": {"stem": "80年代戏剧观讨论围绕写实与____之争展开。", "type": "blank",
        "answer": "写意", "options": [],
        "explanation": "戏剧观讨论围绕“写实”与“写意”两种戏剧观展开，推动了探索戏剧。"}},
    {"ch": "戏剧（80-90年代）", "kw": "探索戏剧的艺术成果", "q": {"stem": "探索戏剧的代表作有高行健的《____》。", "type": "blank",
        "answer": "绝对信号", "options": [],
        "explanation": "《绝对信号》（与刘会远合作）是探索戏剧代表作，创新舞台时空。"}},
    {"ch": "戏剧（80-90年代）", "kw": "现实主义戏剧的坚守", "q": {"stem": "80年代坚守现实主义的剧作家有李龙云，其代表作是《____》。", "type": "blank",
        "answer": "小井胡同", "options": [],
        "explanation": "李龙云《小井胡同》以平民视角写北京胡同的历史变迁。"}},
    {"ch": "戏剧（80-90年代）", "kw": "沙叶新的戏剧", "q": {"stem": "沙叶新《陈毅市长》采用“____”式结构。", "type": "blank",
        "answer": "冰糖葫芦", "options": [],
        "explanation": "《陈毅市长》以十场戏写陈毅十件事，形如冰糖葫芦串。"}},
    {"ch": "戏剧（80-90年代）", "kw": "高行健的戏剧", "q": {"stem": "高行健《车站》借鉴了____（流派）戏剧手法。", "type": "blank",
        "answer": "荒诞派", "options": [],
        "explanation": "《车站》借鉴西方荒诞派戏剧手法，表现等待与荒诞。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "第一次全国文代会", "q": {"stem": "1949年第一次文代会确立了____的文艺方向。", "type": "blank",
        "answer": "文艺为人民服务（为工农兵服务）", "options": [],
        "explanation": "第一次文代会确定文艺为人民大众、首先为工农兵服务的方向。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "对电影《武训传》的批判", "q": {"stem": "1951年批判的电影是《____》。", "type": "blank",
        "answer": "武训传", "options": [],
        "explanation": "对电影《武训传》的批判，揭开了建国后文艺批判运动的序幕。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "对俞平伯《红楼梦》研究的批判", "q": {"stem": "1954年对俞平伯《____》研究展开批判。", "type": "blank",
        "answer": "红楼梦", "options": [],
        "explanation": "对俞平伯《红楼梦研究》的批判，引发红学界“新红学”讨论。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "“双百方针”及其对文艺的影响", "q": {"stem": "“双百方针”是百花齐放、____。", "type": "blank",
        "answer": "百家争鸣", "options": [],
        "explanation": "“双百方针”即百花齐放、百家争鸣，1956年提出。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "革命样板戏", "q": {"stem": "革命样板戏有《红灯记》《智取威虎山》《____》等。", "type": "blank",
        "answer": "沙家浜", "options": [],
        "explanation": "样板戏如《红灯记》《智取威虎山》《沙家浜》，是“文革”时期文艺规范的代表。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "潜在写作（地下文学）", "q": {"stem": "“文革”时期未公开发表的地下创作称为____。", "type": "blank",
        "answer": "潜在写作（地下文学）", "options": [],
        "explanation": "潜在写作指“文革”期间私下写作、当时未公开的作品。"}},
    {"ch": "文学思潮（80-90年代）", "kw": "“方法年”“观念年”与“三论”", "q": {"stem": "“三论”指系统论、控制论和____。", "type": "blank",
        "answer": "信息论", "options": [],
        "explanation": "80年代“方法论热”中的“三论”是系统论、控制论、信息论。"}},
    {"ch": "文学思潮（80-90年代）", "kw": "文学主体性讨论", "q": {"stem": "文学主体性讨论的代表文章出自____（刘再复）。", "type": "blank",
        "answer": "刘再复", "options": [],
        "explanation": "刘再复《论文学的主体性》引发80年代文学主体性讨论。"}},
    {"ch": "文学思潮（80-90年代）", "kw": "李泽厚《启蒙与救亡的双重变奏》", "q": {"stem": "李泽厚提出中国近代“____与救亡的双重变奏”。", "type": "blank",
        "answer": "启蒙", "options": [],
        "explanation": "李泽厚认为中国近现代史是启蒙与救亡双重变奏的历史。"}},
    {"ch": "文学思潮（80-90年代）", "kw": "“重写文学史”", "q": {"stem": "“重写文学史”由陈思和、____等人倡导。", "type": "blank",
        "answer": "王晓明", "options": [],
        "explanation": "1988年陈思和、王晓明提出“重写文学史”，反思既有文学史叙述。"}},
    {"ch": "小说（80年代）", "kw": "反思文学", "q": {"stem": "反思文学代表作家还有张贤亮，其代表作是《____》。", "type": "blank",
        "answer": "绿化树", "options": [],
        "explanation": "张贤亮《绿化树》等反思知青与历史创伤，是反思文学代表作。"}},
    {"ch": "小说（80年代）", "kw": "伤痕文学", "q": {"stem": "伤痕文学主要书写____造成的创伤。", "type": "blank",
        "answer": "“文革”（政治浩劫）", "options": [],
        "explanation": "伤痕文学以控诉“文革”创伤、宣泄悲愤为特征。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'当代第三批挂载 {n} 题')
