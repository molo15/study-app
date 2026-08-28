# -*- coding: utf-8 -*-
import io, sys, json, urllib.request, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TOKEN = 'jfolmogj8xr5h1r6'
BASE = 'http://127.0.0.1:6806'
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

def child_blocks():
    return api('/api/block/getChildBlocks', {'id': doc_id}).get('data') or []

# 确保测试块已删除（若还在则再删）
for _ in range(3):
    blocks = child_blocks()
    test = [b for b in blocks if '测试insert' in (b.get('content') or '')]
    if not test:
        break
    for b in test:
        api('/api/block/deleteBlock', {'id': b['id']})
    time.sleep(1)

blocks = child_blocks()
last = blocks[-1]['id']
print('当前真末尾块:', last, '|', (blocks[-1].get('content') or '')[:20])
print('测试块残留:', any('测试insert' in (b.get('content') or '') for b in blocks))

append_md = """## 相关链接（AI 试点追加）

- 语素与词的结构 → ((20260722172446-1ho36qr "词汇概说"))
- 古词复音化与词汇演变 → ((20260722172513-5asddzy "词汇的发展变化与规范化"))
- 语序与虚词体系 → ((20260722160251-0mrovua "语法概说"))
- 表意文字 / 汉字超时空性（跨科目）→ ((20260722163030-gf2dklc "古代汉语·文字（上）")) · ((20260726103623-p0vjy4q "古代汉语·文字（下）"))
- 本页索引于 → ((20260828095316-qmzglye "现代汉语·知识地图"))"""

r = api('/api/block/insertBlock', {'dataType': 'markdown', 'data': append_md, 'previousID': last})
print('insertBlock -> code={} msg={}'.format(r.get('code'), r.get('msg')))

time.sleep(1.5)
blocks = child_blocks()
print('追加后子块数:', len(blocks))
for b in blocks[-2:]:
    print('  末尾:', b.get('type'), (b.get('content') or '')[:55])

# DOM 验证 block-ref
r2 = api('/api/filetree/getDoc', {'id': doc_id})
content = r2.get('data', {}).get('content', '')
print('「现代汉语的特点」block-ref 次数:', content.count('block-ref'))
