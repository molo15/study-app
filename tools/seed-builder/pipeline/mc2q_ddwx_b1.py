# -*- coding: utf-8 -*-
"""当代文学史 第一批扩充：各章核心考点直问直答"""
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
    {"ch": "文学思潮（1949-1976）", "mk": "双百", "q": {"stem": "1956年提出的“双百”方针是指“百花齐放、____”。", "type": "blank",
        "answer": "百家争鸣", "explanation": "“双百方针”即百花齐放、百家争鸣，1956年提出，对文艺和学术的发展有重要影响。",
        "options": []}},
    {"ch": "文学思潮（1949-1976）", "mk": "武训传", "q": {"stem": "新中国成立后第一次大规模文艺批判运动针对的是电影《____》。", "type": "blank",
        "answer": "武训传", "explanation": "1951年对电影《武训传》的批判，是建国后第一次大规模的文艺批判运动。",
        "options": []}},
    {"ch": "文学思潮（1949-1976）", "mk": "样板戏", "q": {"stem": "“革命样板戏”中属于京剧的有《红灯记》《智取威虎山》和《____》。", "type": "blank",
        "answer": "沙家浜", "explanation": "革命样板戏包括《红灯记》《智取威虎山》《沙家浜》《奇袭白虎团》《海港》等京剧。",
        "options": []}},
    # ---- 小说 50-60 ----
    {"ch": "小说（50-60年代）", "mk": "山药蛋派", "q": {"stem": "山药蛋派的代表作家是____。", "type": "blank",
        "answer": "赵树理", "explanation": "山药蛋派以赵树理为代表，写农村生活，语言质朴幽默，乡土气息浓厚。",
        "options": []}},
    {"ch": "小说（50-60年代）", "mk": "创业史", "q": {"stem": "柳青《创业史》的主人公是____。", "type": "blank",
        "answer": "梁生宝", "explanation": "《创业史》写梁生宝带领农民走合作化道路，是农业合作化题材的代表作。",
        "options": []}},
    {"ch": "小说（50-60年代）", "mk": "红旗谱", "q": {"stem": "梁斌《红旗谱》的主人公是农民英雄____。", "type": "blank",
        "answer": "朱老忠", "explanation": "《红旗谱》写朱老忠等三代农民的革命斗争，是革命历史题材的代表作。",
        "options": []}},
    {"ch": "小说（50-60年代）", "mk": "青春之歌", "q": {"stem": "杨沫《青春之歌》的主人公是知识分子____。", "type": "blank",
        "answer": "林道静", "explanation": "《青春之歌》写林道静从个人反抗走向革命道路的成长历程。",
        "options": []}},
    {"ch": "小说（50-60年代）", "mk": "两大主题", "q": {"stem": "十七年小说的两大主题是（　）", "type": "choice",
        "answer": "革命历史题材和农村现实题材", "explanation": "十七年小说以革命历史题材和农村现实题材为主，产生了《红旗谱》《创业史》等代表作。",
        "options": ["革命历史题材和农村现实题材", "知识分子题材和爱情题材", "工业题材和城市题材", "战争题材和科幻题材"]}},
    # ---- 小说 80年代 ----
    {"ch": "小说（80年代）", "mk": "伤痕文学", "q": {"stem": "伤痕文学的开端之作是卢新华的短篇小说《____》。", "type": "blank",
        "answer": "伤痕", "explanation": "卢新华《伤痕》1978年发表，是伤痕文学的开端之作。",
        "options": []}},
    {"ch": "小说（80年代）", "mk": "反思文学", "q": {"stem": "反思文学的代表作是茹志鹃的《____》。", "type": "blank",
        "answer": "剪辑错了的故事", "explanation": "茹志鹃《剪辑错了的故事》是反思文学代表作，对历史进行理性反思。",
        "options": []}},
    {"ch": "小说（80年代）", "mk": "改革文学", "q": {"stem": "改革文学的开端之作是蒋子龙的《____》。", "type": "blank",
        "answer": "乔厂长上任记", "explanation": "蒋子龙《乔厂长上任记》是改革文学的代表作，塑造了改革者乔光朴的形象。",
        "options": []}},
    {"ch": "小说（80年代）", "mk": "意识流", "q": {"stem": "王蒙“意识流”小说的代表作是《____》。", "type": "blank",
        "answer": "春之声", "explanation": "王蒙《春之声》运用意识流手法，是新时期小说形式探索的代表。",
        "options": []}},
    {"ch": "小说（80年代）", "mk": "路遥", "q": {"stem": "路遥的长篇小说《____》获第三届茅盾文学奖。", "type": "blank",
        "answer": "平凡的世界", "explanation": "路遥《平凡的世界》以孙少安、孙少平兄弟的奋斗写改革开放初期农村巨变，获茅盾文学奖。",
        "options": []}},
    {"ch": "小说（80年代）", "mk": "高晓声", "q": {"stem": "高晓声以农民____为主人公创作了系列乡土小说。", "type": "blank",
        "answer": "陈奂生", "explanation": "高晓声“陈奂生系列”包括《陈奂生上城》《陈奂生转业》等，塑造了当代农民形象。",
        "options": []}},
    {"ch": "小说（80年代）", "mk": "张承志", "q": {"stem": "张承志知青题材小说《____》写草原上额吉与白音宝力格的故事。", "type": "blank",
        "answer": "黑骏马", "explanation": "张承志《黑骏马》写知青在草原上的生活与精神成长，充满草原气息。",
        "options": []}},
    {"ch": "小说（80年代）", "mk": "余华", "q": {"stem": "余华《活着》的主人公是____。", "type": "blank",
        "answer": "福贵", "explanation": "《活着》写农民福贵历经苦难而坚韧活着的生命历程，是余华的重要作品。",
        "options": []}},
    # ---- 小说 90年代 ----
    {"ch": "小说（90年代）", "mk": "长恨歌", "q": {"stem": "王安忆《长恨歌》的女主人公是____。", "type": "blank",
        "answer": "王琦瑶", "explanation": "《长恨歌》以王琦瑶的一生写上海四十年的变迁，获茅盾文学奖。",
        "options": []}},
    {"ch": "小说（90年代）", "mk": "王小波", "q": {"stem": "王小波《黄金时代》中的叙述者主人公是____。", "type": "blank",
        "answer": "王二", "explanation": "王小波《黄金时代》以“王二”为主人公，写知青时代的荒诞与反抗。",
        "options": []}},
    {"ch": "小说（90年代）", "mk": "新历史小说", "q": {"stem": "新历史小说对____进行重新书写和想象，消解了传统历史叙事的宏大性。", "type": "blank",
        "answer": "历史", "explanation": "新历史小说以虚构和想象重新书写历史，代表作家有苏童、格非、莫言等。",
        "options": []}},
    # ---- 新诗 50-60 ----
    {"ch": "新诗（50-60年代）", "mk": "真题补充", "q": {"stem": "贺敬之《回延安》采用了陕北民歌____的形式。", "type": "blank",
        "answer": "信天游", "explanation": "贺敬之《回延安》采用陕北信天游形式，抒发对延安的深情。",
        "options": []}},
    {"ch": "新诗（50-60年代）", "mk": "真题补充", "q": {"stem": "郭小川的政治抒情诗代表作有《____》等。", "type": "blank",
        "answer": "致青年公民", "explanation": "郭小川《致青年公民》等政治抒情诗，以炽热激情和阶梯式排比著称。",
        "options": []}},
    # ---- 新诗 80-90 ----
    {"ch": "新诗（80-90年代）", "mk": "舒婷", "q": {"stem": "朦胧诗代表诗人除北岛、舒婷外，还有以童话诗著称的____。", "type": "blank",
        "answer": "顾城", "explanation": "朦胧诗三大家指北岛、舒婷、顾城，顾城的诗充满童话色彩。",
        "options": []}},
    {"ch": "新诗（80-90年代）", "mk": "海子", "q": {"stem": "海子的代表作《____》中写道“面朝大海，春暖花开”。", "type": "blank",
        "answer": "面朝大海，春暖花开", "explanation": "海子《面朝大海，春暖花开》表达了对幸福生活的向往，是其代表作。",
        "options": []}},
    {"ch": "新诗（80-90年代）", "mk": "舒婷", "q": {"stem": "“卑鄙是卑鄙者的通行证”出自北岛的诗作《____》。", "type": "blank",
        "answer": "回答", "explanation": "北岛《回答》开篇“卑鄙是卑鄙者的通行证，高尚是高尚者的墓志铭”，是朦胧诗代表作。",
        "options": []}},
    # ---- 戏剧 ----
    {"ch": "戏剧（80-90年代）", "mk": "探索戏剧", "q": {"stem": "高行健的《____》是新时期探索戏剧的开端之作。", "type": "blank",
        "answer": "绝对信号", "explanation": "高行健《绝对信号》运用表现主义手法，是新时期探索戏剧的代表作。",
        "options": []}},
    {"ch": "戏剧（80-90年代）", "mk": "现实主义", "q": {"stem": "沙叶新的《____》以“冰糖葫芦式”结构塑造了陈毅形象。", "type": "blank",
        "answer": "陈毅市长", "explanation": "沙叶新《陈毅市长》以片段式结构塑造陈毅形象，是新时期现实主义戏剧代表作。",
        "options": []}},
    # ---- 散文 ----
    {"ch": "散文（80-90年代）", "mk": "文化苦旅", "q": {"stem": "余秋雨的《____》以文化遗迹为对象，是“文化散文”的代表作。", "type": "blank",
        "answer": "文化苦旅", "explanation": "余秋雨《文化苦旅》借山水古迹叩问中国文化精神，开“文化散文”先河。",
        "options": []}},
    # ---- 台港 ----
    {"ch": "台港文学", "mk": "金庸", "q": {"stem": "金庸武侠小说《射雕英雄传》的男主人公是____。", "type": "blank",
        "answer": "郭靖", "explanation": "《射雕英雄传》写郭靖与黄蓉的故事，郭靖是忠厚侠义的大侠形象。",
        "options": []}},
    {"ch": "台港文学", "mk": "白先勇", "q": {"stem": "白先勇的小说集《____》写流亡台北的大陆人的生活。", "type": "blank",
        "answer": "台北人", "explanation": "白先勇《台北人》写流寓台北的大陆各色人物的乡愁与失落，是其代表作。",
        "options": []}},
    {"ch": "台港文学", "mk": "余光中", "q": {"stem": "余光中的《乡愁》表达了____的情感。", "type": "blank",
        "answer": "思乡", "explanation": "余光中《乡愁》借邮票、船票、坟墓、海峡写浓烈的思乡之情。",
        "options": []}},
    # ---- 2000-2016 ----
    {"ch": "2000-2016年文学", "mk": "莫言", "q": {"stem": "莫言于2012年获得____文学奖。", "type": "blank",
        "answer": "诺贝尔", "explanation": "莫言2012年获诺贝尔文学奖，代表作《红高粱家族》《蛙》等。",
        "options": []}},
    {"ch": "2000-2016年文学", "mk": "李洱", "q": {"stem": "李洱的长篇小说《____》获第十届茅盾文学奖。", "type": "blank",
        "answer": "应物兄", "explanation": "李洱《应物兄》获第十届茅盾文学奖，是知识分子题材的厚重之作。",
        "options": []}},
]

n = dup = 0
for it in Q:
    ok = mount(it['ch'], it['q'], it['mk'])
    n += ok
    dup += (not ok)
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'当代第一批挂载 {n} 题（跳过 {dup}）')
