# -*- coding: utf-8 -*-
"""交叉验证修复：多空/括号等价答案 → App 原生 answerVariants 格式。
每题显式精修 answer（主答案，可多元素=多空）+ answerVariants（每空等价答案组）。"""
import json, re

# 待修复清单：id -> (answer, answerVariants)
# answer: list[str]，每个元素一"空"的主答案；answerVariants: list[list[str]]，每空等价组
FIX = {
    # ===== 古汉 =====
    "bank-gudai-hanyu:z_000013":
        (["科学性"], [["科学性", "源流并重"]]),
    "bank-gudai-hanyu:z_000031":
        (["异体字", "意符"], [["异体字"], ["意符", "形旁", "偏旁"]]),
    "bank-gudai-hanyu:z_000040":
        (["包咸", "犹"], [["包咸"], ["犹", "当"]]),
    "bank-gudai-hanyu:m_000245":
        (["衍文", "脱文"], [["衍文", "衍字", "衍"], ["脱文", "脱字", "脱", "夺"]]),
    "bank-gudai-hanyu:z_000042":
        (["直接引申义", "间接引申义"], [["直接引申义", "近引申义"], ["间接引申义", "远引申义"]]),
    "bank-gudai-hanyu:z_000043":
        (["极、尽", "酒醒"], [["极", "尽", "洞穴的顶端", "洞穴的尽头"], ["酒醒"]]),
    "bank-gudai-hanyu:q_000115":
        (["使人贫穷"], [["使人贫穷", "使贫穷", "使百姓贫穷"]]),
    "bank-gudai-hanyu:m_000115":
        (["名词作状语", "在路上"], [["名词作状语"], ["在路上", "半道上"]]),
    "bank-gudai-hanyu:kb_00055":
        (["隶书"], [["隶书", "隶变"]]),
    "bank-gudai-hanyu:kb_00120":
        (["介词“于”", "代词“是”"], [["于"], ["是", "此", "之"]]),
    "bank-gudai-hanyu:kb_00145":
        (["y"], [["y", "ü"]]),
    # ===== 现汉 =====
    "bank-xiandai-hanyu:kb_00015":
        (["结构", "内容"], [["结构", "形式"], ["内容", "意义"]]),
    "bank-xiandai-hanyu:b_000031":
        (["特征"], [["特征", "标志"]]),
    "bank-xiandai-hanyu:z_000117":
        (["附加式", "偏正式"], [["附加式", "派生式"], ["偏正式", "复合式中的偏正"]]),
    "bank-xiandai-hanyu:w_000327":
        (["时间处所补语"], [["时间处所补语", "时地补语"]]),
    "bank-xiandai-hanyu:w_000329":
        (["施事"], [["施事", "施动者"]]),
    "bank-xiandai-hanyu:z_000018":
        (["阻碍方式", "声带是否振动", "气流强弱", "元音"],
         [["阻碍方式", "发音方法中的阻碍情况"], ["声带是否振动"], ["气流强弱"], ["元音"]]),
    "bank-xiandai-hanyu:w_000079":
        (["i", "-i（前）", "-i（后）", "开口呼"],
         [["i"], ["-i前", "-i（前）"], ["-i后", "-i（后）"], ["开口呼"]]),
    "bank-xiandai-hanyu:kb_00001":
        (["修辞规律", "修辞活动", "修辞学"], [["修辞规律"], ["修辞活动"], ["修辞学", "修辞著作"]]),
    "bank-xiandai-hanyu:kb_00036":
        (["形旁", "声旁"], [["形旁", "意符"], ["声旁", "音符"]]),
    "bank-xiandai-hanyu:kb_00082":
        (["成语", "惯用语", "歇后语", "固定"],
         [["成语"], ["惯用语"], ["歇后语", "谚语"], ["固定"]]),
    "bank-xiandai-hanyu:kb_00097":
        (["当事主语"], [["当事主语", "中性主语"]]),
    # ===== 古文史 =====
    "bank-zhongguo-gudai-wenxue:b_000034":
        (["别人的传记"], [["别人的传记", "他人的传记"]]),
    "bank-zhongguo-gudai-wenxue:t_000232":
        (["《庄子》和《楚辞》"], [["《庄子》和《楚辞》", "庄子与楚辞"]]),
}

files = {
    '古汉': r'D:\study_app\tools\seed-builder\out\refined\bank-gudai-hanyu.v012.json',
    '现汉': r'D:\study_app\tools\seed-builder\out\refined\bank-xiandai-hanyu.refined2.json',
    '古文史': r'D:\study_app\tools\seed-builder\out\refined\bank-zhongguo-gudai-wenxue.v012.json',
}
bybank = {
    '古汉': r'D:\study_app\tools\seed-builder\out\refined\bank-gudai-hanyu.v012.json',
    '现汉': r'D:\study_app\tools\seed-builder\out\refined\bank-xiandai-hanyu.refined2.json',
    '古文史': r'D:\study_app\tools\seed-builder\out\refined\bank-zhongguo-gudai-wenxue.v012.json',
}
done = 0
for name, f in files.items():
    qs = json.load(open(f, encoding='utf-8'))
    for q in qs:
        if q['id'] in FIX:
            ans, variants = FIX[q['id']]
            q['answer'] = ans
            q['answerVariants'] = variants
            done += 1
            print('修复', q['id'], '->', ans, '|', variants)
    json.dump(qs, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('共修复', done, '题')
