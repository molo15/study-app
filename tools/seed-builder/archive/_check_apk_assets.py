# -*- coding: utf-8 -*-
import io, sys, os, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

apks = [
    r'D:\study_app\app\build\app\outputs\flutter-apk\考研刷题-v1.1.1-UI修复.apk',
    r'D:\study_app\app\build\app\outputs\flutter-apk\考研刷题-v1.1.2-iOS转场+精简目标.apk',
    r'D:\study_app\app\build\app\outputs\flutter-apk\考研刷题-v1.1.3-覆盖转场+v012题库.apk',
]
for apk in apks:
    if not os.path.exists(apk):
        print('MISS:', apk)
        continue
    z = zipfile.ZipFile(apk)
    banks = sorted(n for n in z.namelist() if n.startswith('assets/assets/banks/') and n.endswith('.zip'))
    print('=' * 10, os.path.basename(apk))
    for b in banks:
        print('   ', os.path.basename(b))
    # 读取 manifest 版本
    for b in banks:
        try:
            mj = zipfile.ZipFile(io.BytesIO(z.read(b))).read('manifest.json')
            import json
            v = json.loads(mj).get('version')
            print('      ->', os.path.basename(b), 'manifest版本', v)
        except Exception as e:
            pass
    z.close()
