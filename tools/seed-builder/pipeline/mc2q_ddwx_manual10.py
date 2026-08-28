# -*- coding: utf-8 -*-
"""当代文学史 扩充第十批：收官"""
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
    {"ch": "小说（80年代）", "kw": "寻根文学", "q": {"stem": "寻根文学代表作还有莫言的《____》。", "type": "blank",
        "answer": "红高粱", "options": [],
        "explanation": "《红高粱》写“高密东北乡”的民间抗日，兼具寻根与新历史意味。"}},
    {"ch": "小说（80年代）", "kw": "新写实小说", "q": {"stem": "新写实小说代表作还有方方的《____》。", "type": "blank",
        "answer": "风景", "options": [],
        "explanation": "方方《风景》写武汉码头家庭的苦难，是新写实代表作。"}},
    {"ch": "小说（80年代）", "kw": "余华的小说创作", "q": {"stem": "余华《兄弟》写____兄弟情。", "type": "blank",
        "answer": "李光头与宋钢", "options": [],
        "explanation": "《兄弟》写李光头、宋钢兄弟在时代巨变中的命运。"}},
    {"ch": "小说（90年代）", "kw": "新现实主义小说", "q": {"stem": "新现实主义小说关注____（国企改革）现实。", "type": "blank",
        "answer": "国企改革（下岗）", "options": [],
        "explanation": "新现实主义小说直面国企改革、下岗等现实矛盾。"}},
    {"ch": "小说（90年代）", "kw": "新生代小说", "q": {"stem": "新生代小说代表作家还有____。", "type": "blank",
        "answer": "朱文", "options": [],
        "explanation": "朱文《我爱美元》等是新生代小说代表作。"}},
    {"ch": "小说（90年代）", "kw": "贾平凹的小说", "q": {"stem": "贾平凹《高兴》写____（农民工）进城。", "type": "blank",
        "answer": "农民工（刘高兴）", "options": [],
        "explanation": "《高兴》写农民刘高兴进城捡破烂的生存，是贾平凹新世纪代表作。"}},
    {"ch": "小说（90年代）", "kw": "陈忠实《白鹿原》", "q": {"stem": "《白鹿原》获第____届茅盾文学奖。", "type": "blank",
        "answer": "四", "options": [],
        "explanation": "《白鹿原》获第四届茅盾文学奖。"}},
    {"ch": "新诗（50-60年代）", "kw": "郭小川的诗歌创作", "q": {"stem": "郭小川善于铺陈排比，其诗被称为“____体”。", "type": "blank",
        "answer": "新辞赋", "options": [],
        "explanation": "郭小川形成铺陈排比的“新辞赋体”诗风。"}},
    {"ch": "新诗（50-60年代）", "kw": "“大我”与“小我”", "q": {"stem": "50年代诗歌强调抒写集体主义的“____”。", "type": "blank",
        "answer": "大我", "options": [],
        "explanation": "当时诗坛强调“大我”，个人化的“小我”抒情受到抑制。"}},
    {"ch": "新诗（80-90年代）", "kw": "“归来”诗人", "q": {"stem": "“归来”诗人还包括____（曾卓等）。", "type": "blank",
        "answer": "曾卓（绿原）", "options": [],
        "explanation": "曾卓《悬崖边的树》、绿原等“归来”诗人复出诗坛。"}},
    {"ch": "新诗（80-90年代）", "kw": "北岛的诗歌", "q": {"stem": "北岛诗歌善于用冷峻的____（意象）表达。", "type": "blank",
        "answer": "意象（象征）", "options": [],
        "explanation": "北岛诗以冷峻的意象和象征著称，如《回答》中的“通行证”。"}},
    {"ch": "台港文学", "kw": "白先勇的小说", "q": {"stem": "白先勇《玉卿嫂》写____的爱情悲剧。", "type": "blank",
        "answer": "玉卿嫂", "options": [],
        "explanation": "《玉卿嫂》写女佣玉卿嫂的爱情悲剧，是白先勇早期名作。"}},
    {"ch": "台港文学", "kw": "余光中的诗歌创作", "q": {"stem": "余光中《白玉苦瓜》以____为意象。", "type": "blank",
        "answer": "白玉苦瓜", "options": [],
        "explanation": "《白玉苦瓜》以苦瓜意象写文化传承与民族情感。"}},
    {"ch": "台港文学", "kw": "梁实秋的散文", "q": {"stem": "梁实秋《雅舍》写的是____生活。", "type": "blank",
        "answer": "雅舍（战时陋室）", "options": [],
        "explanation": "《雅舍》写抗战时期陋室之乐，是《雅舍小品》名篇。"}},
    {"ch": "2000-2016年文学", "kw": "莫言的魔幻现实主义", "q": {"stem": "莫言《生死疲劳》采用____（轮回）叙事。", "type": "blank",
        "answer": "六道轮回", "options": [],
        "explanation": "《生死疲劳》以西门闹的六道轮回写中国乡村五十年变迁。"}},
    {"ch": "2000-2016年文学", "kw": "贾平凹《秦腔》", "q": {"stem": "《秦腔》采用____（密实）的叙事手法。", "type": "blank",
        "answer": "密实流年（琐碎）", "options": [],
        "explanation": "《秦腔》以密实琐碎的日常叙事写乡村的“挽歌”。"}},
    {"ch": "2000-2016年文学", "kw": "毕飞宇的小说", "q": {"stem": "毕飞宇《苏北少年堂吉诃德》是____（自传）作品。", "type": "blank",
        "answer": "自传（回忆）", "options": [],
        "explanation": "《苏北少年堂吉诃德》是毕飞宇的童年自传。"}},
    {"ch": "2000-2016年文学", "kw": "金宇澄《繁花》", "q": {"stem": "《繁花》获第____届茅盾文学奖。", "type": "blank",
        "answer": "九", "options": [],
        "explanation": "《繁花》获第九届茅盾文学奖。"}},
    {"ch": "2000-2016年文学", "kw": "网络诗歌", "q": {"stem": "网络诗歌代表诗人有____（余秀华等）。", "type": "blank",
        "answer": "余秀华", "options": [],
        "explanation": "余秀华《穿过大半个中国去睡你》经网络传播成名，是网络诗歌代表。"}},
    {"ch": "散文（80-90年代）", "kw": "80年代散文家：孙犁、杨绛、陈白尘、汪曾祺", "q": {"stem": "孙犁的散文集有《____》（尺泽集）。", "type": "blank",
        "answer": "尺泽集", "options": [],
        "explanation": "孙犁晚年散文集《尺泽集》等，平淡而隽永。"}},
    {"ch": "散文（80-90年代）", "kw": "学者散文", "q": {"stem": "季羡林的散文属于____（学者）散文。", "type": "blank",
        "answer": "学者", "options": [],
        "explanation": "季羡林《牛棚杂忆》等融学养与人生，是学者散文代表。"}},
    {"ch": "散文（80-90年代）", "kw": "余秋雨《文化苦旅》", "q": {"stem": "《文化苦旅》的“苦旅”指向____之旅。", "type": "blank",
        "answer": "文化反思（精神苦旅）", "options": [],
        "explanation": "“苦旅”喻指作者对中国文化的历史性反思与寻访。"}},
    {"ch": "戏剧（80-90年代）", "kw": "沙叶新的戏剧", "q": {"stem": "沙叶新《耶稣·孔子·披头士列侬》是____（荒诞）喜剧。", "type": "blank",
        "answer": "荒诞（喜剧）", "options": [],
        "explanation": "该剧借耶稣、孔子等人物展开荒诞思辨，是沙叶新探索之作。"}},
    {"ch": "戏剧（80-90年代）", "kw": "现实主义戏剧的坚守", "q": {"stem": "现实主义戏剧坚持反映____（生活真实）。", "type": "blank",
        "answer": "生活真实（典型化）", "options": [],
        "explanation": "现实主义戏剧坚持反映生活真实、塑造典型人物。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "第一次全国文代会", "q": {"stem": "第一次文代会以____（《讲话》）为指导思想。", "type": "blank",
        "answer": "《在延安文艺座谈会上的讲话》", "options": [],
        "explanation": "第一次文代会以《在延安文艺座谈会上的讲话》精神为指导思想。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "第二次全国文代会", "q": {"stem": "1953年第二次文代会，____（周恩来）作政治报告。", "type": "blank",
        "answer": "周恩来", "options": [],
        "explanation": "1953年第二次文代会，周恩来作政治报告，确立社会主义现实主义方向。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "革命样板戏", "q": {"stem": "革命样板戏《智取威虎山》改编自曲波小说《____》。", "type": "blank",
        "answer": "林海雪原", "options": [],
        "explanation": "《智取威虎山》取材自曲波《林海雪原》中杨子荣智取威虎山的故事。"}},
    {"ch": "文学思潮（80-90年代）", "kw": "李泽厚《启蒙与救亡的双重变奏》", "q": {"stem": "李泽厚《启蒙与救亡的双重变奏》发表于____（1986）年。", "type": "blank",
        "answer": "1986", "options": [],
        "explanation": "该文1986年发表于《走向未来》，提出启蒙与救亡双重变奏论。"}},
    {"ch": "文学思潮（80-90年代）", "kw": "新状态文学", "q": {"stem": "“新状态文学”由《钟山》等杂志于____（1994）年倡导。", "type": "blank",
        "answer": "1994", "options": [],
        "explanation": "1994年《钟山》等倡导“新状态文学”，关注当下生存状态。"}},
    {"ch": "文学思潮（80-90年代）", "kw": "“二十世纪中国文学”命题", "q": {"stem": "“二十世纪中国文学”以____（现代性）为线索。", "type": "blank",
        "answer": "现代性", "options": [],
        "explanation": "“二十世纪中国文学”以“现代性”为线索整合百年文学。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'当代第十批挂载 {n} 题')
