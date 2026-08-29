# -*- coding: utf-8 -*-
"""当代文学史 扩充第一批：薄弱点补充"""
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
    {"ch": "2000-2016年文学", "kw": "网络诗歌", "q": {"stem": "网络诗歌的主要传播平台是____。", "type": "blank",
        "answer": "网络论坛（博客）", "options": [],
        "explanation": "网络诗歌以论坛、博客、网站为主要发表与传播平台，打破了纸质媒介的限制。"}},
    {"ch": "2000-2016年文学", "kw": "李洱的小说", "q": {"stem": "长篇小说《花腔》的作者是____。", "type": "blank",
        "answer": "李洱", "options": [],
        "explanation": "李洱《花腔》以多声部叙事重构历史，是其代表作。"}},
    {"ch": "2000-2016年文学", "kw": "金宇澄《繁花》", "q": {"stem": "金宇澄《繁花》用____方言写成，别有韵味。", "type": "blank",
        "answer": "上海话（沪语）", "options": [],
        "explanation": "《繁花》以上海方言入文，极具地域色彩，获茅盾文学奖。"}},
    {"ch": "2000-2016年文学", "kw": "2000年后的戏剧与底层诗歌写作", "q": {"stem": "2000年后的底层诗歌写作关注____群体的生存状态。", "type": "blank",
        "answer": "底层（农民工等）", "options": [],
        "explanation": "新世纪底层诗歌聚焦底层民众的生存与尊严，如“打工诗歌”。"}},
    {"ch": "台港文学", "kw": "余光中的散文", "q": {"stem": "余光中散文的代表作是《____》。", "type": "blank",
        "answer": "听听那冷雨", "options": [],
        "explanation": "《听听那冷雨》写雨与乡愁，是余光中散文名篇。"}},
    {"ch": "台港文学", "kw": "金庸小说的“雅”与“俗”", "q": {"stem": "金庸第一部新武侠小说是《____》。", "type": "blank",
        "answer": "书剑恩仇录", "options": [],
        "explanation": "《书剑恩仇录》开创金庸新武侠，兼具“雅”与“俗”品格。"}},
    {"ch": "小说（50-60年代）", "kw": "十七年小说的两大主题", "q": {"stem": "十七年小说的两大主题是革命历史题材和____题材。", "type": "blank",
        "answer": "农村（社会主义）建设", "options": [],
        "explanation": "十七年小说两大主题：革命历史斗争与农村社会主义改造建设。"}},
    {"ch": "小说（50-60年代）", "kw": "赵树理《“锻炼锻炼”》", "q": {"stem": "赵树理《“锻炼锻炼”》是____题材小说。", "type": "blank",
        "answer": "农村", "options": [],
        "explanation": "《“锻炼锻炼”》写农村整风与社员改造，属农村题材。"}},
    {"ch": "小说（50-60年代）", "kw": "历史题材的曲喻创作", "q": {"stem": "姚雪垠《李自成》是____题材长篇历史小说。", "type": "blank",
        "answer": "历史（明末农民战争）", "options": [],
        "explanation": "《李自成》以明末农民战争为题材，是十七年历史小说的代表。"}},
    {"ch": "小说（80年代）", "kw": "张承志的小说", "q": {"stem": "张承志《黑骏马》以____草原生活为题材。", "type": "blank",
        "answer": "蒙古族（草原）", "options": [],
        "explanation": "《黑骏马》写蒙古族牧民生活与心灵世界，是张承志代表作。"}},
    {"ch": "小说（90年代）", "kw": "新现实主义小说", "q": {"stem": "“新现实主义小说”的代表作家有谈歌、何申、____。", "type": "blank",
        "answer": "关仁山", "options": [],
        "explanation": "谈歌、何申、关仁山被称为“河北三驾马车”，是新现实主义小说的代表。"}},
    {"ch": "小说（90年代）", "kw": "解构性女性写作：徐坤、斯妤", "q": {"stem": "徐坤、斯妤的创作属于____写作。", "type": "blank",
        "answer": "解构性女性", "options": [],
        "explanation": "徐坤、斯妤以解构方式书写女性经验，属解构性女性写作。"}},
    {"ch": "戏剧散文（50-60年代）", "kw": "50、60年代戏剧的发展阶段", "q": {"stem": "50年代话剧的代表作是老舍的《____》。", "type": "blank",
        "answer": "茶馆", "options": [],
        "explanation": "老舍《茶馆》是50年代话剧的高峰，被誉为“半个世纪的时代图景”。"}},
    {"ch": "戏剧散文（50-60年代）", "kw": "“社会主义教育剧”", "q": {"stem": "“社会主义教育剧”的代表作有《____》。", "type": "blank",
        "answer": "年青的一代", "options": [],
        "explanation": "《年青的一代》《千万不要忘记》等是60年代“社会主义教育剧”代表作。"}},
    {"ch": "戏剧散文（50-60年代）", "kw": "历史剧热潮", "q": {"stem": "60年代历史剧的代表作是田汉的《____》。", "type": "blank",
        "answer": "关汉卿", "options": [],
        "explanation": "田汉《关汉卿》借历史题材抒写现实情怀，是历史剧名作。"}},
    {"ch": "戏剧散文（50-60年代）", "kw": "刘白羽的散文", "q": {"stem": "刘白羽的散文集有《____》。", "type": "blank",
        "answer": "红玛瑙集", "options": [],
        "explanation": "刘白羽散文雄浑壮阔，《红玛瑙集》是其代表作。"}},
    {"ch": "散文（80-90年代）", "kw": "思想散文", "q": {"stem": "思想散文（学者散文）的代表作家有____。", "type": "blank",
        "answer": "余秋雨", "options": [],
        "explanation": "余秋雨《文化苦旅》等以历史文化反思见长，是思想散文代表。"}},
    {"ch": "散文（80-90年代）", "kw": "90年代“散文热”", "q": {"stem": "90年代“散文热”与____（随笔）创作大兴有关。", "type": "blank",
        "answer": "随笔（学者散文）", "options": [],
        "explanation": "90年代随笔、文化散文大量涌现，形成“散文热”现象。"}},
    {"ch": "散文（80-90年代）", "kw": "女性散文", "q": {"stem": "女性散文的代表作家有张洁、铁凝、____。", "type": "blank",
        "answer": "王安忆", "options": [],
        "explanation": "张洁、铁凝、王安忆等以女性视角书写散文，是女性散文代表。"}},
    {"ch": "散文（80-90年代）", "kw": "悲悼散文", "q": {"stem": "以怀念故人、寄托哀思为内容的散文称为____散文。", "type": "blank",
        "answer": "悲悼", "options": [],
        "explanation": "悲悼散文写悼念追思，如巴金《怀念萧珊》。"}},
    {"ch": "散文（80-90年代）", "kw": "跨文体散文", "q": {"stem": "跨文体散文打破了____之间的界限。", "type": "blank",
        "answer": "文体（体裁）", "options": [],
        "explanation": "跨文体散文融合小说、诗歌、评论等因素，突破传统文体边界。"}},
    {"ch": "文学思潮（80-90年代）", "kw": "“二十世纪中国文学”命题", "q": {"stem": "“二十世纪中国文学”概念由钱理群、黄子平、____提出。", "type": "blank",
        "answer": "陈平原", "options": [],
        "explanation": "1985年钱理群、黄子平、陈平原提出“二十世纪中国文学”命题。"}},
    {"ch": "文学思潮（80-90年代）", "kw": "新状态文学", "q": {"stem": "“新状态文学”的倡导主要在____年代。", "type": "blank",
        "answer": "90", "options": [],
        "explanation": "“新状态文学”是90年代中期提出的文学思潮概念。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "“文革”时期文学思潮的本质", "q": {"stem": "“文革”时期文学思潮的本质是文学高度____化。", "type": "blank",
        "answer": "政治（工具）", "options": [],
        "explanation": "“文革”时期文学沦为政治工具，创作规范极端政治化。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "第二次全国文代会", "q": {"stem": "1953年第二次文代会确立了____的文艺方向。", "type": "blank",
        "answer": "社会主义现实主义", "options": [],
        "explanation": "第二次文代会把社会主义现实主义确立为创作与批评的最高准则。"}},
    {"ch": "新诗（50-60年代）", "kw": "新生活叙事诗", "q": {"stem": "50年代“新生活叙事诗”的代表作是《____》。", "type": "blank",
        "answer": "放声歌唱", "options": [],
        "explanation": "贺敬之《放声歌唱》等政治抒情诗，是新生活叙事诗的代表。"}},
    {"ch": "新诗（80-90年代）", "kw": "“归来”诗人", "q": {"stem": "“归来”诗人包括艾青、流沙河、____。", "type": "blank",
        "answer": "公刘", "options": [],
        "explanation": "“归来”诗人指新时期复出的艾青、流沙河、公刘等。"}},
    {"ch": "新诗（80-90年代）", "kw": "北岛的诗歌", "q": {"stem": "北岛诗句“卑鄙是卑鄙者的通行证”出自《____》。", "type": "blank",
        "answer": "回答", "options": [],
        "explanation": "《回答》是北岛代表作，“卑鄙是卑鄙者的通行证”为名句。"}},
    {"ch": "新诗（80-90年代）", "kw": "顾城的诗歌", "q": {"stem": "顾城被称为“____诗人”，诗风纯净。", "type": "blank",
        "answer": "童话", "options": [],
        "explanation": "顾城以童话般的纯净诗风著称，被称为“童话诗人”。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'当代第一批挂载 {n} 题')
