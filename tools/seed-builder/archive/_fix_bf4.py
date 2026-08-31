# -*- coding: utf-8 -*-
"""P1-B/F + P2 修复（v3，修正版）：
- 对 ALL 题型：去除解析中的 素材块/正文块/素材n/对应素材标题 引用、等级尾巴、本题属于尾巴、解析冒号前缀
- 对 short_answer：若解析为底稿残留/提示语/过短，清洗后>=25 保留，否则置空（App 只显示完整参考答案 answer）
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

MAT_REF = [
    r'素材块\s*[0-9a-zA-Z、，,~\-]+',
    r'正文块\s*[0-9a-zA-Z/、，,]+',
    r'素材n\s*[0-9a-zA-Z\[\]为\]、，,]+',
    r'素材\s*[0-9a-zA-Z]{5,}[、，,，~\-]*',
    r'对应素材标题\s*["“\'【】0-9a-zA-Z★]+["”\']?',
]
WORK_TAIL = [
    r'，?存量题未覆盖[。]?',
    r'，?存量题[^。]{0,18}未覆盖[。]?',
    r'，?本题做系统对比[。]?',
    r'，?本题做[^。]{0,12}考查[。]?',
    r'，?本题补全[。]?',
    r'，?本题补齐[。]?',
    r'，?是覆盖缺口补齐项[。]?',
    r'，?本题系统整合[。]?',
    r'，?本题要求展开[^。]{0,14}[。]?',
    r'，?本题做细目考查[。]?',
    r'，?本题做系统考查[。]?',
    r'，?本题整合为[^。]{0,12}[。]?',
    r'，?本题补[^。]{0,10}[。]?',
    r'，?存量题[^。]{0,24}[。]?',
    r'，?本题保留考查[。]?',
    r'，?本题作为真题同类题保留考查[。]?',
    r'，?本题即真题考查[。]?',
    r'，?本题将两句合并考查[^。]{0,14}[。]?',
    r'，?本题整合翻译与活用辨析[^。]{0,10}[。]?',
    r'，?本题综合考查[^。]{0,16}[。]?',
    r'，?本题系统对比[。]?',
    r'，?本题做系统对比[。]?',
    r'，?本题为经典断句翻译练习[^。]{0,20}[。]?',
    r'，?本题为默写[^。]{0,40}[。]?',
]
# 记录含出题语境词的尾巴统一处理
def clean_format(e):
    if not e:
        return e
    e = re.sub(r'[（(](基础|变式|拓展|提升|综合|识记|理解)[）)]$', '', e)
    e = re.sub(r'本题属于.{0,25}常考基础点[,。，]?\s*', '', e)
    e = re.sub(r'^解析[:：]\s*', '', e)
    for pat in MAT_REF:
        e = re.sub(pat, '', e)
    for pat in WORK_TAIL:
        e = re.sub(pat, '', e)
    e = e.strip()
    e = re.sub(r'^[，,。；;、：:\s]+', '', e)
    e = re.sub(r'[，,。；;、：:\s]+$', '', e)
    # 残句
    e = re.sub(r'^记载', '', e)
    e = re.sub(r'^指出[:：]?', '', e)
    e = re.sub(r'^明确[:：]?', '', e)
    return e.strip()

def clean_hint(e):
    e = re.sub(r'^解析[:：]\s*', '', e)
    e = re.sub(r'^(须答出|本题考查|本题为|本题是|答题要点[:：]?|须从|注意从|可从)[，,：:]?\s*', '', e)
    e = re.sub(r'^(需|应|要)?(从|由|按)[^。]{0,8}(作答|入手|出发)[，,：:]?\s*', '', e)
    return e.strip()

total = {'format': 0, 'sa_keep': 0, 'sa_empty': 0, 'sa_noans': 0}
for bank, p in SRCS.items():
    d = json.load(open(p, encoding='utf-8'))
    n_f = n_k = n_e = n_no = 0
    for q in d:
        expl = q.get('explanation') or ''
        newf = clean_format(expl)
        if newf != expl:
            q['explanation'] = newf
            n_f += 1
        if q.get('type') == 'short_answer':
            e2 = q.get('explanation') or ''
            e_norm = re.sub(r'\s+', '', e2)
            is_bad = (not e_norm or len(e_norm) < 20 or
                      re.search(r'素材块|正文块|素材n|素材[0-9a-zA-Z]{5,}', e_norm) or
                      re.match(r'^(解析[:：]|须答出|本题考查|本题为|本题是|答题要点)', e2.strip()) or
                      re.search(r'存量题|本题(做|为|属|即|将|要求|补|保留)', e_norm))
            if is_bad:
                newh = clean_hint(e2)
                if len(newh) >= 25:
                    q['explanation'] = newh
                    n_k += 1
                else:
                    ans = q.get('answer') or ''
                    if isinstance(ans, list):
                        ans = '；'.join(str(x) for x in ans)
                    if len(re.sub(r'\s+', '', str(ans))) >= 25:
                        q['explanation'] = ''
                        n_e += 1
                    else:
                        n_no += 1
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    total['format'] += n_f
    total['sa_keep'] += n_k
    total['sa_empty'] += n_e
    total['sa_noans'] += n_no
    print(f'[{bank}] 格式{n_f} / 简答保留{n_k} / 置空{n_e} / 未动{n_no}')
print('合计:', total)
