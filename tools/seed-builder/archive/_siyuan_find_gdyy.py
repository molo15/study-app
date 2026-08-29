# -*- coding: utf-8 -*-
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
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode('utf-8'))

# 1) 列出所有笔记本，找古代汉语
nb = api('/api/notebook/lsNotebooks', {})
print('=== 笔记本 ===')
gdyy_nb = None
for b in nb.get('data') or []:
    print(' ', b.get('name'), b.get('id'))
    if '古代汉语' in (b.get('name') or ''):
        gdyy_nb = b['id']
print('古代汉语笔记本:', gdyy_nb)
