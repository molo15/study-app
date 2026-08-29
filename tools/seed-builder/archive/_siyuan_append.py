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
# 1) 取文档直接子块
r = api('/api/block/getChildBlocks', {'id': doc_id})
blocks = r.get('data') or []
print('文档子块数:', len(blocks))
for b in blocks:
    print('  子块:', b.get('id'), b.get('type'), (b.get('content') or '')[:25])
last_id = blocks[-1]['id'] if blocks else doc_id
print('末尾块 id:', last_id)

# 2) 追加"相关链接"块（含双链引用）
append_md = """## 相关链接（AI 试点追加）

- 语素与词的结构 → ((20260722172446-1ho36qr "词汇概说"))
- 古词复音化与词汇演变 → ((20260722172513-5asddzy "词汇的发展变化与规范化"))
- 语序与虚词体系 → ((20260722160251-0mrovua "语法概说"))
- 表意文字 / 汉字超时空性（跨科目）→ ((20260722163030-gf2dklc "古代汉语·文字（上）")) · ((20260726103623-p0vjy4q "古代汉语·文字（下）"))
- 本页索引于 → ((20260828094939-f08k7sq "现代汉语·知识地图"))"""

a = api('/api/block/appendBlock', {
    'dataType': 'markdown',
    'data': append_md,
    'previousID': last_id,
})
print('appendBlock -> code={} msg={}'.format(a.get('code'), a.get('msg')))
print('data:', json.dumps(a.get('data'), ensure_ascii=False) if a.get('data') else None)
