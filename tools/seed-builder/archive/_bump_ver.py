# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\study_app\app\pubspec.yaml'
s = open(p, encoding='utf-8').read()
old = 'version: 1.1.2+4'
new = 'version: 1.1.3+5'
if old not in s:
    print('ERROR: version line not found')
    sys.exit(1)
s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(s)
print('OK: pubspec version -> 1.1.3+5')
