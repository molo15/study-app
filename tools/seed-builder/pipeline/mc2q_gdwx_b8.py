# -*- coding: utf-8 -*-
"""古代文学史 第八批扩充：核心考点补充（一祖三宗、词中老杜、续书等）"""
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
    {"ch": "宋代文学", "mk": "江西", "q": {"stem": "江西诗派的“一祖三宗”中，“一祖”指的是（　）", "type": "choice",
        "answer": "杜甫", "explanation": "江西诗派“一祖三宗”以杜甫为一祖，黄庭坚、陈师道、陈与义为三宗。",
        "options": ["杜甫", "李白", "韩愈", "陶渊明"]}},
    {"ch": "宋代文学", "mk": "周邦彦", "q": {"stem": "周邦彦因词艺精湛、长于格律，被称为“____”。", "type": "blank",
        "answer": "词中老杜", "explanation": "周邦彦词格律精严、章法多变，被后世称为“词中老杜”。",
        "options": []}},
    {"ch": "清代文学", "mk": "红楼梦", "q": {"stem": "《红楼梦》后四十回一般认为系____所续。", "type": "blank",
        "answer": "高鹗", "explanation": "《红楼梦》前八十回为曹雪芹作，后四十回一般认为由高鹗续成。",
        "options": []}},
    {"ch": "隋唐五代文学", "mk": "边塞", "q": {"stem": "王昌龄《出塞》“秦时明月汉时关，____”。", "type": "blank",
        "answer": "万里长征人未还", "explanation": "“秦时明月汉时关，万里长征人未还”出自王昌龄《出塞》，被誉为“七绝压卷之作”。",
        "options": []}},
    {"ch": "隋唐五代文学", "mk": "李贺与李商隐", "q": {"stem": "李贺《雁门太守行》“黑云压城城欲摧，____”。", "type": "blank",
        "answer": "甲光向日金鳞开", "explanation": "“黑云压城城欲摧，甲光向日金鳞开”出自李贺《雁门太守行》，写边关危局。",
        "options": []}},
    {"ch": "隋唐五代文学", "mk": "元白", "q": {"stem": "白居易《琵琶行》“同是天涯沦落人，____”。", "type": "blank",
        "answer": "相逢何必曾相识", "explanation": "“同是天涯沦落人，相逢何必曾相识”出自白居易《琵琶行》。",
        "options": []}},
    {"ch": "秦汉文学", "mk": "汉赋四大家", "q": {"stem": "下列不属于“汉赋四大家”的是（　）", "type": "choice",
        "answer": "贾谊", "explanation": "汉赋四大家是司马相如、扬雄、班固、张衡；贾谊是骚体赋代表，不在四大家之列。",
        "options": ["贾谊", "司马相如", "班固", "张衡"]}},
    {"ch": "隋唐五代文学", "mk": "李白", "q": {"stem": "李白诗歌中“日照香炉生紫烟”出自其《____》。", "type": "blank",
        "answer": "望庐山瀑布", "explanation": "“日照香炉生紫烟，遥看瀑布挂前川”出自李白《望庐山瀑布》。",
        "options": []}},
]

n = dup = 0
for it in Q:
    ok = mount(it['ch'], it['q'], it['mk'])
    n += ok
    dup += (not ok)
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'第八批挂载 {n} 题（跳过 {dup}）')
