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
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode('utf-8'))

def find(nb, path, target):
    try:
        tr = api('/api/filetree/listDocsByPath', {'notebook': nb, 'path': path})
        files = tr['data']['files'] or []
    except Exception as e:
        return None
    for d in files:
        if d['name'] == target:
            return d['id']
        if d.get('subFileCount', 0) > 0:
            r = find(nb, d['path'], target)
            if r:
                return r
    return None

XDHY = '20260721175205-gpyhylx'   # 现代汉语
GDHY = '20260722162828-fvyl4ks'   # 古代汉语

targets = [
    ('现代汉语', XDHY, '声调'),
    ('现代汉语', XDHY, '词汇概说'),
    ('现代汉语', XDHY, '语法概说'),
    ('现代汉语', XDHY, '词汇的发展变化和词汇的规范化'),
    ('古代汉语', GDHY, '文字（上）'),
    ('古代汉语', GDHY, '文字（下）'),
]
for label, nb, t in targets:
    i = find(nb, '/', t)
    print('{} · {}  ->  id={}'.format(label, t, i))
