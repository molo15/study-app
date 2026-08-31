# -*- coding: utf-8 -*-
"""APK 内 q_000088 完整题目。"""
import io, sys, json, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
APK = r'D:\study_app\app\build\app\outputs\flutter-apk\app-release.apk'
z = zipfile.ZipFile(APK)
zz = zipfile.ZipFile(io.BytesIO(z.read('assets/flutter_assets/assets/banks/bank-zhongguo-xiandai-wenxue-v0.14.0.zip')))
qs = []
for nn in zz.namelist():
    if nn.startswith('questions/') and nn.endswith('.json'):
        qs.extend(json.loads(zz.read(nn)))
for q in qs:
    if q['id'].endswith('q_000088'):
        print(q['id'], '| type:', q.get('type'))
        for o in q.get('options', []):
            m = ' <==正确' if o['text'] == q.get('answer') else ''
            print('   ', o['key'], o.get('text','')[:30], m)
        print('answer:', q.get('answer'))
        print('expl:', q.get('explanation'))
        break
# 看 v09 源
print()
print('=== v09 源 ===')
v = json.load(open(r'D:\study_app\tools\seed-builder\out\v09xiandaiwenxue\bank-zhongguo-xiandai-wenxue.v09.json', encoding='utf-8'))
for q in v:
    if q['id'].endswith('q_000088'):
        for o in q.get('options', []):
            print('   ', o.get('key'), o.get('text','')[:30])
        print('answer:', q.get('answer'))
        print('expl:', q.get('explanation'))
        break
