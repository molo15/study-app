# -*- coding: utf-8 -*-
"""第三轮：清理 c_ 简答解析中的出题工作底稿
- 覆盖…考点 / 覆盖缺口考点 / 为审查报告覆盖缺口第X项
- 素材见[...] / 依据…素材块 / 整合[...]
- 须从…作答 / 简答须… / 需答… 等句尾工作指示
- （测试）（★考点）（缺口考点）（基础）（变式）等标注
- 出题语境词 如“标题考点”
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

WORK2 = [
    # 句尾工作指示（以“作/答/需/须”结尾的工作语）
    r'[，,;；]?(作答|答题|简答|解题)?[须需]从[^。]{0,20}(作答|答题|说明|展开|对比|区分|点出|分点|进行|组织)[。]?$',
    r'[，,;；]?(作答|答题|简答)?[须需][答出|点明|点出|涵盖|答全|分清|区分|先总体|分层|分点|注意|结合|围绕][^。]{0,25}[。]?$',
    r'[，,;；]?答题[需须][^。]{0,25}[。]?$',
    r'[，,;；]?作答以自圆其说为主[。]?$',
    r'[，,;；]?分论点依据文学史通识组织[。]?$',
    r'[，,;；]?素材仅存标题未展开细目[。]?$',
    r'[，,;；]?素材未展开细节[。]?$',
    r'[，,;；]?老舍一侧为答题对照所需的常识性概括[。]?$',
    # 覆盖考点
    r'[，,;；]?覆盖[“”\']?[^，。]{2,24}[“”\']?考点[。]?$',
    r'[，,;；]?覆盖缺口考点[“”\']?[^，。]{0,20}[。]?$',
    r'[，,;；]?为审查报告覆盖缺口[第]?[一二三四五六0-9]*项[。]?$',
    r'[，,;；]?属存量未覆盖的缺口考点[。]?$',
    r'[，,;；]?属缺口考点[。]?$',
    r'[，,;；]?为缺口考点[。]?$',
    r'[，,;；]?存量仅考[^。]{0,15}[。]?$',
    r'[，,;；]?存量题未覆盖[。]?$',
    # 素材引用
    r'[，,;；]?素材见\[[^\]]*\](\[[^\]]*\])*[。]?$',
    r'[，,;；]?整合\[[^\]]*\](\[[^\]]*\])*[。]?$',
    r'[，,;；]?依据[-0-9a-zA-Z、，,及\[进\]{0,30}素材块?[。]?$',
    r'[，,;；]?素材为[^。]{0,15}选段[。]?$',
    r'[，,;；]?素材完整列出[^。]{0,15}[。]?$',
    # 标题考点
    r'[，,;；]?["“\']?[^。]{2,30}["”\']?标题考点[。]?$',
    r'[，,;；]?为素材[^。]{0,10}(标示|标注)的[^。]{0,12}考点[。]?$',
    # 标注
    r'[（(](测试|★考点|★★考点|★★★考点|缺口考点|基础|变式|拓展|提升|综合|识记|理解)[）)]$',
    r'[（(]★[）)]$',
]

def clean3(e):
    if not e:
        return e
    for p in WORK2:
        e = re.sub(p, '', e)
    e = e.strip()
    e = re.sub(r'[，,。；;、：:\s]+$', '', e)
    e = re.sub(r'^[，,。；;、：:\s]+', '', e)
    return e

total = 0
for bank, p in SRCS.items():
    d = json.load(open(p, encoding='utf-8'))
    n = 0
    for q in d:
        if q.get('type') != 'short_answer':
            continue
        e = q.get('explanation') or ''
        new = clean3(e)
        if new != e:
            q['explanation'] = new
            n += 1
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    total += n
    print(f'[{bank}] 三轮清理 {n}')
print('合计:', total)
