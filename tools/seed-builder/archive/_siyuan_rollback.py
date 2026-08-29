# -*- coding: utf-8 -*-
import io, sys, json, urllib.request, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TOKEN = 'jfolmogj8xr5h1r6'
BASE = 'http://127.0.0.1:6806'
NB = '20260721175205-gpyhylx'
MOC_ID = '20260828095316-qmzglye'
doc_id = '20260722163653-x5l3egw'

def api(method, data):
    req = urllib.request.Request(
        BASE + method,
        data=json.dumps(data).encode('utf-8'),
        headers={'Authorization': 'Token ' + TOKEN, 'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode('utf-8'))

# 1) 删除 MOC 文档
r = api('/api/filetree/removeDoc', {'notebook': NB, 'path': '/' + MOC_ID + '.sy'})
print('删除 MOC 文档 -> code={} msg={}'.format(r.get('code'), r.get('msg')))

# 2) 删除「现代汉语的特点」追加的相关链接块
# 相关链接是 h 块 + 下面的 l 块；先删 h 块（含其子列表），再确认
for attempt in range(3):
    blocks = api('/api/block/getChildBlocks', {'id': doc_id}).get('data') or []
    targets = [b for b in blocks if '相关链接（AI 试点追加）' in (b.get('content') or '') or '语素与词的结构' in (b.get('content') or '')]
    if not targets:
        print('相关链接块已清理')
        break
    for b in targets:
        dr = api('/api/block/deleteBlock', {'id': b['id']})
        print('删除块', b['id'], b.get('type'), '-> code={}'.format(dr.get('code')))
    time.sleep(1)

# 3) 最终验证
time.sleep(1)
tr = api('/api/filetree/listDocsByPath', {'notebook': NB, 'path': '/'})
print()
print('=== 现代汉语根目录（应恢复 4 项）===')
for d in tr['data']['files'] or []:
    print('  -', d['name'])
blocks = api('/api/block/getChildBlocks', {'id': doc_id}).get('data') or []
print()
print('「现代汉语的特点」子块数:', len(blocks), '（原为 18）')
print('末尾块:', (blocks[-1].get('content') or '')[:30])
r2 = api('/api/filetree/getDoc', {'id': doc_id})
content = r2.get('data', {}).get('content', '')
print('block-ref 残留:', content.count('block-ref'))
print('相关链接残留:', '相关链接' in content)
