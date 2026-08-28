# -*- coding: utf-8 -*-
"""拉取思源笔记古代文学史笔记本结构"""
import io, sys, json, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'http://127.0.0.1:6806'
TOKEN = 'jfolmogj8xr5h1r6'

def api(path, data):
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode('utf-8'),
                                 headers={'Authorization': 'Token ' + TOKEN,
                                          'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode('utf-8'))

try:
    r = api('/api/notebook/lsNotebooks', {})
    print('CODE:', r.get('code'), 'MSG:', r.get('msg'))
    data = r.get('data')
    if isinstance(data, list):
        for nb in data:
            if isinstance(nb, dict):
                print('NB:', nb.get('name'), nb.get('id'))
    else:
        print('data type:', type(data), str(data)[:500])
except Exception as e:
    print('ERR:', type(e).__name__, e)
