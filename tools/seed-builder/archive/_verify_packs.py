# -*- coding: utf-8 -*-
import io, sys, glob, zipfile, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
names = {'bank-xiandai-hanyu': '现代汉语', 'bank-gudai-hanyu': '古代汉语',
         'bank-zhongguo-xiandai-wenxue': '现代文学', 'bank-zhongguo-dangdai-wenxue': '当代文学',
         'bank-zhongguo-gudai-wenxue': '古代文学'}
tot_mc = 0
for zp in sorted(glob.glob(r'D:\study_app\app\assets\banks\*.zip')):
    with zipfile.ZipFile(zp) as z:
        m = json.loads(z.read('manifest.json'))
        bank = m.get('bankId')
        mc = 0; total = 0; ids = set(); dup = 0; badans = 0; opt4 = 0; opt5 = 0
        for n in z.namelist():
            if n.startswith('questions/') and n.endswith('.json'):
                for q in json.loads(z.read(n)):
                    total += 1
                    if q['id'] in ids:
                        dup += 1
                    ids.add(q['id'])
                    if q.get('type') == 'multi_choice':
                        mc += 1
                        if len(q['options']) == 4: opt4 += 1
                        if len(q['options']) == 5: opt5 += 1
                        texts = [o['text'] for o in q['options']]
                        for a in q['answer']:
                            if a not in texts:
                                badans += 1
        print(names.get(bank, bank), '| v', m.get('version'), '| fmt', m.get('formatVersion'),
              '| idSchema', m.get('idSchema'), '| 总题', total, '| 多选', mc,
              '| 4选项', opt4, '| 5选项', opt5, '| 重复id', dup, '| 答案错位', badans,
              '| 声称题数', m.get('questionCount'))
        tot_mc += mc
print('多选总计:', tot_mc)
