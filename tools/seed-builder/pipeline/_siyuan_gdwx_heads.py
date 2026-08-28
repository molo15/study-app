# -*- coding: utf-8 -*-
"""拉取古代文学史所有文档的标题结构（h1-h4），了解素材覆盖范围"""
import io, sys, json, urllib.request, re, html
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'http://127.0.0.1:6806'
TOKEN = 'jfolmogj8xr5h1r6'
NB = '20260727111143-1ssxrs2'

def api(path, data):
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode('utf-8'),
                                 headers={'Authorization': 'Token ' + TOKEN, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode('utf-8'))

# 1. 所有文档
r = api('/api/query/sql', {'stmt': "SELECT id, hpath FROM blocks WHERE box='" + NB + "' AND type='d' ORDER BY hpath"})
docs = [(row['hpath'], row['id']) for row in (r.get('data') or [])]
print('文档总数:', len(docs))

# 2. 每个文档的标题结构
def headings(content):
    out = []
    for m in re.finditer(r'data-subtype="(h[1-4])"[^>]*>.*?<div contenteditable="true"[^>]*>(.*?)<span', content, re.S):
        lvl = m.group(1)
        txt = re.sub(r'<[^>]+>', '', m.group(2))
        txt = html.unescape(txt).strip()
        if txt:
            out.append((lvl, txt))
    return out

for hp, did in docs:
    try:
        r2 = api('/api/filetree/getDoc', {'id': did})
        content = r2.get('data', {}).get('content', '')
        hs = headings(content)
        if hs:
            print('\n###', hp)
            for lvl, t in hs:
                print('  ' * (int(lvl[1])-1), t[:50])
    except Exception as e:
        print(hp, 'ERR', e)
