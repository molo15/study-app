# -*- coding: utf-8 -*-
import io, sys, os, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def scan(apk, label):
    z = zipfile.ZipFile(apk)
    so = 'lib/arm64-v8a/libapp.so'
    data = z.read(so)
    print('=' * 12, label, os.path.basename(apk))
    keys = ['v0.11.0', 'v0.12.0', 'id_schema', 'idSchema', 'q-b',
            'assets/banks', 'bank-gudai-hanyu', '_discoverBundledBanks', 'rebuild']
    for k in keys:
        found = False
        for enc in ('utf-8', 'utf-16-le', 'utf-16-be', 'ascii'):
            try:
                if k.encode(enc) in data:
                    found = True
                    break
            except Exception:
                pass
        print('   {:24s} -> {}'.format(k, 'Y' if found else '.'))
    z.close()

scan(r'D:\study_app\app\build\app\outputs\flutter-apk\考研刷题-v1.1.2-iOS转场+精简目标.apk', 'A')
scan(r'D:\study_app\app\build\app\outputs\flutter-apk\考研刷题-v1.1.3-覆盖转场+v012题库.apk', 'B')
