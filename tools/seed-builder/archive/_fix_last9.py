# -*- coding: utf-8 -*-
"""处理最后 9 条顽固残留：解析直接用 answer 完整答案替换（answer 均为长答案）。"""
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

cases = [
    (r'out\v09gudaihanyu\bank-gudai-hanyu.v09.json', ['m_000543', 'c_000020']),
    (r'out\v09xiandaiwenxue\bank-zhongguo-xiandai-wenxue.v09.json', ['c_000011', 'c_000026', 'c_000030', 'c_000031', 'c_000120']),
]
# 需要保留"答题思路"前缀的（解析有实质价值的）改为清洗：
# c_000011 和 m_000543 保留清洗后的思路文本；其余直接用 answer
for p, tails in cases:
    d = json.load(open(p, encoding='utf-8'))
    for q in d:
        if any(q.get('id', '').endswith(t) for t in tails):
            ans = q.get('answer') or ''
            if isinstance(ans, list):
                ans = '；'.join(str(x) for x in ans)
            old = q.get('explanation') or ''
            print('处理', q.get('id'))
            # 判断解析是否有实质内容（长度>25 且非纯工作词）
            e_norm = re.sub(r'\s+', '', old)
            is_workonly = ('覆盖缺口' in e_norm or '核心考点' in e_norm or '类强化' in e_norm
                           or '标题考点' in e_norm or (len(e_norm) < 40))
            if is_workonly:
                q['explanation'] = str(ans).strip()
                print('  -> 用answer替换:', str(ans)[:60])
            else:
                # 保留思路，去掉句尾工作词
                new = re.sub(r'[，,;；]?(简答|答题)?须[^。]{0,30}[。]?$', '', old)
                new = re.sub(r'[，,;；]?作答时注意[^。]{0,20}[。]?$', '', new)
                new = new.strip().rstrip('，,；;')
                q['explanation'] = new
                print('  -> 保留思路:', new[:60])
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('done')
