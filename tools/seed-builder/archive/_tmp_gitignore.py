# -*- coding: utf-8 -*-
import io
p = r'D:\study_app\.gitignore'
s = open(p, encoding='utf-8').read()
add = '''
# 开发日志与临时产物（不入库）
app/analyze_*.txt
app/test_*.txt
app/build_apk*.txt
app/test_run.txt
_shot*.png
tmp_*.png
/backup/
'''
if 'app/analyze_*.txt' not in s:
    open(p, 'w', encoding='utf-8').write(s.rstrip() + '\n' + add)
    print('gitignore updated')
else:
    print('already present')
