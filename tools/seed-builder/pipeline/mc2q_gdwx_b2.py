# -*- coding: utf-8 -*-
"""古代文学史 名词解释→基础题 第二批（隋唐五代/宋代）+ 修正第一批2处重复"""
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

# ---------- 修正第一批重复 ----------
def remove_dup(chapter, keyword):
    for k in KP['knowledge']:
        if k['chapter'] != chapter:
            continue
        k['basicQuestions'] = [q for q in k.get('basicQuestions', [])
                               if keyword not in q['stem']]

# 元嘉体：删除与已有填空重复的“代表诗人”选择，改为不同角度
remove_dup('魏晋南北朝文学', '“元嘉体”代表诗人有谢灵运')
# 搜神记：删除与已有填空重复的“作者”选择，改为不同角度
remove_dup('魏晋南北朝文学', '志怪小说集《搜神记》的作者是')
# 春秋三传：与已有填空重复的选择题，改为考“以记事为主/史学价值”不同角度 → 保留一个即可，删除选择题
remove_dup('先秦文学', '“春秋三传”指的是（　）')

# ---------- 隋唐五代 ----------
SD = [
    {"ch": "隋唐五代文学", "mk": "上官", "q": {"stem": "“上官体”因初唐诗人____得名，其诗绮靡浮艳，是齐梁宫体诗的余风。", "type": "blank",
        "answer": "上官仪", "explanation": "上官体是初唐诗人上官仪所开创的诗体，多为奉和应诏之作，绮靡浮艳。",
        "options": []}},
    {"ch": "隋唐五代文学", "mk": "上官", "q": {"stem": "下列不属于“初唐四杰”的是（　）", "type": "choice",
        "answer": "王昌龄", "explanation": "初唐四杰指王勃、杨炯、卢照邻、骆宾王，简称“王杨卢骆”；王昌龄是盛唐边塞诗人。",
        "options": ["王昌龄", "王勃", "杨炯", "骆宾王"]}},
    {"ch": "隋唐五代文学", "mk": "上官", "q": {"stem": "“文章四友”指杜审言、李峤、____、崔融。", "type": "blank",
        "answer": "苏味道", "explanation": "文章四友是杜审言、李峤、苏味道、崔融的合称，都是五律形成的推动者。",
        "options": []}},
    {"ch": "隋唐五代文学", "mk": "陈子昂", "q": {"stem": "陈子昂《修竹篇序》以汉魏诗歌为高标，感叹“____”的失落。", "type": "blank",
        "answer": "风骨和兴寄", "explanation": "《修竹篇序》是陈子昂的创作理论纲领，痛责浮靡文风，感叹“风骨”和“兴寄”的失落。",
        "options": []}},
    {"ch": "隋唐五代文学", "mk": "王孟", "q": {"stem": "“王孟韦柳”指王维、孟浩然、____、柳宗元四位山水田园诗人。", "type": "blank",
        "answer": "韦应物", "explanation": "王孟韦柳是王维、孟浩然与中唐韦应物、柳宗元的合称，为唐代山水田园诗歌流派的代表。",
        "options": []}},
    {"ch": "隋唐五代文学", "mk": "王孟", "q": {"stem": "“王孟诗派”又称（　）", "type": "choice",
        "answer": "山水田园诗派", "explanation": "王孟诗派是盛唐最有影响的诗歌流派之一，又称山水田园诗派，孟浩然、王维为代表。",
        "options": ["山水田园诗派", "边塞诗派", "元白诗派", "韩孟诗派"]}},
    {"ch": "隋唐五代文学", "mk": "韩孟", "q": {"stem": "“韩孟诗派”以____为领袖，主张“不平则鸣”“以丑为美”。", "type": "blank",
        "answer": "韩愈", "explanation": "韩孟诗派是中唐诗歌流派，以韩愈为领袖，包括孟郊、李贺、卢仝等，尚奇险怪异。",
        "options": []}},
    {"ch": "隋唐五代文学", "mk": "元白", "q": {"stem": "新乐府运动的倡导者是（　）", "type": "choice",
        "answer": "白居易、元稹", "explanation": "新乐府运动由白居易、元稹等倡导，主张以自创新题咏写时事，补察时政。",
        "options": ["白居易、元稹", "韩愈、柳宗元", "元稹、李贺", "杜甫、元结"]}},
    {"ch": "隋唐五代文学", "mk": "元白", "q": {"stem": "用新题写时事的“新乐府”诗始创于（　）", "type": "choice",
        "answer": "杜甫", "explanation": "新乐府诗始创于杜甫，为元结、顾况继承，又得到白居易、元稹大力提倡。",
        "options": ["杜甫", "李白", "元稹", "元结"]}},
    {"ch": "隋唐五代文学", "mk": "元白", "q": {"stem": "“元白”是唐代诗人元稹和____的合称。", "type": "blank",
        "answer": "白居易", "explanation": "元白是元稹、白居易的合称，二人同为新乐府运动倡导者，诗风平易浅切。",
        "options": []}},
    {"ch": "隋唐五代文学", "mk": "元白", "q": {"stem": "狭义的“元和体”指元稹、白居易的（　）", "type": "choice",
        "answer": "次韵相酬的长篇排律和中短篇杂体诗", "explanation": "狭义元和体指元白诗中的次韵相酬长篇排律和流连光景的中短篇杂体诗。",
        "options": ["次韵相酬的长篇排律和中短篇杂体诗", "新乐府讽喻诗", "山水田园诗", "边塞征战诗"]}},
    {"ch": "隋唐五代文学", "mk": "古文", "q": {"stem": "“古文”这一概念由____最先提出，他把骈文视为“俗文字”。", "type": "blank",
        "answer": "韩愈", "explanation": "古文运动以提倡古文、反对骈文为特点，“古文”概念由韩愈最先提出。",
        "options": []}},
    {"ch": "隋唐五代文学", "mk": "古文", "q": {"stem": "“气盛言宜”出自韩愈《____》。", "type": "blank",
        "answer": "答李翊书", "explanation": "韩愈在《答李翊书》中提出“气盛，则言之短长与声之高下者皆宜”，即气盛言宜。",
        "options": []}},
    {"ch": "隋唐五代文学", "mk": "古文", "q": {"stem": "韩愈《原道》一文的中心是反对（　）", "type": "choice",
        "answer": "佛老", "explanation": "《原道》是韩愈政治思想和哲学理论的代表作，中心是反对佛老、发挥儒家正统思想。",
        "options": ["佛老", "骈文", "科举", "藩镇"]}},
    {"ch": "隋唐五代文学", "mk": "古文", "q": {"stem": "下列不属于柳宗元《三戒》的是（　）", "type": "choice",
        "answer": "《捕蛇者说》", "explanation": "《三戒》包括《临江之麋》《黔之驴》《永某氏之鼠》三篇寓言，《捕蛇者说》是柳宗元另一篇散文。",
        "options": ["《捕蛇者说》", "《黔之驴》", "《临江之麋》", "《永某氏之鼠》"]}},
    {"ch": "隋唐五代文学", "mk": "变文", "q": {"stem": "唐代说唱文学“变文”是____的底本。", "type": "blank",
        "answer": "俗讲", "explanation": "变文是唐代民间说唱文学，为俗讲的底本，散文与韵文相结合，配有图画。",
        "options": []}},
    {"ch": "隋唐五代文学", "mk": "花间", "q": {"stem": "“花间派”因词集《____》得名，以温庭筠、韦庄为代表。", "type": "blank",
        "answer": "花间集", "explanation": "花间派以温庭筠、韦庄为代表，专写男女相思离别，因《花间集》得名。",
        "options": []}},
]

