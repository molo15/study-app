# -*- coding: utf-8 -*-
"""当代文学史 扩充第八批：继续扩充"""
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
    {"ch": "小说（80年代）", "kw": "路遥的小说", "q": {"stem": "路遥《人生》中的主人公是____。", "type": "blank",
        "answer": "高加林", "options": [],
        "explanation": "《人生》写农村青年高加林的人生抉择与爱情悲剧。"}},
    {"ch": "小说（80年代）", "kw": "高晓声的乡土小说", "q": {"stem": "高晓声以“____”系列写农民命运。", "type": "blank",
        "answer": "陈奂生", "options": [],
        "explanation": "高晓声《陈奂生上城》等“陈奂生系列”写改革开放初期的农民。"}},
    {"ch": "小说（80年代）", "kw": "陆文夫的小说", "q": {"stem": "陆文夫《围墙》是____（讽喻）小说。", "type": "blank",
        "answer": "讽喻（世情）", "options": [],
        "explanation": "《围墙》借修围墙讽喻世态，是陆文夫“小巷文学”代表作。"}},
    {"ch": "小说（80年代）", "kw": "余华的小说创作", "q": {"stem": "余华《在细雨中呼喊》是其____（转型）期作品。", "type": "blank",
        "answer": "转型（回归写实）", "options": [],
        "explanation": "《在细雨中呼喊》标志余华由先锋向写实转型。"}},
    {"ch": "小说（90年代）", "kw": "解构性女性写作：徐坤、斯妤", "q": {"stem": "徐坤的小说多写____（知识女性）困境。", "type": "blank",
        "answer": "知识女性", "options": [],
        "explanation": "徐坤以解构笔法写知识女性在男权话语中的困境。"}},
    {"ch": "小说（90年代）", "kw": "女性写作：陈染、林白", "q": {"stem": "陈染《私人生活》是____（女性）写作代表作。", "type": "blank",
        "answer": "女性（私人化）", "options": [],
        "explanation": "陈染《私人生活》写女性个体的私密经验，是私人化写作代表。"}},
    {"ch": "小说（90年代）", "kw": "王安忆《小鲍庄》", "q": {"stem": "《小鲍庄》写了“____”（仁义）精神。", "type": "blank",
        "answer": "仁义（仁义之村）", "options": [],
        "explanation": "《小鲍庄》以“仁义”为核心，写乡村伦理的坚守与困境。"}},
    {"ch": "小说（90年代）", "kw": "王小波的小说", "q": {"stem": "王小波的小说充满____（反讽）与荒诞。", "type": "blank",
        "answer": "反讽（智性）", "options": [],
        "explanation": "王小波以反讽、荒诞和智性书写历史与人性。"}},
    {"ch": "新诗（80-90年代）", "kw": "顾城的诗歌", "q": {"stem": "顾城《一代人》只有____（两）句。", "type": "blank",
        "answer": "两", "options": [],
        "explanation": "《一代人》全诗两句：“黑夜给了我黑色的眼睛，我却用它寻找光明。”"}},
    {"ch": "新诗（80-90年代）", "kw": "北岛的诗歌", "q": {"stem": "北岛《回答》写于____（1976）年前后。", "type": "blank",
        "answer": "1976", "options": [],
        "explanation": "《回答》写于1976年前后，是朦胧诗的代表作。"}},
    {"ch": "新诗（80-90年代）", "kw": "新生代诗人", "q": {"stem": "新生代诗主张“____”（回到日常）写作。", "type": "blank",
        "answer": "回到日常（反崇高）", "options": [],
        "explanation": "新生代诗人主张回到日常、消解崇高，如“他们”“莽汉”诗派。"}},
    {"ch": "新诗（50-60年代）", "kw": "贺敬之的诗歌创作", "q": {"stem": "贺敬之《放声歌唱》是____（政治抒情）诗。", "type": "blank",
        "answer": "政治抒情", "options": [],
        "explanation": "《放声歌唱》是贺敬之政治抒情诗代表作。"}},
    {"ch": "台港文学", "kw": "余光中的散文", "q": {"stem": "余光中散文《听听那冷雨》写____（冷雨）意象。", "type": "blank",
        "answer": "冷雨（乡愁）", "options": [],
        "explanation": "《听听那冷雨》以冷雨意象写乡愁与家国情怀。"}},
    {"ch": "台港文学", "kw": "金庸小说的文化底蕴与现代意识", "q": {"stem": "金庸小说《鹿鼎记》的主角是____。", "type": "blank",
        "answer": "韦小宝", "options": [],
        "explanation": "《鹿鼎记》主角韦小宝一反传统侠客形象，体现金庸的现代解构。"}},
    {"ch": "台港文学", "kw": "白先勇的小说", "q": {"stem": "白先勇被誉为____（台湾）现代派代表。", "type": "blank",
        "answer": "台湾", "options": [],
        "explanation": "白先勇是台湾现代派小说代表作家。"}},
    {"ch": "2000-2016年文学", "kw": "贾平凹《秦腔》", "q": {"stem": "《秦腔》的主人公是____。", "type": "blank",
        "answer": "张引生（引生）", "options": [],
        "explanation": "《秦腔》以“疯子”引生的视角写清风街的乡村变迁。"}},
    {"ch": "2000-2016年文学", "kw": "毕飞宇的小说", "q": {"stem": "毕飞宇《哺乳期的女人》写____（母亲）与孩子。", "type": "blank",
        "answer": "乡村女性（惠嫂）", "options": [],
        "explanation": "《哺乳期的女人》写乡村女性惠嫂与留守儿童旺旺，获鲁迅文学奖。"}},
    {"ch": "2000-2016年文学", "kw": "莫言《红高粱》", "q": {"stem": "《红高粱》改编的电影导演是____。", "type": "blank",
        "answer": "张艺谋", "options": [],
        "explanation": "《红高粱》1987年由张艺谋改编为电影，获柏林电影节金熊奖。"}},
    {"ch": "2000-2016年文学", "kw": "莫言的魔幻现实主义", "q": {"stem": "莫言《丰乳肥臀》以____（上官鲁氏）为主人公。", "type": "blank",
        "answer": "上官鲁氏", "options": [],
        "explanation": "《丰乳肥臀》写母亲上官鲁氏及其子女在历史中的命运。"}},
    {"ch": "散文（80-90年代）", "kw": "80年代散文家：孙犁、杨绛、陈白尘、汪曾祺", "q": {"stem": "汪曾祺的散文平实淡雅，如《____》。", "type": "blank",
        "answer": "葡萄月令", "options": [],
        "explanation": "汪曾祺《葡萄月令》等散文平淡有味，富生活气息。"}},
    {"ch": "散文（80-90年代）", "kw": "思想散文", "q": {"stem": "思想散文追求____（思辨）深度。", "type": "blank",
        "answer": "思辨（思想）", "options": [],
        "explanation": "思想散文以思想的深度和文化的反思见长。"}},
    {"ch": "散文（80-90年代）", "kw": "跨文体散文", "q": {"stem": "跨文体散文又称____（杂糅）文体散文。", "type": "blank",
        "answer": "杂糅（越界）", "options": [],
        "explanation": "跨文体散文融合多种文体因素，突破传统散文边界。"}},
    {"ch": "戏剧散文（50-60年代）", "kw": "杨朔的散文", "q": {"stem": "杨朔散文的经典写法是先写____（物）后抒情。", "type": "blank",
        "answer": "物（借物）", "options": [],
        "explanation": "杨朔散文常先写物（如荔枝蜜、茶花），再托物言志抒情。"}},
    {"ch": "戏剧散文（50-60年代）", "kw": "老舍《茶馆》", "q": {"stem": "《茶馆》的语言特色是____（京味）口语。", "type": "blank",
        "answer": "京味（北京口语）", "options": [],
        "explanation": "《茶馆》以地道的北京口语写活各色人物，京味浓郁。"}},
    {"ch": "戏剧散文（50-60年代）", "kw": "田汉《关汉卿》", "q": {"stem": "《关汉卿》写关汉卿创作《____》（窦娥冤）的故事。", "type": "blank",
        "answer": "窦娥冤", "options": [],
        "explanation": "《关汉卿》以关汉卿写作《窦娥冤》为线索，塑造为民请命的形象。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "对电影《武训传》的批判", "q": {"stem": "对《武训传》的批判拉开了____（文艺批判）运动的序幕。", "type": "blank",
        "answer": "文艺批判", "options": [],
        "explanation": "1951年对《武训传》的批判，是建国后首次大规模文艺批判运动。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "对俞平伯《红楼梦》研究的批判", "q": {"stem": "对《红楼梦研究》的批判主要针对____（红学）研究方法。", "type": "blank",
        "answer": "红学（考证方法）", "options": [],
        "explanation": "批判俞平伯的“自传说”等考证方法，引发红学研究转向。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "革命样板戏", "q": {"stem": "革命样板戏遵循“____”（三突出）原则。", "type": "blank",
        "answer": "三突出", "options": [],
        "explanation": "样板戏遵循“三突出”原则（突出正面人物等），是“文革”文艺规范。"}},
    {"ch": "文学思潮（80-90年代）", "kw": "“二十世纪中国文学”命题", "q": {"stem": "“二十世纪中国文学”的提出时间是____年。", "type": "blank",
        "answer": "1985", "options": [],
        "explanation": "1985年钱理群、黄子平、陈平原提出“二十世纪中国文学”命题。"}},
    {"ch": "文学思潮（80-90年代）", "kw": "“重写文学史”", "q": {"stem": "“重写文学史”主张重新评价____（文学史）定论。", "type": "blank",
        "answer": "文学史（既有定论）", "options": [],
        "explanation": "“重写文学史”反思既有文学史叙述，重新评价作家作品。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'当代第八批挂载 {n} 题')
