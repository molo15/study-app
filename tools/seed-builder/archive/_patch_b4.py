# -*- coding: utf-8 -*-
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'D:\study_app\tools\seed-builder\pipeline\pack_v012.py'
s = open(p, encoding='utf-8').read()

old = '''        manifest = {
            "formatVersion": 4, "bankId": bank, "name": name, "version": VERSION,
            "generatedAt": GENERATED_AT, "chapters": chapter_groups,
            "questionFiles": [], "mockPapers": mock,
            "knowledge": knowledge, "overviews": overviews,
        }'''
new = '''        manifest = {
            "formatVersion": 4, "bankId": bank, "name": name, "version": VERSION,
            "idSchema": "q-b",  # v1.1.3: 题 id 前缀体系标识（q_/b_），供 App 端不兼容升级判断
            "generatedAt": GENERATED_AT, "chapters": chapter_groups,
            "questionFiles": [], "mockPapers": mock,
            "knowledge": knowledge, "overviews": overviews,
        }'''
if old not in s:
    print('ERROR: manifest block not found')
    sys.exit(1)
s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(s)
print('OK: pack_v012.py manifest added idSchema')

# 检查 refined 输入文件是否存在
BASE = r'D:\study_app\tools\seed-builder'
print()
for line in open(p, encoding='utf-8').read().split('\n'):
    if 'out/refined/' in line:
        rel = line.split('(')[-1].rstrip('),').strip('"')
        full = os.path.join(BASE, rel)
        print('  {}: {}'.format('OK ' if os.path.exists(full) else 'MISS', rel))
