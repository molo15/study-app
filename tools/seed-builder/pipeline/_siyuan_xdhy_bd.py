# -*- coding: utf-8 -*-
"""拉取现代汉语 标点符号 素材"""
import io, sys, json, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TOKEN = 'jfolmogj8xr5h1r6'
BASE = 'http://127.0.0.1:6806'

def api(method, data):
    req = urllib.request.Request(
        BASE + method,
        data=json.dumps(data).encode('utf-8'),
        headers={'Authorization': 'Token ' + TOKEN, 'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))

r = api('/api/export/exportMdContent', {'id': '20260722173140-d76l4xn'})
d = r.get('data')
md = d.get('content') if isinstance(d, dict) else None
print('### 现代汉语-标点符号')
if md:
    body = md
    if body.startswith('---'):
        parts = body.split('---', 2)
        if len(parts) >= 3:
            body = parts[2]
    print(body[:6000])
