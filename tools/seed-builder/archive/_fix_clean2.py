# -*- coding: utf-8 -*-
"""第二轮精确清理：残留的 素材块[xxx] / 对应素材块[xxx] / 半截引导词 / 出题语境词
只清理引用与引导词，保留实质内容。对所有题型生效。
"""
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRCS = {
    'bank-xiandai-hanyu': r'out\v09\bank-xiandai-hanyu.v09.json',
    'bank-gudai-hanyu': r'out\v09gudaihanyu\bank-gudai-hanyu.v09.json',
    'bank-zhongguo-gudai-wenxue': r'out\v09gudaiwenxue\bank-zhongguo-gudai-wenxue.v09.json',
    'bank-zhongguo-xiandai-wenxue': r'out\v09xiandaiwenxue\bank-zhongguo-xiandai-wenxue.v09.json',
    'bank-zhongguo-dangdai-wenxue': r'out\v09dangdai\bank-zhongguo-dangdai-wenxue.v09.json',
}

# 素材引用（含方括号格式）
MAT = [
    r'(对应)?素材块\s*\[?[0-9a-zA-Z\-]+\]?\s*[:：]?',
    r'(对应)?素材块\s*[0-9a-zA-Z\-]+\s*[:：]?',
    r'正文块\s*[0-9a-zA-Z/、，,]+',
    r'素材n\s*[0-9a-zA-Z\[\]为\]、，,]+',
    r'素材\s*\[?[0-9a-zA-Z\-]+\]?\s*[:：]?',
    r'对应素材标题\s*["“\'【】0-9a-zA-Z★]+["”\']?',
]
# 出题工作语境半截词（句末）
WORK = [
    r'作答须[^。]*[。]?$', r'答题须[^。]*[。]?$', r'答题[时要点][^。]*[。]?$',
    r'须答出[^。]*[。]?$', r'须从[^。]*[。]?$', r'须按[^。]*[。]?$', r'须抓住[^。]*[。]?$',
    r'本题为[^。]{0,12}[。]?$', r'本题属[^。]{0,12}[。]?$', r'本题做[^。]{0,12}[。]?$',
    r'本题即[^。]{0,12}[。]?$', r'本题将[^。]{0,12}[。]?$', r'本题保留考查[。]?$',
    r'本题作为[^。]{0,20}[。]?$', r'本题整合[^。]{0,12}[。]?$', r'本题补[^。]{0,10}[。]?$',
    r'存量题[^。]{0,24}[。]?$', r'覆盖缺口[^。]{0,20}[。]?$',
    r'为审查报告覆盖缺口[^。]{0,15}[。]?$', r'系统对比[。]?$', r'系统整合[。]?$',
    r'细目考查[。]?$', r'保留考查[。]?$', r'真题同类[^。]{0,15}[。]?$',
    r'强化练习[。]?$', r'类强化[。]?$', r'出题时[^。]{0,10}[。]?$',
    r'题补[^。]{0,8}[。]?$', r'题做[^。]{0,8}[。]?$',
    r'求方法作同类强化[。]?$', r'本题求方法[^。]{0,10}[。]?$',
    r'简答须[^。]{0,15}[。]?$', r'作答时[^。]{0,12}[。]?$',
]
# 句首引导词
LEAD = [
    r'^(须答出|本题考查|本题为|本题是|答题要点[:：]?|须从|须按|须抓住|作答须|答题须|注意从|可从|本题属|本题做)[，,：:]?\s*',
    r'^(需|应|要)?(从|由|按)[^。]{0,8}(作答|入手|出发)[，,：:]?\s*',
]
# 素材引用后续“记载/明确/指出”等
VERB = [r'^记载[:：]?', r'^指出[:：]?', r'^明确[:：]?', r'^为[:：]?', r'^引[:：]?']

def clean2(e):
    if not e:
        return e
    for p in MAT:
        e = re.sub(p, '', e)
    for p in WORK:
        e = re.sub(p, '', e)
    for p in LEAD:
        e = re.sub(p, '', e)
    for p in VERB:
        e = re.sub(p, '', e)
    # 清理“的作答/的考查/的运用”残留引导
    e = re.sub(r'^[，,。；;、：:\s]+', '', e)
    e = re.sub(r'[，,。；;、：:\s]+$', '', e)
    # 若结尾只剩“等块内容组织”“各书定义”“记载”类
    e = re.sub(r'等块内容组织[。]?$', '', e)
    e = re.sub(r'各书定义[。]?$', '', e)
    e = re.sub(r'提供各书定义与例字[。]?$', '', e)
    e = re.sub(r'及[^。]{0,6}相关例证[。]?$', '', e)
    return e.strip()

total = 0
for bank, p in SRCS.items():
    d = json.load(open(p, encoding='utf-8'))
    n = 0
    for q in d:
        e = q.get('explanation') or ''
        new = clean2(e)
        if new != e:
            q['explanation'] = new
            n += 1
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    total += n
    print(f'[{bank}] 二次清理 {n}')
print('合计:', total)