# ---------- 宋代 ----------
SDG = [
    {"ch": "宋代文学", "mk": "西昆", "q": {"stem": "宋初诗坛的“西昆体”因《____》得名，代表诗人有杨亿、刘筠等。", "type": "blank",
        "answer": "西昆酬唱集", "explanation": "西昆体因《西昆酬唱集》得名，师法李商隐诗的雕润密丽，呈现出整饬典丽的特征。",
        "options": []}},
    {"ch": "宋代文学", "mk": "豪放", "q": {"stem": "豪放词派的开创者是（　）", "type": "choice",
        "answer": "苏轼", "explanation": "苏轼是豪放派的开创者，冲破词的“艳科”范围，扩大了词的题材，境界雄奇阔大。",
        "options": ["苏轼", "柳永", "周邦彦", "秦观"]}},
    {"ch": "宋代文学", "mk": "江西", "q": {"stem": "“江西诗派”尊____为祖师，吕本中作《江西诗社宗派图》。", "type": "blank",
        "answer": "黄庭坚", "explanation": "江西诗派是中国历史上第一个有组织、有理论宗旨的诗歌流派，尊黄庭坚为师派之祖。",
        "options": []}},
    {"ch": "宋代文学", "mk": "婉约", "q": {"stem": "《鹊桥仙》（“纤云弄巧”）的作者是（　）", "type": "choice",
        "answer": "秦观", "explanation": "《鹊桥仙》（纤云弄巧）是北宋秦观的词作，歌颂牛郎织女坚贞不渝的爱情。",
        "options": ["秦观", "柳永", "晏殊", "周邦彦"]}},
    {"ch": "宋代文学", "mk": "李清照", "q": {"stem": "“词别是一家”是____在《词论》中提出的词学观点。", "type": "blank",
        "answer": "李清照", "explanation": "“词别是一家”是李清照在《词论》中提出的观点，强调词是与诗不同的独立抒情文体。",
        "options": []}},
    {"ch": "宋代文学", "mk": "四大诗人", "q": {"stem": "“诚斋体”是南宋诗人____所创，风格活泼自然、饶有谐趣。", "type": "blank",
        "answer": "杨万里", "explanation": "诚斋体是杨万里所创诗体，严羽《沧浪诗话》称之为“杨诚斋体”。",
        "options": []}},
    {"ch": "宋代文学", "mk": "四大诗人", "q": {"stem": "下列不属于“南宋中兴四大诗人”的是（　）", "type": "choice",
        "answer": "苏辙", "explanation": "南宋中兴四大诗人是尤袤、杨万里、范成大、陆游，又称南宋四大家。",
        "options": ["苏辙", "陆游", "杨万里", "范成大"]}},
    {"ch": "宋代文学", "mk": "辛弃疾", "q": {"stem": "辛派词人主要成员有陈亮、刘过和____。", "type": "blank",
        "answer": "刘克庄", "explanation": "辛派词人受辛弃疾影响形成，主要成员有陈亮、刘过、刘克庄等。",
        "options": []}},
    {"ch": "宋代文学", "mk": "姜夔", "q": {"stem": "南宋词论家张炎以“七宝楼台”比喻____的词。", "type": "blank",
        "answer": "吴文英", "explanation": "张炎《词源》称“吴梦窗词，如七宝楼台”，吴梦窗即吴文英。",
        "options": []}},
    {"ch": "宋代文学", "mk": "真题补充", "q": {"stem": "“文以载道”是宋代理学家____提出的文道关系主张。", "type": "blank",
        "answer": "周敦颐", "explanation": "“文以载道”由周敦颐提出，由韩愈“文以明道”发展而来，是古代对文学本质的重要论述。",
        "options": []}},
    {"ch": "宋代文学", "mk": "真题补充", "q": {"stem": "“文道一贯”是____倡导的文学观点，强调道是文之根本。", "type": "blank",
        "answer": "朱熹", "explanation": "朱熹倡导文道一贯，强调文道统一，认为道是文的根本，文是道的枝叶。",
        "options": []}},
    {"ch": "宋代文学", "mk": "四大诗人", "q": {"stem": "“永嘉四灵”指徐照、徐玑、赵师秀和____。", "type": "blank",
        "answer": "翁卷", "explanation": "永嘉四灵是南宋永嘉四位诗人徐照、徐玑、赵师秀、翁卷，因字中都带“灵”字得名。",
        "options": []}},
    {"ch": "宋代文学", "mk": "四大诗人", "q": {"stem": "“江湖诗派”因陈起刊刻的《____》得名。", "type": "blank",
        "answer": "江湖集", "explanation": "江湖诗派是南宋末年诗歌流派，因陈起刊刻《江湖集》得名，诗人多身份卑微。",
        "options": []}},
]

n = 0
for it in SD + SDG:
    mount(it['ch'], it['q'], it['mk'])
    n += 1

json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('第二批挂载', n, '题')
from collections import Counter
cc = Counter(k['chapter'] for k in KP['knowledge'])
print({c: cc[c] for c in cc})
