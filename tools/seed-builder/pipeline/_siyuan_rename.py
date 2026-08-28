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
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode('utf-8'))

# 重命名"未命名文档" → MOC 标题
r = api('/api/filetree/renameDoc', {
    'notebook': NB,
    'path': '/未命名文档.sy',
    'title': '现代汉语 · 知识地图（MOC）',
})
print('renameDoc -> code={} msg={} data={}'.format(r.get('code'), r.get('msg'), json.dumps(r.get('data'), ensure_ascii=False) if r.get('data') else None))
