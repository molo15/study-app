# -*- coding: utf-8 -*-
"""古代文学史 名词解释→基础题 挂载（第一批：先秦/秦汉/魏晋）
人工设计高质量直问直答基础题，挂载到对应章节知识点（匹配到则追加，否则归入章节真题补充点）。
"""
import io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

KP = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json', encoding='utf-8'))

def norm(s):
    return re.sub(r'[（）()。，、；：""“”\'  ]', '', s)

def kp_text(kp):
    return kp['name'] + (kp.get('summary') or '') + ''.join(q['stem'] for q in kp.get('basicQuestions', []))

def mount(chapter, q, match_kw):
    """挂载：优先匹配含 match_kw 的知识点，否则归入章节真题补充点"""
    kps = [k for k in KP['knowledge'] if k['chapter'] == chapter]
    best = None
    for k in kps:
        if match_kw and match_kw in kp_text(k):
            best = k
            break
    if best is not None:
        # 去重
        for exist in best.get('basicQuestions', []):
            if norm(exist['stem']) == norm(q['stem']):
                return
        best['basicQuestions'].append(q)
        return
    # 归入真题补充点
    zhen = None
    for k in kps:
        if '真题补充' in k['name']:
            zhen = k
            break
    if zhen is None:
        zhen = {"id": f"k_zhen_gdwx_{chapter.replace('（','').replace('）','')}",
                "name": f"{chapter}（真题补充）", "parent": "root", "chapter": chapter,
                "hot": False, "summary": "考研真题补充知识点，覆盖该章重要考点。", "basicQuestions": []}
        KP['knowledge'].append(zhen)
    for exist in zhen.get('basicQuestions', []):
        if norm(exist['stem']) == norm(q['stem']):
            return
    zhen['basicQuestions'].append(q)

# ================= 先秦 =================
XQ = [
    {"chapter": "先秦文学", "match": "诗", "q": {"stem": "《诗经》的“六义”是指风、雅、颂和（　）", "type": "choice",
        "answer": "赋、比、兴", "explanation": "“诗有六义”指风、雅、颂、赋、比、兴，前三者为体裁，后三者为表现手法。",
        "options": ["赋、比、兴", "赋、兴、观", "群、怨、观", "礼、乐、射"]}},
    {"chapter": "先秦文学", "match": "诗", "q": {"stem": "《诗经》中风、雅、颂的划分依据是（　）", "type": "choice",
        "answer": "音乐性质的不同", "explanation": "风雅颂是由音乐性质的不同划分而成的：《风》是各地民歌，《雅》是宫廷宴享乐歌，《颂》是祭祀乐歌。",
        "options": ["音乐性质的不同", "篇幅长短的不同", "作者身份的不同", "产生年代的不同"]}},
    {"chapter": "先秦文学", "match": "诗", "q": {"stem": "《诗经》“赋比兴”中“赋”的含义是（　）", "type": "choice",
        "answer": "平铺直叙、铺陈排比", "explanation": "“赋”是平铺直叙、铺陈排比，相当于排比修辞；“比”是比喻，“兴”是起兴。",
        "options": ["平铺直叙、铺陈排比", "托物起兴、借物抒情", "以彼物比此物", "先言他物以引起所咏之词"]}},
    {"chapter": "先秦文学", "match": "诗", "q": {"stem": "《诗经》中篇幅最长的诗篇是《____》", "type": "blank",
        "answer": "七月", "explanation": "《七月》是《诗经·国风》中的名篇，也是其中最长的一首诗，共八章八十八句。",
        "options": []}},
    {"chapter": "先秦文学", "match": "诗", "q": {"stem": "汉代“三家诗”指的是（　）", "type": "choice",
        "answer": "鲁诗、韩诗、齐诗", "explanation": "三家诗是《诗》学名词，为“鲁诗”“韩诗”“齐诗”的合称，汉代被立为博士。",
        "options": ["鲁诗、韩诗、齐诗", "毛诗、鲁诗、齐诗", "韩诗、毛诗、郑诗", "齐诗、赵诗、韩诗"]}},
    {"chapter": "先秦文学", "match": "左传", "q": {"stem": "“春秋三传”指的是（　）", "type": "choice",
        "answer": "《左传》《公羊传》《谷梁传》", "explanation": "春秋三传是《左氏春秋传》《春秋公羊传》《春秋谷梁传》的合称。",
        "options": ["《左传》《公羊传》《谷梁传》", "《左传》《国语》《战国策》", "《公羊传》《谷梁传》《尚书》", "《左传》《论语》《孟子》"]}},
    {"chapter": "先秦文学", "match": "左传", "q": {"stem": "《左传》的史书体例属于（　）", "type": "choice",
        "answer": "编年体", "explanation": "《左传》是一部成书于战国初期的编年体史书，旧传为左丘明所作。",
        "options": ["编年体", "纪传体", "国别体", "纪事本末体"]}},
    {"chapter": "先秦文学", "match": "左传", "q": {"stem": "“春秋笔法”又称“____”，即寓褒贬于曲折的文笔之中。", "type": "blank",
        "answer": "微言大义", "explanation": "春秋笔法又称“春秋书法”或“微言大义”，是孔子首创的寓褒贬于曲折文笔中的历史叙述方式。",
        "options": []}},
    {"chapter": "先秦文学", "match": "楚辞", "q": {"stem": "楚辞作为一种新诗体，又称（　）", "type": "choice",
        "answer": "骚体", "explanation": "楚辞是战国时产生于楚地、由屈原吸取楚神巫文化和民间歌谣特色创造的新诗体，又称骚体。",
        "options": ["骚体", "乐府", "近体诗", "词体"]}},
    {"chapter": "先秦文学", "match": "楚辞", "q": {"stem": "《楚辞·九歌》共____篇，是屈原据民间祭神乐歌改作而成。", "type": "blank",
        "answer": "十一", "explanation": "《九歌》共十一篇：《东皇太一》《云中君》《湘君》《湘夫人》《大司命》《少司命》《东君》《河伯》《山鬼》《国殇》《礼魂》。",
        "options": []}},
    {"chapter": "先秦文学", "match": "先秦", "q": {"stem": "“声音之道与政通”一语出自（　）", "type": "choice",
        "answer": "《乐记》", "explanation": "“声音之道与政通”是公孙尼子《乐记》中音乐政治化的阐释。",
        "options": ["《乐记》", "《诗大序》", "《文心雕龙》", "《毛诗序》"]}},
]

