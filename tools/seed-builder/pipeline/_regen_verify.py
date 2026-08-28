# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
src = open(r'D:\study_app\tools\seed-builder\pipeline\verify_v011.py', encoding='utf-8').read()
dst = src.replace('v0.11.0', 'v0.13.0')
open(r'D:\study_app\tools\seed-builder\pipeline\verify_v013.py', 'w', encoding='utf-8').write(dst)
print('verify_v013.py 重新生成，长度', len(dst))
