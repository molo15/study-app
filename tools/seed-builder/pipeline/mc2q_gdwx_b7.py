# -*- coding: utf-8 -*-
"""古代文学史 第七批扩充：名句出处、别称号、作品细节等"""
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
            return False
    best['basicQuestions'].append(q)
    return True

Q = [
    # ---- 秦汉 ----
    {"ch": "秦汉文学", "mk": "乐府", "q": {"stem": "汉乐府“感于哀乐，____”，标志着中国叙事诗的成熟。", "type": "blank",
        "answer": "缘事而发", "explanation": "“感于哀乐，缘事而发”是汉乐府的基本精神，其叙事性标志着中国叙事诗的成熟。",
        "options": []}},
    {"ch": "秦汉文学", "mk": "乐府", "q": {"stem": "“乐府双璧”指《孔雀东南飞》和《____》。", "type": "blank",
        "answer": "木兰诗", "explanation": "《孔雀东南飞》与北朝民歌《木兰诗》并称“乐府双璧”。",
        "options": []}},
    # ---- 魏晋 ----
    {"ch": "魏晋南北朝文学", "mk": "鲍照", "q": {"stem": "鲍照在诗歌创作上成就最高的是____体。", "type": "blank",
        "answer": "七言歌行", "explanation": "鲍照大力创作七言歌行，其《拟行路难》对七言诗的发展有重大贡献。",
        "options": []}},
    {"ch": "魏晋南北朝文学", "mk": "谢朓", "q": {"stem": "谢朓名句“余霞散成绮，____”。", "type": "blank",
        "answer": "澄江静如练", "explanation": "“余霞散成绮，澄江静如练”出自谢朓《晚登三山还望京邑》。",
        "options": []}},
    # ---- 隋唐 ----
    {"ch": "隋唐五代文学", "mk": "杜甫", "q": {"stem": "杜甫名句“朱门酒肉臭，____”揭露贫富悬殊。", "type": "blank",
        "answer": "路有冻死骨", "explanation": "“朱门酒肉臭，路有冻死骨”出自杜甫《自京赴奉先县咏怀五百字》，控诉社会不公。",
        "options": []}},
    {"ch": "隋唐五代文学", "mk": "韩孟", "q": {"stem": "孟郊《游子吟》“谁言寸草心，____”。", "type": "blank",
        "answer": "报得三春晖", "explanation": "“谁言寸草心，报得三春晖”出自孟郊《游子吟》，歌颂母爱。",
        "options": []}},
    {"ch": "隋唐五代文学", "mk": "杜牧", "q": {"stem": "杜牧《山行》“停车坐爱枫林晚，____”。", "type": "blank",
        "answer": "霜叶红于二月花", "explanation": "“停车坐爱枫林晚，霜叶红于二月花”出自杜牧《山行》。",
        "options": []}},
    {"ch": "隋唐五代文学", "mk": "花间", "q": {"stem": "李煜《虞美人》“问君能有几多愁，____”。", "type": "blank",
        "answer": "恰似一江春水向东流", "explanation": "“问君能有几多愁，恰似一江春水向东流”是李煜《虞美人》名句。",
        "options": []}},
    # ---- 宋代 ----
    {"ch": "宋代文学", "mk": "江西", "q": {"stem": "黄庭坚提出的诗法主张是“点铁成金”和“____”。", "type": "blank",
        "answer": "夺胎换骨", "explanation": "黄庭坚主张“点铁成金”“夺胎换骨”，是江西诗派的重要诗法。",
        "options": []}},
    {"ch": "宋代文学", "mk": "四大诗人", "q": {"stem": "陆游临终名句“王师北定中原日，____”。", "type": "blank",
        "answer": "家祭无忘告乃翁", "explanation": "“王师北定中原日，家祭无忘告乃翁”出自陆游《示儿》，表现至死不渝的爱国情怀。",
        "options": []}},
    {"ch": "宋代文学", "mk": "苏轼", "q": {"stem": "苏轼《念奴娇·赤壁怀古》开篇名句“大江东去，____”。", "type": "blank",
        "answer": "浪淘尽", "explanation": "“大江东去，浪淘尽”是苏轼《念奴娇·赤壁怀古》开篇，是豪放词的代表作。",
        "options": []}},
    {"ch": "宋代文学", "mk": "柳永", "q": {"stem": "柳永《雨霖铃》名句“今宵酒醒何处？____”。", "type": "blank",
        "answer": "杨柳岸晓风残月", "explanation": "“今宵酒醒何处？杨柳岸晓风残月”是柳永《雨霖铃》名句，写别后孤寂。",
        "options": []}},
    # ---- 元代 ----
    {"ch": "元代文学", "mk": "元诗四大家", "q": {"stem": "“元诗四大家”指虞集、杨载、范梈和____。", "type": "blank",
        "answer": "揭傒斯", "explanation": "元诗四大家是虞集、杨载、范梈、揭傒斯，代表元代中期诗坛风气。",
        "options": []}},
    {"ch": "元代文学", "mk": "散曲", "q": {"stem": "马致远散曲代表作《天净沙·秋思》被称为“秋思之祖”，其名句是“____，断肠人在天涯”。", "type": "blank",
        "answer": "夕阳西下", "explanation": "《天净沙·秋思》“夕阳西下，断肠人在天涯”以萧瑟秋景烘托游子愁思，被称为“秋思之祖”。",
        "options": []}},
    # ---- 清代 ----
    {"ch": "清代文学", "mk": "戏曲", "q": {"stem": "《长生殿》的作者洪昇，《桃花扇》的作者____，二人并称“南洪北孔”。", "type": "blank",
        "answer": "孔尚任", "explanation": "洪昇作《长生殿》、孔尚任作《桃花扇》，并称“南洪北孔”。",
        "options": []}},
    {"ch": "清代文学", "mk": "桐城", "q": {"stem": "桐城派姚鼐提出文章的“____”说（义理、考据、辞章）。", "type": "blank",
        "answer": "义理考据辞章（三者统一）", "explanation": "姚鼐主张义理、考据、辞章三者统一，是桐城派文论的核心。",
        "options": []}},
    # ---- 近代 ----
    {"ch": "近代文学", "mk": "小说界革命", "q": {"stem": "黄遵宪倡导“我手写____”，主张诗歌口语化。", "type": "blank",
        "answer": "我口", "explanation": "黄遵宪提出“我手写我口”，主张以白话口语入诗，是诗界革命的重要主张。",
        "options": []}},
    # ---- 先秦 ----
    {"ch": "先秦文学", "mk": "庄子", "q": {"stem": "《庄子》现存共____篇。", "type": "blank",
        "answer": "三十三", "explanation": "《庄子》现存三十三篇，分内篇、外篇、杂篇，内篇一般认为庄子自著。",
        "options": []}},
    {"ch": "先秦文学", "mk": "尚书", "q": {"stem": "《尚书》又称《____》，分为《虞书》《夏书》《商书》《周书》。", "type": "blank",
        "answer": "书经（书）", "explanation": "《尚书》是我国第一部历史散文集，又称《书》或《书经》。",
        "options": []}},
]

n = 0
dup = 0
for it in Q:
    ok = mount(it['ch'], it['q'], it['mk'])
    if ok:
        n += 1
    else:
        dup += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'第七批挂载 {n} 题（跳过重复 {dup}）')
