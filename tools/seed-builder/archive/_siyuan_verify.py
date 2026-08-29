# -*- coding: utf-8 -*-
import io, sys, json, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TOKEN = 'jfolmogj8xr5h1r6'
BASE = 'http://127.0.0.1:6806'
NB = '20260721175205-gpyhylx'

def api(method, data):
    req = urllib.request.Request(
        BASE + method,
        data=json.dumps(data).encode('utf-8'),
        headers={'Authorization': 'Token ' + TOKEN, 'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode('utf-8'))

# 1) 根目录确认 MOC 文档
tr = api('/api/filetree/listDocsByPath', {'notebook': NB, 'path': '/'})
print('=== 现代汉语根目录 ===')
for d in tr['data']['files'] or []:
    print('  -', d['name'], '[' + d['id'] + ']')

# 2) 拉 MOC 内容（前 60 行）
moc_id = '20260828094939-f08k7sq'
r = api('/api/export/exportMdContent', {'id': moc_id})
d = r.get('data')
md = d.get('md') if isinstance(d, dict) else d
print()
print('=== MOC 内容（前 40 行）===')
if md:
    for line in md.split('\n')[:40]:
        print(line)
