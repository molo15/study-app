# -*- coding: utf-8 -*-
import io, sys, json, urllib.request, time
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
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode('utf-8'))

r = api('/api/export/exportData', {})
d = r.get('data')
print('导出结果 code=', r.get('code'), 'msg=', r.get('msg'))
if isinstance(d, dict) and d.get('zipPath'):
    zip_path = d['zipPath']
    print('zipPath:', zip_path)
    url = BASE + '/api/export/' + zip_path.split('/')[-1] if not zip_path.startswith('http') else zip_path
    # 用完整 URL 下载
    dl = BASE + '/api/export/' + zip_path.split('/')[-1] + '?token=' + TOKEN if not zip_path.startswith('http') else zip_path
    print('下载 URL (省略 token):', dl.replace(TOKEN, '***'))
    try:
        req = urllib.request.Request(dl, headers={'Authorization': 'Token ' + TOKEN})
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
            fn = r'D:\study_app\backup\siyuan-export-' + time.strftime('%Y%m%d_%H%M%S') + '.zip'
            open(fn, 'wb').write(data)
            print('已保存:', fn, len(data), 'bytes')
    except Exception as e:
        print('下载失败:', e)
else:
    print('返回 data:', json.dumps(d, ensure_ascii=False)[:300] if d else None)
