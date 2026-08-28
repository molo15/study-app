# -*- coding: utf-8 -*-
"""拉取现代文学史 市民通俗小说(一)(二)、散文(三) 素材"""
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

dump_doc('20260728083324-8k7nkg8', '市民通俗小说（一）', 3500)
dump_doc('20260728095202-w89ibbi', '市民通俗小说（二）', 3500)
