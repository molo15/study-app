# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

samples = [
    '素材块zhmatvj、g531w5t记载比喻的定义与明喻、暗喻、借喻、博喻的分类，存量题未覆盖。',
    '解析：本题考查两种易混修辞格的辨析，须抓住「相关」与「相似」这一根本差异并结合例证说明。（拓展）',
    '素材块76aoq0a、2guk7r5、bdyqapv记载序跋的定义与关系，存量题q_000217只考跋的判断，本题做系统对比。',
    '对应素材标题"一、词汇的发展变化★★★【陕师16年-简答题】【陕师19、22年-论述题】"及正文块 aquqps6/87u4epd/gc22jj6/zn4487',
    '解析：类书为陕师17年名词解释真题。须答出概念、源流、体例、代表著作及不足。（基础）',
    '解析：须答出诔的用途（表彰功德、抒发哀悼）、所属类别（哀祭体）及代表作品。（变式）',
]

def clean_workexpl(e):
    e = re.sub(r'素材块[0-9a-zA-Z、，,]+', '', e)
    e = re.sub(r'对应素材标题[“”\"\'【】0-9a-zA-Z★]+', '', e)
    e = re.sub(r'正文块[0-9a-zA-Z/、，,]+', '', e)
    e = re.sub(r'素材n[0-9a-zA-Z\[\]为\]、，,]+', '', e)
    e = re.sub(r'素材[0-9a-zA-Z]{5,}[、，,，]*', '', e)
    e = re.sub(r'[（(](基础|变式|拓展|提升|综合|识记|理解)[）)]$', '', e)
    e = re.sub(r'本题属于.{0,25}常考基础点[,。，]?', '', e)
    e = re.sub(r'^解析[:：]\s*', '', e)
    e = re.sub(r'^(须答出|本题考查|本题为|本题是|答题要点[:：]?|须从|注意从|可从)[，,：:]?\s*', '', e)
    e = re.sub(r'^(需|应|要)?(从|由|按)[^。]{0,8}(作答|入手|出发)[，,：:]?\s*', '', e)
    e = e.strip()
    e = re.sub(r'^[，,。；;、：:\s]+', '', e)
    e = re.sub(r'[，,。；;、：:\s]+$', '', e)
    return e

for s in samples:
    print('IN :', s)
    print('OUT:', clean_workexpl(s))
    print()