# ================= 秦汉 =================
QH = [
    {"chapter": "秦汉文学", "match": "赋", "q": {"stem": "汉赋中具有开拓意义和典范作用的代表作《子虚赋》《上林赋》的作者是（　）", "type": "choice",
        "answer": "司马相如", "explanation": "《子虚赋》《上林赋》是司马相如的代表作，也是汉赋中具有开拓意义的典范作品。",
        "options": ["司马相如", "枚乘", "班固", "贾谊"]}},
    {"chapter": "秦汉文学", "match": "赋", "q": {"stem": "“枚马”是西汉辞赋家____和司马相如的并称。", "type": "blank",
        "answer": "枚乘", "explanation": "“枚马”出自刘勰《文心雕龙·诠赋》，指枚乘与司马相如，二人都以工于辞赋著称。",
        "options": []}},
    {"chapter": "秦汉文学", "match": "赋", "q": {"stem": "标志新体赋——汉大赋正式形成的作品是枚乘的《____》", "type": "blank",
        "answer": "七发", "explanation": "枚乘《七发》的出现标志着新体赋——汉大赋正式形成。",
        "options": []}},
    {"chapter": "秦汉文学", "match": "汉乐府", "q": {"stem": "我国诗史上文人创作的第一首自传体五言长篇叙事诗是蔡文姬的《____》", "type": "blank",
        "answer": "悲愤诗", "explanation": "蔡文姬《悲愤诗》是我国诗史上文人创作的第一首自传体五言长篇叙事诗。",
        "options": []}},
    {"chapter": "秦汉文学", "match": "汉赋", "q": {"stem": "汉赋的体制特点是（　）", "type": "choice",
        "answer": "韵散兼行，介于诗歌和散文之间", "explanation": "汉赋是汉代的有韵散文，包括骚体赋、汉大赋和抒情小赋，韵散兼行，介于诗歌和散文之间。",
        "options": ["韵散兼行，介于诗歌和散文之间", "纯以韵语写成，讲究格律", "以散体为主，完全不押韵", "以对偶句式为主，辞采富丽"]}},
    {"chapter": "秦汉文学", "match": "都", "q": {"stem": "以都市为描写对象的“都城赋”最早产生于汉代，首创者是（　）", "type": "choice",
        "answer": "班固", "explanation": "都城赋又称都邑赋，最早产生于汉代，首创者是班固。",
        "options": ["班固", "司马相如", "张衡", "扬雄"]}},
    {"chapter": "秦汉文学", "match": "汉书", "q": {"stem": "我国现存最早的目录学文献是（　）", "type": "choice",
        "answer": "《汉书·艺文志》", "explanation": "《汉书·艺文志》由班固编纂，以刘歆《七略》为蓝本，是我国现存最早的目录学文献。",
        "options": ["《汉书·艺文志》", "《七略》", "《隋书·经籍志》", "《四库全书总目》"]}},
    {"chapter": "秦汉文学", "match": "古诗", "q": {"stem": "《古诗十九首》由南朝萧统编入（　）", "type": "choice",
        "answer": "《昭明文选》", "explanation": "南朝萧统从无名氏《古诗》中选录十九首编入《昭明文选》，即《古诗十九首》。",
        "options": ["《昭明文选》", "《玉台新咏》", "《乐府诗集》", "《古诗源》"]}},
]

