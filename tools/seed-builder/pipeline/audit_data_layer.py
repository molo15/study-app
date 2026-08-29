# -*- coding: utf-8 -*-
"""全面数据审查：题量分布/章节覆盖/解析缺口/重复题/选项异常"""
import io, sys, glob, zipfile, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
names = {'bank-xiandai-hanyu': '现代汉语', 'bank-gudai-hanyu': '古代汉语',
         'bank-zhongguo-xiandai-wenxue': '现代文学', 'bank-zhongguo-dangdai-wenxue': '当代文学',
         'bank-zhongguo-gudai-wenxue': '古代文学'}
type_names = {'single_choice': '单选', 'multi_choice': '多选', 'blank': '填空',
              'short_answer': '简答', 'true_false': '判断'}

report = []
all_stems = collections.defaultdict(list)
for zp in sorted(glob.glob(r'D:\study_app\app\assets\banks\*.zip')):
    with zipfile.ZipFile(zp) as z:
        m = json.loads(z.read('manifest.json'))
        bank = m.get('bankId')
        label = names.get(bank, bank)
        lines = [f'\n===== {label} (v{m.get("version")}) =====']
        qs_all = []
        chap_count = collections.Counter()
        type_count = collections.Counter()
        no_expl = 0
        for n in z.namelist():
            if n.startswith('questions/') and n.endswith('.json'):
                ch = n.split('测试-')[-1].replace('.json', '') if '测试-' in n else n.split('/')[-1]
                for q in json.loads(z.read(n)):
                    qs_all.append(q)
                    chap_count[ch] += 1
                    type_count[q.get('type')] += 1
                    if not (q.get('explanation') or '').strip():
                        no_expl += 1
                    all_stems[q.get('stem', '')].append((bank, q.get('id')))
        lines.append(f'总题数: {len(qs_all)}')
        lines.append('题型分布: ' + ' | '.join(f'{type_names.get(t,t)} {c}' for t, c in type_count.most_common()))
        lines.append(f'解析缺失题数: {no_expl}')
        lines.append('章节分布:')
        for ch, c in chap_count.most_common():
            lines.append(f'  {ch}: {c}')
        report.append('\n'.join(lines))

# 全局重复 stem
dup = {s: v for s, v in all_stems.items() if len(v) > 1 and s}
report.append(f'\n===== 全局重复题干（相同 stem 多题） =====')
report.append(f'重复 stem 数: {len(dup)}')
for s, v in list(dup.items())[:10]:
    report.append(f'  [{v[0][0]}] {s[:40]} x{len(v)}')

# 选项异常：选择题少于 2 选项
report.append('\n===== 选项异常 =====')
bad_opt = 0
for zp in sorted(glob.glob(r'D:\study_app\app\assets\banks\*.zip')):
    with zipfile.ZipFile(zp) as z:
        for n in z.namelist():
            if n.startswith('questions/') and n.endswith('.json'):
                for q in json.loads(z.read(n)):
                    if q.get('type') in ('single_choice', 'multi_choice', 'true_false'):
                        if len(q.get('options') or []) < 2:
                            bad_opt += 1
report.append(f'选择/判断题选项少于2个: {bad_opt}')

out = '\n'.join(report)
with open(r'D:\study_app\docs\审核-数据层-2026-08-29.txt', 'w', encoding='utf-8') as f:
    f.write(out)
print(out[:3000])
print('...')
print('已写入 docs/审核-数据层-2026-08-29.txt')
