# -*- coding: utf-8 -*-
"""拉取指定笔记本全部叶子文档内容 → 本地 md（多选出题素材）
用法: python _pull_notebook.py <box_id> <输出名>
"""
import io, sys, json, urllib.request, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
src = open(r'D:\study_app\tools\seed-builder\pipeline\_siyuan_docs.py', encoding='utf-8').read()
BASE = re.search(r"BASE = '([^']+)'", src).group(1)
TOKEN = re.search(r"TOKEN = '([^']+)'", src).group(1)

def api(path, data):
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode('utf-8'),
                                 headers={'Authorization': 'Token ' + TOKEN, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode('utf-8'))

box = sys.argv[1]
outname = sys.argv[2]

# 所有文档
r = api('/api/query/sql', {'stmt': f"SELECT b.id, b.hpath FROM blocks b WHERE b.box='{box}' AND b.type='d' ORDER BY b.hpath"})
docs = r.get('data') or []
print(f'共 {len(docs)} 个文档')

out = []
for d in docs:
    doc_id = d['id']
    hpath = d['hpath']
    # 跳过"真题汇总"类（非知识点正文）与课后习题
    if '真题' in hpath or '习题答案' in hpath:
        continue
    out.append(f'\n\n## {hpath}\n')
    r2 = api('/api/query/sql', {'stmt': f"SELECT b.type, b.content, b.sort FROM blocks b WHERE b.root_id='{doc_id}' AND b.type IN ('h','p','l','ol','li') ORDER BY b.sort LIMIT 500"})
    for row in (r2.get('data') or []):
        c = (row.get('content') or '').strip()
        if not c:
            continue
        t = row['type']
        prefix = {'h': '# ', 'p': '', 'l': '- ', 'ol': '1. ', 'li': '- '}.get(t, '')
        out.append(prefix + c)

os.makedirs(r'D:\study_app\tools\mc_assets', exist_ok=True)
path = rf'D:\study_app\tools\mc_assets\{outname}.md'
with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('saved:', path, os.path.getsize(path), 'bytes')
