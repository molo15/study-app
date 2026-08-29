# -*- coding: utf-8 -*-
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
stmt = "SELECT id, hpath FROM blocks WHERE box='" + NB + "' AND type='d' ORDER BY hpath LIMIT 300"
r = api('/api/query/sql', {'stmt': stmt})
print('code', r.get('code'), r.get('msg'))
for row in r.get('data') or []:
    print(row.get('hpath'), '|', row.get('id'))
