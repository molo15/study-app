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

# 1) 根目录
tr = api('/api/filetree/listDocsByPath', {'notebook': NB, 'path': '/'})
print('=== 现代汉语根目录 ===')
for d in tr['data']['files'] or []:
    print('  -', d['name'], '[' + d['id'] + ']')

# 2) 「现代汉语的特点」末尾追加块验证
doc_id = '20260722163653-x5l3egw'
r = api('/api/filetree/getDoc', {'id': doc_id})
content = r.get('data', {}).get('content', '')
print()
print('「现代汉语的特点」block-ref 次数:', content.count('block-ref'))
print('含"相关链接":', '相关链接' in content)
idx = content.find('相关链接')
if idx >= 0:
    print('=== 追加块 DOM 片段 ===')
    print(content[idx: idx + 700])
