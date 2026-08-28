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

doc_id = '20260722163653-x5l3egw'  # 现代汉语的特点
r = api('/api/filetree/getDoc', {'id': doc_id})
print('code=', r.get('code'))
d = r.get('data') or {}
print('data keys:', list(d.keys())[:15])
blocks = d.get('blocks') or []
print('blocks 数量:', len(blocks))
print('rootID:', d.get('rootID'))
for b in blocks[:5]:
    print('  块:', b.get('id'), b.get('type'), (b.get('content') or '')[:30])
last = blocks[-1] if blocks else None
print('最后块:', last.get('id') if last else None, last.get('type') if last else None, (last.get('content') or '')[:30])
