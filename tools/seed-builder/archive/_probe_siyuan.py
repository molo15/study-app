# -*- coding: utf-8 -*-
"""拉取指定文档下文本块内容"""
import io, sys, json, urllib.request, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
src = open(r'D:\study_app\tools\seed-builder\pipeline\_siyuan_docs.py', encoding='utf-8').read()
BASE = re.search(r"BASE = '([^']+)'", src).group(1)
TOKEN = re.search(r"TOKEN = '([^']+)'", src).group(1)

def api(path, data):
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode('utf-8'),
                                 headers={'Authorization': 'Token ' + TOKEN, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))

doc = sys.argv[1] if len(sys.argv) > 1 else '20260722172427-nj587dw'  # 词汇
r = api('/api/query/sql', {'stmt': f"SELECT b.type, b.content FROM blocks b WHERE b.root_id='{doc}' AND b.type IN ('h','p','l','ol','li') ORDER BY b.sort LIMIT 200"})
n = 0
for row in (r.get('data') or []):
    c = (row.get('content') or '').strip()
    if not c:
        continue
    n += 1
    print(f"[{row.get('type')}] {c[:120]}")
    if n >= 150:
        break
