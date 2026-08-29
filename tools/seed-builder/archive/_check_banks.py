# -*- coding: utf-8 -*-
import io, sys, os, json, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print('=== assets/banks 现有 zip ===')
for f in sorted(os.listdir(r'D:\study_app\app\assets\banks')):
    p = os.path.join(r'D:\study_app\app\assets\banks', f)
    if f.endswith('.zip'):
        z = zipfile.ZipFile(p)
        try:
            mj = json.loads(z.read('manifest.json'))
            total = 0
            for qf in mj.get('questionFiles', []):
                qs = json.loads(z.read(qf))
                total += len(qs)
            print('  {}: 版本{} 题{} format{}'.format(f, mj.get('version'), total, mj.get('formatVersion')))
        except Exception as e:
            print('  {}: 读取失败 {}'.format(f, e))
        z.close()

print()
print('=== home_page 内置题库引用 ===')
s = open(r'D:\study_app\app\lib\ui\home_page.dart', encoding='utf-8').read()
for l in s.split('\n'):
    if 'v0.' in l and 'zip' in l:
        print('  ', l.strip()[:100])
