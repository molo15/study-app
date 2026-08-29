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
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode('utf-8'))

tr = api('/api/filetree/listDocsByPath', {'notebook': NB, 'path': '/'})
files = tr['data']['files'] or []
print('第一条记录的 keys:', list(files[0].keys()) if files else 'EMPTY')
print()
print(json.dumps(files[0], ensure_ascii=False, indent=1)[:800])
