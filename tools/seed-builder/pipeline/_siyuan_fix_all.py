# -*- coding: utf-8 -*-
import io, sys, json, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TOKEN = 'jfolmogj8xr5h1r6'
BASE = 'http://127.0.0.1:6806'
NB = '20260721175205-gpyhylx'
MOC_ID = '20260828095316-qmzglye'

def api(method, data):
    req = urllib.request.Request(
        BASE + method,
        data=json.dumps(data).encode('utf-8'),
        headers={'Authorization': 'Token ' + TOKEN, 'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode('utf-8'))

# 1) 验证新 MOC 引用是否解析为 BlockRef
r = api('/api/filetree/getDoc', {'id': MOC_ID})
content = r.get('data', {}).get('content', '')
print('新 MOC BlockRef 出现次数:', content.count('BlockRef'))

# 2) 重命名新 MOC
rr = api('/api/filetree/renameDoc', {'notebook': NB, 'path': '/' + MOC_ID + '.sy', 'title': '现代汉语 · 知识地图（MOC）'})
print('rename -> code={} msg={}'.format(rr.get('code'), rr.get('msg')))

# 3) 「现代汉语的特点」追加相关链接（英文引号）
doc_id = '20260722163653-x5l3egw'
cb = api('/api/block/getChildBlocks', {'id': doc_id})
blocks = cb.get('data') or []
last_id = blocks[-1]['id'] if blocks else doc_id
print('末尾块:', last_id)

append_md = """## 相关链接（AI 试点追加）

- 语素与词的结构 → ((20260722172446-1ho36qr "词汇概说"))
- 古词复音化与词汇演变 → ((20260722172513-5asddzy "词汇的发展变化与规范化"))
- 语序与虚词体系 → ((20260722160251-0mrovua "语法概说"))
- 表意文字 / 汉字超时空性（跨科目）→ ((20260722163030-gf2dklc "古代汉语·文字（上）")) · ((20260726103623-p0vjy4q "古代汉语·文字（下）"))
- 本页索引于 → ((20260828095316-qmzglye "现代汉语·知识地图"))"""

a = api('/api/block/appendBlock', {'dataType': 'markdown', 'data': append_md, 'previousID': last_id})
print('appendBlock -> code={} msg={}'.format(a.get('code'), a.get('msg')))
