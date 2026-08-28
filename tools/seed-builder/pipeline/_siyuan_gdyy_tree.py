# -*- coding: utf-8 -*-
import io, sys, json, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TOKEN = 'jfolmogj8xr5h1r6'
BASE = 'http://127.0.0.1:6806'
NB = '20260722162828-fvyl4ks'  # 古代汉语

def api(method, data):
    req = urllib.request.Request(
        BASE + method,
        data=json.dumps(data).encode('utf-8'),
        headers={'Authorization': 'Token ' + TOKEN, 'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))

# 1) 文档树
tr = api('/api/filetree/getDocByPath', {'notebook': NB, 'path': '/'})
def walk(node, depth=0):
    print('  ' * depth + '[' + (node.get('type') or '') + '] ' + (node.get('name') or node.get('id') or ''))
    for c in (node.get('children') or []):
        walk(c, depth + 1)
walk(tr.get('data') or {})
