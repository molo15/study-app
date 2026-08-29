# -*- coding: utf-8 -*-
"""当代文学史 扩充第五批：选择辨析题"""
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
    {"ch": "小说（80年代）", "kw": "伤痕文学", "q": {"stem": "下列属于伤痕文学代表作的是（　）", "type": "choice",
        "answer": "《伤痕》", "options": ["《伤痕》", "《乔厂长上任记》", "《爸爸爸》", "《哦，香雪》"],
        "explanation": "卢新华《伤痕》是伤痕文学开山作；《乔厂长上任记》属改革文学，《爸爸爸》属寻根文学。"}},
    {"ch": "小说（80年代）", "kw": "反思文学", "q": {"stem": "《人到中年》的作者是（　）", "type": "choice",
        "answer": "谌容", "options": ["谌容", "茹志鹃", "张洁", "刘心武"],
        "explanation": "谌容《人到中年》写中年知识分子的困境，是反思文学代表作。"}},
    {"ch": "小说（80年代）", "kw": "改革文学", "q": {"stem": "《乔厂长上任记》的主人公是（　）", "type": "choice",
        "answer": "乔光朴", "options": ["乔光朴", "陈奂生", "林震", "梁生宝"],
        "explanation": "蒋子龙《乔厂长上任记》塑造了改革者乔光朴的形象。"}},
    {"ch": "小说（80年代）", "kw": "寻根文学", "q": {"stem": "韩少功《爸爸爸》中的人物“丙崽”具有____色彩。", "type": "choice",
        "answer": "象征（寓言）", "options": ["象征（寓言）", "写实", "讽刺（纯现实）", "抒情"],
        "explanation": "“丙崽”是象征性形象，承载对民族文化心理的反思。"}},
    {"ch": "小说（80年代）", "kw": "路遥的小说", "q": {"stem": "路遥《平凡的世界》属于____题材。", "type": "choice",
        "answer": "农村（城乡交叉）", "options": ["农村（城乡交叉）", "工业改革", "军事", "武侠"],
        "explanation": "《平凡的世界》写农村青年在城乡之间的奋斗与理想。"}},
    {"ch": "小说（80年代）", "kw": "新写实小说", "q": {"stem": "下列属于新写实小说的是（　）", "type": "choice",
        "answer": "《一地鸡毛》", "options": ["《一地鸡毛》", "《红高粱》", "《棋王》", "《伤痕》"],
        "explanation": "刘震云《一地鸡毛》写日常生活琐碎，是新写实小说代表作。"}},
    {"ch": "小说（90年代）", "kw": "新历史小说", "q": {"stem": "《白鹿原》属于（　）", "type": "choice",
        "answer": "新历史小说", "options": ["新历史小说", "伤痕文学", "先锋小说", "改革文学"],
        "explanation": "《白鹿原》以宗族史写民族史，属新历史小说。"}},
    {"ch": "小说（90年代）", "kw": "王安忆《长恨歌》", "q": {"stem": "《长恨歌》的故事背景是（　）", "type": "choice",
        "answer": "上海", "options": ["上海", "北京", "广州", "成都"],
        "explanation": "《长恨歌》以王琦瑶的一生写上海城市文化的变迁。"}},
    {"ch": "小说（90年代）", "kw": "王朔的“顽主”与调侃", "q": {"stem": "王朔小说《顽主》体现了（　）风格", "type": "choice",
        "answer": "调侃消解", "options": ["调侃消解", "崇高抒情", "古典雅致", "写实纪实"],
        "explanation": "王朔以“顽主”式调侃消解崇高与理想。"}},
    {"ch": "小说（90年代）", "kw": "陈忠实《白鹿原》", "q": {"stem": "《白鹿原》中白鹿两家的代表人物是（　）", "type": "choice",
        "answer": "白嘉轩与鹿子霖", "options": ["白嘉轩与鹿子霖", "白嘉轩与朱先生", "鹿子霖与田小娥", "白孝文与鹿兆鹏"],
        "explanation": "《白鹿原》以白嘉轩与鹿子霖两家恩怨为主线写宗法社会的解体。"}},
    {"ch": "新诗（80-90年代）", "kw": "朦胧诗", "q": {"stem": "朦胧诗的代表诗人不包括（　）", "type": "choice",
        "answer": "艾青", "options": ["艾青", "北岛", "舒婷", "顾城"],
        "explanation": "艾青是“归来”诗人，北岛、舒婷、顾城是朦胧诗代表。"}},
    {"ch": "新诗（80-90年代）", "kw": "舒婷的诗歌", "q": {"stem": "“我必须是你近旁的一株木棉”出自舒婷的（　）", "type": "choice",
        "answer": "《致橡树》", "options": ["《致橡树》", "《祖国啊，我亲爱的祖国》", "《神女峰》", "《惠安女子》"],
        "explanation": "“木棉”意象出自《致橡树》，表达独立平等的爱情观。"}},
    {"ch": "新诗（80-90年代）", "kw": "海子的诗歌", "q": {"stem": "“面朝大海，春暖花开”的作者是（　）", "type": "choice",
        "answer": "海子", "options": ["海子", "顾城", "北岛", "韩东"],
        "explanation": "《面朝大海，春暖花开》是海子代表作。"}},
    {"ch": "台港文学", "kw": "白先勇的小说", "q": {"stem": "《游园惊梦》的作者是（　）", "type": "choice",
        "answer": "白先勇", "options": ["白先勇", "梁实秋", "余光中", "金庸"],
        "explanation": "《游园惊梦》是白先勇《台北人》中的名篇。"}},
    {"ch": "台港文学", "kw": "余光中的诗歌创作", "q": {"stem": "“乡愁是一枚小小的邮票”出自（　）", "type": "choice",
        "answer": "《乡愁》", "options": ["《乡愁》", "《听听那冷雨》", "《白玉苦瓜》", "《等你，在雨中》"],
        "explanation": "“邮票”“船票”“坟墓”“海峡”是《乡愁》的经典意象。"}},
    {"ch": "台港文学", "kw": "金庸小说的“雅”与“俗”", "q": {"stem": "金庸小说《笑傲江湖》中的主角是（　）", "type": "choice",
        "answer": "令狐冲", "options": ["令狐冲", "乔峰", "杨过", "郭靖"],
        "explanation": "令狐冲是《笑傲江湖》主角，乔峰、杨过、郭靖分别是天龙、神雕、射雕主角。"}},
    {"ch": "2000-2016年文学", "kw": "莫言《红高粱》", "q": {"stem": "《红高粱》塑造的“我爷爷”是（　）", "type": "choice",
        "answer": "余占鳌", "options": ["余占鳌", "朱老忠", "梁生宝", "白嘉轩"],
        "explanation": "“我爷爷”即余占鳌，是《红高粱》中的民间英雄。"}},
    {"ch": "2000-2016年文学", "kw": "毕飞宇的小说", "q": {"stem": "毕飞宇《推拿》写的是（　）群体", "type": "choice",
        "answer": "盲人", "options": ["盲人", "农民工", "知青", "下岗工人"],
        "explanation": "《推拿》写盲人推拿师的生活与尊严，获茅盾文学奖。"}},
    {"ch": "2000-2016年文学", "kw": "金宇澄《繁花》", "q": {"stem": "《繁花》的故事主要发生在（　）", "type": "choice",
        "answer": "上海", "options": ["上海", "北京", "苏州", "香港"],
        "explanation": "《繁花》以上海为背景，以上海方言写市井人生。"}},
    {"ch": "2000-2016年文学", "kw": "李洱的小说", "q": {"stem": "李洱《应物兄》获得（　）", "type": "choice",
        "answer": "茅盾文学奖", "options": ["茅盾文学奖", "鲁迅文学奖", "诺贝尔文学奖", "人民文学奖"],
        "explanation": "《应物兄》获第十届茅盾文学奖。"}},
    {"ch": "散文（80-90年代）", "kw": "巴金《随想录》", "q": {"stem": "《随想录》的核心精神是（　）", "type": "choice",
        "answer": "讲真话", "options": ["讲真话", "闲适", "山水游记", "文化考据"],
        "explanation": "《随想录》以“讲真话”为核心，是巴金晚年反省的结晶。"}},
    {"ch": "散文（80-90年代）", "kw": "余秋雨《文化苦旅》", "q": {"stem": "《文化苦旅》中的名篇有（　）", "type": "choice",
        "answer": "《道士塔》", "options": ["《道士塔》", "《荔枝蜜》", "《茶花赋》", "《白杨礼赞》"],
        "explanation": "《道士塔》反思敦煌文化劫难，是《文化苦旅》名篇。"}},
    {"ch": "戏剧散文（50-60年代）", "kw": "老舍《茶馆》", "q": {"stem": "《茶馆》共写了____个时代（幕）。", "type": "choice",
        "answer": "三个（三幕）", "options": ["三个（三幕）", "两个", "四个", "五个"],
        "explanation": "《茶馆》三幕分别写戊戌变法后、民国初、抗战后三个时代。"}},
    {"ch": "戏剧散文（50-60年代）", "kw": "“第四种剧本”", "q": {"stem": "“第四种剧本”突破了（　）的局限。", "type": "choice",
        "answer": "公文化概念化", "options": ["公文化概念化", "舞台时空", "语言形式", "演员表演"],
        "explanation": "“第四种剧本”针对当时公文化、概念化的创作倾向而提出。"}},
    {"ch": "戏剧散文（50-60年代）", "kw": "杨朔的散文", "q": {"stem": "杨朔散文《荔枝蜜》运用了（　）手法", "type": "choice",
        "answer": "托物言志", "options": ["托物言志", "意识流", "反讽", "纪实"],
        "explanation": "《荔枝蜜》借蜜蜂托物言志，赞颂无私奉献的劳动者。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "革命样板戏", "q": {"stem": "下列属于革命样板戏的是（　）", "type": "choice",
        "answer": "《红灯记》", "options": ["《红灯记》", "《茶馆》", "《关汉卿》", "《小井胡同》"],
        "explanation": "《红灯记》是革命样板戏；《茶馆》《关汉卿》是五六十年代话剧。"}},
    {"ch": "文学思潮（1949-1976）", "kw": "“双百方针”及其对文艺的影响", "q": {"stem": "“双百方针”提出的年份是（　）", "type": "choice",
        "answer": "1956", "options": ["1956", "1949", "1953", "1966"],
        "explanation": "“双百方针”于1956年提出，促进了文艺的短暂繁荣。"}},
    {"ch": "文学思潮（80-90年代）", "kw": "“重写文学史”", "q": {"stem": "“重写文学史”的倡导者是（　）", "type": "choice",
        "answer": "陈思和与王晓明", "options": ["陈思和与王晓明", "钱理群与黄子平", "李泽厚", "刘再复"],
        "explanation": "1988年陈思和、王晓明在《上海文论》倡导“重写文学史”。"}},
    {"ch": "小说（50-60年代）", "kw": "杨沫《青春之歌》", "q": {"stem": "林道静是____中的主人公", "type": "choice",
        "answer": "《青春之歌》", "options": ["《青春之歌》", "《创业史》", "《红旗谱》", "《红岩》"],
        "explanation": "林道静是杨沫《青春之歌》的女主人公。"}},
    {"ch": "戏剧（80-90年代）", "kw": "沙叶新的戏剧", "q": {"stem": "《陈毅市长》的主人公是（　）", "type": "choice",
        "answer": "陈毅", "options": ["陈毅", "周恩来", "彭德怀", "邓小平"],
        "explanation": "沙叶新《陈毅市长》以陈毅为主人公，采用“冰糖葫芦式”结构。"}},
]

n = 0
for it in Q:
    if mount(it['ch'], it['q'], it['kw']):
        n += 1
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'当代第五批挂载 {n} 题')
