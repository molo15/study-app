# -*- coding: utf-8 -*-
"""当代文学史 扩充第四批：散文/戏剧/广度扩充"""
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
    {"ch": "散文（80-90年代）", "kw": "80年代散文家：孙犁、杨绛、陈白尘、汪曾祺", "q": {"stem": "杨绛的散文集代表作是《____》。", "type": "blank",
        "answer": "干校六记", "options": [],
        "explanation": "杨绛《干校六记》以平静笔触写干校生活，是80年代散文名作。"}},
    {"ch": "散文（80-90年代）", "kw": "巴金《随想录》", "q": {"stem": "巴金《随想录》被誉为“讲真话的____”。", "type": "blank",
        "answer": "大书", "options": [],
        "explanation": "《随想录》以“讲真话”著称，是巴金晚年反思之作。"}},
    {"ch": "散文（80-90年代）", "kw": "学者散文", "q": {"stem": "学者散文以____（学养）与理性见长。", "type": "blank",
        "answer": "学养（文化底蕴）", "options": [],
        "explanation": "学者散文融学识、思考于文，如余秋雨、张中行等。"}},
    {"ch": "散文（80-90年代）", "kw": "余秋雨《文化苦旅》", "q": {"stem": "余秋雨《文化苦旅》是____散文的典范。", "type": "blank",
        "answer": "文化（学者）", "options": [],
        "explanation": "《文化苦旅》以文化遗址为对象反思历史文化，是文化散文典范。"}},
    {"ch": "散文（80-90年代）", "kw": "思想散文", "q": {"stem": "思想散文又称____散文。", "type": "blank",
        "answer": "学者", "options": [],
        "explanation": "思想散文（学者散文）以思想性、学理性见长。"}},
    {"ch": "戏剧散文（50-60年代）", "kw": "“第四种剧本”", "q": {"stem": "“第四种剧本”的代表作有《____》。", "type": "blank",
        "answer": "布谷鸟又叫了", "options": [],
        "explanation": "杨履方《布谷鸟又叫了》突破公文化、概念化，是“第四种剧本”代表作。"}},
    {"ch": "戏剧散文（50-60年代）", "kw": "老舍《茶馆》", "q": {"stem": "《茶馆》以____茶馆的兴衰为线索。", "type": "blank",
        "answer": "裕泰", "options": [],
        "explanation": "《茶馆》以裕泰茶馆的变迁串起半个世纪的社会图景。"}},
    {"ch": "戏剧散文（50-60年代）", "kw": "杨朔的散文", "q": {"stem": "杨朔散文讲究“____”的写法。", "type": "blank",
        "answer": "托物言志", "options": [],
        "explanation": "杨朔散文常借物抒情、托物言志，如《荔枝蜜》《茶花赋》。"}},
    {"ch": "戏剧散文（50-60年代）", "kw": "秦牧的散文", "q": {"stem": "秦牧的《艺海拾贝》是____（知识）散文集。", "type": "blank",
        "answer": "知识（文艺随笔）", "options": [],
        "explanation": "秦牧散文以知识性、趣味性见长，《艺海拾贝》谈文艺创作。"}},
    {"ch": "戏剧散文（50-60年代）", "kw": "历史剧热潮", "q": {"stem": "60年代郭沫若的历史剧代表作是《____》。", "type": "blank",
        "answer": "蔡文姬", "options": [],
        "explanation": "郭沫若《蔡文姬》（1959）是60年代历史剧热潮的代表作。"}},
    {"ch": "戏剧散文（50-60年代）", "kw": "田汉《关汉卿》", "q": {"stem": "田汉《关汉卿》以____为主人公。", "type": "blank",
        "answer": "关汉卿", "options": [],
        "explanation": "《关汉卿》借元代戏剧家关汉卿形象抒写“为民请命”的志士情怀。"}},
    {"ch": "2000-2016年文学", "kw": "莫言的魔幻现实主义", "q": {"stem": "莫言于2012年获得____文学奖。", "type": "blank",
        "answer": "诺贝尔", "options": [],
        "explanation": "莫言2012年获诺贝尔文学奖，是首位获此奖的中国籍作家。"}},
    {"ch": "2000-2016年文学", "kw": "贾平凹《秦腔》", "q": {"stem": "贾平凹《秦腔》获第____届茅盾文学奖。", "type": "blank",
        "answer": "七", "options": [],
        "explanation": "《秦腔》获第七届茅盾文学奖，写乡村在现代化中的失落。"}},
    {"ch": "2000-2016年文学", "kw": "毕飞宇的小说", "q": {"stem": "毕飞宇《玉米》书写____的遭际。", "type": "blank",
        "answer": "乡村女性", "options": [],
        "explanation": "《玉米》以乡村女性命运折射时代变迁。"}},
    {"ch": "2000-2016年文学", "kw": "打工文学与底层写作", "q": {"stem": "“打工诗歌”的代表诗人有____。", "type": "blank",
        "answer": "郑小琼", "options": [],
        "explanation": "郑小琼以打工经历入诗，是“打工诗歌”代表诗人。"}},
    {"ch": "2000-2016年文学", "kw": "网络诗歌", "q": {"stem": "网络诗歌的兴起与____（媒介）的普及密切相关。", "type": "blank",
        "answer": "互联网", "options": [],
        "explanation": "网络诗歌依托互联网平台发表传播，突破了纸媒门槛。"}},
    {"ch": "台港文学", "kw": "白先勇的小说", "q": {"stem": "白先勇《纽约客》写____的漂泊。", "type": "blank",
        "answer": "海外华人", "options": [],
        "explanation": "《纽约客》写旅美华人在异乡的漂泊与失落。"}},
    {"ch": "台港文学", "kw": "余光中的诗歌创作", "q": {"stem": "余光中因《乡愁》等诗被称为“____诗人”。", "type": "blank",
        "answer": "乡愁", "options": [],
        "explanation": "《乡愁》使余光中获“乡愁诗人”之誉。"}},
    {"ch": "台港文学", "kw": "梁实秋的散文", "q": {"stem": "梁实秋散文以____（闲适、幽默）见长。", "type": "blank",
        "answer": "闲适幽默", "options": [],
        "explanation": "梁实秋散文从容闲适、幽默风趣，如《雅舍小品》。"}},
    {"ch": "台港文学", "kw": "金庸小说的文化底蕴与现代意识", "q": {"stem": "金庸“射雕三部曲”是《射雕英雄传》《神雕侠侣》和《____》。", "type": "blank",
        "answer": "倚天屠龙记", "options": [],
        "explanation": "“射雕三部曲”含《射雕英雄传》《神雕侠侣》《倚天屠龙记》。"}},
    {"ch": "台港文学", "kw": "余光中的散文", "q": {"stem": "《听听那冷雨》抒发的核心情感是____。", "type": "blank",
        "answer": "乡愁", "options": [],
        "explanation": "《听听那冷雨》借雨写乡愁与家国之思。"}},
    {"ch": "小说（80年代）", "kw": "新写实小说", "q": {"stem": "池莉《烦恼人生》是新____小说的代表作。", "type": "blank",
        "answer": "写实", "options": [],
        "explanation": "《烦恼人生》写普通人琐碎日常，是新写实小说代表作。"}},
    {"ch": "小说（80年代）", "kw": "寻根文学", "q": {"stem": "阿城《棋王》将____（棋道）与人生相融合。", "type": "blank",
        "answer": "棋道（传统文化）", "options": [],
        "explanation": "《棋王》写知青王一生，以棋道寄寓传统文化精神。"}},
    {"ch": "小说（80年代）", "kw": "反思文学", "q": {"stem": "谌容《人到中年》写____的困境。", "type": "blank",
        "answer": "中年知识分子", "options": [],
        "explanation": "《人到中年》以陆文婷的遭遇写中年知识分子的奉献与困顿。"}},
    {"ch": "小说（80年代）", "kw": "改革文学", "q": {"stem": "张洁《沉重的翅膀》是____题材小说。", "type": "blank",
        "answer": "改革（工业改革）", "options": [],
        "explanation": "《沉重的翅膀》写工业改革的艰难，是改革文学代表作。"}},
    {"ch": "小说（80年代）", "kw": "伤痕文学", "q": {"stem": "刘心武《班主任》塑造了____这一被“文革”毒害的形象。", "type": "blank",
        "answer": "谢惠敏", "options": [],
        "explanation": "《班主任》中的谢惠敏是“文革”造成的“好学生”，发人深省。"}},
    {"ch": "新诗（80-90年代）", "kw": "新生代诗人", "q": {"stem": "韩东《有关大雁塔》体现了新生代诗人对____的解构。", "type": "blank",
        "answer": "崇高（文化象征）", "options": [],
        "explanation": "新生代诗人主张“回到日常”，解构朦胧诗的崇高抒情。"}},
    {"ch": "小说（90年代）", "kw": "女性写作：陈染、林白", "q": {"stem": "林白《一个人的战争》是____化写作的代表。", "type": "blank",
        "answer": "私人（个人）", "options": [],
        "explanation": "《一个人的战争》以女性自叙写私人经验，是私人化写作代表。"}},
    {"ch": "小说（90年代）", "kw": "新历史小说", "q": {"stem": "刘震云《故乡天下黄花》是____小说代表作。", "type": "blank",
        "answer": "新历史", "options": [],
        "explanation": "《故乡天下黄花》以民间视角重写乡村历史，属新历史小说。"}},
    {"ch": "戏剧（80-90年代）", "kw": "高行健的戏剧", "q": {"stem": "高行健于2000年获____文学奖。", "type": "blank",
        "answer": "诺贝尔", "options": [],
        "explanation": "高行健2000年获诺贝尔文学奖，是首位获此奖的华人作家。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'当代第四批挂载 {n} 题')
