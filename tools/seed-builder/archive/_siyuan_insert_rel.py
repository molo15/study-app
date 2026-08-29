# -*- coding: utf-8 -*-
import io, sys, json, urllib.request
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

blocks = child_blocks()

# 1) 删除测试块
for b in blocks:
    if '测试insert' in (b.get('content') or ''):
        dr = api('/api/block/deleteBlock', {'id': b['id']})
        print('删除测试块 -> code={}'.format(dr.get('code')))

blocks = child_blocks()
last = blocks[-1]['id']
print('当前末尾块:', last, (blocks[-1].get('content') or '')[:20])

# 2) insertBlock 追加正式相关链接（英文引号引用）
append_md = """## 相关链接（AI 试点追加）

- 语素与词的结构 → ((20260722172446-1ho36qr "词汇概说"))
- 古词复音化与词汇演变 → ((20260722172513-5asddzy "词汇的发展变化与规范化"))
- 语序与虚词体系 → ((20260722160251-0mrovua "语法概说"))
- 表意文字 / 汉字超时空性（跨科目）→ ((20260722163030-gf2dklc "古代汉语·文字（上）")) · ((20260726103623-p0vjy4q "古代汉语·文字（下）"))
- 本页索引于 → ((20260828095316-qmzglye "现代汉语·知识地图"))"""

r = api('/api/block/insertBlock', {'dataType': 'markdown', 'data': append_md, 'previousID': last})
print('insertBlock 相关链接 -> code={} msg={}'.format(r.get('code'), r.get('msg')))

# 3) 验证
import time; time.sleep(1)
blocks = child_blocks()
print()
print('追加后子块数:', len(blocks))
for b in blocks[-2:]:
    print('  末尾:', b.get('type'), (b.get('content') or '')[:50])
