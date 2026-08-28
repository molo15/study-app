# -*- coding: utf-8 -*-
import io, sys, json, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TOKEN = 'jfolmogj8xr5h1r6'
BASE = 'http://127.0.0.1:6806'
NB = '20260721175205-gpyhylx'

def api(method, data):
    req = urllib.request.Request(
        BASE + method,
        data=json.dumps(data).encode('utf-8'),
        headers={'Authorization': 'Token ' + TOKEN, 'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode('utf-8'))

def find(path, target, depth=0):
    """深度优先找目标文档 id"""
    try:
        tr = api('/api/filetree/listDocsByPath', {'notebook': NB, 'path': path})
        files = tr['data']['files'] or []
    except Exception as e:
        return None
    for d in files:
        if d['name'] == target:
            return d['id']
        if d.get('subFileCount', 0) > 0:
            r = find(d['path'], target, depth + 1)
            if r:
                return r
    return None

target = '现代汉语的特点'
doc_id = find('/', target)
print('文档 id:', doc_id, '(', target, ')')
if doc_id:
    r = api('/api/export/exportMdContent', {'id': doc_id})
    md = r.get('data') or r.get('data', {}).get('md') if isinstance(r.get('data'), dict) else r.get('data')
    # data 可能是字符串（md）或 dict
    if isinstance(r, dict):
        d = r.get('data')
        if isinstance(d, dict):
            md = d.get('md') or d.get('content') or d.get('markdown') or json.dumps(d, ensure_ascii=False)
        else:
            md = d
    print('=== 文档内容 (markdown) ===')
    print(md if md else '(空)')
