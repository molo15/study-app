# -*- coding: utf-8 -*-
"""P1-B/F 修复：简答/名解/论述题解析清洗
- 去掉 素材块/正文块/对应素材标题 等底稿引用
- 去掉 解析：前缀、等级标注尾巴、(基础/变式/拓展)
- 去掉 “须答出”“本题考查”“本题为”“答题要点” 等机械提示前缀（保留实质内容）
- 若清洗后为空或过短(<20)，用 answer 完整答案作为解析
- 若清洗后仍有实质内容(>=20)，保留清洗后文本（去掉与 answer 重复的开头）
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

def clean_workexpl(e):
    """清洗解析中的工作底稿/机械提示/格式尾巴"""
    # 去素材引用（素材块xxx / 正文块xxx / 对应素材标题xxx / 素材nxxx）
    e = re.sub(r'素材块[0-9a-zA-Z、，,]+', '', e)
    e = re.sub(r'对应素材标题[“”"\'【】0-9a-zA-Z★]+', '', e)
    e = re.sub(r'正文块[0-9a-zA-Z/、，,]+', '', e)
    e = re.sub(r'素材n[0-9a-zA-Z\[\]为\]、，,]+', '', e)
    e = re.sub(r'素材[0-9a-zA-Z]{5,}[、，,，]*', '', e)
    # 去等级尾巴
    e = re.sub(r'[（(](基础|变式|拓展|提升|综合|识记|理解)[）)]$', '', e)
    e = re.sub(r'本题属于.{0,25}常考基础点[,。，]?', '', e)
    # 去前缀
    e = re.sub(r'^解析[:：]\s*', '', e)
    e = re.sub(r'^(须答出|本题考查|本题为|本题是|答题要点[:：]?|须从|注意从|可从)[，,：:]?\s*', '', e)
    e = re.sub(r'^(需|应|要)?(从|由|按)[^。]{0,8}(作答|入手|出发)[，,：:]?\s*', '', e)
    e = e.strip()
    e = re.sub(r'^[，,。；;、：:\s]+', '', e)
    e = re.sub(r'[，,。；;、：:\s]+$', '', e)
    return e

total_fixed = 0
stats = {'cleaned': 0, 'from_answer': 0}
for bank, p in SRCS.items():
    d = json.load(open(p, encoding='utf-8'))
    n_clean = n_ans = 0
    for q in d:
        if q.get('type') != 'short_answer':
            continue
        expl = q.get('explanation') or ''
        ans = q.get('answer') or ''
        if isinstance(ans, list):
            ans = '；'.join(str(x) for x in ans)
        ans = str(ans).strip()
        # 判定是否需要处理：底稿/提示语/过短
        e_norm = re.sub(r'\s+', '', expl)
        need = (not e_norm or len(e_norm) < 20 or
                re.search(r'素材块|正文块|素材n|对应素材标题|素材[0-9a-zA-Z]{5,}', e_norm) or
                re.match(r'^(解析[:：]|须答出|本题考查|本题为|答题要点)', expl.strip()))
        if not need:
            continue
        new = clean_workexpl(expl)
        if len(new) >= 25:
            q['explanation'] = new
            n_clean += 1
        elif len(re.sub(r'\s+', '', ans)) >= 25:
            q['explanation'] = ans  # answer 作为解析
            n_ans += 1
        else:
            q['explanation'] = new if new else ans
            n_ans += 1
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    total_fixed += n_clean + n_ans
    stats['cleaned'] += n_clean
    stats['from_answer'] += n_ans
    print(f'[{bank}] 清洗 {n_clean} / 用答案 {n_ans}')
print('合计:', total_fixed, stats)
