# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
d = json.load(open(r'D:\study_app\tools\seed-builder\out\reports\expl_audit\G_modern_detail.json', encoding='utf-8'))
print('total:', len(d))
for o in d:
    print(f"{o['kp_id']}|{o['bq_idx']}|{o['type']}|{(o['stem'] or '')[:24]}")