# ================= 魏晋 =================
WJ = [
    {"chapter": "魏晋南北朝文学", "match": "建安", "q": {"stem": "“建安风骨”是对汉魏之际____等人诗文俊爽刚健风格的概括。", "type": "blank",
        "answer": "曹氏父子、建安七子", "explanation": "建安风骨是对汉魏之际曹氏父子、建安七子等人诗文俊爽刚健风格的概括。",
        "options": []}},
    {"chapter": "魏晋南北朝文学", "match": "建安", "q": {"stem": "下列不属于“建安七子”的是（　）", "type": "choice",
        "answer": "曹植", "explanation": "建安七子指孔融、陈琳、王粲、徐干、阮瑀、应玚、刘桢；曹植是“三曹”之一，不在七子之列。",
        "options": ["曹植", "王粲", "陈琳", "孔融"]}},
    {"chapter": "魏晋南北朝文学", "match": "曹植", "q": {"stem": "《赠白马王彪》的作者是（　）", "type": "choice",
        "answer": "曹植", "explanation": "《赠白马王彪》是曹植于黄初四年创作的一首抒情长诗。",
        "options": ["曹植", "曹丕", "曹彰", "曹操"]}},
    {"chapter": "魏晋南北朝文学", "match": "嵇康", "q": {"stem": "音乐美学论文《声无哀乐论》的作者是（　）", "type": "choice",
        "answer": "嵇康", "explanation": "《声无哀乐论》是魏晋时嵇康所作的音乐美学议论文。",
        "options": ["嵇康", "阮籍", "向秀", "刘伶"]}},
    {"chapter": "魏晋南北朝文学", "match": "太康", "q": {"stem": "“太康文学”以____为代表，诗风繁缛。", "type": "blank",
        "answer": "陆机、潘岳", "explanation": "“太康文学”指以陆机、潘岳为代表的西晋文学，表现出繁缛的诗风。",
        "options": []}},
    {"chapter": "魏晋南北朝文学", "match": "永明", "q": {"stem": "“永明体”又称（　）", "type": "choice",
        "answer": "新体诗", "explanation": "永明体是中国南朝齐武帝永明年间形成的诗体，又称新体诗，代表作家有谢朓、沈约、王融。",
        "options": ["新体诗", "近体诗", "宫体诗", "元嘉体"]}},
    {"chapter": "魏晋南北朝文学", "match": "徐庾", "q": {"stem": "“徐庾体”属于（　）诗风。", "type": "choice",
        "answer": "宫体诗", "explanation": "徐庾体指南朝梁徐、庾二家父子的诗风文体，他们都是宫体诗的代表作家，风格绮艳流丽。",
        "options": ["宫体诗", "田园诗", "边塞诗", "玄言诗"]}},
    {"chapter": "魏晋南北朝文学", "match": "元嘉", "q": {"stem": "“元嘉体”代表诗人有谢灵运、颜延之和（　）", "type": "choice",
        "answer": "鲍照", "explanation": "“元嘉体”之名始见于严羽《沧浪诗话》，用以概括谢灵运、颜延之和鲍照的诗风。",
        "options": ["鲍照", "谢朓", "沈约", "王融"]}},
    {"chapter": "魏晋南北朝文学", "match": "骈文", "q": {"stem": "骈文又称（　）", "type": "choice",
        "answer": "骈俪文", "explanation": "骈文是魏晋以来产生的与散文相对的文体，以四六句式为主、讲究对仗，又称骈俪文。",
        "options": ["骈俪文", "古文", "今文", "赋体文"]}},
    {"chapter": "魏晋南北朝文学", "match": "文选", "q": {"stem": "我国现存最早的诗文总集是（　）", "type": "choice",
        "answer": "《昭明文选》", "explanation": "《昭明文选》又称《文选》，由梁太子萧统组织编选，是中国现存最早的一部诗文总集。",
        "options": ["《昭明文选》", "《玉台新咏》", "《文心雕龙》", "《诗品》"]}},
    {"chapter": "魏晋南北朝文学", "match": "文心雕龙", "q": {"stem": "《文心雕龙》的作者是（　）", "type": "choice",
        "answer": "刘勰", "explanation": "《文心雕龙》是南朝刘勰创作的文学理论著作，是文学理论批评史上第一部有严密体系的专著。",
        "options": ["刘勰", "钟嵘", "萧统", "陆机"]}},
    {"chapter": "魏晋南北朝文学", "match": "搜神", "q": {"stem": "志怪小说集《搜神记》的作者是（　）", "type": "choice",
        "answer": "干宝", "explanation": "《搜神记》是东晋史学家干宝记录古代神奇怪异故事的志怪小说集。",
        "options": ["干宝", "刘义庆", "葛洪", "张华"]}},
    {"chapter": "魏晋南北朝文学", "match": "世说", "q": {"stem": "志人小说《世说新语》由____组织文人编写而成。", "type": "blank",
        "answer": "刘义庆", "explanation": "《世说新语》由南朝刘宋宗室临川王刘义庆组织一批文人编写，主要记述魏晋名士言谈轶事。",
        "options": []}},
]

n = 0
for item in XQ + QH + WJ:
    mount(item['chapter'], item['q'], item['match'])
    n += 1

json.dump(KP, open(r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'第一批挂载 {n} 题')
# 统计各章
from collections import Counter
cc = Counter(k['chapter'] for k in KP['knowledge'])
for ch in ['先秦文学', '秦汉文学', '魏晋南北朝文学']:
    print(ch, cc[ch], '知识点')
