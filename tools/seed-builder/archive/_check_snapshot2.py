# -*- coding: utf-8 -*-
import io, sys, os, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check(apk):
    z = zipfile.ZipFile(apk)
    so = [n for n in z.namelist() if n == 'lib/arm64-v8a/libapp.so'][0]
    data = z.read(so)
    print('=' * 12, os.path.basename(apk), len(data))
    keys = ['今日任务', '待复习', '新题', '错题', '考研·古代汉语', '考研刷题', '题库包', '重点题目', '章节知识概览', '整本随机刷', '距考试还有']
    for k in keys:
        le = k.encode('utf-16-le')
        be = k.encode('utf-16-be')
        print('   {:12s} -> LE:{} BE:{}'.format(k, 'Y' if le in data else '.', 'Y' if be in data else '.'))
    z.close()

check(r'D:\study_app\app\build\app\outputs\flutter-apk\考研刷题-v1.1.2-iOS转场+精简目标.apk')
check(r'D:\study_app\app\build\app\outputs\flutter-apk\考研刷题-v1.1.3-覆盖转场+v012题库.apk')
