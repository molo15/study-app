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
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode('utf-8'))

moc_id = '20260828094939-f08k7sq'
# 尝试多种方式读取内容
for method, payload in [
    ('/api/filetree/getDoc', {'id': moc_id}),
    ('/api/block/getBlockKramdown', {'id': moc_id}),
    ('/api/block/getChildBlocks', {'id': moc_id}),
]:
    try:
        r = api(method, payload)
        d = r.get('data')
        print('=== {} ==='.format(method))
        if isinstance(d, dict):
            for k in ['type', 'content', 'md', 'kramdown', 'name']:
                if k in d:
                    print('  {}: {}'.format(k, (str(d[k]))[:200]))
            if 'blocks' in d:
                print('  blocks 数:', len(d['blocks']))
                for b in d['blocks'][:3]:
                    print('    -', b.get('id'), b.get('type'), (b.get('content') or '')[:50])
        elif isinstance(d, list):
            print('  list 长度:', len(d))
            for b in d[:3]:
                print('    -', b.get('id'), b.get('type'), (b.get('content') or '')[:50])
        else:
            print('  data:', str(d)[:200])
    except Exception as e:
        print('=== {} ERROR: {} ==='.format(method, e))
    print()
