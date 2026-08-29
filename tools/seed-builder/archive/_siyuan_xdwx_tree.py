# -*- coding: utf-8 -*-
"""列出中国现代文学史文档树"""
import io, sys, json, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TOKEN = 'jfolmogj8xr5h1r6'
BASE = 'http://127.0.0.1:6806'
NB = '20260728080131-vcrup20'

def api(method, data):
    req = urllib.request.Request(
        BASE + method,
        data=json.dumps(data).encode('utf-8'),
        headers={'Authorization': 'Token ' + TOKEN, 'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))

def walk(path, depth=0):
    r = api('/api/filetree/listDocsByPath', {'notebook': NB, 'path': path})
    for d in (r.get('data') or {}).get('files') or []:
        if d.get('subFileCount', 0) > 0:
            print('  ' * depth + 'DIR ' + d['name'] + ' [' + d['id'] + ']')
            walk(d['path'], depth + 1)
        else:
            print('  ' * depth + 'DOC ' + d['name'] + ' [' + d['id'] + ']')

walk('/')
