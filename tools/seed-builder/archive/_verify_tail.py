# -*- coding: utf-8 -*-
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for f in [r'D:\study_app\tools\seed-builder\out\knowledge\古代汉语.knowledge.json',
          r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json']:
    k = json.load(open(f, encoding='utf-8'))
    print('===', os.path.basename(f))
    # 抽3条清洗后的解析
    shown = 0
    for x in k['knowledge']:
        for bq in x.get('basicQuestions', []):
            e = (bq.get('explanation') or '').strip()
            if e and shown < 3:
                print('  [', x.get('name'), ']', (bq.get('stem') or '')[:20])
                print('    expl:', e[:100])
                shown += 1
    # 检查清洗后过短或空
    short = sum(1 for x in k['knowledge'] for bq in x.get('basicQuestions', [])
                if len(re.sub(r'\s+', '', bq.get('explanation') or '')) < 15)
    empty = sum(1 for x in k['knowledge'] for bq in x.get('basicQuestions', [])
                if not (bq.get('explanation') or '').strip())
    print('  清洗后过短(<15):', short, ' 空:', empty)
