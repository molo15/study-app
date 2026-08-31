# -*- coding: utf-8 -*-
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'out\v09gudaiwenxue\bank-zhongguo-gudai-wenxue.v09.json'
d = json.load(open(p, encoding='utf-8'))
n = 0
for q in d:
    if q.get('type') == 'short_answer':
        e = (q.get('explanation') or '').strip()
        e_norm = re.sub(r'\s+', '', e)
        if re.match(r'^(解析[:：]|须答出|本题考查|本题为|本题是|答题要点)', e) or len(e_norm) < 20:
            print(q.get('id'), '|', e[:60])
            n += 1
            if n >= 15:
                break
print('命中短答:', n)
