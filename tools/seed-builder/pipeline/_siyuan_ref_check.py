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

# 看 MOC 一个引用块的 DOM，确认是否解析为 BlockRef
moc_id = '20260828094939-f08k7sq'
r = api('/api/filetree/getDoc', {'id': moc_id})
content = r.get('data', {}).get('content', '')
# 统计 DOM 里 BlockRef 引用数量
blockref = content.count('BlockRef')
# 找一段含引用的 DOM
idx = content.find('BlockRef')
print('MOC DOM 中 BlockRef 出现次数:', blockref)
print()
print('=== 含引用的 DOM 片段（前 1500 字符）===')
if idx >= 0:
    print(content[max(0, idx - 300): idx + 700])
else:
    # 打印原始引用文本片段
    import re
    m = re.search(r'\(\(20260722\d{5,}[^)]*\)\)', content)
    print('未发现 BlockRef；原文引用片段:')
    print(m.group(0) if m else '无')
