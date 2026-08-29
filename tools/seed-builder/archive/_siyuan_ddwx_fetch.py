# -*- coding: utf-8 -*-
"""拉取当代 新诗(50-60)、台港、戏剧(80-90) 素材"""
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
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))

def dump_doc(doc_id, title, maxlen=3000):
    r = api('/api/export/exportMdContent', {'id': doc_id})
    d = r.get('data')
    md = d.get('content') if isinstance(d, dict) else None
    print('=' * 30)
    print('###', title)
    print('=' * 30)
    if md:
        body = md
        if body.startswith('---'):
            parts = body.split('---', 2)
            if len(parts) >= 3:
                body = parts[2]
        print(body[:maxlen])
    else:
        print('(空)')
    print()

dump_doc('20260728163840-kg4fhk9', '50、60年代新诗概述', 3000)
dump_doc('20260728163841-mrs0mwz', '郭小川、贺敬之', 2500)
dump_doc('20260728170030-7kszyef', '台港：白先勇梁实秋余光中', 2800)
dump_doc('20260728170050-pj3vo71', '台港：金庸', 2500)
dump_doc('20260728165527-0nzwjh3', '80、90年代戏剧概述', 2500)
dump_doc('20260728165730-fsxigrn', '沙叶新、高行健', 2500)
