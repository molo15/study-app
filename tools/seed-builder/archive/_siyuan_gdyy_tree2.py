# -*- coding: utf-8 -*-
import io, sys, json, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TOKEN = 'jfolmogj8xr5h1r6'
BASE = 'http://127.0.0.1:6806'
NB = '20260722162828-fvyl4ks'  # 古代汉语

def api(method, data):
    req = urllib.request.Request(
        BASE + method,
        data=json.dumps(data).encode('utf-8'),
        headers={'Authorization': 'Token ' + TOKEN, 'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))

def list_dir(path):
    """返回 (文档列表, 子目录列表)"""
    r = api('/api/filetree/listDocsByPath', {'notebook': NB, 'path': path})
    docs, subs = [], []
    for d in (r.get('data') or {}).get('files') or []:
        if d.get('subFileCount', 0) > 0:
            subs.append(d)
        else:
            docs.append(d)
    return docs, subs

def walk(path, depth=0):
    docs, subs = list_dir(path)
    for d in docs:
        print('  ' * depth + 'DOC ' + d['name'] + ' [' + d['id'] + ']')
    for s in subs:
        print('  ' * depth + 'DIR ' + s['name'] + ' [' + s['id'] + ']')
        walk(s['path'], depth + 1)

walk('/')
