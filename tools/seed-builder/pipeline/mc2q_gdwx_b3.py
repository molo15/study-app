# -*- coding: utf-8 -*-
"""古代文学史 名词解释→基础题 第三批（元代/明代/清代/近代）"""
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

# ---------- 元代 ----------
YD = [
    {"ch": "元代文学", "mk": "元杂剧", "q": {"stem": "“诸宫调”因____而得名，是宋金元时期的大型说唱文学。", "type": "choice",
        "answer": "集若干套不同宫调的曲子轮递歌唱", "explanation": "诸宫调从变文和教坊大曲、杂曲基础上发展而来，因集若干套不同宫调的曲子轮递歌唱得名。",
        "options": ["集若干套不同宫调的曲子轮递歌唱", "用同一宫调演唱全篇", "以琵琶独奏为主", "只说不唱"]}},
    {"ch": "元代文学", "mk": "四大悲剧", "q": {"stem": "元杂剧《汉宫秋》的作者是（　）", "type": "choice",
        "answer": "马致远", "explanation": "《汉宫秋》是马致远的历史剧，为元朝四大悲剧之一，写汉元帝被迫送王昭君出塞和亲。",
        "options": ["马致远", "关汉卿", "白朴", "郑光祖"]}},
    {"ch": "元代文学", "mk": "元杂剧", "q": {"stem": "下列不属于“元曲四大家”的是（　）", "type": "choice",
        "answer": "王实甫", "explanation": "元曲四大家指关汉卿、白朴、马致远、郑光祖；王实甫虽为著名杂剧家但不在四大家之列。",
        "options": ["王实甫", "关汉卿", "白朴", "郑光祖"]}},
    {"ch": "元代文学", "mk": "元杂剧", "q": {"stem": "元杂剧的剧本体制一般由“____”构成。", "type": "blank",
        "answer": "四折一楔子", "explanation": "元杂剧主要由“四折一楔子”构成，一折用同一宫调的一套曲子，由一人主唱。",
        "options": []}},
    {"ch": "元代文学", "mk": "南戏", "q": {"stem": "南戏是中国戏剧最早的成熟形式之一，兴起于北宋末至元末明初，又称（　）", "type": "choice",
        "answer": "温州杂剧（永嘉杂剧）", "explanation": "南戏有多种异名，南方称戏文，又有温州杂剧、永嘉杂剧、南曲戏文等名称。",
        "options": ["温州杂剧（永嘉杂剧）", "北杂剧", "诸宫调", "传奇折子戏"]}},
    {"ch": "元代文学", "mk": "元诗", "q": {"stem": "“铁崖体”是元代诗人____创造的诗体。", "type": "blank",
        "answer": "杨维桢", "explanation": "铁崖为杨维桢的号，他追求构思超乎寻常、意境奇特非凡，创造了铁崖体。",
        "options": []}},
]

