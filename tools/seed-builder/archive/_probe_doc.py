# -*- coding: utf-8 -*-
"""探查 getDoc 返回结构"""
import io, sys, json, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'http://127.0.0.1:6806'
TOKEN = 'jfolmogj8xr5h1r6'
def api(path, data):
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode('utf-8'),
                                 headers={'Authorization': 'Token ' + TOKEN, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode('utf-8'))
r = api('/api/filetree/getDoc', {'id': '20260727154018-20sz1q6'})
print('code', r.get('code'), 'msg', r.get('msg'))
d = r.get('data')
print('data type:', type(d))
print(str(d)[:1500])
