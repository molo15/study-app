# -*- coding: utf-8 -*-
"""拉取古代汉语稀疏章节素材：古书的标点、古书的文体、训诂"""
import io, sys, json, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TOKEN = 'jfolmogj8xr5h1r6'
BASE = 'http://127.0.0.1:6806'
NB = '20260722162828-fvyl4ks'  # 古代汉语

def api(method, data):
    req = urllib.request.Request(
        BASE + method,
        data=json.dumps(data).encode('utf-8'),
        headers={'Authorization': 'Token ' + TOKEN, 'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))

def dump_doc(doc_id, title, maxlen=4000):
    r = api('/api/export/exportMdContent', {'id': doc_id})
    d = r.get('data')
    md = d.get('content') if isinstance(d, dict) else None
    print('=' * 30)
    print('###', title)
    print('=' * 30)
    if md:
        # 去掉 frontmatter
        body = md
        if body.startswith('---'):
            parts = body.split('---', 2)
            if len(parts) >= 3:
                body = parts[2]
        print(body[:maxlen])
    else:
        print('(空)')
    print()

# 古书的标点
dump_doc('20260726152621-4xisloy', '古书的标点-标点', 5000)
