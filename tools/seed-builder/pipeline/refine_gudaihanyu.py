# -*- coding: utf-8 -*-
"""古代汉语：补 knowledgeId + 笔记扩充基础题 → v012"""
import json, re, os
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "..", "out")
SRC = os.path.join(OUT, "refined", "bank-gudai-hanyu.refined2.json")
KN = os.path.join(OUT, "knowledge", "古代汉语.knowledge.json")
DST = os.path.join(OUT, "refined", "bank-gudai-hanyu.v012.json")

def norm(s):
    if not s: return ""
    s = re.sub(r"[（(][^）)]*[）)]", "", s)          # 去括号注释
    s = re.sub(r"[《》“”\"'。，、；：？！·…—\- ]", "", s)   # 去标点空白
    s = re.sub(r"\(|\)|（|）", "", s)
    return s

def ch_key(ch):
    return ch.replace("（", "").replace("）", "").strip()

# ========== 章 → 知识点映射表（关键词长词优先） ==========
KP = {
 "修辞": [
    ("起兴", "k_gdyy_xiuci_02"), ("比喻", "k_gdyy_xiuci_02"), ("夸张", "k_gdyy_xiuci_02"), ("借代", "k_gdyy_xiuci_02"), ("引用", "k_gdyy_xiuci_02"),
    ("互文", "k_gdyy_xiuci_03"), ("变文", "k_gdyy_xiuci_03"), ("并提", "k_gdyy_xiuci_03"), ("倒装", "k_gdyy_xiuci_03"), ("委婉", "k_gdyy_xiuci_03"), ("顶真", "k_gdyy_xiuci_03"), ("析字", "k_gdyy_xiuci_03"), ("排比", "k_gdyy_xiuci_03"),
    ("修辞学", "k_gdyy_xiuci_01"), ("修辞", "k_gdyy_xiuci_01"),
 ],
 "古书的文体": [
    ("文体分类", "k_gdyy_wenti_02"), ("散文", "k_gdyy_wenti_02"), ("韵文", "k_gdyy_wenti_02"), ("骈文", "k_gdyy_wenti_02"),
    ("传状", "k_gdyy_wenti_03"), ("论辩", "k_gdyy_wenti_03"), ("杂记", "k_gdyy_wenti_03"),
    ("奏议", "k_gdyy_wenti_04"), ("诏令", "k_gdyy_wenti_04"), ("碑志", "k_gdyy_wenti_04"),
    ("哀祭", "k_gdyy_wenti_05"), ("序跋", "k_gdyy_wenti_05"), ("书启", "k_gdyy_wenti_05"), ("箴铭", "k_gdyy_wenti_05"), ("颂赞", "k_gdyy_wenti_05"),
    ("文体研究", "k_gdyy_wenti_01"), ("体论文", "k_gdyy_wenti_01"), ("文心雕龙", "k_gdyy_wenti_01"), ("体大思精", "k_gdyy_wenti_01"),
 ],
 "古书的标点": [
    ("句读", "k_gdyy_biaodian_01"), ("断句", "k_gdyy_biaodian_01"), ("标点符号", "k_gdyy_biaodian_02"), ("标点古书", "k_gdyy_biaodian_03"), ("句号", "k_gdyy_biaodian_03"), ("虚词", "k_gdyy_biaodian_03"), ("标点", "k_gdyy_biaodian_03"),
 ],
 "工具书简介": [
    ("说文解字", "k_gdyy_gongjushu_01"), ("许慎", "k_gdyy_gongjushu_01"), ("康熙字典", "k_gdyy_gongjushu_02"), ("中华大字典", "k_gdyy_gongjushu_02"), ("汉语大字典", "k_gdyy_gongjushu_02"),
    ("辞源", "k_gdyy_gongjushu_03"), ("辞海", "k_gdyy_gongjushu_03"), ("汉语大词典", "k_gdyy_gongjushu_03"), ("尔雅", "k_gdyy_gongjushu_03"), ("方言", "k_gdyy_gongjushu_03"), ("释名", "k_gdyy_gongjushu_03"), ("词典", "k_gdyy_gongjushu_03"),
    ("虚词", "k_gdyy_gongjushu_04"), ("经传释词", "k_gdyy_gongjushu_04"), ("助字辨略", "k_gdyy_gongjushu_04"), ("词诠", "k_gdyy_gongjushu_04"),
    ("类书", "k_gdyy_gongjushu_05"), ("永乐大典", "k_gdyy_gongjushu_05"), ("古今图书集成", "k_gdyy_gongjushu_05"), ("艺文类聚", "k_gdyy_gongjushu_05"), ("太平御览", "k_gdyy_gongjushu_05"),
    ("政书", "k_gdyy_gongjushu_06"), ("通典", "k_gdyy_gongjushu_06"), ("文献通考", "k_gdyy_gongjushu_06"),
    ("广雅", "k_gdyy_gongjushu_07"), ("王念孙", "k_gdyy_gongjushu_07"), ("毛诗古音考", "k_gdyy_gongjushu_07"), ("训诂", "k_gdyy_gongjushu_07"),
    ("注音", "k_gdyy_gongjushu_08"), ("反切", "k_gdyy_gongjushu_08"), ("编排", "k_gdyy_gongjushu_08"), ("部首", "k_gdyy_gongjushu_08"),
 ],
 "文字（上）": [
    ("六书", "k_gdyy_wenzi_shang_01"), ("象形", "k_gdyy_wenzi_shang_02"), ("指事", "k_gdyy_wenzi_shang_02"), ("会意", "k_gdyy_wenzi_shang_03"), ("形声", "k_gdyy_wenzi_shang_04"), ("形旁", "k_gdyy_wenzi_shang_04"), ("声旁", "k_gdyy_wenzi_shang_04"), ("转注", "k_gdyy_wenzi_shang_05"), ("假借", "k_gdyy_wenzi_shang_06"), ("造字", "k_gdyy_wenzi_shang_01"), ("许慎", "k_gdyy_wenzi_shang_01"),
 ],
 "文字（下）": [
    ("古今字", "k_gdyy_wenzi_xia_01"), ("异体字", "k_gdyy_wenzi_xia_02"), ("繁简字", "k_gdyy_wenzi_xia_03"), ("简化字", "k_gdyy_wenzi_xia_03"), ("繁体字", "k_gdyy_wenzi_xia_03"), ("通假字", "k_gdyy_wenzi_xia_04"), ("通假", "k_gdyy_wenzi_xia_04"), ("形体", "k_gdyy_wenzi_xia_06"), ("隶变", "k_gdyy_wenzi_xia_08"), ("小篆", "k_gdyy_wenzi_xia_08"), ("甲骨文", "k_gdyy_wenzi_xia_07"), ("金文", "k_gdyy_wenzi_xia_07"), ("今字", "k_gdyy_wenzi_xia_01"),
 ],
 "绪论": [
    ("书面语", "k_gdyy_xulun_01"), ("文言", "k_gdyy_xulun_01"), ("口语", "k_gdyy_xulun_01"), ("王力", "k_gdyy_xulun_05"), ("词汇为主", "k_gdyy_xulun_05"), ("教学", "k_gdyy_xulun_03"), ("学习方法", "k_gdyy_xulun_04"), ("历史", "k_gdyy_xulun_06"), ("时代差异", "k_gdyy_xulun_06"), ("古代汉语", "k_gdyy_xulun_01"), ("性质", "k_gdyy_xulun_02"),
 ],
 "训诂": [
    ("形训", "k_gdyy_xungu_03"), ("声训", "k_gdyy_xungu_03"), ("义训", "k_gdyy_xungu_03"), ("训诂", "k_gdyy_xungu_01"), ("笺", "k_gdyy_xungu_04"), ("注", "k_gdyy_xungu_04"), ("疏", "k_gdyy_xungu_04"), ("正义", "k_gdyy_xungu_04"), ("传", "k_gdyy_xungu_04"), ("毛传", "k_gdyy_xungu_04"), ("尔雅注", "k_gdyy_xungu_05"), ("说文解字注", "k_gdyy_xungu_05"), ("广雅疏证", "k_gdyy_xungu_05"), ("经义述闻", "k_gdyy_xungu_05"),
 ],
 "词汇": [
    ("单音词", "k_gdyy_cihui_01"), ("联绵词", "k_gdyy_cihui_01"), ("连绵词", "k_gdyy_cihui_01"), ("重言词", "k_gdyy_cihui_01"), ("叠音词", "k_gdyy_cihui_01"), ("双声", "k_gdyy_cihui_01"), ("叠韵", "k_gdyy_cihui_01"), ("外来词", "k_gdyy_cihui_01"), ("单纯词", "k_gdyy_cihui_01"), ("偏义复词", "k_gdyy_cihui_02"), ("复合词", "k_gdyy_cihui_02"), ("合成词", "k_gdyy_cihui_02"), ("连类而及", "k_gdyy_cihui_02"),
    ("历史词", "k_gdyy_cihui_03"), ("古今词义", "k_gdyy_cihui_03"), ("词汇的发展", "k_gdyy_cihui_03"), ("古用今废", "k_gdyy_cihui_03"), ("新生词", "k_gdyy_cihui_03"),
    ("词义扩大", "k_gdyy_cihui_04"), ("词义缩小", "k_gdyy_cihui_04"), ("词义转移", "k_gdyy_cihui_04"), ("扩大", "k_gdyy_cihui_04"), ("缩小", "k_gdyy_cihui_04"), ("转移", "k_gdyy_cihui_04"),
    ("感情色彩", "k_gdyy_cihui_05"), ("褒贬", "k_gdyy_cihui_05"), ("词义轻重", "k_gdyy_cihui_05"), ("轻重", "k_gdyy_cihui_05"),
    ("本义", "k_gdyy_cihui_06"), ("引申义", "k_gdyy_cihui_07"), ("引申", "k_gdyy_cihui_07"), ("单向引申", "k_gdyy_cihui_07"), ("多向引申", "k_gdyy_cihui_07"), ("辐射式", "k_gdyy_cihui_07"), ("链条式", "k_gdyy_cihui_07"), ("递进式", "k_gdyy_cihui_07"), ("同义词", "k_gdyy_cihui_08"), ("互训", "k_gdyy_cihui_08"), ("同训", "k_gdyy_cihui_08"), ("递训", "k_gdyy_cihui_08"), ("连文", "k_gdyy_cihui_08"), ("异文", "k_gdyy_cihui_08"), ("避讳", "k_gdyy_cihui_08"),
 ],
 "诗词格律": [
    ("近体诗", "k_gdyy_shici_01"), ("律诗", "k_gdyy_shici_01"), ("绝句", "k_gdyy_shici_01"), ("平仄", "k_gdyy_shici_04"), ("拗救", "k_gdyy_shici_04"), ("对仗", "k_gdyy_shici_05"), ("押韵", "k_gdyy_shici_03"), ("对联", "k_gdyy_shici_06"), ("对偶", "k_gdyy_shici_05"), ("粘对", "k_gdyy_shici_04"), ("颔联", "k_gdyy_shici_02"), ("颈联", "k_gdyy_shici_02"), ("格律", "k_gdyy_shici_01"),
 ],
 "语法（上）": [
    ("名词", "k_gdyy_yufa_shang_02"), ("动词", "k_gdyy_yufa_shang_02"), ("形容词", "k_gdyy_yufa_shang_02"), ("数量词", "k_gdyy_yufa_shang_02"), ("代词", "k_gdyy_yufa_shang_03"), ("之", "k_gdyy_yufa_shang_03"), ("其", "k_gdyy_yufa_shang_03"), ("副词", "k_gdyy_yufa_shang_04"), ("介词", "k_gdyy_yufa_shang_05"), ("连词", "k_gdyy_yufa_shang_05"), ("语气词", "k_gdyy_yufa_shang_06"), ("助词", "k_gdyy_yufa_shang_06"), ("叹词", "k_gdyy_yufa_shang_06"), ("兼词", "k_gdyy_yufa_shang_07"), ("诸", "k_gdyy_yufa_shang_07"), ("焉", "k_gdyy_yufa_shang_07"), ("固定结构", "k_gdyy_yufa_shang_08"), ("固定格式", "k_gdyy_yufa_shang_08"), ("词类活用", "k_gdyy_yufa_shang_01"), ("语法研究", "k_gdyy_yufa_shang_01"),
 ],
 "语法（下）": [
    ("词类活用", "k_gdyy_yufa_xia_01"), ("名词作状语", "k_gdyy_yufa_xia_03"), ("使动", "k_gdyy_yufa_xia_04"), ("意动", "k_gdyy_yufa_xia_05"), ("判断句", "k_gdyy_yufa_xia_06"), ("被动句", "k_gdyy_yufa_xia_07"), ("宾语前置", "k_gdyy_yufa_xia_08"), ("前置", "k_gdyy_yufa_xia_08"), ("活用", "k_gdyy_yufa_xia_01"), ("用作动词", "k_gdyy_yufa_xia_02"),
 ],
 "音韵": [
    ("三十六字母", "k_gdyy_yinyun_02"), ("字母", "k_gdyy_yinyun_02"), ("守温", "k_gdyy_yinyun_02"), ("五音", "k_gdyy_yinyun_03"), ("七音", "k_gdyy_yinyun_03"), ("清浊", "k_gdyy_yinyun_03"), ("全清", "k_gdyy_yinyun_03"), ("次浊", "k_gdyy_yinyun_03"), ("韵头", "k_gdyy_yinyun_04"), ("韵腹", "k_gdyy_yinyun_04"), ("韵尾", "k_gdyy_yinyun_04"), ("阴声韵", "k_gdyy_yinyun_05"), ("阳声韵", "k_gdyy_yinyun_05"), ("入声韵", "k_gdyy_yinyun_05"), ("反切", "k_gdyy_yinyun_06"), ("切韵", "k_gdyy_yinyun_07"), ("广韵", "k_gdyy_yinyun_07"), ("中古音", "k_gdyy_yinyun_07"), ("韵镜", "k_gdyy_yinyun_08"), ("尖音", "k_gdyy_yinyun_08"), ("团音", "k_gdyy_yinyun_08"), ("平分阴阳", "k_gdyy_yinyun_09"), ("浊上变去", "k_gdyy_yinyun_09"), ("入派三声", "k_gdyy_yinyun_09"), ("声调", "k_gdyy_yinyun_09"), ("上古音", "k_gdyy_yinyun_10"), ("叶音说", "k_gdyy_yinyun_10"), ("古韵", "k_gdyy_yinyun_10"), ("音韵", "k_gdyy_yinyun_01"), ("破读", "k_gdyy_yinyun_06"), ("读破", "k_gdyy_yinyun_06"),
 ],
}

