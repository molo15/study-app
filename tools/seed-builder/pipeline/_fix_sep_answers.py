# -*- coding: utf-8 -*-
"""精修含顿号/斜杠答案的 blank 题：多空列举→每空 variants，单空等价→等价组。"""
import json

FIX = {
    # 现汉
    "bank-xiandai-hanyu:w_000296":
        (["年纪小", "还", "懂"], [["年纪小"], ["还"], ["懂"]]),
    "bank-xiandai-hanyu:w_000305":
        (["的、了、吗、呢、吧、啊"], [["的", "了", "吗", "呢", "吧", "啊"]]),
    "bank-xiandai-hanyu:w_000067":
        (["p", "b"], [["p", "t", "k", "q", "ch", "c"], ["b", "d", "g", "j", "zh", "z"]]),
    "bank-xiandai-hanyu:w_000073":
        (["i", "i", "n"], [["i", "u", "ü"], ["i", "u", "o"], ["n", "ng"]]),
    "bank-xiandai-hanyu:w_000078":
        (["a", "i", "ng"], [["a", "e", "o"], ["i", "u"], ["n", "ng"]]),
    # 古汉
    "bank-gudai-hanyu:z_000045":
        (["责备、谴责"], [["责备", "谴责"]]),
    "bank-gudai-hanyu:m_000100":
        (["接着、于是"], [["接着", "于是"]]),
    "bank-gudai-hanyu:q_000232":
        (["每年每月"], [["每年", "每月", "岁岁", "月月"]]),
    "bank-gudai-hanyu:kb_00111":
        (["谦称、尊称"], [["谦称", "尊称"]]),
    # 古文史（四家诗：第4空毛亨毛苌）
    "bank-zhongguo-gudai-wenxue:t_000082":
        (["辕固生", "申培", "韩婴", "毛亨、毛苌"],
         [["辕固生", "齐之辕固生"], ["申培", "鲁之申培"], ["韩婴", "燕之韩婴"], ["毛亨毛苌", "毛亨、毛苌", "毛苌、毛亨"]]),
    # 当代
    "bank-zhongguo-dangdai-wenxue:q_000084":
        (["白发、皱纹"], [["白发", "皱纹"]]),
}

files = {
    '现汉': r'D:\study_app\tools\seed-builder\out\refined\bank-xiandai-hanyu.refined2.json',
    '古汉': r'D:\study_app\tools\seed-builder\out\refined\bank-gudai-hanyu.v012.json',
    '古文史': r'D:\study_app\tools\seed-builder\out\refined\bank-zhongguo-gudai-wenxue.v012.json',
    '当代': r'D:\study_app\tools\seed-builder\out\refined\bank-zhongguo-dangdai-wenxue.refined2.json',
}
done = 0
for name, f in files.items():
    qs = json.load(open(f, encoding='utf-8'))
    for q in qs:
        if q['id'] in FIX:
            ans, var = FIX[q['id']]
            q['answer'] = ans
            q['answerVariants'] = var
            done += 1
            print('精修', q['id'], '->', ans, var)
    json.dump(qs, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('共精修', done, '题')
