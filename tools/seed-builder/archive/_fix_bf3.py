# -*- coding: utf-8 -*-
"""P1-B/F 修复（v2 方案）：
简答/名解/论述题：
- 解析含底稿残留/机械提示/过短 → 清洗；清洗后仍有实质(>=25) 则保留清洗版，否则置空
  让 App 只展示完整参考答案(answer)。
- 同时处理 P2 格式：等级尾巴/本题属于尾巴/解析冒号前缀（对所有题型生效）
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

# P2 格式清洗（所有题型）
def clean_format(e):
    if not e:
        return e
    e = re.sub(r'[（(](基础|变式|拓展|提升|综合|识记|理解)[）)]$', '', e)
    e = re.sub(r'本题属于.{0,25}常考基础点[,。，]?\s*', '', e)
    e = re.sub(r'^解析[:：]\s*', '', e)
    # 素材/底稿引用
    e = re.sub(r'素材块[0-9a-zA-Z、，,]+', '', e)
    e = re.sub(r'正文块[0-9a-zA-Z/、，,]+', '', e)
    e = re.sub(r'素材n[0-9a-zA-Z\[\]为\]、，,]+', '', e)
    e = re.sub(r'素材[0-9a-zA-Z]{5,}[、，,，]*', '', e)
    e = re.sub(r'对应素材标题["“\'【】0-9a-zA-Z★]+["”\']?', '', e)
    # 出题工作语境残句
    e = re.sub(r'，?存量题未覆盖[。]?', '', e)
    e = re.sub(r'，?存量题[^。]{0,15}未覆盖[。]?', '', e)
    e = re.sub(r'，?本题做系统对比[。]?', '', e)
    e = re.sub(r'，?本题做[^。]{0,10}考查[。]?', '', e)
    e = re.sub(r'，?本题补全[。]?', '', e)
    e = re.sub(r'，?本题补齐[。]?', '', e)
    e = re.sub(r'，?是覆盖缺口补齐项[。]?', '', e)
    e = re.sub(r'，?本题系统整合[。]?', '', e)
    e = re.sub(r'，?本题要求展开[^。]{0,10}[。]?', '', e)
    e = re.sub(r'，?本题做细目考查[。]?', '', e)
    e = re.sub(r'，?本题做系统考查[。]?', '', e)
    e = re.sub(r'，?本题整合为[^。]{0,10}[。]?', '', e)
    e = re.sub(r'，?存量题只考[^。]{0,12}[。]?', '', e)
    e = re.sub(r'，?存量题只考了[^。]{0,15}[。]?', '', e)
    e = re.sub(r'，?存量题[^。]{0,20}[。]?', '', e)
    e = e.strip()
    e = re.sub(r'^[，,。；;、：:\s]+', '', e)
    e = re.sub(r'[，,。；;、：:\s]+$', '', e)
    return e

# 简答提示语清洗
def clean_hint(e):
    e = re.sub(r'^解析[:：]\s*', '', e)
    e = re.sub(r'^(须答出|本题考查|本题为|本题是|答题要点[:：]?|须从|注意从|可从)[，,：:]?\s*', '', e)
    e = re.sub(r'^(需|应|要)?(从|由|按)[^。]{0,8}(作答|入手|出发)[，,：:]?\s*', '', e)
    return e.strip()

total = {'format': 0, 'bf_clean': 0, 'bf_empty': 0}
for bank, p in SRCS.items():
    d = json.load(open(p, encoding='utf-8'))
    n_f = n_c = n_e = 0
    for q in d:
        expl = q.get('explanation') or ''
        # 先做格式清洗（所有题型）
        newf = clean_format(expl)
        if newf != expl:
            q['explanation'] = newf
            n_f += 1
        # 简答题：判断是否需要处理提示语
        if q.get('type') == 'short_answer':
            e2 = q.get('explanation') or ''
            e_norm = re.sub(r'\s+', '', e2)
            need = (not e_norm or len(e_norm) < 20 or
                    re.match(r'^(解析[:：]|须答出|本题考查|本题为|答题要点)', e2.strip()))
            if need:
                newh = clean_hint(e2)
                if len(newh) >= 25:
                    q['explanation'] = newh
                    n_c += 1
                else:
                    q['explanation'] = ''
                    n_e += 1
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    total['format'] += n_f
    total['bf_clean'] += n_c
    total['bf_empty'] += n_e
    print(f'[{bank}] 格式清洗{n_f} / 简答保留{n_c} / 简答置空{n_e}')
print('合计:', total)
