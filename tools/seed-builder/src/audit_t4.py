#!/usr/bin/env python3
"""
T4 全量模拟审计：对 5 个 bank 全部题目模拟 100 个虚拟真人做题，审查 bug。
- 100 人分 5 个能力档（各 20 人）：正确率 90%/75%/60%/45%/30%
- 判分规则与 App（grading.dart）一致：
  单选/判断：集合完全相等；多选：全对=对/部分=部分/零命中=错
  填空：归一化（去空白小写）后完全相等；简答：参考答案关键词命中
- 输出：
  ① 数据完整性错误（可判分性检查）
  ② 100 人正确率异常题（全错/全对）
  ③ 每题正确率分布汇总
"""
import json, os, re, random, statistics
from collections import Counter, defaultdict

BANKS = ['bank-gudai-hanyu','bank-xiandai-hanyu','bank-zhongguo-gudai-wenxue',
         'bank-zhongguo-xiandai-wenxue','bank-zhongguo-dangdai-wenxue']
T1 = 'out/t1'
random.seed(2026)

# ---------- 判分（与 App grading.dart 一致） ----------
def norm(s): return re.sub(r'\s+', '', s or '').lower()

def grade(q, user):
    """user: 单选=A / 多选=set / 判断=正确/错误 / 填空=str / 简答=str"""
    qtype = q['type']
    if qtype in ('single_choice', 'true_false'):
        return 'correct' if user == q['answer'] else 'wrong'
    if qtype == 'multi_choice':
        correct = set(q['answer'])
        u = set(user)
        if u == correct: return 'correct'
        return 'partial' if u & correct else 'wrong'
    if qtype == 'blank':
        answers = {norm(a) for a in q['answer']}
        return 'correct' if norm(user) in answers else 'wrong'
    if qtype == 'short_answer':
        # 简答：用户答包含参考答案任一要点（简化：包含参考答案前 6 字）
        ref = q.get('answer', '')
        return 'correct' if ref and norm(ref)[:6] in norm(user) else 'wrong'
    return 'unknown'

# ---------- 虚拟考生作答 ----------
def answer(q, accuracy):
    """按能力概率作答；不会（低能）写空/乱选"""
    qtype = q['type']
    if random.random() > accuracy:
        # 答错/不会：低能力更容易空着
        if accuracy < 0.45 and random.random() < 0.6:
            if qtype == 'single_choice': return 'Z'
            if qtype == 'true_false': return '不知道'
            if qtype == 'multi_choice': return []
            return ''
    # 正确作答
    if qtype == 'single_choice':
        return q['answer']
    if qtype == 'true_false':
        return q['answer']
    if qtype == 'multi_choice':
        return list(q['answer'])
    if qtype == 'blank':
        return q['answer'][0]
    if qtype == 'short_answer':
        return q.get('answer', '')
    return ''

# ---------- 数据完整性检查（可判分性） ----------
def data_issues(q):
    errs = []
    qid, t = q['id'], q['type']
    # 答案存在
    if not q.get('answer'):
        errs.append(f'{qid} 缺 answer')
    if t in ('single_choice','true_false'):
        opts = [o['key'] for o in q.get('options', [])]
        if t == 'single_choice':
            if q.get('answer') not in opts: errs.append(f'{qid} 单选答案不在 options: {q.get("answer")} vs {opts}')
        else:
            if q.get('answer') not in ('正确','错误'): errs.append(f'{qid} 判断答案非法: {q.get("answer")}')
    elif t == 'multi_choice':
        opts = [o['key'] for o in q.get('options', [])]
        if not isinstance(q.get('answer'), list) or not set(q['answer']).issubset(opts):
            errs.append(f'{qid} 多选答案非法: {q.get("answer")}')
    elif t == 'blank':
        if not isinstance(q.get('answer'), list) or not q['answer']:
            errs.append(f'{qid} 填空答案非数组/空')
    if not q.get('chapter'):
        errs.append(f'{qid} 缺 chapter')
    if not q.get('source') or not q['source'].get('docPath'):
        errs.append(f'{qid} 缺 source.docPath')
    if t == 'short_answer' and not q.get('answerFormat'):
        errs.append(f'{qid} 简答缺 answerFormat')
    return errs

# ---------- 主流程 ----------
report = []
all_issues = defaultdict(list)
total_q = 0
for b in BANKS:
    d = json.load(open(f'{T1}/{b}.merged.json', encoding='utf-8'))
    qs = d['questions']
    total_q += len(qs)
    bank_issues = []
    weird = []
    acc_list = []
    for q in qs:
        # 数据完整性
        errs = data_issues(q)
        if errs:
            all_issues['data'].append(errs)
            bank_issues.append(q['id'])
        # 100 人模拟
        accs = []
        for acc in (0.9, 0.75, 0.6, 0.45, 0.3):
            for _ in range(20):
                g = grade(q, answer(q, acc))
                accs.append(1 if g == 'correct' else 0)
        acc_list.append(statistics.mean(accs))
        # 异常识别
        if statistics.mean(accs) == 0:
            weird.append((q['id'], q['type'], q['stem'][:40], '全错(答案可能错/不可判分)'))
        elif statistics.mean(accs) >= 0.99:
            weird.append((q['id'], q['type'], q['stem'][:40], '全对(太简单或答案格式异常)'))
    print(f'\n== {b}: {len(qs)} 题 ==')
    print(f'  数据问题题数: {len(bank_issues)}')
    print(f'  100人正确率: 均值 {statistics.mean(acc_list):.2%} 中位 {statistics.median(acc_list):.2%} 最低 {min(acc_list):.2%}')
    print(f'  异常题（全错/全对）: {len(weird)}')
    for w in weird[:8]:
        print(f'    {w}')
    report.append((b, len(qs), len(bank_issues), len(weird)))

print('\n' + '='*60)
print('【汇总】')
for b, n, di, w in report:
    print(f'  {b}: {n} 题, 数据问题 {di}, 异常 {w}')
print(f'  总题数: {total_q}')
print(f'  数据问题总数: {len(all_issues["data"])}')
if all_issues['data']:
    print('\n【数据问题前 30 条】')
    for e in all_issues['data'][:30]:
        print('  ', e)
