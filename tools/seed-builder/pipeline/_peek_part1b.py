# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
D = json.load(open(r'D:\study_app\tools\seed-builder\out\reports\docx题库_第一部分.json', encoding='utf-8'))
for q in D['袁行霈中国文学史'].get('名词解释', []):
    expl = ' '.join(str(q['expl'])[:110].split())
    print('◆', q['stem'][:40])
    print('  ', expl)
print()
print('现代文学三十年 名词解释数:', len(D['现代文学三十年'].get('名词解释', [])))
print('当代文学史 名词解释数:', len(D['洪子诚当代文学史'].get('名词解释', [])))
