# -*- coding: utf-8 -*-
"""补充审查：knowledge/overview 完整性 + answerFormat 覆盖"""
import io, sys, glob, zipfile, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
for zp in sorted(glob.glob(r'D:\study_app\app\assets\banks\*.zip')):
    with zipfile.ZipFile(zp) as z:
        m = json.loads(z.read('manifest.json'))
        kfiles = [n for n in z.namelist() if n.startswith('knowledge/') and n.endswith('.json')]
        ofiles = [n for n in z.namelist() if n.startswith('overview/') and n.endswith('.json')]
        chfiles = [n for n in z.namelist() if n.startswith('questions/') and n.endswith('.json')]
        # answerFormat 覆盖
        n_blank_short = n_with_af = 0
        for n in chfiles:
            for q in json.loads(z.read(n)):
                if q.get('type') in ('blank', 'short_answer'):
                    n_blank_short += 1
                    if (q.get('answerFormat') or '').strip():
                        n_with_af += 1
        print(f'===== {m.get("name")} v{m.get("version")} =====')
        print(f'  章节文件 {len(chfiles)} | 知识卡 {len(kfiles)} | 概览 {len(ofiles)}')
        print(f'  填空/简答题 {n_blank_short} 个，有 answerFormat {n_with_af} 个 ({(n_with_af/max(n_blank_short,1)*100):.0f}%)')
        if ofiles:
            print('  概览章节:', sorted(o.split('/')[-1].replace('.json','') for o in ofiles)[:6], '...')
