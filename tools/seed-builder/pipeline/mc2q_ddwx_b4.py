# -*- coding: utf-8 -*-
"""当代文学史 第四批扩充：流派与经典考点"""
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
    # ---- 小说 50-60 ----
    {"ch": "小说（50-60年代）", "mk": "真题补充", "q": {"stem": "十七年革命历史长篇小说“三红一创”指《红日》《红岩》《红旗谱》和《____》。", "type": "blank",
        "answer": "创业史", "explanation": "“三红一创”指《红日》《红岩》《红旗谱》《创业史》，是十七年长篇小说代表作。",
        "options": []}},
    {"ch": "小说（50-60年代）", "mk": "山药蛋派", "q": {"stem": "与“山药蛋派”相对、以孙犁为代表的散文诗化小说流派是“____派”。", "type": "blank",
        "answer": "荷花淀", "explanation": "以孙犁为代表的“荷花淀派”追求散文诗化的小说风格，代表作家有刘绍棠、从维熙等。",
        "options": []}},
    # ---- 小说 80 ----
    {"ch": "小说（80年代）", "mk": "真题补充", "q": {"stem": "先锋小说的代表作家有苏童、格非、____等。", "type": "blank",
        "answer": "余华", "explanation": "先锋小说代表作家有马原、苏童、格非、余华、孙甘露等，重形式探索。",
        "options": []}},
    {"ch": "小说（80年代）", "mk": "真题补充", "q": {"stem": "莫言的小说《____》以“高密东北乡”为背景写抗日传奇。", "type": "blank",
        "answer": "红高粱家族", "explanation": "莫言《红高粱家族》以高密东北乡为背景，写“我爷爷”“我奶奶”的抗日故事。",
        "options": []}},
    {"ch": "小说（90年代）", "mk": "真题补充", "q": {"stem": "新写实小说的代表作家有刘震云、池莉、____等。", "type": "blank",
        "answer": "方方", "explanation": "新写实小说代表作家有刘震云、池莉、方方、刘恒等，写凡人琐事的原生状态。",
        "options": []}},
    {"ch": "小说（90年代）", "mk": "贾平凹", "q": {"stem": "陈忠实的长篇小说《____》写白、鹿两家的恩怨与宗法文化。", "type": "blank",
        "answer": "白鹿原", "explanation": "陈忠实《白鹿原》以白、鹿两家故事写宗法文化与历史变迁，获茅盾文学奖。",
        "options": []}},
    # ---- 台港 ----
    {"ch": "台港文学", "mk": "真题补充", "q": {"stem": "林海音的小说《____》以北平城南童年往事为题材。", "type": "blank",
        "answer": "城南旧事", "explanation": "林海音《城南旧事》写北平城南的童年记忆，后被改编为同名电影。",
        "options": []}},
    # ---- 2000-2016 ----
    {"ch": "2000-2016年文学", "mk": "真题补充", "q": {"stem": "刘慈欣的长篇科幻小说《____》获雨果奖。", "type": "blank",
        "answer": "三体", "explanation": "刘慈欣《三体》获2015年雨果奖最佳长篇小说奖，是中国科幻文学的里程碑。",
        "options": []}},
    {"ch": "2000-2016年文学", "mk": "真题补充", "q": {"stem": "“80后”文学的代表作家有韩寒、郭敬明、____等。", "type": "blank",
        "answer": "张悦然", "explanation": "80后作家以韩寒、郭敬明、张悦然、安妮宝贝等为代表，多写都市青春经验。",
        "options": []}},
    {"ch": "2000-2016年文学", "mk": "真题补充", "q": {"stem": "阎连科的长篇小说《____》获2014年卡夫卡文学奖。", "type": "blank",
        "answer": "炸裂志", "explanation": "阎连科《炸裂志》获2014年卡夫卡文学奖，是其“神实主义”代表作。",
        "options": []}},
]

n = dup = 0
for it in Q:
    ok = mount(it['ch'], it['q'], it['mk'])
    n += ok
    dup += (not ok)
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'当代第四批挂载 {n} 题（跳过 {dup}）')
