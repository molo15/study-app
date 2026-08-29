# -*- coding: utf-8 -*-
import io, sys, os, json, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

banks = ['bank-gudai-hanyu', 'bank-xiandai-hanyu', 'bank-zhongguo-xiandai-wenxue']

for b in banks:
    print('=' * 14, b)
    for ver in ['0.11.0', '0.12.0']:
        p = os.path.join(r'D:\study_app\app\assets\banks', '{}-v{}.zip'.format(b, ver))
        z = zipfile.ZipFile(p)
        mj = json.loads(z.read('manifest.json'))
        # 取第一个题文件的 3 个题 id
        qf = mj['questionFiles'][0]
        qs = json.loads(z.read(qf))
        ids = [q['id'] for q in qs[:3]]
        sample_know = None
        if 'knowledge' in mj and mj['knowledge']:
            sample_know = mj['knowledge'][0]['id']
        print('  v{}: 题 id 示例 {}'.format(ver, ids))
        print('       knowledgeId 示例 {}'.format(sample_know))
        z.close()