# ---------- 明代 ----------
MD = [
    {"ch": "明代文学", "mk": "章回", "q": {"stem": "章回小说的基本特点是（　）", "type": "choice",
        "answer": "分回标目，故事连接，段落整齐", "explanation": "章回小说是明代产生的中国古典长篇小说民族形式，特点是分回标目、故事连接、段落整齐。",
        "options": ["分回标目，故事连接，段落整齐", "以散体为主，不分章节", "以韵文为主，讲究格律", "按时间顺序连续叙事，无回目"]}},
    {"ch": "明代文学", "mk": "徐渭", "q": {"stem": "《四声猿》是明代____创作的一组杂剧。", "type": "blank",
        "answer": "徐渭", "explanation": "《四声猿》是徐渭的杂剧，包括《渔阳弄》《雌木兰》《女状元》《翠乡梦》四剧。",
        "options": []}},
    {"ch": "明代文学", "mk": "传奇", "q": {"stem": "明传奇是由宋元____发展而来的中长篇戏曲。", "type": "choice",
        "answer": "南戏", "explanation": "明传奇由宋元南戏发展而来，是明代戏曲的主体，以南曲演唱为主。",
        "options": ["南戏", "元杂剧", "诸宫调", "院本"]}},
    {"ch": "明代文学", "mk": "传奇", "q": {"stem": "“明中叶三大传奇”是《宝剑记》《____》《鸣凤记》。", "type": "blank",
        "answer": "浣纱记", "explanation": "明中叶三大传奇是李开先《宝剑记》、梁辰鱼《浣纱记》和王世贞《鸣凤记》的合称。",
        "options": []}},
    {"ch": "明代文学", "mk": "汤显祖", "q": {"stem": "“汤沈之争”是指汤显祖与沈璟围绕____产生的分歧。", "type": "choice",
        "answer": "曲律", "explanation": "汤沈之争围绕曲律展开：汤显祖重剧作曲意，可突破格律；沈璟注重严守音律。",
        "options": ["曲律", "题材", "语言风格", "表演形式"]}},
    {"ch": "明代文学", "mk": "汤显祖", "q": {"stem": "下列不属于“临川四梦”的是（　）", "type": "choice",
        "answer": "《浣纱记》", "explanation": "临川四梦是汤显祖《牡丹亭》《紫钗记》《邯郸记》《南柯记》四剧的合称。",
        "options": ["《浣纱记》", "《牡丹亭》", "《紫钗记》", "《南柯记》"]}},
    {"ch": "明代文学", "mk": "西游", "q": {"stem": "鲁迅认为明朝小说创作两大主潮之一是以《西游记》《封神传》为代表的（　）", "type": "choice",
        "answer": "神魔小说", "explanation": "神魔小说以讲神魔之争为内容，《西游记》《封神传》为代表作。",
        "options": ["神魔小说", "世情小说", "历史演义小说", "公案小说"]}},
    {"ch": "明代文学", "mk": "真题补充", "q": {"stem": "“明代四大奇书”指的是（　）", "type": "choice",
        "answer": "《三国演义》《水浒传》《西游记》《金瓶梅》", "explanation": "明代四大奇书是《三国演义》《水浒传》《西游记》《金瓶梅》四部长篇章回小说。",
        "options": ["《三国演义》《水浒传》《西游记》《金瓶梅》", "《三国演义》《水浒传》《西游记》《红楼梦》", "《西厢记》《琵琶记》《牡丹亭》《长生殿》", "《三国演义》《水浒传》《金瓶梅》《红楼梦》"]}},
    {"ch": "明代文学", "mk": "拟话本", "q": {"stem": "“拟话本”是文人模仿____形式编写的小说。", "type": "blank",
        "answer": "话本", "explanation": "拟话本由文人模仿话本形式编写，鲁迅在《中国小说史略》中最先应用这一术语。",
        "options": []}},
    {"ch": "明代文学", "mk": "诗文流派", "q": {"stem": "“童心说”是明代思想家____提出的文学观念。", "type": "blank",
        "answer": "李贽", "explanation": "童心说是李贽提出的文学观念，认为文学作品必须真实坦率地表露作者内心的真实感情。",
        "options": []}},
]

