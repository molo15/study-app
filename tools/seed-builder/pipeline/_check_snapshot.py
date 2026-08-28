# -*- coding: utf-8 -*-
import io, sys, os, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
apk = r'D:\study_app\app\build\app\outputs\flutter-apk\考研刷题-v1.1.3-覆盖转场+v012题库.apk'
z = zipfile.ZipFile(apk)
# 找到 Dart 快照 / kernel
targets = [n for n in z.namelist() if n.endswith(('kernel_blob.bin', 'isolate_snapshot_data', 'vm_snapshot_data', 'app.so'))]
print('Dart 快照文件:', targets)
keys = ['今日任务', '待复习', '新题', '错题', '考研·古代汉语', '考研刷题', '题库包 v', '共 ']
for t in targets:
    data = z.read(t)
    print('=' * 10, t, len(data), 'bytes')
    for k in keys:
        kb = k.encode('utf-8')
        print('   ', k, '->', ('FOUND' if kb in data else 'not found'))
z.close()
