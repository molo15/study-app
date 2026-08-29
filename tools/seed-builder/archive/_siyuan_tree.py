# -*- coding: utf-8 -*-
"""拉取指定笔记本文档树"""
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

NB = sys.argv[1] if len(sys.argv) > 1 else '20260727111143-1ssxrs2'
try:
    r = api('/api/filetree/getDocByPath', {'path': '/' + NB, 'depth': 3})
    data = r.get('data')
    def walk(doc, dep=0):
        if not isinstance(doc, dict):
            return
        print('  ' * dep + '▸', doc.get('name'), '|', doc.get('id'))
        for sub in (doc.get('children') or []):
            walk(sub, dep + 1)
    walk(data)
except Exception as e:
    print('ERR:', type(e).__name__, e)
