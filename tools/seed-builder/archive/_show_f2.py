# -*- coding: utf-8 -*-
import io, sys, json, zipfile, glob, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

banks = glob.glob(r'D:\study_app\app\assets\banks\bank-*.zip')
targets = {
    'bank-xiandai-hanyu': ['z_000109', 'q_000009', 'q_000004'],
    'bank-zhongguo-dangdai-wenxue': ['t_000073'],
    'bank-zhongguo-gudai-wenxue': ['q_000080', 'q_000001', 'q_000010'],
    'bank-zhongguo-xiandai-wenxue': ['t_000336', 't_000373', 't_000124', 't_000207', 't_000313', 't_000217', 't_000178'],
}
for b in banks:
    bank = os.path.basename(b).replace('-v0.14.0.zip', '')
    if bank not in targets:
        continue
    z = zipfile.ZipFile(b)
    for n in z.namelist():
        if not n.startswith('questions/'):
            continue
        for q in json.loads(z.read(n)):
            qid = q.get('id', '')
            if any(qid.endswith(t) for t in targets[bank]):
                print('='*90)
                print(bank, qid)
                print('题干:', (q.get('stem') or '')[:80])
                for o in q.get('options', []):
                    mark = ' <== answer' if o.get('text') == q.get('answer') else ''
                    print('   ', o.get('key'), o.get('text'), mark)
                print('answer:', q.get('answer'))
                print('解析:', (q.get('explanation') or '')[:500])
