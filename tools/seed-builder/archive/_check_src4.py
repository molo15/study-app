# -*- coding: utf-8 -*-
"""查看 4 条题源 options 顺序，重写解析结尾为文本结论（免疫洗牌）。"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
v09m = json.load(open(r'D:\study_app\tools\seed-builder\out\v09xiandaiwenxue\bank-zhongguo-xiandai-wenxue.v09.json', encoding='utf-8'))
for q in v09m:
    if q['id'] in ('bank-zhongguo-xiandai-wenxue:q_000088', 'bank-zhongguo-xiandai-wenxue:q_000163', 'bank-zhongguo-xiandai-wenxue:q_000142'):
        print('===', q['id'], '| type:', q.get('type'))
        print('  options:')
        for o in q.get('options', []):
            print('    ', o.get('key'), '|', o.get('text','')[:46])
        print('  answer:', q.get('answer'))
        print('  expl:', (q.get('explanation') or '')[-120:])
        print()
