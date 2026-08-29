# -*- coding: utf-8 -*-
import io, sys, os, zipfile, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
for apk in [
    r'D:\study_app\app\build\app\outputs\flutter-apk\考研刷题-v1.1.1-UI修复.apk',
    r'D:\study_app\app\build\app\outputs\flutter-apk\考研刷题-v1.1.2-iOS转场+精简目标.apk',
    r'D:\study_app\app\build\app\outputs\flutter-apk\考研刷题-v1.1.3-覆盖转场+v012题库.apk',
]:
    if not os.path.exists(apk):
        print('MISS', os.path.basename(apk)); continue
    z = zipfile.ZipFile(apk)
    banks = sorted(n for n in z.namelist() if '/banks/' in n and n.endswith('.zip'))
    print('=' * 10, os.path.basename(apk))
    for b in banks:
        try:
            mj = json.loads(zipfile.ZipFile(io.BytesIO(z.read(b))).read('manifest.json'))
            print('   ', os.path.basename(b), 'v' + str(mj.get('version')), 'idSchema=' + str(mj.get('idSchema')))
        except Exception as e:
            print('   ', os.path.basename(b), 'ERR', e)
    z.close()
