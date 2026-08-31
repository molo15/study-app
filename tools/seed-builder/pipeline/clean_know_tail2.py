# -*- coding: utf-8 -*-
"""清洗 knowledge.json basicQuestions 解析中的「本题属于…即可应对同类题目」模板尾巴。"""
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

FILES = [
    r'out\knowledge\古代汉语.knowledge.json',
    r'out\knowledge\中国当代文学史.knowledge.json',
    r'out\knowledge\中国现代文学史.knowledge.json',
    r'out\knowledge\中国古代文学史.knowledge.json',
    r'out\knowledge\现代汉语.knowledge.json',
]
# 匹配整段模板尾巴
pat = re.compile(r'[。；;]?本题属于.{0,40}即可应对同类题目[。]?\s*$')
pat2 = re.compile(r'[。；;]?本题属于.{0,40}常考基础点[，,。]?掌握其概念与例证即可应对同类题目[。]?\s*$')
total = 0
for f in FILES:
    k = json.load(open(f, encoding='utf-8'))
    n = 0
    for x in k['knowledge']:
        for bq in x.get('basicQuestions', []):
            e = bq.get('explanation') or ''
            new = pat2.sub('', e)
            new = pat.sub('', new)
            new = re.sub(r'[，,。；;、：:\s]+$', '', new).strip()
            if new != e:
                bq['explanation'] = new
                n += 1
    json.dump(k, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    total += n
    print(f'{f}: 清洗 {n}')
print('合计:', total)
