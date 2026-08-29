# -*- coding: utf-8 -*-
"""当代文学史 扩充第十一批：冲刺目标"""
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
    {"ch": "小说（80年代）", "kw": "路遥的小说", "q": {"stem": "路遥《平凡的世界》获____（茅盾文学奖）。", "type": "blank",
        "answer": "茅盾文学奖", "options": [],
        "explanation": "《平凡的世界》获第三届茅盾文学奖。"}},
    {"ch": "小说（80年代）", "kw": "高晓声的乡土小说", "q": {"stem": "高晓声是“____”（乡土）派作家。", "type": "blank",
        "answer": "乡土", "options": [],
        "explanation": "高晓声写苏南农村的农民，是乡土小说家。"}},
    {"ch": "小说（80年代）", "kw": "陆文夫的小说", "q": {"stem": "陆文夫被誉为“____”（小巷）作家。", "type": "blank",
        "answer": "小巷", "options": [],
        "explanation": "陆文夫多写苏州小巷人物，被誉为“小巷作家”。"}},
    {"ch": "小说（90年代）", "kw": "新历史小说", "q": {"stem": "苏童《妻妾成群》的女主人公是____。", "type": "blank",
        "answer": "颂莲", "options": [],
        "explanation": "《妻妾成群》写女大学生颂莲嫁入陈家的悲剧。"}},
    {"ch": "小说（90年代）", "kw": "王安忆《小鲍庄》", "q": {"stem": "《小鲍庄》的“捞渣”是____（仁义）象征。", "type": "blank",
        "answer": "仁义（善良）", "options": [],
        "explanation": "“捞渣”以牺牲精神象征仁义，是《小鲍庄》的核心意象。"}},
    {"ch": "新诗（50-60年代）", "kw": "贺敬之的诗歌创作", "q": {"stem": "贺敬之《桂林山水歌》写____（桂林）山水。", "type": "blank",
        "answer": "桂林", "options": [],
        "explanation": "《桂林山水歌》以民歌体写桂林山水之美。"}},
    {"ch": "新诗（80-90年代）", "kw": "顾城的诗歌", "q": {"stem": "顾城的诗多写____（童年/自然）世界。", "type": "blank",
        "answer": "童年与自然", "options": [],
        "explanation": "顾城以纯净的童年视角写自然与幻想，被称为“童话诗人”。"}},
    {"ch": "新诗（80-90年代）", "kw": "海子的诗歌", "q": {"stem": "海子《亚洲铜》写____（亚洲/土地）主题。", "type": "blank",
        "answer": "土地（亚洲文明）", "options": [],
        "explanation": "《亚洲铜》以“亚洲铜”意象写土地与文明。"}},
    {"ch": "台港文学", "kw": "余光中的散文", "q": {"stem": "余光中散文《听听那冷雨》发表于____（1974）年。", "type": "blank",
        "answer": "1974", "options": [],
        "explanation": "《听听那冷雨》1974年发表，是余光中散文代表作。"}},
    {"ch": "台港文学", "kw": "金庸小说的文化底蕴与现代意识", "q": {"stem": "金庸小说以____（历史）为背景。", "type": "blank",
        "answer": "历史（朝代）", "options": [],
        "explanation": "金庸小说多依托真实历史背景，如《射雕》之于南宋。"}},
    {"ch": "2000-2016年文学", "kw": "莫言《红高粱》", "q": {"stem": "《红高粱》写____（抗日）传奇。", "type": "blank",
        "answer": "抗日（民间）", "options": [],
        "explanation": "《红高粱》写高密东北乡民众抗日的民间传奇。"}},
    {"ch": "2000-2016年文学", "kw": "毕飞宇的小说", "q": {"stem": "毕飞宇《玉米》系列写____（乡村）女性命运。", "type": "blank",
        "answer": "乡村", "options": [],
        "explanation": "《玉米》三部曲以乡村女性命运折射时代变迁。"}},
    {"ch": "2000-2016年文学", "kw": "李洱的小说", "q": {"stem": "李洱《花腔》的主人公是____。", "type": "blank",
        "answer": "葛任", "options": [],
        "explanation": "《花腔》围绕知识分子葛任之死展开多声部叙述。"}},
    {"ch": "2000-2016年文学", "kw": "打工文学与底层写作", "q": {"stem": "打工文学的代表刊物是____（《天涯》等）。", "type": "blank",
        "answer": "《天涯》（打工文学期刊）", "options": [],
        "explanation": "《天涯》等刊物的“底层写作”栏目推动了打工文学。"}},
    {"ch": "散文（80-90年代）", "kw": "90年代“散文热”", "q": {"stem": "90年代散文热中，____（文化）散文销量最高。", "type": "blank",
        "answer": "文化（学者）", "options": [],
        "explanation": "90年代以余秋雨为代表的文化散文热销，推动“散文热”。"}},
    {"ch": "散文（80-90年代）", "kw": "巴金《随想录》", "q": {"stem": "《随想录》是巴金在____（晚年）完成的。", "type": "blank",
        "answer": "晚年", "options": [],
        "explanation": "《随想录》写于1978至1986年间，是巴金晚年的忏悔与反思。"}},
    {"ch": "戏剧（80-90年代）", "kw": "高行健的戏剧", "q": {"stem": "高行健主张“____”（写意）戏剧。", "type": "blank",
        "answer": "写意（假定性）", "options": [],
        "explanation": "高行健主张戏剧的“假定性”与写意性，代表作《绝对信号》等。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "对俞平伯《红楼梦》研究的批判", "q": {"stem": "对《红楼梦研究》批判的导火索是____（俞平伯）的文章。", "type": "blank",
        "answer": "俞平伯（《红楼梦简论》）", "options": [],
        "explanation": "李希凡、蓝翎批判俞平伯《红楼梦简论》，引发全国性讨论。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "清查“胡风反革命集团”及其文艺思想", "q": {"stem": "胡风文艺思想主张“____”（主观战斗）精神。", "type": "blank",
        "answer": "主观战斗", "options": [],
        "explanation": "胡风强调作家主观战斗精神与“写真实”，其理论在50年代遭批判。"}},
    {"ch": "文学思潮（80-90年代）", "kw": "“重写文学史”", "q": {"stem": "“重写文学史”专栏设于《____》（上海文论）。", "type": "blank",
        "answer": "上海文论", "options": [],
        "explanation": "1988年《上海文论》开设“重写文学史”专栏，由陈思和、王晓明主持。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'当代第十一批挂载 {n} 题')
