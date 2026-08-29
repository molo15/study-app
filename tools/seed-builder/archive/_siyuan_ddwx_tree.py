# -*- coding: utf-8 -*-
"""列出中国当代文学史文档树"""
import io, sys, json, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TOKEN = 'jfolmogj8xr5h1r6'
BASE = 'http://127.0.0.1:6806'
NB = '20260728161404-kkq5v9t'

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
    for dd in (r.get('data') or {}).get('files') or []:
        if dd.get('subFileCount', 0) > 0:
            print('  ' * depth + 'DIR ' + dd['name'] + ' [' + dd['id'] + ']')
            walk(dd['path'], depth + 1)
        else:
            print('  ' * depth + 'DOC ' + dd['name'] + ' [' + dd['id'] + ']')

walk('/')
