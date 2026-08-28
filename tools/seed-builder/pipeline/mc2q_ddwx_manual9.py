# -*- coding: utf-8 -*-
"""当代文学史 扩充第九批：继续扩充"""
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
    {"ch": "小说（80年代）", "kw": "伤痕文学", "q": {"stem": "伤痕文学的代表作家还有____（从维熙等）。", "type": "blank",
        "answer": "从维熙", "options": [],
        "explanation": "从维熙《大墙下的红玉兰》等也是伤痕文学代表。"}},
    {"ch": "小说（80年代）", "kw": "反思文学", "q": {"stem": "王蒙《布礼》是____（反思）文学代表作。", "type": "blank",
        "answer": "反思", "options": [],
        "explanation": "《布礼》写革命者在历史挫折中的反思，是反思文学代表作。"}},
    {"ch": "小说（80年代）", "kw": "改革文学", "q": {"stem": "改革文学中“工业改革”题材的代表是张洁《____》。", "type": "blank",
        "answer": "沉重的翅膀", "options": [],
        "explanation": "张洁《沉重的翅膀》写工业改革的艰难，是改革文学代表作。"}},
    {"ch": "小说（80年代）", "kw": "寻根文学", "q": {"stem": "寻根文学的宣言性文章是韩少功的《____》。", "type": "blank",
        "answer": "文学的“根”", "options": [],
        "explanation": "韩少功《文学的“根”》（1985）是寻根文学的宣言。"}},
    {"ch": "小说（80年代）", "kw": "新写实小说", "q": {"stem": "新写实小说代表作还有刘恒的《____》（狗日的粮食）。", "type": "blank",
        "answer": "狗日的粮食", "options": [],
        "explanation": "刘恒《狗日的粮食》写生存的原始与无奈，是新写实代表作。"}},
    {"ch": "小说（80年代）", "kw": "王蒙的意识流小说", "q": {"stem": "王蒙《蝴蝶》写____（老干部）的反思。", "type": "blank",
        "answer": "老干部（张思远）", "options": [],
        "explanation": "《蝴蝶》写老干部张思远的人生反思，融合意识流手法。"}},
    {"ch": "小说（90年代）", "kw": "新历史小说", "q": {"stem": "新历史小说代表作有苏童的《____》（妻妾成群）。", "type": "blank",
        "answer": "妻妾成群", "options": [],
        "explanation": "苏童《妻妾成群》写旧式家庭的女性命运，是新历史小说代表作。"}},
    {"ch": "小说（90年代）", "kw": "王安忆《长恨歌》", "q": {"stem": "《长恨歌》获第____届茅盾文学奖。", "type": "blank",
        "answer": "五", "options": [],
        "explanation": "《长恨歌》获第五届茅盾文学奖。"}},
    {"ch": "小说（90年代）", "kw": "王小波的小说", "q": {"stem": "王小波的杂文集代表作是《____》（沉默的大多数）。", "type": "blank",
        "answer": "沉默的大多数", "options": [],
        "explanation": "《沉默的大多数》是王小波杂文集，体现其独立思想。"}},
    {"ch": "小说（90年代）", "kw": "王朔的“顽主”与调侃", "q": {"stem": "王朔小说《动物凶猛》后被改编为电影《____》。", "type": "blank",
        "answer": "阳光灿烂的日子", "options": [],
        "explanation": "《动物凶猛》被姜文改编为电影《阳光灿烂的日子》。"}},
    {"ch": "新诗（80-90年代）", "kw": "朦胧诗", "q": {"stem": "朦胧诗在____（1978）年《今天》创刊后兴起。", "type": "blank",
        "answer": "1978", "options": [],
        "explanation": "1978年《今天》创刊，朦胧诗由此走向读者。"}},
    {"ch": "新诗（80-90年代）", "kw": "舒婷的诗歌", "q": {"stem": "舒婷《神女峰》表达了对____（传统贞操观）的反思。", "type": "blank",
        "answer": "传统贞操观（女性命运）", "options": [],
        "explanation": "《神女峰》以“与其在悬崖上展览千年，不如在爱人肩头痛哭一晚”反思女性命运。"}},
    {"ch": "新诗（80-90年代）", "kw": "海子的诗歌", "q": {"stem": "海子于____（1989）年去世。", "type": "blank",
        "answer": "1989", "options": [],
        "explanation": "海子1989年3月26日在山海关卧轨自杀。"}},
    {"ch": "新诗（80-90年代）", "kw": "顾城的诗歌", "q": {"stem": "顾城《远和近》写____（人际距离）的荒诞。", "type": "blank",
        "answer": "人际距离（心理距离）", "options": [],
        "explanation": "《远和近》以“你”“我”“云”写人际与自然的距离。"}},
    {"ch": "台港文学", "kw": "白先勇的小说", "q": {"stem": "白先勇小说集《台北人》共____（十四）篇。", "type": "blank",
        "answer": "十四", "options": [],
        "explanation": "《台北人》共收14个短篇，均写台北的大陆移民。"}},
    {"ch": "台港文学", "kw": "余光中的散文", "q": {"stem": "余光中自称“右手写诗，左手写____（散文）”。", "type": "blank",
        "answer": "散文", "options": [],
        "explanation": "余光中诗文双绝，自称右手写诗、左手写散文。"}},
    {"ch": "台港文学", "kw": "金庸小说的“雅”与“俗”", "q": {"stem": "金庸小说“飞雪连天射白鹿，笑书神侠倚碧鸳”共____（部）。", "type": "blank",
        "answer": "十四", "options": [],
        "explanation": "“飞雪连天射白鹿，笑书神侠倚碧鸳”涵盖金庸14部武侠小说。"}},
    {"ch": "2000-2016年文学", "kw": "贾平凹《秦腔》", "q": {"stem": "《秦腔》以____（秦腔）戏曲为文化符号。", "type": "blank",
        "answer": "秦腔", "options": [],
        "explanation": "《秦腔》以“秦腔”为文化符号，写乡村文化的衰落。"}},
    {"ch": "2000-2016年文学", "kw": "毕飞宇的小说", "q": {"stem": "毕飞宇《玉米》三部曲包括《玉米》《玉秀》和《____》。", "type": "blank",
        "answer": "玉秧", "options": [],
        "explanation": "《玉米》《玉秀》《玉秧》合称“玉米”三部曲。"}},
    {"ch": "2000-2016年文学", "kw": "李洱的小说", "q": {"stem": "李洱《石榴树上结樱桃》写____（乡村选举）。", "type": "blank",
        "answer": "乡村（换届选举）", "options": [],
        "explanation": "《石榴树上结樱桃》写农村基层民主选举的复杂现实。"}},
    {"ch": "2000-2016年文学", "kw": "打工文学与底层写作", "q": {"stem": "打工文学的代表作有____（《国家订单》）。", "type": "blank",
        "answer": "国家订单（王十月）", "options": [],
        "explanation": "王十月《国家订单》等是打工文学代表作。"}},
    {"ch": "散文（80-90年代）", "kw": "90年代“散文热”", "q": {"stem": "90年代散文的畅销与____（报刊副刊）发展有关。", "type": "blank",
        "answer": "报纸副刊（文化市场）", "options": [],
        "explanation": "90年代报刊副刊与文化市场繁荣，推动了“散文热”。"}},
    {"ch": "散文（80-90年代）", "kw": "悲悼散文", "q": {"stem": "张洁《世界上最疼我的那个人去了》是____（悲悼）散文。", "type": "blank",
        "answer": "悲悼（悼母）", "options": [],
        "explanation": "《世界上最疼我的那个人去了》悼念母亲，是悲悼散文名作。"}},
    {"ch": "散文（80-90年代）", "kw": "女性散文", "q": {"stem": "女性散文多书写____（女性）的生命经验。", "type": "blank",
        "answer": "女性（性别）", "options": [],
        "explanation": "女性散文以女性视角书写身体、情感与性别经验。"}},
    {"ch": "戏剧（80-90年代）", "kw": "高行健的戏剧", "q": {"stem": "高行健《野人》探索了____（多声部）舞台。", "type": "blank",
        "answer": "多声部（综合）", "options": [],
        "explanation": "《野人》综合歌舞、面具等，探索多声部戏剧。"}},
    {"ch": "戏剧（80-90年代）", "kw": "戏剧观讨论与探索戏剧", "q": {"stem": "探索戏剧代表作还有魏明伦的《____》（潘金莲）。", "type": "blank",
        "answer": "潘金莲", "options": [],
        "explanation": "魏明伦《潘金莲》以荒诞手法为潘金莲翻案，是探索戏剧代表作。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "清查“胡风反革命集团”及其文艺思想", "q": {"stem": "胡风提出的文艺观点是“____”（主观战斗精神）。", "type": "blank",
        "answer": "主观战斗精神", "options": [],
        "explanation": "胡风强调作家的“主观战斗精神”，主张“写真实”，遭批判。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "“双百方针”及其对文艺的影响", "q": {"stem": "“双百方针”提出后，出现了____（百花齐放）的局面。", "type": "blank",
        "answer": "百花齐放（短暂繁荣）", "options": [],
        "explanation": "“双百”时期文艺创作一度活跃，如《茶馆》等作品出现。"}},
    {"ch": "文学思潮（80-90年代）", "kw": "“方法年”“观念年”与“三论”", "q": {"stem": "“观念年”指1985年文学____（观念）的更新。", "type": "blank",
        "answer": "观念（批评方法）", "options": [],
        "explanation": "1985年前后被称“方法年”“观念年”，文学批评观念方法革新。"}},
    {"ch": "文学思潮（80-90年代）", "kw": "文学主体性讨论", "q": {"stem": "文学主体性讨论针对的是____（机械）反映论。", "type": "blank",
        "answer": "机械反映论（客体性）", "options": [],
        "explanation": "刘再复《论文学的主体性》批评机械反映论，强调创作主体性。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'当代第九批挂载 {n} 题')
