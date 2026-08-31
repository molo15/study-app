# -*- coding: utf-8 -*-
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRCS = {
    'bank-xiandai-hanyu': r'out\v09\bank-xiandai-hanyu.v09.json',
    'bank-gudai-hanyu': r'out\v09gudaihanyu\bank-gudai-hanyu.v09.json',
    'bank-zhongguo-gudai-wenxue': r'out\v09gudaiwenxue\bank-zhongguo-gudai-wenxue.v09.json',
    'bank-zhongguo-xiandai-wenxue': r'out\v09xiandaiwenxue\bank-zhongguo-xiandai-wenxue.v09.json',
    'bank-zhongguo-dangdai-wenxue': r'out\v09dangdai\bank-zhongguo-dangdai-wenxue.v09.json',
}
# 残留检测
pat_mat = re.compile(r'素材块|正文块|素材n|素材[0-9a-zA-Z]{5,}|对应素材标题')
pat_grade = re.compile(r'[（(](基础|变式|拓展|提升|综合|识记|理解)[）)]$')
pat_lead = re.compile(r'^解析[:：]')
pat_hint = re.compile(r'^(须答出|本题考查|本题为|本题是|答题要点|须从|注意从|可从)')
pat_half = re.compile(r'(作答须|作答时|须[从按]|须答出|答题[时要点]|本题为|本题做|本题属|存量题|覆盖缺口|补齐项|系统对比|系统整合|细目考查|保留考查|真题同类|强化练习|类强化|出题时|题补|题做|求方法作同类强化)')
for bank, p in SRCS.items():
    d = json.load(open(p, encoding='utf-8'))
    c_mat = c_grade = c_lead = c_hint = c_half = 0
    half_samples = []
    for q in d:
        e = re.sub(r'\s+', '', q.get('explanation') or '')
        if not e: continue
        if pat_mat.search(e): c_mat += 1
        if pat_grade.search(e): c_grade += 1
        if pat_lead.match(e): c_lead += 1
        if pat_hint.match(e): c_hint += 1
        m = pat_half.search(e)
        if m:
            c_half += 1
            if len(half_samples) < 8:
                half_samples.append((q.get('id'), q.get('type'), m.group(0), e[-45:]))
    print(f'== {bank}: 素材{c_mat} 等级{c_grade} 前缀{c_lead} 提示{c_hint} 半截词{c_half}')
    for s in half_samples:
        print('   ', s)
