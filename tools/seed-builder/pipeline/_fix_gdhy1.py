# -*- coding: utf-8 -*-
"""修复古代汉语：choice选项去括号 + 短解析加长"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'D:\study_app\tools\seed-builder\out\knowledge\古代汉语.knowledge.json'
KP = json.load(open(P, encoding='utf-8'))

# 1. 修复 choice 选项（去掉括号说明，保证选项简洁无括号）
FIX_OPTS = {
    '“句读之不知”中“句读”指的是（　)': (['断句', '标点符号', '朗读节奏', '词义解释'], '断句'),
    '古汉语中“衣”指上衣，“裳”指（　)': (['下衣', '帽子', '鞋子', '外衣'], '下衣'),
    '下列属于词义扩大的是（　)': (['河', '汤', '涕', '走'], '河'),
    '“尔雅”中“尔”意为（　)': (['近', '你', '远', '多'], '近'),
}
FIX_OPTS_KEYS = {
    '句读之不知': (['断句', '标点符号', '朗读节奏', '词义解释'], '断句'),
    '古汉语中“衣”指上衣': (['下衣', '帽子', '鞋子', '外衣'], '下衣'),
    '下列属于词义扩大': (['河', '汤', '涕', '走'], '河'),
    '尔雅”中“尔”意为': (['近', '你', '远', '多'], '近'),
}
for k in KP['knowledge']:
    for q in k.get('basicQuestions', []):
        for key, (opts, ans) in FIX_OPTS_KEYS.items():
            if key in q['stem'] and q['type'] == 'choice':
                q['options'] = opts
                q['answer'] = ans

# 2. 加长短解析
EXT = {
    '写在书前的文字称为____。': '序（叙）写在书前，跋写在书后，序跋是说明著作缘起、旨趣的文体。',
    '“人、口、手”等描摹人体器官形状，都是____字。': '象形字用描摹事物形状的方式造字，如“人、口、手、日、月”。',
    '“嘻，善哉！技盖至此乎”中“嘻”是____词。': '“嘻”独立成句、表示赞叹，是叹词。叹词不与其他词组合。',
    '三十六字母中“影”母属于____音。': '“影、晓、匣、喻”是喉音，三十六字母按发音部位分五音、七音。',
}
for k in KP['knowledge']:
    for q in k.get('basicQuestions', []):
        if q['stem'] in EXT:
            q['explanation'] = EXT[q['stem']]

json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('修复完成')
