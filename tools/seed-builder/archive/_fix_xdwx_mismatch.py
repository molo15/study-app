# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国现代文学史.knowledge.json', encoding='utf-8'))
fixes = [
    ('围城》文化反省层对传统文化批判的独特之处', '通过“最新式”的文人（留学生或“高级”知识分子）形象的塑造去实现', '通过“最新式”的文人群像的塑造去实现'),
    ('冰心体"散文内容上宣扬的哲学', '爱的哲学（自然爱、母爱、儿童爱）', '爱的哲学'),
    ('1930年代文艺运动的主潮是', '无产阶级文艺思潮及其创作（以左联为代表）', '无产阶级文艺思潮及其创作'),
    ('1930年代文艺运动的补充主潮', '自由主义文艺思潮及创作（新月派、京派）', '自由主义文艺思潮及创作'),
    ('《日出》采用的结构方法', '“横断面的描写”法（人像展览式）', '“横断面的描写”法'),
    ('山药蛋派的代表人物简记', '西李马胡孙（西戎、李束为、马烽、胡正、孙谦）', '西李马胡孙'),
    ('再到"国民性', '多解性（说不尽的阿Q）', '多解性'),
    ('其杂文的基本艺术手段', '勾画“个”与“类”统一的类型形象（“社会相”“共名”）', '勾画“个”与“类”统一的类型形象'),
]
n = 0
for k in d['knowledge']:
    for q in k.get('basicQuestions', []):
        for stemf, old, new in fixes:
            if stemf in q.get('stem', '') and q.get('answer') == old:
                q['answer'] = new
                n += 1
json.dump(d, open(r'D:\study_app\tools\seed-builder\out\knowledge\中国现代文学史.knowledge.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('修复:', n, '处')
