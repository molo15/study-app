# -*- coding: utf-8 -*-
"""当代文学史 扩充第二批：作家作品精准挂载"""
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
    {"ch": "小说（80年代）", "kw": "伤痕文学", "q": {"stem": "伤痕文学的开山之作是卢新华的《____》。", "type": "blank",
        "answer": "伤痕", "options": [],
        "explanation": "卢新华《伤痕》发表于1978年，标志着伤痕文学的发端。"}},
    {"ch": "小说（80年代）", "kw": "反思文学", "q": {"stem": "反思文学代表作有茹志鹃的《____》。", "type": "blank",
        "answer": "剪辑错了的故事", "options": [],
        "explanation": "茹志鹃《剪辑错了的故事》以反思姿态审视历史，是反思文学代表作。"}},
    {"ch": "小说（80年代）", "kw": "改革文学", "q": {"stem": "改革文学的代表作是蒋子龙的《____》。", "type": "blank",
        "answer": "乔厂长上任记", "options": [],
        "explanation": "蒋子龙《乔厂长上任记》塑造改革者形象，是改革文学代表作。"}},
    {"ch": "小说（80年代）", "kw": "寻根文学", "q": {"stem": "寻根文学代表作有韩少功的《____》。", "type": "blank",
        "answer": "爸爸爸", "options": [],
        "explanation": "韩少功《爸爸爸》以丙崽形象反思民族文化心理，是寻根文学代表作。"}},
    {"ch": "小说（80年代）", "kw": "路遥的小说", "q": {"stem": "路遥《平凡的世界》的主人公是____。", "type": "blank",
        "answer": "孙少平（孙少安）", "options": [],
        "explanation": "《平凡的世界》以孙少平、孙少安兄弟的奋斗为主线，写黄土高原农村青年。"}},
    {"ch": "小说（80年代）", "kw": "高晓声的乡土小说", "q": {"stem": "高晓声塑造的经典农民形象是____。", "type": "blank",
        "answer": "陈奂生", "options": [],
        "explanation": "高晓声以“陈奂生”系列（《陈奂生上城》等）写农民命运。"}},
    {"ch": "小说（80年代）", "kw": "王蒙的意识流小说", "q": {"stem": "王蒙《春之声》借鉴了____的创作手法。", "type": "blank",
        "answer": "意识流", "options": [],
        "explanation": "《春之声》以主人公的意识流动结构全篇，是王蒙意识流小说的代表。"}},
    {"ch": "小说（80年代）", "kw": "新写实小说", "q": {"stem": "新写实小说代表作家有池莉、方方、____。", "type": "blank",
        "answer": "刘震云", "options": [],
        "explanation": "池莉、方方、刘震云等是新写实小说代表，写凡人琐事的原生态。"}},
    {"ch": "小说（80年代）", "kw": "余华的小说创作", "q": {"stem": "余华《活着》的主人公是____。", "type": "blank",
        "answer": "福贵", "options": [],
        "explanation": "《活着》写福贵的一生，体现“活着”本身的坚韧。"}},
    {"ch": "小说（80年代）", "kw": "陆文夫的小说", "q": {"stem": "陆文夫《美食家》以____（城市）生活为背景。", "type": "blank",
        "answer": "苏州", "options": [],
        "explanation": "《美食家》写苏州饮食文化与世态人情，是陆文夫代表作。"}},
    {"ch": "小说（90年代）", "kw": "新历史小说", "q": {"stem": "新历史小说的代表作有莫言的《____》。", "type": "blank",
        "answer": "红高粱", "options": [],
        "explanation": "《红高粱》以民间视角重写历史，是新历史小说的代表作。"}},
    {"ch": "小说（90年代）", "kw": "女性写作：陈染、林白", "q": {"stem": "陈染、林白的创作属于____写作。", "type": "blank",
        "answer": "女性（私人化）", "options": [],
        "explanation": "陈染《私人生活》、林白《一个人的战争》是女性私人化写作的代表。"}},
    {"ch": "小说（90年代）", "kw": "新生代小说", "q": {"stem": "新生代小说的代表作家有____。", "type": "blank",
        "answer": "韩东（朱文）", "options": [],
        "explanation": "韩东、朱文等新生代作家多写日常琐碎与边缘经验。"}},
    {"ch": "小说（90年代）", "kw": "王安忆《长恨歌》", "q": {"stem": "王安忆《长恨歌》的女主人公是____。", "type": "blank",
        "answer": "王琦瑶", "options": [],
        "explanation": "《长恨歌》以王琦瑶的一生写上海城市变迁。"}},
    {"ch": "小说（90年代）", "kw": "王小波的小说", "q": {"stem": "王小波《黄金时代》的主人公是____。", "type": "blank",
        "answer": "王二", "options": [],
        "explanation": "《黄金时代》写王二的知青岁月，充满反讽与荒诞。"}},
    {"ch": "小说（90年代）", "kw": "王朔的“顽主”与调侃", "q": {"stem": "王朔小说以____的语言风格著称。", "type": "blank",
        "answer": "调侃（反讽）", "options": [],
        "explanation": "王朔以“顽主”式调侃消解崇高，语言戏谑反讽。"}},
    {"ch": "小说（90年代）", "kw": "贾平凹的小说", "q": {"stem": "贾平凹《废都》的男主人公是____。", "type": "blank",
        "answer": "庄之蝶", "options": [],
        "explanation": "《废都》以作家庄之蝶的沉沦写文化人的精神困境。"}},
    {"ch": "小说（90年代）", "kw": "陈忠实《白鹿原》", "q": {"stem": "《白鹿原》中白鹿原的族长是____。", "type": "blank",
        "answer": "白嘉轩", "options": [],
        "explanation": "白嘉轩是《白鹿原》中白鹿原的族长，体现传统宗法文化的坚守。"}},
    {"ch": "新诗（80-90年代）", "kw": "朦胧诗", "q": {"stem": "朦胧诗的主要阵地是民间刊物《____》。", "type": "blank",
        "answer": "今天", "options": [],
        "explanation": "《今天》杂志（1978年创刊）是朦胧诗的重要阵地。"}},
    {"ch": "新诗（80-90年代）", "kw": "舒婷的诗歌", "q": {"stem": "舒婷《致橡树》表达了____的爱情观。", "type": "blank",
        "answer": "独立平等", "options": [],
        "explanation": "《致橡树》以木棉与橡树的并立，表达独立平等的爱情观。"}},
    {"ch": "新诗（80-90年代）", "kw": "新生代诗人", "q": {"stem": "新生代诗人又被称为“____诗人”。", "type": "blank",
        "answer": "第三代", "options": [],
        "explanation": "继朦胧诗（第二代）之后，新生代诗人被称为“第三代诗人”。"}},
    {"ch": "新诗（80-90年代）", "kw": "海子的诗歌", "q": {"stem": "海子诗歌中反复出现的核心意象是____。", "type": "blank",
        "answer": "麦地（麦子）", "options": [],
        "explanation": "“麦地”是海子诗歌的核心意象，寄托其对土地与生命的深情。"}},
    {"ch": "台港文学", "kw": "白先勇的小说", "q": {"stem": "白先勇《台北人》书写____的怀乡与沉浮。", "type": "blank",
        "answer": "流落台北的大陆人", "options": [],
        "explanation": "《台北人》写大陆移民流落台北后的今昔之感，是白先勇代表作。"}},
    {"ch": "台港文学", "kw": "梁实秋的散文", "q": {"stem": "梁实秋的散文集代表作是《____》。", "type": "blank",
        "answer": "雅舍小品", "options": [],
        "explanation": "梁实秋《雅舍小品》以闲适幽默见长，是台湾散文名作。"}},
    {"ch": "台港文学", "kw": "余光中的诗歌创作", "q": {"stem": "余光中《乡愁》以“邮票、船票、____、海峡”为意象。", "type": "blank",
        "answer": "坟墓", "options": [],
        "explanation": "《乡愁》依次以邮票、船票、坟墓、海峡写乡愁的深化。"}},
    {"ch": "台港文学", "kw": "金庸小说的文化底蕴与现代意识", "q": {"stem": "金庸小说将____、武侠与文化相融合。", "type": "blank",
        "answer": "历史", "options": [],
        "explanation": "金庸小说以历史为背景，融武侠、文化、人性于一体。"}},
    {"ch": "2000-2016年文学", "kw": "贾平凹《秦腔》", "q": {"stem": "贾平凹《秦腔》以____（村）为背景写乡村变迁。", "type": "blank",
        "answer": "清风街", "options": [],
        "explanation": "《秦腔》以清风街为舞台，写传统乡村在现代化中的衰变。"}},
    {"ch": "2000-2016年文学", "kw": "毕飞宇的小说", "q": {"stem": "毕飞宇《推拿》聚焦____群体的生活。", "type": "blank",
        "answer": "盲人", "options": [],
        "explanation": "《推拿》以盲人推拿师为主角，获茅盾文学奖。"}},
    {"ch": "2000-2016年文学", "kw": "打工文学与底层写作", "q": {"stem": "打工文学关注____群体的生存境遇。", "type": "blank",
        "answer": "农民工（底层）", "options": [],
        "explanation": "打工文学以进城务工者为书写对象，关注底层的尊严与命运。"}},
    {"ch": "2000-2016年文学", "kw": "莫言《红高粱》", "q": {"stem": "莫言《红高粱》的故事发生在____。", "type": "blank",
        "answer": "高密东北乡", "options": [],
        "explanation": "《红高粱》以高密东北乡为背景，写民间抗日传奇。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'当代第二批挂载 {n} 题')
