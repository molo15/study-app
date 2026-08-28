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

before = len(child_blocks())
print('追加前子块数:', before)

# 测试1：纯文本 markdown 追加（previousID=文档根块 id）
t1 = api('/api/block/appendBlock', {'dataType': 'markdown', 'data': '测试追加-纯文本-12345', 'previousID': doc_id})
print('append(markdown纯文本, prev=doc根) -> code={}'.format(t1.get('code')))
after1 = len(child_blocks())
print('追加后子块数:', after1)

# 测试2：DOM 方式追加含 block-ref 的块
dom = '<p>相关链接（AI 试点追加）：<span data-type="block-ref" data-subtype="s" data-id="20260722163030-gf2dklc">古代汉语·文字（上）</span></p>'
t2 = api('/api/block/appendBlock', {'dataType': 'dom', 'data': dom, 'previousID': doc_id})
print('append(dom含block-ref) -> code={} msg={}'.format(t2.get('code'), t2.get('msg')))
after2 = len(child_blocks())
print('再次追加后子块数:', after2)

# 打印末尾块
blocks = child_blocks()
print()
print('末尾 3 块:')
for b in blocks[-3:]:
    print('  -', b.get('type'), (b.get('content') or '')[:45])
