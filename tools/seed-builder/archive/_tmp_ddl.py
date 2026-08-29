# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
s = open(r'D:\study_app\app\lib\models\models.dart', encoding='utf-8').read()
qi = s.find('class Question {')
seg = s[qi:qi+4200]
j = seg.find('Map<String, dynamic> toMap()')
if j < 0:
    j = seg.find('toMap()')
print(seg[j:j+700])
