# -*- coding: utf-8 -*-
"""尝试多种方式拉取笔记本文档树"""
import io, sys, json, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'http://127.0.0.1:6806'
TOKEN = 'jfolmogj8xr5h1r6'
def api(path, data):
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode('utf-8'),
                                 headers={'Authorization': 'Token ' + TOKEN, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode('utf-8'))

NB = '20260727111143-1ssxrs2'
for p, d in [('/api/filetree/listDocsByPath', {'path': '/' + NB}),
             ('/api/filetree/getDocByPath', {'path': '/' + NB + '/'}),
             ('/api/filetree/listDocsByPath', {'path': '/' + NB, 'sortMode': 0}),
             ('/api/filetree/getDocsByPath', {'path': '/' + NB})]:
    try:
        r = api(p, d)
        print('API', p, 'code', r.get('code'))
        data = r.get('data')
        if isinstance(data, list):
            for x in data[:60]:
                if isinstance(x, dict):
                    print('  ', x.get('name'), '|', x.get('id'), '|', x.get('subFileCount'))
        elif isinstance(data, dict):
            print('  keys:', list(data.keys())[:10])
            for k, v in (data.items() if isinstance(data, dict) else []):
                if k in ('name', 'id', 'title'):
                    print('   ', k, v)
        break
    except Exception as e:
        print('API', p, 'ERR:', type(e).__name__, e)
