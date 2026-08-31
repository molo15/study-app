# -*- coding: utf-8 -*-
"""G 模板题修复 Part1：修正 answer 与 options（数据正确性）"""
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'out\knowledge\现代汉语.knowledge.json'
k = json.load(open(P, encoding='utf-8'))

# 修正映射： (kp_id, bq_idx) -> dict(action)
# action: fix_answer={old:new, options:[...]}, fix_options_only, fix_blank_answer={new}, fix_bad_option
FIXES = {
    # 客观题答案修正
    ('k_xdyy_yuyin_01', 2): dict(kind='choice', ans_new='社会性',
        options=['生理性', '物理性', '社会性', '自然性']),
    ('k_xdyy_yuyin_03', 2): dict(kind='choice', ans_new='音色',
        options=['音高', '音强', '音色', '音长']),
    ('k_xdyy_yuyin_04', 2): dict(kind='choice', ans_new='共鸣器形状',
        options=['发音体', '发音方法', '共鸣器形状', '音长']),
    ('k_xdyy_yuyin_16', 3): dict(kind='choice', ans_new='发音部位不同',
        options=['发音体不同', '发音部位不同', '共鸣器形状不同', '舌位前后不同']),
    ('k_xdyy_yuyin_16', 4): dict(kind='choice', ans_new='拉丁字母',
        options=['英文字母', '拉丁字母', '法文字母', '俄文字母']),
    ('k_xdyy_yuyin_16', 8): dict(kind='choice', ans_new='huār',
        options=['huā', 'huār', 'huāer', 'huā－er']),
    ('k_xdyy_yuyin_19', 2): dict(kind='choice', ans_new='阳平',
        options=['阴平', '阳平', '轻声', '去声']),
    ('k_xdyy_yufa_02', 5): dict(kind='choice', ans_new='区别词',
        options=['动词', '名词', '副词', '区别词']),
    ('k_xdyy_yufa_03', 2): dict(kind='choice', ans_new='名词',
        options=['代词', '动词', '形容词', '名词']),
    ('k_xdyy_yufa_03', 3): dict(kind='choice', ans_new='名词',
        options=['动词', '形容词', '名词', '副词']),
    ('k_xdyy_yufa_03', 4): dict(kind='choice', ans_new='动量词',
        options=['名量词', '动量词', '时量词', '形量词']),
    ('k_xdyy_yufa_03', 5): dict(kind='choice', ans_new='动词',
        options=['名词', '动词', '形容词', '副词']),
    # 借喻vs借代：答案文字写反，修正选项为正确表述，答案取正确项
    ('k_xdyy_xiuci_04', 6): dict(kind='choice', ans_new='借喻考虑的是事物之间的相似性，借代考虑的是事物之间的相关性',
        options=['借喻考虑的是事物之间的相似性，借代考虑的是事物之间的相关性',
                 '借喻考虑的是事物之间的相关性，借代考虑的是事物之间的相似性',
                 '借喻考虑的是事物之间的相同性，借代考虑的是事物之间的相异性',
                 '借喻考虑的是事物之间的相异性，借代考虑的是事物之间的相同性']),
    # 填空答案污染
    ('k_xdyy_cihui_10', 1): dict(kind='blank', ans_new='核心部分；新词的创造'),
    ('k_xdyy_yufa_05', 5): dict(kind='blank', ans_new='中心语'),
    ('k_xdyy_yufa_10', 3): dict(kind='blank', ans_new='分句'),
    # 选项污染修复（喻词不出现/成为 -> 借喻、暗喻），修复脏选项
    ('k_xdyy_xiuci_04', 4): dict(kind='choice', ans_new='借喻、暗喻',
        options=['明喻、暗喻', '暗喻、借喻', '借喻、暗喻', '明喻、借喻']),
}

applied = 0
for x in k['knowledge']:
    for i, bq in enumerate(x.get('basicQuestions', [])):
        key = (x['id'], i)
        if key not in FIXES:
            continue
        f = FIXES[key]
        if f['kind'] == 'choice':
            bq['answer'] = f['ans_new']
            bq['options'] = f['options']
        else:
            bq['answer'] = f['ans_new']
        applied += 1
        print(f"FIX {x['id']}[{i}] -> {bq['answer']}")

json.dump(k, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('applied:', applied)
