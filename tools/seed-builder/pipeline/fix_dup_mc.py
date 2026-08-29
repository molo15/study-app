# -*- coding: utf-8 -*-
"""修复同科内重复题：删除指定 id 并重打包 v0.14.0"""
import io, sys, zipfile, json, os, tempfile, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# (zip 名, 待删 id, 原因)
TARGETS = [
    ('bank-xiandai-hanyu-v0.14.0.zip', 'bank-xiandai-hanyu:mc_000044', '标号多选与 mc_000043 重复'),
    ('bank-gudai-hanyu-v0.14.0.zip', 'bank-gudai-hanyu:c_000079', '反切名词解释与 c_000018 重复'),
    ('bank-zhongguo-xiandai-wenxue-v0.14.0.zip', 'bank-zhongguo-xiandai-wenxue:t_000356', '七月诗派单选与基础题 kb_00316 重复'),
]
BANKS = r'D:\study_app\app\assets\banks'

for zname, did, reason in TARGETS:
    zp = os.path.join(BANKS, zname)
    tmp = os.path.join(BANKS, zname + '.tmp')
    removed = 0
    with zipfile.ZipFile(zp) as zin:
        names = zin.namelist()
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
            for n in names:
                data = zin.read(n)
                if n.startswith('questions/') and n.endswith('.json'):
                    qs = json.loads(data)
                    nq = [q for q in qs if q['id'] != did]
                    removed += len(qs) - len(nq)
                    if len(qs) != len(nq):
                        data = json.dumps(nq, ensure_ascii=False, indent=1).encode('utf-8')
                elif n == 'manifest.json':
                    m = json.loads(data)
                    m['questionCount'] = m.get('questionCount', 0) - 1
                    data = json.dumps(m, ensure_ascii=False, indent=2).encode('utf-8')
                zout.writestr(n, data)
    os.replace(tmp, zp)
    print(f'{zname}: 删除 {removed} 题 ({reason})')

print('done')
