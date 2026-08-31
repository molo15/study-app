# -*- coding: utf-8 -*-
"""修 b_000318 + 14 条 c_ 残留：
- b_000318: 解析改为文本结论（不含字母）
- c_ 简答: 清「依据-xxx」素材引用尾巴
"""
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# b_000318 当代
P4 = r'D:\study_app\tools\seed-builder\out\v09dangdai\bank-zhongguo-dangdai-wenxue.v09.json'
v09d = json.load(open(P4, encoding='utf-8'))
for q in v09d:
    if q['id'] == 'bank-zhongguo-dangdai-wenxue:b_000318':
        old = q.get('explanation', '')
        # 去掉字母排除结论，改为文本描述
        q['explanation'] = re.sub(r'。?[A-D]、?[A-D]?不属于其内容分类$', '', old)
        q['explanation'] = q['explanation'].strip() + '。知识青年上山下乡、拨乱反正成就不属于悲悼散文的两类内容。'
        print('b_000318 new:', q['explanation'][-70:])
json.dump(v09d, open(P4, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 14 条 c_ 现代文学
P3 = r'D:\study_app\tools\seed-builder\out\v09xiandaiwenxue\bank-zhongguo-xiandai-wenxue.v09.json'
v09m = json.load(open(P3, encoding='utf-8'))
n = 0
for q in v09m:
    if q['id'].startswith('bank-zhongguo-xiandai-wenxue:c_'):
        e = q.get('explanation', '')
        new = re.sub(r'[。;；]?依据-[0-9a-z]+、[\s\S]*$', '', e).strip()
        new = re.sub(r'[。]?依据-[0-9a-z]+$', '', new).strip()
        if new != e:
            q['explanation'] = new
            n += 1
json.dump(v09m, open(P3, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('c_ 简答清洗:', n)
