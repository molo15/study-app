# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
s = open(r'D:\study_app\app\lib\ui\home_page.dart', encoding='utf-8').read()
seen = set()
for m in re.finditer(r"'([^']*[\u4e00-\u9fff][^']*)'", s):
    t = m.group(1).strip()
    if t and t not in seen:
        seen.add(t)
        print(t)
print('---总条数:', len(seen))
