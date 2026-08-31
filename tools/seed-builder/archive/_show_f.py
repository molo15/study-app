# -*- coding: utf-8 -*-
import io, sys, json, zipfile, glob, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

banks = glob.glob(r'D:\study_app\app\assets\banks\bank-*.zip')
targets = {
    'bank-xiandai-hanyu': ['z_000109', 'q_000009', 'q_000004'],
    'bank-zhongguo-dangdai-wenxue': ['t_000073'],
    'bank-zhongguo-gudai-wenxue': ['q_000080', 'q_000001', 'q_000010'],
    'bank-zhongguo-xiandai-wenxue': ['kb_00387'],
}
for b in banks:
    bank = os.path.basename(b).replace('-v0.14.0.zip', '')
    if bank not in targets: continue
    z = zipfile.ZipFile(b)
    for n in z.namelist():
        if not n.startswith('questions/'): continue
        for q in json.loads(z.read(n)):
            qid = q.get('id', '')
            if any(qid.endswith(t) for t in targets[bank]):
                print('='*80)
                print(bank, qid)
                print('题型:', q.get('type'), '| 章节:', q.get('chapter'), '| 知识点:', q.get('knowledgeId'))
                print('题干:', q.get('stem'))
                print('选项:')
                for o in q.get('options', []):
                    print('   ', o.get('key'), o.get('text'))
                print('answer:', q.get('answer'))
                print('解析:', q.get('explanation'))
