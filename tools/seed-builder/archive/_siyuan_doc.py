# -*- coding: utf-8 -*-
"""拉取指定文档块的纯文本内容"""
import io, sys, json, urllib.request, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'http://127.0.0.1:6806'
TOKEN = 'jfolmogj8xr5h1r6'
def api(path, data):
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode('utf-8'),
                                 headers={'Authorization': 'Token ' + TOKEN, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode('utf-8'))

def doc_content(doc_id, max_chars=2500):
    r = api('/api/filetree/getDoc', {'id': doc_id})
    dom = r.get('data')
    # 提取文本
    texts = []
    def walk(block):
        if isinstance(block, dict):
            t = block.get('Type') or block.get('type')
            content = block.get('Content') or block.get('content') or ''
            if t in ('h', 'p', 'li', 'code', 'blockquote'):
                if isinstance(content, str) and content.strip():
                    texts.append(content.strip())
            for sub in (block.get('Children') or block.get('children') or []):
                walk(sub)
    walk(dom)
    return '\n'.join(texts)[:max_chars]

doc_id = sys.argv[1]
name = sys.argv[2] if len(sys.argv) > 2 else ''
print('====', name, '====')
print(doc_content(doc_id))
