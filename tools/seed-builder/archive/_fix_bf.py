# -*- coding: utf-8 -*-
"""P1-B/F 修复：简答/名解/论述题解析若为“素材底稿残留/提示语/过短”，直接采用 answer 完整答案作为解析。
处理源文件：5 科 v09 json（保留轨测试题）。
规则：
- 对 short_answer 题
- 若解析含 素材块/对应素材标题/正文块/素材n / 或匹配“须答出|本题考查|本题为|答题要点|须从|注意从|可从”开头提示
- 或解析长度过短(<40)
→ 解析 = answer 完整文本（answer 已有完整答案）；若解析已有实质内容且较长，仅去格式尾巴。
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

pat_resid = re.compile(r'素材块|对应素材标题|正文块|素材n|素材[0-9a-z]{5,}')
pat_hint = re.compile(r'^(解析[:：]?\s*)?(须答出|本题考查|本题为|答题要点|须从|注意从|可从)')

def clean_tail(e):
    """去等级标注尾巴（基础/变式/拓展）+ 本题属于尾巴 + 解析冒号前缀"""
    e = re.sub(r'[（(](基础|变式|拓展|提升|综合|识记|理解)[）)]$', '', e)
    e = re.sub(r'本题属于.{0,25}常考基础点[,。，]?', '', e)
    e = re.sub(r'^解析[:：]\s*', '', e)
    return e.strip()

total_fixed = 0
for bank, p in SRCS.items():
    d = json.load(open(p, encoding='utf-8'))
    n = 0
    for q in d:
        if q.get('type') != 'short_answer':
            continue
        expl = q.get('explanation') or ''
        ans = q.get('answer') or ''
        if isinstance(ans, list):
            ans = '、'.join(ans)
        ans = str(ans).strip()
        e = re.sub(r'\s+', '', expl)
        a = re.sub(r'\s+', '', ans)
        # 判定是否为“无实质解析”
        bad = False
        if not e or len(e) < 40:
            bad = True
        elif pat_resid.search(e):
            bad = True
        elif pat_hint.match(expl.strip()):
            bad = True
        if bad and len(a) >= 20:
            # 用 answer 作为解析（保持格式，去等级尾巴）
            new_expl = clean_tail(ans)
            if len(new_expl) >= 20 and new_expl != e:
                q['explanation'] = new_expl
                n += 1
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    total_fixed += n
    print(f'[{bank}] 修复 {n} 条短答解析')
print('合计:', total_fixed)
