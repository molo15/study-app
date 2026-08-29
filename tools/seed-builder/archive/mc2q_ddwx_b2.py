# -*- coding: utf-8 -*-
"""当代文学史 第二批扩充"""
import io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'D:\study_app\tools\seed-builder\out\knowledge\中国当代文学史.knowledge.json'
KP = json.load(open(P, encoding='utf-8'))

def norm(s):
    return re.sub(r'[（）()。，、；：""“”\'  ]', '', s)

def mount(chapter, q, match_kw):
    kps = [k for k in KP['knowledge'] if k['chapter'] == chapter]
    best = None
    for k in kps:
        if match_kw and match_kw in k['name']:
            best = k
            break
    if best is None:
        for k in kps:
            if '真题补充' in k['name']:
                best = k
                break
    if best is None:
        best = {"id": "k_zhen_ddwx_" + chapter, "name": chapter + "（真题补充）",
                "parent": "root", "chapter": chapter, "hot": False,
                "summary": "考研真题补充知识点，覆盖该章重要考点。", "basicQuestions": []}
        KP['knowledge'].append(best)
    for e in best.get('basicQuestions', []):
        if norm(e['stem']) == norm(q['stem']):
            return False
    best['basicQuestions'].append(q)
    return True

Q = [
    # ---- 文学思潮 1949-1976 ----
    {"ch": "文学思潮（1949-1976）", "mk": "真题补充", "q": {"stem": "1949年7月召开的____文代会，标志着新中国文学的开端。", "type": "blank",
        "answer": "第一次", "explanation": "1949年7月第一次文代会召开，确立了新中国文艺的方向，是当代文学的开端。",
        "options": []}},
    {"ch": "文学思潮（1949-1976）", "mk": "俞平伯", "q": {"stem": "1954年开展的学术批判运动针对的是俞平伯的《____》研究。", "type": "blank",
        "answer": "红楼梦", "explanation": "1954年对俞平伯《红楼梦》研究的批判，由两个“小人物”批判文章引发。",
        "options": []}},
    # ---- 小说 50-60 ----
    {"ch": "小说（50-60年代）", "mk": "三里湾", "q": {"stem": "赵树理《三里湾》是____题材的代表作。", "type": "choice",
        "answer": "农业合作化", "explanation": "《三里湾》写三里湾村农业合作化运动中的矛盾与新人，是赵树理十七年时期代表作。",
        "options": ["农业合作化", "革命历史", "工业建设", "知识分子改造"]}},
    {"ch": "小说（50-60年代）", "mk": "茹志鹃", "q": {"stem": "茹志鹃的短篇小说《____》以战争为背景写军民之情。", "type": "blank",
        "answer": "百合花", "explanation": "茹志鹃《百合花》以小见大，写解放战争中的军民之情，风格清新。",
        "options": []}},
    {"ch": "小说（50-60年代）", "mk": "组织部", "q": {"stem": "王蒙《组织部来了个年轻人》中的主人公是____。", "type": "blank",
        "answer": "林震", "explanation": "《组织部来了个年轻人》写青年林震在区委组织部遇到的官僚主义问题。",
        "options": []}},
    # ---- 小说 80 ----
    {"ch": "小说（80年代）", "mk": "陆文夫", "q": {"stem": "陆文夫以写苏州“小巷文学”著称，其代表作是《____》。", "type": "blank",
        "answer": "美食家", "explanation": "陆文夫《美食家》通过“吃”写苏州世态人情，是小巷文学代表作。",
        "options": []}},
    # ---- 小说 90 ----
    {"ch": "小说（90年代）", "mk": "女性写作", "q": {"stem": "林白以女性身体书写著称的长篇小说是《____》。", "type": "blank",
        "answer": "一个人的战争", "explanation": "林白《一个人的战争》大胆书写女性经验，是90年代女性写作的代表作。",
        "options": []}},
    {"ch": "小说（90年代）", "mk": "新生代小说", "q": {"stem": "90年代“新生代”小说又被称为____代作家。", "type": "blank",
        "answer": "晚生", "explanation": "新生代作家又称晚生代，代表有韩东、朱文、何顿等，关注当下日常经验。",
        "options": []}},
    {"ch": "小说（90年代）", "mk": "小鲍庄", "q": {"stem": "王安忆《小鲍庄》是____文学的代表作。", "type": "blank",
        "answer": "寻根", "explanation": "《小鲍庄》写乡村的仁厚与苦难，被视为寻根文学的代表作。",
        "options": []}},
    {"ch": "小说（90年代）", "mk": "王朔", "q": {"stem": "王朔小说中塑造了一群调侃一切的“____”形象。", "type": "blank",
        "answer": "顽主", "explanation": "王朔《顽主》等作品塑造了以调侃消解崇高的“顽主”形象。",
        "options": []}},
    {"ch": "小说（90年代）", "mk": "贾平凹", "q": {"stem": "贾平凹《废都》的主人公是作家____。", "type": "blank",
        "answer": "庄之蝶", "explanation": "《废都》写西京作家庄之蝶的精神困境，是贾平凹90年代代表作。",
        "options": []}},
    # ---- 戏剧 50-60 ----
    {"ch": "戏剧散文（50-60年代）", "mk": "第四种", "q": {"stem": "1957年提出的“第四种剧本”指的是突破____三类题材的剧本。", "type": "blank",
        "answer": "工农兵", "explanation": "“第四种剧本”指突破工业、农业、部队题材，写“人”的剧本，代表作《布谷鸟又叫了》。",
        "options": []}},
    {"ch": "戏剧散文（50-60年代）", "mk": "关汉卿", "q": {"stem": "田汉的历史剧《____》写元代戏剧家关汉卿与珠帘秀的故事。", "type": "blank",
        "answer": "关汉卿", "explanation": "田汉《关汉卿》借古写今，塑造了为民请命的戏剧家关汉卿形象。",
        "options": []}},
    {"ch": "戏剧散文（50-60年代）", "mk": "秦牧", "q": {"stem": "秦牧的知识性散文代表作是《____》。", "type": "blank",
        "answer": "社稷坛抒情", "explanation": "秦牧《社稷坛抒情》融知识、趣味与哲理于一体，是其知识性散文代表作。",
        "options": []}},
    # ---- 散文 80-90 ----
    {"ch": "散文（80-90年代）", "mk": "孙犁", "q": {"stem": "杨绛记述“文革”中干校生活的散文集是《____》。", "type": "blank",
        "answer": "干校六记", "explanation": "杨绛《干校六记》以平静笔触写干校生活，是知识分子散文的代表作。",
        "options": []}},
    {"ch": "散文（80-90年代）", "mk": "学者散文", "q": {"stem": "90年代“学者散文”的代表作家有____、季羡林、余秋雨等。", "type": "blank",
        "answer": "张中行", "explanation": "学者散文以张中行、季羡林、金克木、余秋雨等为代表，学养深厚、思辨性强。",
        "options": []}},
    # ---- 新诗 50-60 ----
    {"ch": "新诗（50-60年代）", "mk": "大我", "q": {"stem": "50-60年代新诗强调表现“大我”，即（　）", "type": "choice",
        "answer": "集体、阶级的情怀", "explanation": "50-60年代新诗强调“大我”，指集体、阶级的宏大情怀，淡化个人“小我”。",
        "options": ["集体、阶级的情怀", "个人的私密情感", "自然的审美感受", "历史的怀旧情绪"]}},
    # ---- 文学思潮 80-90 ----
    {"ch": "文学思潮（80-90年代）", "mk": "方法年", "q": {"stem": "文学批评界1985年被称为“方法年”，1986年被称为“____”。", "type": "blank",
        "answer": "观念年", "explanation": "1985年方法论热被称为“方法年”，1986年进而讨论文学观念，被称为“观念年”。",
        "options": []}},
    {"ch": "文学思潮（80-90年代）", "mk": "主体性", "q": {"stem": "刘再复提出“____”，强调文学应以人为中心。", "type": "blank",
        "answer": "文学主体性", "explanation": "刘再复提出“文学主体性”理论，强调人在文学中的主体地位，是80年代重要论争。",
        "options": []}},
    {"ch": "文学思潮（80-90年代）", "mk": "李泽厚", "q": {"stem": "李泽厚提出近代中国历史是“____的双重变奏”。", "type": "blank",
        "answer": "启蒙与救亡", "explanation": "李泽厚《启蒙与救亡的双重变奏》论述近代以来启蒙与救亡的相互缠绕。",
        "options": []}},
    # ---- 台港 ----
    {"ch": "台港文学", "mk": "余光中", "q": {"stem": "余光中的散文名篇《____》写台湾的雨与对大陆的乡愁。", "type": "blank",
        "answer": "听听那冷雨", "explanation": "余光中《听听那冷雨》借雨写乡愁，是其散文代表作。",
        "options": []}},
    {"ch": "台港文学", "mk": "金庸", "q": {"stem": "金庸武侠小说“飞雪连天射白鹿，笑书神侠倚碧鸳”，其中写虚竹、段誉的是《____》。", "type": "blank",
        "answer": "天龙八部", "explanation": "《天龙八部》以萧峰、虚竹、段誉三线并进，是金庸武侠的巅峰之作。",
        "options": []}},
    # ---- 2000-2016 ----
    {"ch": "2000-2016年文学", "mk": "秦腔", "q": {"stem": "贾平凹《秦腔》获第七届____文学奖。", "type": "blank",
        "answer": "茅盾", "explanation": "贾平凹《秦腔》写乡村文化的挽歌，获第七届茅盾文学奖。",
        "options": []}},
    {"ch": "2000-2016年文学", "mk": "打工文学", "q": {"stem": "“打工文学”以____的生活和情感为书写对象。", "type": "blank",
        "answer": "进城务工人员", "explanation": "打工文学书写进城务工人员的生存境遇，代表有《国家订单》等。",
        "options": []}},
]

n = dup = 0
for it in Q:
    ok = mount(it['ch'], it['q'], it['mk'])
    n += ok
    dup += (not ok)
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'当代第二批挂载 {n} 题（跳过 {dup}）')
