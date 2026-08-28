# -*- coding: utf-8 -*-
import io, sys, json, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

z = zipfile.ZipFile(r'D:\study_app\app\assets\banks\bank-gudai-hanyu-v0.11.0.zip')
m = json.loads(z.read('manifest.json').decode('utf-8'))
ks = [k for k in m['knowledge'] if k['chapter'] == '修辞']
print('修辞知识点数:', len(ks))
print()
for k in ks:
    print(f"  {k['id']} {k['name']}  [{k['questionCount']}题] hot={k['hot']}")

ov = [o for o in m['overviews'] if o['chapter'] == '修辞']
print()
print('修辞 overview:', json.dumps(ov, ensure_ascii=False, indent=1))

# 检查基础题文件里的修辞题目数
print()
for fn in m['questionFiles']:
    if '修辞' in fn:
        qs = json.loads(z.read(fn).decode('utf-8'))
        print(f'{fn}: {len(qs)} 题')
        # 检查是否都绑定了新知识点 id
        kids = {q.get('knowledgeId') for q in qs}
        print('  绑定知识点:', sorted(kids))
