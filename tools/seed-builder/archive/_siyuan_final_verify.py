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

# 1) 根目录（确认 MOC 命名）
tr = api('/api/filetree/listDocsByPath', {'notebook': NB, 'path': '/'})
print('=== 现代汉语根目录 ===')
for d in tr['data']['files'] or []:
    print('  -', d['name'], '[' + d['id'] + ']')

# 2) MOC 引用统计
moc_id = '20260828094939-f08k7sq'
kr = api('/api/block/getBlockKramdown', {'id': moc_id})
md = kr.get('data', {}).get('kramdown', '')
import re
refs = re.findall(r'\(\((\d{14}-[a-z0-9]{7})', md)
print()
print('MOC 引用数:', len(refs), '（去重后:', len(set(refs)), '）')

# 3) 「现代汉语的特点」追加块验证
doc_id = '20260722163653-x5l3egw'
cb = api('/api/block/getChildBlocks', {'id': doc_id})
blocks = cb.get('data') or []
print()
print('「现代汉语的特点」末尾追加块:')
for b in blocks[-2:]:
    print('  -', b.get('type'), (b.get('content') or '')[:60])
