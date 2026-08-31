# -*- coding: utf-8 -*-
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'out\v09gudaihanyu\bank-gudai-hanyu.v09.json'
d = json.load(open(p, encoding='utf-8'))

# 检查 B 素材残留题清洗后的解析
print('=== B 素材残留题清洗后 ===')
for q in d:
    e = q.get('explanation') or ''
    if '素材' in e:
        print(q.get('id'), q.get('type'), '|', e[:90])
        if q.get('type') == 'short_answer':
            print('   answer:', (q.get('answer') or '')[:50])
        print()

# 抽样检查普通题清洗后解析（应保留实质内容）
print('=== 普通题清洗后抽样（古代汉语前10条含解析的）===')
cnt = 0
for q in d:
    e = (q.get('explanation') or '').strip()
    if e and cnt < 10:
        print(q.get('id'), '|', e[:80])
        cnt += 1
