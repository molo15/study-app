# -*- coding: utf-8 -*-
import io
p = r'D:\study_app\.gitignore'
s = open(p, encoding='utf-8').read()
add = '''
# 一次性临时脚本
tools/_tmp_*.py
'''
if 'tools/_tmp_*.py' not in s:
    open(p, 'w', encoding='utf-8').write(s.rstrip() + '\n' + add)
    print('updated')
else:
    print('present')
