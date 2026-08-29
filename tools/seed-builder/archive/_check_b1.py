# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
KP = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json', encoding='utf-8'))
kws = ['六义', '风、雅、颂的划分', '赋”的含义', '最长的诗篇', '三家诗', '春秋三传', '编年体', '微言大义',
       '骚体', '十一篇', '政通', '子虚赋', '枚马', '七发', '悲愤诗', '体制特点', '都城赋', '目录学文献',
       '古诗十九首》由', '建安风骨', '建安七子', '赠白马王彪', '声无哀乐', '太康文学', '永明体', '徐庾体',
       '元嘉体', '骈俪文', '最早的诗文总集', '文心雕龙', '搜神记', '世说新语》由']
for ch in ['先秦文学', '秦汉文学', '魏晋南北朝文学']:
    print('###', ch)
    for k in KP['knowledge']:
        if k['chapter'] != ch:
            continue
        for q in k.get('basicQuestions', []):
            if any(x in q['stem'] for x in kws):
                print('  [' + k['name'] + '] ' + q['stem'][:42])
