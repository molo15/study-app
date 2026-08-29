# -*- coding: utf-8 -*-
"""当代文学史 第三批扩充：知名作家-作品对应"""
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
    # ---- 小说 80年代 ----
    {"ch": "小说（80年代）", "mk": "真题补充", "q": {"stem": "张洁的短篇小说《____》是新时期爱情题材小说的发轫之作。", "type": "blank",
        "answer": "爱，是不能忘记的", "explanation": "张洁《爱，是不能忘记的》大胆触及爱情与婚姻，是新时期爱情题材小说的先声。",
        "options": []}},
    {"ch": "小说（80年代）", "mk": "真题补充", "q": {"stem": "汪曾祺的小说《受戒》写小和尚____与农家女英子的纯真感情。", "type": "blank",
        "answer": "明海", "explanation": "汪曾祺《受戒》写小和尚明海与英子的朦胧恋情，语言冲淡，风格清新。",
        "options": []}},
    {"ch": "小说（80年代）", "mk": "真题补充", "q": {"stem": "阿城的小说《棋王》中的主人公是知青棋手____。", "type": "blank",
        "answer": "王一生", "explanation": "阿城《棋王》写知青王一生痴迷下棋，蕴含道家文化精神，是寻根文学代表作。",
        "options": []}},
    {"ch": "小说（80年代）", "mk": "真题补充", "q": {"stem": "韩少功的小说《____》是寻根文学的代表作。", "type": "blank",
        "answer": "爸爸爸", "explanation": "韩少功《爸爸爸》塑造了“丙崽”形象，反思民族文化，是寻根文学代表作。",
        "options": []}},
    {"ch": "小说（80年代）", "mk": "真题补充", "q": {"stem": "苏童的小说《妻妾成群》被改编成电影《____》。", "type": "blank",
        "answer": "大红灯笼高高挂", "explanation": "苏童《妻妾成群》写陈家大院妻妾争斗，被张艺谋改编为电影《大红灯笼高高挂》。",
        "options": []}},
    # ---- 小说 90年代 ----
    {"ch": "小说（90年代）", "mk": "真题补充", "q": {"stem": "刘震云的小说《一地鸡毛》写____的琐碎生活。", "type": "blank",
        "answer": "小林（小公务员）", "explanation": "《一地鸡毛》写小公务员林震一家柴米油盐的琐碎生活，是新写实小说的代表作。",
        "options": []}},
    {"ch": "小说（90年代）", "mk": "真题补充", "q": {"stem": "毕飞宇的长篇小说《推拿》以____群体为描写对象。", "type": "blank",
        "answer": "盲人推拿师", "explanation": "毕飞宇《推拿》写盲人推拿师群体的生存与尊严，获茅盾文学奖。",
        "options": []}},
    {"ch": "小说（90年代）", "mk": "真题补充", "q": {"stem": "新现实主义小说代表作家刘醒龙，其代表作是《____》。", "type": "blank",
        "answer": "分享艰难", "explanation": "刘醒龙《分享艰难》是新现实主义小说的代表作，写基层改革的艰难。",
        "options": []}},
    # ---- 戏剧 50-60 ----
    {"ch": "戏剧散文（50-60年代）", "mk": "历史剧", "q": {"stem": "60年代历史剧热潮中，郭沫若创作了历史剧《____》。", "type": "blank",
        "answer": "蔡文姬", "explanation": "郭沫若《蔡文姬》借古写今，是60年代历史剧热潮的代表作之一。",
        "options": []}},
    {"ch": "戏剧散文（50-60年代）", "mk": "真题补充", "q": {"stem": "60年代“社会主义教育剧”的代表作有《年青的一代》《____》等。", "type": "blank",
        "answer": "千万不要忘记", "explanation": "《千万不要忘记》《年青的一代》是60年代社会主义教育剧的代表作。",
        "options": []}},
    # ---- 新诗 80-90 ----
    {"ch": "新诗（80-90年代）", "mk": "真题补充", "q": {"stem": "“第三代诗歌”又称新生代诗歌，代表诗人有韩东、____等。", "type": "blank",
        "answer": "于坚", "explanation": "第三代诗歌代表诗人有韩东、于坚、杨黎等，主张回到日常口语。",
        "options": []}},
    # ---- 2000-2016 ----
    {"ch": "2000-2016年文学", "mk": "真题补充", "q": {"stem": "迟子建的长篇小说《____》以鄂温克族最后一个酋长女人的口吻写民族百年史。", "type": "blank",
        "answer": "额尔古纳河右岸", "explanation": "迟子建《额尔古纳河右岸》写鄂温克族的百年变迁，获茅盾文学奖。",
        "options": []}},
    {"ch": "2000-2016年文学", "mk": "真题补充", "q": {"stem": "严歌苓的长篇小说《陆犯焉识》写知识分子____的坎坷一生。", "type": "blank",
        "answer": "陆焉识", "explanation": "严歌苓《陆犯焉识》写知识分子陆焉识在历史动荡中的命运，后被改编为电影《归来》。",
        "options": []}},
    {"ch": "2000-2016年文学", "mk": "真题补充", "q": {"stem": "铁凝的短篇小说《____》写山村少女对现代文明的向往。", "type": "blank",
        "answer": "哦，香雪", "explanation": "铁凝《哦，香雪》写山村少女香雪对火车所代表的现代文明的向往。",
        "options": []}},
]

n = dup = 0
for it in Q:
    ok = mount(it['ch'], it['q'], it['mk'])
    n += ok
    dup += (not ok)
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'当代第三批挂载 {n} 题（跳过 {dup}）')
