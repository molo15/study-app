# -*- coding: utf-8 -*-
"""校验古代文学史新增名词转题的完整性与质量"""
import io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
KP = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json', encoding='utf-8'))

bad_choice = []
bad_blank = []
short_expl = []
total = 0
for k in KP['knowledge']:
    for q in k.get('basicQuestions', []):
        total += 1
        if q['type'] == 'choice':
            if len(q.get('options', [])) != 4:
                bad_choice.append(('选项数!=4', k['name'], q['stem']))
            if q['answer'] not in q.get('options', []):
                bad_choice.append(('答案不在选项', k['name'], q['stem'], q['answer'], q.get('options')))
            # 答案重复（多选答案出现在选项中多次）
            if q.get('options', []).count(q['answer']) > 1:
                bad_choice.append(('答案重复选项', k['name'], q['stem']))
        elif q['type'] == 'blank':
            if not q.get('answer') or len(q['answer']) < 1:
                bad_blank.append((k['name'], q['stem']))
        if len(q.get('explanation', '')) < 12:
            short_expl.append((k['name'], q['stem'], q.get('explanation')))

print('总题数:', total)
print('choice异常:', len(bad_choice))
for b in bad_choice:
    print('  ', b)
print('blank异常:', len(bad_blank))
for b in bad_blank:
    print('  ', b)
print('解析过短:', len(short_expl))
for b in short_expl:
    print('  ', b)

# 重复题干检查
seen = {}
dups = []
for k in KP['knowledge']:
    for q in k.get('basicQuestions', []):
        ns = re.sub(r'[（）()。，、；：""“”\'  ]', '', q['stem'])
        if ns in seen:
            dups.append((seen[ns], k['name'], q['stem']))
        else:
            seen[ns] = k['name']
print('重复题干:', len(dups))
for d in dups:
    print('  ', d)
