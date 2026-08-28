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
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode('utf-8'))

result = []

def walk(path, parents):
    try:
        tr = api('/api/filetree/listDocsByPath', {'notebook': NB, 'path': path})
        files = tr['data']['files'] or []
    except Exception as e:
        return
    for d in files:
        p = parents + [d['name']]
        result.append({'id': d['id'], 'path': '/'.join(p), 'sub': d.get('subFileCount', 0)})
        if d.get('subFileCount', 0) > 0:
            walk(d['path'], p)

walk('/', [])
json.dump(result, open(r'D:\study_app\tools\seed-builder\out\siyuan_xdhy_docs.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('共 {} 个文档'.format(len(result)))
for r in result:
    print('{}  [{}]'.format(r['path'], r['id']))
