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
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))

def dump_doc(doc_id, title):
    r = api('/api/export/exportMdContent', {'id': doc_id})
    d = r.get('data')
    md = d.get('md') if isinstance(d, dict) else None
    print('=' * 30)
    print('###', title, '(', doc_id, ')')
    print('=' * 30)
    if md:
        print(md[:3500])
    else:
        print('(空 / 导出失败)', json.dumps(d, ensure_ascii=False)[:300])
    print()

dump_doc('20260726154749-l3xwpgv', '修辞学概况')
dump_doc('20260726155113-1ctyuwj', '古汉语中常见的修辞格')
