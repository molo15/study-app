# -*- coding: utf-8 -*-
"""用 SQL 查询笔记本下所有文档块"""
import io, sys, json, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'http://127.0.0.1:6806'
TOKEN = 'jfolmogj8xr5h1r6'
def api(path, data):
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode('utf-8'),
                                 headers={'Authorization': 'Token ' + TOKEN, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode('utf-8'))
NB = sys.argv[1]
r = api('/api/query/sql', {'stmt': f"SELECT b.id, b.hpath FROM blocks b WHERE b.box_id='{NB}' AND b.type='d' ORDER BY b.hpath"})
for row in r.get('data', []):
    print(row.get('hpath'), '|', row.get('id'))
