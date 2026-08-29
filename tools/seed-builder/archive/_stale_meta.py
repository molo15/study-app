# -*- coding: utf-8 -*-
import json, zipfile, os
BASE = r'D:\study_app\tools\seed-builder'
# 每库最新 backup（含 .new 优先）
BACKUP = {
 'bank-gudai-hanyu':'out/legacy_banks_backup/bank-gudai-hanyu-v0.9.0.zip.new',
 'bank-xiandai-hanyu':'out/legacy_banks_backup/bank-xiandai-hanyu-v0.9.0.zip.bak4',
 'bank-zhongguo-gudai-wenxue':'out/legacy_banks_backup/bank-zhongguo-gudai-wenxue-v0.9.0.zip.bak4',
 'bank-zhongguo-xiandai-wenxue':'out/legacy_banks_backup/bank-zhongguo-xiandai-wenxue-v0.9.0.zip.bak4',
 'bank-zhongguo-dangdai-wenxue':'out/legacy_banks_backup/bank-zhongguo-dangdai-wenxue-v0.9.0.zip.bak4',
}
stale = {
 'bank-gudai-hanyu':['bank-gudai-hanyu:m_000539','bank-gudai-hanyu:m_000524','bank-gudai-hanyu:q_000026','bank-gudai-hanyu:q_000132'],
 'bank-xiandai-hanyu':['bank-xiandai-hanyu:q_000010','bank-xiandai-hanyu:z_000141','bank-xiandai-hanyu:w_000049','bank-xiandai-hanyu:w_000279','bank-xiandai-hanyu:k_000224','bank-xiandai-hanyu:w_000050','bank-xiandai-hanyu:w_000138','bank-xiandai-hanyu:w_000452','bank-xiandai-hanyu:w_000093','bank-xiandai-hanyu:k_000227'],
 'bank-zhongguo-gudai-wenxue':['bank-zhongguo-gudai-wenxue:q_000116'],
 'bank-zhongguo-xiandai-wenxue':['bank-zhongguo-xiandai-wenxue:q_000061','bank-zhongguo-xiandai-wenxue:q_000102','bank-zhongguo-xiandai-wenxue:q_000001','bank-zhongguo-xiandai-wenxue:q_000005','bank-zhongguo-xiandai-wenxue:q_000140','bank-zhongguo-xiandai-wenxue:q_000052','bank-zhongguo-xiandai-wenxue:q_000120'],
 'bank-zhongguo-dangdai-wenxue':['bank-zhongguo-dangdai-wenxue:q_000072','bank-zhongguo-dangdai-wenxue:q_000053','bank-zhongguo-dangdai-wenxue:q_000094','bank-zhongguo-dangdai-wenxue:q_000114','bank-zhongguo-dangdai-wenxue:q_000111','bank-zhongguo-dangdai-wenxue:q_000130','bank-zhongguo-dangdai-wenxue:q_000017','bank-zhongguo-dangdai-wenxue:q_000036'],
}
for bank, files in stale.items():
    zp = os.path.join(BASE, BACKUP[bank])
    z = zipfile.ZipFile(zp)
    # 读取所有 question json
    qmap = {}
    for n in z.namelist():
        if n.startswith('questions/') and n.endswith('.json'):
            for q in json.loads(z.read(n).decode('utf-8')):
                qmap[q['id']] = q
    print('=====', bank)
    for sid in files:
        q = qmap.get(sid)
        if q:
            print(f"  {sid.split(':')[1]} type={q.get('type')} chapter={q.get('chapter','')} stem={q.get('stem','')[:30]}")
        else:
            print(f"  {sid} 不在backup")
