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
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read().decode('utf-8'))

# 列出笔记本
r = api('/api/notebook/lsNotebooks', {})
notebooks = r['data']['notebooks']
for nb in notebooks:
    nid, name = nb['id'], nb['name']
    # 拉根目录文档树
    try:
        tr = api('/api/filetree/listDocsByPath', {'notebook': nid, 'path': '/'})
        docs = tr['data']['files'] or []
        print('【{}】({}) {} 个文档:'.format(name, nid, len(docs)))
        for d in docs:
            sub = ' (子文档 {})'.format(d.get('subFileCount', 0)) if d.get('subFileCount') else ''
            print('    - {}  [{}{}]'.format(d.get('name', ''), d.get('type', ''), sub))
    except Exception as e:
        print('【{}】读取失败: {}'.format(name, e))
    print()