def map_kid(ch, stem):
    if ch in KP:
        for kw, kid in KP[ch]:
            if kw in stem:
                return kid
    return None

def main():
    qs = json.load(open(SRC, encoding="utf-8"))
    kn = json.load(open(KN, encoding="utf-8"))
    kps = kn if isinstance(kn, list) else kn.get("knowledge", kn.get("nodes", []))
    # 章 → 首知识点（兜底）
    first_kid = {}
    for kp in kps:
        ch = kp.get("chapter", "")
        if ch not in first_kid:
            first_kid[ch] = kp["id"]

    # 1) 补 knowledgeId
    fixed = 0; fallback = 0
    for q in qs:
        if q.get("knowledgeId"):
            continue
        if q.get("purpose") != "basic":
            continue
        kid = map_kid(q["chapter"], q["stem"])
        if not kid:
            kid = first_kid.get(q["chapter"])
            fallback += 1
        if kid:
            q["knowledgeId"] = kid
            fixed += 1
    print(f"basic 补 knowledgeId: {fixed}（兜底 {fallback}）")
    nokid = sum(1 for q in qs if q.get("purpose") == "basic" and not q.get("knowledgeId"))
    print(f"仍缺 knowledgeId 的 basic: {nokid}")

    # 2) 笔记扩充题
    EX = [
     ("词汇","单音词","古代汉语以____词为主（先秦至魏晋），现代汉语以复音词占绝大多数。","单音"),
     ("词汇","单音词","由一个词素组成、两个不同音节密不可分、合起来表示一个完整意义的词叫____。","连绵词"),
     ("词汇","单音词","连绵词又叫“连绵字”或“____”。","连语"),
     ("词汇","单音词","“参差”“犹豫”“玲珑”这类由声母相同或相近的两个音节组成的连绵词叫____连绵词。","双声"),
     ("词汇","单音词","“逍遥”“玫瑰”“峥嵘”这类韵母相同或相近的两个音节组成的连绵词叫____连绵词。","叠韵"),
     ("词汇","单音词","重叠两个相同音节组成、书面上写作两个相同的字的词叫____词。","重言"),
     ("词汇","合成词","用两个单音的近义词或反义词作为词素组成，其中一个词素的本来意义成为整个词的意义，另一个词素只起陪衬作用的词叫____。","偏义复词"),
     ("词汇","合成词","偏义复词中，两个意义相关相类的词组合在一起产生的偏义现象又叫____。","连类而及"),
     ("词汇","词汇的发展","词汇发展中，古用今废的词（如“笏”“媵”）叫____词。","历史"),
     ("词汇","词汇的发展","古代汉语以单音词为主，现代汉语以____词为主。","复音"),
     ("词汇","词义的扩大、缩小、转移","“江”由专指长江扩大为泛指河流，属于词义的____。","扩大"),
     ("词汇","词义的扩大、缩小、转移","“金”由泛指金属缩小为专指黄金，属于词义的____。","缩小"),
     ("词汇","词义的扩大、缩小、转移","“走”由“跑”义转移为“行走”义，属于词义的____。","转移"),
     ("词汇","词义感情色彩与轻重程度的变化","“爪牙”由“得力助手”演变为“帮凶”，属于词义____的变化。","感情色彩"),
     ("词汇","词义感情色彩与轻重程度的变化","“恨”古义为遗憾、不满，今义为怨恨，属于词义____的变化。","轻重"),
     ("词汇","词的本义","一个词由文字形体所表现出来的、并有上古文献资料印证的初始意义叫____。","本义"),
     ("词汇","词的本义","“斤”的本义是____（砍伐树木的工具）。","短斧"),
     ("词汇","词的引申义与引申方式","在本义的基础上发展衍生出来的相关意义叫____。","引申义"),
     ("词汇","词的引申义与引申方式","以本义为起点向一个方向引申的方式叫____引申。","单向"),
     ("词汇","词的引申义与引申方式","以本义为中心向两个或多个方向引申的方式叫____引申。","多向"),
     ("词汇","词的引申义与引申方式","“绝”断丝—割断—中断—隔绝—辽远这一引申系列属于____引申。","单向"),
     ("词汇","同义词辨析","“饥：饿也。饿：饥也”这种用同义词互相训释的方法叫____。","互训"),
     ("词汇","同义词辨析","“谄”可用于语言和体态，“谀”专用于语言的奉承，二者辨析在于____广狭不同。","范围"),
     ("文字（上）","六书说","“王”字本象斧状兵器“钺”之形，这种造字法属于____。","象形"),
     ("文字（上）","六书说","探求词的本义的两个途径是分析字形和____印证。","文献"),
     ("文字（下）","古今字","在某一种意义上先后产生的形体不同的一组字叫____。","古今字"),
     ("文字（下）","异体字","音同义同、笔画不同、在任何情况下都可以互换使用的一组字叫____。","异体字"),
     ("文字（下）","繁简字","简化字与被简化的繁体字合称为____字。","繁简"),
     ("文字（下）","古今字","“辟”与“避”、“取”与“娶”这类字属于____字。","古今"),
     ("文字（下）","通假字","“蚤”通“早”、“说”通“悦”这类属于____字。","通假"),
     ("音韵","反切","用两个字拼合成另一个字的传统注音方法叫____。","反切"),
     ("音韵","反切","反切取上字的____与下字的韵母和声调相拼合，得出被切字的读音。","声母"),
     ("音韵","声类、字母与三十六字母","宋代人在唐代守温和尚三十字母的基础上增补调整而成的字母系统叫____。","三十六字母"),
     ("音韵","五音七音与清浊","音韵学家依据发音部位划分的唇、舌、齿、牙、喉五类声母叫____。","五音"),
     ("音韵","阴声韵、阳声韵、入声韵","以元音收尾或没有韵尾的韵叫____声韵。","阴"),
     ("音韵","阴声韵、阳声韵、入声韵","以鼻音收尾的韵叫____声韵。","阳"),
     ("音韵","反切","改变一个字的原来读音以区别意义或词性的方法叫____，也叫读破。","破读"),
     ("音韵","上古音","明代陈第著____，彻底推翻了“叶音说”。","《毛诗古音考》"),
     ("音韵","中古声调到北京音的变化","中古汉语四声演变为现代普通话四声的规律是平分阴阳、____、入派三声。","浊上变去"),
     ("工具书简介","词典与《辞源》《辞海》《汉语大词典》","《尔雅》是我国第一部____（工具书类型）。","词典"),
     ("工具书简介","词典与《辞源》《辞海》《汉语大词典》","《方言》是我国最早研究____的专著，作者是扬雄。","方言"),
     ("工具书简介","词典与《辞源》《辞海》《汉语大词典》","《释名》是我国第一部____（训诂方式）学专著，东汉刘熙著。","声训"),
     ("工具书简介","训诂必读书目","《广雅》为三国魏____所著，清代王念孙的《广雅疏证》是对它的注释。","张揖"),
     ("工具书简介","训诂必读书目","清代王念孙著____，对《广雅》作了系统疏证。","《广雅疏证》"),
     ("音韵","《切韵》《广韵》与中古音","《广韵》全称《____》，是中古韵书的代表作，分206韵。","大宋重修广韵"),
     ("音韵","《切韵》《广韵》与中古音","《中原音韵》的作者是____，它是研究近古普通话语音的重要韵书。","周德清"),
     ("工具书简介","词典与《辞源》《辞海》《汉语大词典》","“望洋”“犹豫”“贪婪”等连绵词在书写上字无定形，这一现象体现的训诂方法是____。","因声求义"),
    ]

    existing = {norm(q["stem"]) for q in qs}
    new = []
    for ch, kpname, stem, ans in EX:
        nstem = norm(stem)
        if nstem in existing:
            continue
        kid = None
        for kp in kps:
            if kp.get("chapter") == ch and kp["name"].startswith(kpname[:4]):
                kid = kp["id"]; break
        if not kid:
            kid = first_kid.get(ch)
        q = {
            "id": f"gh_{len(qs)+len(new)+1:05d}",
            "type": "blank",
            "stem": stem,
            "options": [],
            "answer": ans,
            "explanation": f"依据古代汉语词汇/文字/音韵/工具书知识要点：{stem.replace('____','【'+ans+'】')}",
            "chapter": ch,
            "tags": ["笔记扩充"],
            "difficulty": "easy",
            "purpose": "basic",
            "knowledgeId": kid,
            "answerVariants": [],
        }
        new.append(q)
        existing.add(nstem)
    print(f"笔记扩充新增: {len(new)} 题")
    print(f"扩充各章: {Counter(q['chapter'] for q in new)}")

    qs.extend(new)
    # 题型/章节统计
    print("合并后总", len(qs), "| basic", sum(1 for q in qs if q.get('purpose')=='basic'), "| test", sum(1 for q in qs if q.get('purpose')=='test'))
    print("章节:", dict(Counter(q['chapter'] for q in qs)))
    nokid2 = sum(1 for q in qs if q.get("purpose")=="basic" and not q.get("knowledgeId"))
    print("合并后 basic 缺 knowledgeId:", nokid2)
    json.dump(qs, open(DST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("输出 →", DST)

if __name__ == "__main__":
    main()
