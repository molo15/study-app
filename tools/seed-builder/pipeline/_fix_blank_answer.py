# -*- coding: utf-8 -*-
"""复查并修复 blank 答案格式：
1) answer 含 '|' 的（多空）拆成数组（App _decodeAnswer 数组→Set，每空一个元素，判分才正确）
2) 检查答案残留异常（如末尾带年份、括号残留、空格）"""
import json, re, collections

files = {
    '古文史': r'D:\study_app\tools\seed-builder\out\refined\bank-zhongguo-gudai-wenxue.v012.json',
    '古汉': r'D:\study_app\tools\seed-builder\out\refined\bank-gudai-hanyu.v012.json',
    '现汉': r'D:\study_app\tools\seed-builder\out\refined\bank-xiandai-hanyu.refined2.json',
    '现文史': r'D:\study_app\tools\seed-builder\out\refined\bank-zhongguo-xiandai-wenxue.quota.json',
    '当代': r'D:\study_app\tools\seed-builder\out\refined\bank-zhongguo-dangdai-wenxue.refined2.json',
}
for name, f in files.items():
    qs = json.load(open(f, encoding='utf-8'))
    pipe_fixed = 0
    residual = []
    for q in qs:
        if q['type'] != 'blank':
            continue
        a = q.get('answer')
        # 含 | 的多空拆数组
        if isinstance(a, str) and '|' in a:
            parts = [p.strip() for p in a.split('|') if p.strip()]
            if len(parts) >= 2:
                q['answer'] = parts
                pipe_fixed += 1
        # 残留检查：答案含括号/年份/冒号/空白
        a2 = q.get('answer')
        joined = ' '.join(a2) if isinstance(a2, list) else str(a2)
        if re.search(r'[（(]|研|：|:|\s{2,}', joined):
            residual.append((q['id'], joined[:40]))
    json.dump(qs, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{name}: |拆数组 {pipe_fixed} 题 | 疑似残留 {len(residual)}')
    for r in residual[:5]:
        print('   ', r)
