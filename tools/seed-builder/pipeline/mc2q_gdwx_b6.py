# -*- coding: utf-8 -*-
"""古代文学史 第六批扩充：作者-作品对应、名句出处、号/别称等经典单点考点"""
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
    # ---- 先秦 ----
    {"ch": "先秦文学", "mk": "庄子", "q": {"stem": "“庖丁解牛”的寓言出自《庄子》中的《____》。", "type": "blank",
        "answer": "养生主", "explanation": "“庖丁解牛”出自《庄子·养生主》，以解牛喻养生之道。",
        "options": []}},
    {"ch": "先秦文学", "mk": "战国策", "q": {"stem": "《战国策》主要记录的是____的言行和游说之辞。", "type": "blank",
        "answer": "纵横家", "explanation": "《战国策》记述战国时期纵横家的政治主张和策略，由西汉刘向编订。",
        "options": []}},
    # ---- 秦汉 ----
    {"ch": "秦汉文学", "mk": "汉书", "q": {"stem": "《吕氏春秋》是秦相____的门客辑合百家九流之说编写的集体著作。", "type": "blank",
        "answer": "吕不韦", "explanation": "《吕氏春秋》完成于统一前，是吕不韦门客编写的集体著作，体系严密。",
        "options": []}},
    {"ch": "秦汉文学", "mk": "汉赋四大家", "q": {"stem": "东汉张衡的《____》是京都大赋的代表作。", "type": "blank",
        "answer": "二京赋", "explanation": "张衡《二京赋》铺写东京、西京（洛阳、长安）的繁盛，是东汉京都大赋代表作。",
        "options": []}},
    # ---- 魏晋 ----
    {"ch": "魏晋南北朝文学", "mk": "正始", "q": {"stem": "阮籍的代表作是八十二首《____》。", "type": "blank",
        "answer": "咏怀诗", "explanation": "阮籍《咏怀诗》八十二首，借古讽今、寄托遥深，是正始文学的代表。",
        "options": []}},
    {"ch": "魏晋南北朝文学", "mk": "太康", "q": {"stem": "左思借古讽今的组诗代表作是《____》。", "type": "blank",
        "answer": "咏史", "explanation": "左思《咏史》八首借咏史抒写抱负，被誉为“左思风力”。",
        "options": []}},
    # ---- 隋唐 ----
    {"ch": "隋唐五代文学", "mk": "王孟", "q": {"stem": "苏轼评价王维的诗是“诗中有画，____”。", "type": "blank",
        "answer": "画中有诗", "explanation": "苏轼评王维“诗中有画，画中有诗”，概括其诗歌高度的画意。",
        "options": []}},
    {"ch": "隋唐五代文学", "mk": "陈子昂", "q": {"stem": "陈子昂《登幽州台歌》“前不见古人，____”。", "type": "blank",
        "answer": "后不见来者", "explanation": "“前不见古人，后不见来者”是陈子昂《登幽州台歌》名句，抒发怀才不遇的悲慨。",
        "options": []}},
    {"ch": "隋唐五代文学", "mk": "李贺与李商隐", "q": {"stem": "李贺的诗歌在文学史上被称为（　）", "type": "choice",
        "answer": "诗鬼", "explanation": "李贺诗歌想象奇诡、瑰丽凄艳，世称“诗鬼”。",
        "options": ["诗鬼", "诗圣", "诗仙", "诗魔"]}},
    {"ch": "隋唐五代文学", "mk": "李贺与李商隐", "q": {"stem": "李商隐《无题》“春蚕到死丝方尽，____”。", "type": "blank",
        "answer": "蜡炬成灰泪始干", "explanation": "“春蚕到死丝方尽，蜡炬成灰泪始干”是李商隐《无题》名句，写爱情的执着。",
        "options": []}},
    {"ch": "隋唐五代文学", "mk": "唐传奇", "q": {"stem": "唐传奇《李娃传》的作者是（　）", "type": "choice",
        "answer": "白行简", "explanation": "《李娃传》是白行简的传奇代表作，写荥阳公子与妓女李娃的爱情故事。",
        "options": ["白行简", "元稹", "蒋防", "沈既济"]}},
    {"ch": "隋唐五代文学", "mk": "古文运动", "q": {"stem": "韩愈与柳宗元倡导的古文运动，主张“____”，即文以载道。", "type": "blank",
        "answer": "文以明道", "explanation": "韩愈提出“文以明道”，强调文章要为阐扬儒家之道服务，反对骈文的浮靡。",
        "options": []}},
    # ---- 宋代 ----
    {"ch": "宋代文学", "mk": "苏轼", "q": {"stem": "苏轼号____，其散文与欧阳修并称“欧苏”。", "type": "blank",
        "answer": "东坡居士", "explanation": "苏轼号东坡居士，与欧阳修并称“欧苏”，是豪放词派的开创者。",
        "options": []}},
    {"ch": "宋代文学", "mk": "辛弃疾", "q": {"stem": "辛弃疾的词集名为《____》。", "type": "blank",
        "answer": "稼轩长短句", "explanation": "辛弃疾号稼轩，其词集名《稼轩长短句》，是南宋豪放词的代表。",
        "options": []}},
    {"ch": "宋代文学", "mk": "李清照", "q": {"stem": "李清照号____，其词被称为“易安体”。", "type": "blank",
        "answer": "易安居士", "explanation": "李清照号易安居士，其词婉约清丽，世称“易安体”。",
        "options": []}},
    {"ch": "宋代文学", "mk": "姜夔", "q": {"stem": "姜夔自度曲《____》写扬州战乱后的荒凉，是咏史名篇。", "type": "blank",
        "answer": "扬州慢", "explanation": "姜夔《扬州慢》自度曲，写金兵南侵后扬州的萧条，寄托黍离之悲。",
        "options": []}},
    # ---- 明代 ----
    {"ch": "明代文学", "mk": "汤显祖", "q": {"stem": "《牡丹亭》的女主人公是____。", "type": "blank",
        "answer": "杜丽娘", "explanation": "《牡丹亭》写杜丽娘与柳梦梅生死相恋的故事，杜丽娘是至情至性的女性形象。",
        "options": []}},
    # ---- 清代 ----
    {"ch": "清代文学", "mk": "红楼梦", "q": {"stem": "《红楼梦》原名《____》。", "type": "blank",
        "answer": "石头记", "explanation": "《红楼梦》又名《石头记》，写贾宝玉、林黛玉的爱情悲剧和贾府的兴衰。",
        "options": []}},
    {"ch": "清代文学", "mk": "儒林外史", "q": {"stem": "《儒林外史》“范进中举”一节，主要讽刺的是（　）", "type": "choice",
        "answer": "科举制度", "explanation": "《儒林外史》以“范进中举”等情节辛辣讽刺科举制度对读书人的毒害。",
        "options": ["科举制度", "封建礼教", "官场腐败", "婚姻制度"]}},
    # ---- 元代 ----
    {"ch": "元代文学", "mk": "西厢", "q": {"stem": "《西厢记》的女主人公是____。", "type": "blank",
        "answer": "崔莺莺", "explanation": "《西厢记》写张生与崔莺莺的爱情故事，崔莺莺是敢于追求自由爱情的女性形象。",
        "options": []}},
    {"ch": "元代文学", "mk": "窦娥", "q": {"stem": "《窦娥冤》中窦娥临刑前发下的“三桩誓愿”不包括（　）", "type": "choice",
        "answer": "六月飞雪封山", "explanation": "窦娥三桩誓愿是血溅白练、六月飞雪、大旱三年；“六月飞雪封山”不属其中。",
        "options": ["六月飞雪封山", "血溅白练", "六月飞雪", "大旱三年"]}},
    # ---- 近代 ----
    {"ch": "近代文学", "mk": "龚自珍", "q": {"stem": "龚自珍《己亥杂诗》“我劝天公重抖擞，____”。", "type": "blank",
        "answer": "不拘一格降人才", "explanation": "“我劝天公重抖擞，不拘一格降人才”是龚自珍《己亥杂诗》名句，呼唤变革人才。",
        "options": []}},
    {"ch": "近代文学", "mk": "谴责小说", "q": {"stem": "谴责小说《老残游记》的作者是（　）", "type": "choice",
        "answer": "刘鹗", "explanation": "《老残游记》是刘鹗所作谴责小说，借老残游历揭露晚清社会黑暗。",
        "options": ["刘鹗", "李宝嘉", "吴趼人", "曾朴"]}},
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
print(f'第六批挂载 {n} 题（跳过重复 {dup}）')
