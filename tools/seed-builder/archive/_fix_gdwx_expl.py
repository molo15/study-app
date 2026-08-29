# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json', encoding='utf-8'))
m = {
    '元杂剧的结构体制一般为____一楔子': '元杂剧结构体制一般为四折一楔子，由曲词、宾白、科范三部分组成。',
    '被称为“南戏之祖”的元代作品是高明的《____》': '高明《琵琶记》被称为“南戏之祖”，写蔡伯喈与赵五娘的故事。',
    '《聊斋志异》的作者蒲松龄号（　）': '蒲松龄字留仙，号柳泉居士，著文言短篇小说集大成之作《聊斋志异》。',
    '常州词派由张惠言开山，至____发扬光大，蔚为宗派': '常州词派由张惠言开山，至周济发扬光大，是清代影响最大的词派。',
    '桐城派中首创散文“义法”说的是（　）': '方苞首创“义法”说，是桐城派奠基人；姚鼐主张义理考据辞章统一。',
    '清代词人纳兰性德的词集是《____》': '纳兰性德词集名《饮水词》，词风凄婉深挚，王国维称其“北宋以来，一人而已”。',
}
n = 0
for k in d['knowledge']:
    for q in k.get('basicQuestions', []):
        for stem, new in m.items():
            if stem in q.get('stem', ''):
                q['explanation'] = new
                n += 1
json.dump(d, open(r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('补齐:', n, '处')
