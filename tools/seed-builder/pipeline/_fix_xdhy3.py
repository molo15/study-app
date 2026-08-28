# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json'
KP = json.load(open(P, encoding='utf-8'))
EXT = {
    '群山在呼唤': '赋予“群山”人的动作“呼唤”，是拟人。比拟分拟人和拟物两类，把物当人来写叫拟人。',
    '飞流直下三千尺': '“三千尺”是扩大夸张，极力写瀑布之高。夸张分扩大、缩小、超前三类。',
    '谁是我们最可爱的人呢': '自问自答以引起注意，是设问。设问与反问不同，反问答案在问中。',
    '我失骄杨君失柳': '“杨柳”一词兼指两种意义（杨花柳絮与杨开慧、柳直荀），是语义双关。',
    '巧克力是____个语素': '“巧克力”是音译外来词，整体一个语素，属单纯词。',
    '咖啡是一个音译外来词': '“咖啡”整体是一个音译语素，不可再分，属单纯词。',
    '多美的景色啊': '感叹句末尾用叹号，表达强烈的感情。叹号还可用于祈使句末尾。',
}
n = 0
for k in KP['knowledge']:
    for q in k.get('basicQuestions', []):
        if len(q.get('explanation', '')) >= 20:
            continue
        for key, e in EXT.items():
            if key in q['stem']:
                q['explanation'] = e
                n += 1
                break
json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('修复短解析', n)
