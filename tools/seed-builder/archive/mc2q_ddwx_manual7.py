# -*- coding: utf-8 -*-
"""当代文学史 扩充第七批：继续扩充"""
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
    {"ch": "小说（80年代）", "kw": "伤痕文学", "q": {"stem": "伤痕文学得名于卢新华的小说《____》。", "type": "blank",
        "answer": "伤痕", "options": [],
        "explanation": "“伤痕文学”因卢新华《伤痕》而得名，开新时期文学之端。"}},
    {"ch": "小说（80年代）", "kw": "反思文学", "q": {"stem": "反思文学比伤痕文学更注重____（理性）反思。", "type": "blank",
        "answer": "历史理性（深层反思）", "options": [],
        "explanation": "反思文学由伤痕的宣泄转向对历史教训的理性反思。"}},
    {"ch": "小说（80年代）", "kw": "改革文学", "q": {"stem": "改革文学塑造的典型形象是____（改革者）。", "type": "blank",
        "answer": "改革者（乔光朴等）", "options": [],
        "explanation": "改革文学着力塑造改革者形象，如乔光朴。"}},
    {"ch": "小说（80年代）", "kw": "寻根文学", "q": {"stem": "寻根文学主张向____（民族文化）寻根。", "type": "blank",
        "answer": "民族文化（传统）", "options": [],
        "explanation": "寻根文学主张从民族文化传统中寻找文学之根。"}},
    {"ch": "小说（80年代）", "kw": "新写实小说", "q": {"stem": "新写实小说追求“____”（原生态）还原生活。", "type": "blank",
        "answer": "零度叙事（原生态）", "options": [],
        "explanation": "新写实小说以“零度叙事”还原日常生活的原生态。"}},
    {"ch": "小说（80年代）", "kw": "王蒙的意识流小说", "q": {"stem": "王蒙意识流小说突破传统____（结构/时序）。", "type": "blank",
        "answer": "叙事时序（线性结构）", "options": [],
        "explanation": "王蒙以联想、闪回打破线性时序，如《春之声》《布礼》。"}},
    {"ch": "小说（90年代）", "kw": "新历史小说", "q": {"stem": "新历史小说以____（民间）视角重写历史。", "type": "blank",
        "answer": "民间（边缘）", "options": [],
        "explanation": "新历史小说淡化宏大叙事，以民间、边缘视角重构历史。"}},
    {"ch": "小说（90年代）", "kw": "王安忆《长恨歌》", "q": {"stem": "《长恨歌》写了上海女人____的一生。", "type": "blank",
        "answer": "王琦瑶", "options": [],
        "explanation": "《长恨歌》以王琦瑶的一生串起上海城市变迁。"}},
    {"ch": "小说（90年代）", "kw": "陈忠实《白鹿原》", "q": {"stem": "《白鹿原》中的朱先生是____（儒家/乡贤）形象。", "type": "blank",
        "answer": "儒家（乡贤）", "options": [],
        "explanation": "朱先生是《白鹿原》中的儒家乡贤，体现传统道德理想。"}},
    {"ch": "小说（90年代）", "kw": "贾平凹的小说", "q": {"stem": "贾平凹《废都》曾引发____（争议）。", "type": "blank",
        "answer": "广泛争议", "options": [],
        "explanation": "《废都》因大胆的性描写和颓废基调引发争议。"}},
    {"ch": "新诗（80-90年代）", "kw": "朦胧诗", "q": {"stem": "朦胧诗得名于对其____（晦涩）的批评。", "type": "blank",
        "answer": "朦胧晦涩", "options": [],
        "explanation": "朦胧诗因意象朦胧、诗意晦涩而得名，后成为流派称谓。"}},
    {"ch": "新诗（80-90年代）", "kw": "舒婷的诗歌", "q": {"stem": "舒婷《祖国啊，我亲爱的祖国》是____（抒情）诗。", "type": "blank",
        "answer": "爱国抒情", "options": [],
        "explanation": "《祖国啊，我亲爱的祖国》抒写对祖国的深情与期望。"}},
    {"ch": "新诗（80-90年代）", "kw": "海子的诗歌", "q": {"stem": "海子主张“____”（大诗）理想。", "type": "blank",
        "answer": "大诗（史诗）", "options": [],
        "explanation": "海子追求“大诗”理想，试图以诗歌重建精神家园。"}},
    {"ch": "台港文学", "kw": "白先勇的小说", "q": {"stem": "白先勇《孽子》写____（同性恋）群体的命运。", "type": "blank",
        "answer": "同性恋（边缘群体）", "options": [],
        "explanation": "《孽子》写台北同性恋者的遭际，是白先勇重要作品。"}},
    {"ch": "台港文学", "kw": "余光中的诗歌创作", "q": {"stem": "余光中《白玉苦瓜》以____（苦瓜）为意象。", "type": "blank",
        "answer": "白玉苦瓜", "options": [],
        "explanation": "《白玉苦瓜》以苦瓜意象写文化传承与民族情感。"}},
    {"ch": "台港文学", "kw": "金庸小说的“雅”与“俗”", "q": {"stem": "金庸小说将____（通俗）与雅文学品格结合。", "type": "blank",
        "answer": "武侠通俗", "options": [],
        "explanation": "金庸武侠小说雅俗共赏，兼具通俗可读性与文学品格。"}},
    {"ch": "2000-2016年文学", "kw": "莫言的魔幻现实主义", "q": {"stem": "莫言小说融____（魔幻）与现实于一体。", "type": "blank",
        "answer": "魔幻（想象）", "options": [],
        "explanation": "莫言借鉴拉美魔幻现实主义，将想象、传说与乡土现实融合。"}},
    {"ch": "2000-2016年文学", "kw": "毕飞宇的小说", "q": {"stem": "毕飞宇《青衣》的女主人公是____。", "type": "blank",
        "answer": "筱燕秋", "options": [],
        "explanation": "《青衣》写京剧演员筱燕秋的艺术执念与人生悲剧。"}},
    {"ch": "2000-2016年文学", "kw": "李洱的小说", "q": {"stem": "李洱《花腔》采用____（多声部）叙事。", "type": "blank",
        "answer": "多声部", "options": [],
        "explanation": "《花腔》以不同叙述者的“花腔”并置重构历史。"}},
    {"ch": "2000-2016年文学", "kw": "网络诗歌", "q": {"stem": "网络诗歌常体现出____（互动）性。", "type": "blank",
        "answer": "互动（即时）", "options": [],
        "explanation": "网络诗歌即时发布、读者互动，是其区别于纸媒诗的特点。"}},
    {"ch": "散文（80-90年代）", "kw": "90年代“散文热”", "q": {"stem": "90年代“散文热”中____（随笔）体大盛。", "type": "blank",
        "answer": "随笔", "options": [],
        "explanation": "90年代随笔、文化散文、学者散文兴起，形成“散文热”。"}},
    {"ch": "散文（80-90年代）", "kw": "巴金《随想录》", "q": {"stem": "《随想录》分五集，共____（篇）文章。", "type": "blank",
        "answer": "150", "options": [],
        "explanation": "《随想录》共五集150篇，是巴金晚年的心灵忏悔录。"}},
    {"ch": "散文（80-90年代）", "kw": "学者散文", "q": {"stem": "张中行的散文属于____（学者）散文。", "type": "blank",
        "answer": "学者", "options": [],
        "explanation": "张中行《负暄琐话》等以学者随笔著称。"}},
    {"ch": "戏剧（80-90年代）", "kw": "现实主义戏剧的坚守", "q": {"stem": "《小井胡同》以____（北京）胡同为舞台。", "type": "blank",
        "answer": "北京", "options": [],
        "explanation": "李龙云《小井胡同》写北京小井胡同的市民历史。"}},
    {"ch": "戏剧（80-90年代）", "kw": "沙叶新的戏剧", "q": {"stem": "沙叶新《假如我是真的》属于____（讽刺）剧。", "type": "blank",
        "answer": "讽刺（社会批判）", "options": [],
        "explanation": "《假如我是真的》以讽刺笔法批判特权，是沙叶新代表作。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "第一次全国文代会", "q": {"stem": "1949年第一次文代会是____（中华全国文学艺术工作者）代表大会。", "type": "blank",
        "answer": "中华全国文学艺术工作者", "options": [],
        "explanation": "第一次文代会（1949年）即中华全国文学艺术工作者代表大会。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "清查“胡风反革命集团”及其文艺思想", "q": {"stem": "“胡风反革命集团”案发生于____年代。", "type": "blank",
        "answer": "五十（1955年）", "options": [],
        "explanation": "1955年胡风等人被打成“反革命集团”，是重大文艺冤案。"}},
    {"ch": "文学思潮（80-90年代）", "kw": "新状态文学", "q": {"stem": "“新状态文学”强调表现____（当下状态）。", "type": "blank",
        "answer": "当下生存状态", "options": [],
        "explanation": "“新状态文学”关注当下转型期的生存状态，由《钟山》等倡导。"}},
    {"ch": "文学思潮（80-90年代）", "kw": "李泽厚《启蒙与救亡的双重变奏》", "q": {"stem": "李泽厚认为____（救亡）压倒了启蒙。", "type": "blank",
        "answer": "救亡", "options": [],
        "explanation": "李泽厚认为中国近代救亡主题压倒了启蒙主题，造成历史复杂性。"}},
    {"ch": "戏剧散文（50-60年代）", "kw": "50、60年代戏剧的发展阶段", "q": {"stem": "50年代初戏剧一度出现____（公式化）倾向。", "type": "blank",
        "answer": "公式化概念化", "options": [],
        "explanation": "50年代初部分戏剧流于公式化、概念化，后经“第四种剧本”等突破。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'当代第七批挂载 {n} 题')
