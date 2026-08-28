# -*- coding: utf-8 -*-
import io, sys, os, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
apk = r'D:\study_app\app\build\app\outputs\flutter-apk\考研刷题-v1.1.3-覆盖转场+v012题库.apk'
z = zipfile.ZipFile(apk)
names = z.namelist()
banks = [n for n in names if 'banks' in n and n.endswith('.zip')]
print('banks 相关条目:')
for b in banks:
    print('   ', b)
print()
print('assets 顶层示例:')
for n in names:
    if n.startswith('assets/') and '/' in n[len('assets/'):]:
        pass
top = sorted(set(n.split('/')[0] + '/' + (n.split('/')[1] if len(n.split('/'))>1 else '') for n in names if n.endswith('.zip')))
for t in top[:20]:
    print('   ', t)
z.close()