# ---------- 清代 ----------
QD = [
    {"ch": "清代文学", "mk": "纳兰", "q": {"stem": "清代词人纳兰性德的词集名为《____》。", "type": "blank",
        "answer": "饮水词", "explanation": "纳兰性德是清代最著名词人之一，其“纳兰词”集名《饮水词》，在中国词坛享有很高声誉。",
        "options": []}},
    {"ch": "清代文学", "mk": "诗文词派", "q": {"stem": "浙西词派的创始者是____。", "type": "blank",
        "answer": "朱彝尊", "explanation": "浙西词派是清代前期最大的词派，创始者朱彝尊及主要作者都是浙江人，故得名。",
        "options": []}},
    {"ch": "清代文学", "mk": "戏曲", "q": {"stem": "“结构第一”是李渔戏曲理论的经典命题，出自《____》。", "type": "blank",
        "answer": "闲情偶寄", "explanation": "“结构第一”出自李渔《闲情偶寄》，是李渔戏曲理论的核心观点。",
        "options": []}},
    {"ch": "清代文学", "mk": "戏曲", "q": {"stem": "“南洪北孔”指的是清初剧作家（　）", "type": "choice",
        "answer": "洪昇和孔尚任", "explanation": "“南洪北孔”指洪昇（浙江人）与孔尚任（山东人），代表作分别为《长生殿》《桃花扇》。",
        "options": ["洪昇和孔尚任", "洪昇和汤显祖", "孔尚任和李渔", "李渔和蒋士铨"]}},
    {"ch": "清代文学", "mk": "桐城", "q": {"stem": "“桐城中兴”运动是____为使桐城派适应时代需求而进行的革新。", "type": "blank",
        "answer": "曾国藩", "explanation": "“桐城中兴”是曾国藩为革新桐城派而进行的运动，强调经世致用。",
        "options": []}},
    {"ch": "清代文学", "mk": "诗文词派", "q": {"stem": "常州词派由清代常州词人____所开创。", "type": "blank",
        "answer": "张惠言", "explanation": "常州词派是清代嘉庆以后的重要词派，由张惠言开创，周济加以发展。",
        "options": []}},
    {"ch": "清代文学", "mk": "诗文词派", "q": {"stem": "“性灵说”是中国古代诗论主张，以清代____倡导最力。", "type": "choice",
        "answer": "袁枚", "explanation": "性灵说以袁枚倡导最力，要求诗歌表现真性情，与神韵说、格调说、肌理说并为清代前期四大诗论派别。",
        "options": ["袁枚", "王士禛", "沈德潜", "翁方纲"]}},
]

# ---------- 近代 ----------
JD = [
    {"ch": "近代文学", "mk": "龚自珍", "q": {"stem": "《己亥杂诗》的作者是（　）", "type": "choice",
        "answer": "龚自珍", "explanation": "《己亥杂诗》是龚自珍创作的一组诗集，他是近代历史开端之际得风气之先的启蒙思想家。",
        "options": ["龚自珍", "魏源", "黄遵宪", "梁启超"]}},
    {"ch": "近代文学", "mk": "梁启超", "q": {"stem": "近代诗话著作《饮冰室诗话》的作者是____。", "type": "blank",
        "answer": "梁启超", "explanation": "《饮冰室诗话》是梁启超著，论诗首重“新意境”。",
        "options": []}},
    {"ch": "近代文学", "mk": "小说界革命", "q": {"stem": "“熏浸刺提”是____提出的关于新小说的文学主张。", "type": "blank",
        "answer": "梁启超", "explanation": "“熏浸刺提”语出梁启超《小说与群治之关系》，是他提出的新小说主张。",
        "options": []}},
    {"ch": "近代文学", "mk": "南社", "q": {"stem": "文学团体“南社”1909年成立于____。", "type": "blank",
        "answer": "苏州", "explanation": "南社发端于辛亥革命前后，1909年成立于苏州，主要作家有柳亚子、陈去病、高旭等。",
        "options": []}},
    {"ch": "近代文学", "mk": "谴责小说", "q": {"stem": "谴责小说的特点是“辞气浮露，____”。", "type": "choice",
        "answer": "笔无藏锋", "explanation": "谴责小说暴露社会黑暗、指责政治腐败，特点是“辞气浮露，笔无藏锋”。",
        "options": ["笔无藏锋", "委婉含蓄", "温柔敦厚", "微言大义"]}},
]

n = 0
for it in YD + MD + QD + JD:
    mount(it['ch'], it['q'], it['mk'])
    n += 1

json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('第三批挂载', n, '题')
from collections import Counter
cc = Counter()
for k in KP['knowledge']:
    cc[k['chapter']] += len(k.get('basicQuestions', []))
print(cc)
