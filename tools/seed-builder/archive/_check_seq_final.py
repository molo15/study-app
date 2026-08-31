# -*- coding: utf-8 -*-
"""验证最终 v0.14.0 里 q_000088 洗牌后解析一致性 + 全量整串枚举复核。"""
import io, sys, json, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load_qs(path):
    z = zipfile.ZipFile(path)
    qs = []
    for n in z.namelist():
        if n.startswith('questions/') and n.endswith('.json'):
            qs.extend(json.loads(z.read(n)))
    return qs

# 1. q_000088
qs = load_qs(r'D:\study_app\app\assets\banks\bank-zhongguo-xiandai-wenxue-v0.14.0.zip')
for q in qs:
    if q['id'].endswith('q_000088'):
        print('=== q_000088')
        for o in q.get('options', []):
            m = ' <==正确' if o['text'] == q.get('answer') else ''
            print('   ', o['key'], o['text'][:24], m)
        print('  answer:', q['answer'][:18])
        print('  expl tail:', q['explanation'][-40:])
        break

# 2. 全量整串枚举一致性：找出所有 "故X、Y项不选" 模式的解析，人工核对
print()
print('=== 全量"故X、Y、Z项不选"枚举检查 ===')
pat = re.compile(r'故([ABCDEF](?:、[ABCDEF]){1,5})项?不选')
tot = 0
for f in ['bank-zhongguo-xiandai-wenxue-v0.14.0.zip']:
    qs = load_qs(r'D:\study_app\app\assets\banks\\' + f)
    for q in qs:
        if q.get('type') not in ('single_choice', 'multi_choice'):
            continue
        expl = re.sub(r'\s+', '', q.get('explanation', ''))
        m = pat.search(expl)
        if m:
            opts = q.get('options', [])
            ans = q.get('answer')
            if isinstance(ans, list):
                at = set(ans)
                ok = {o['key'] for o in opts if o['text'] in at}
            else:
                ok = {o['key'] for o in opts if o['text'] == ans}
            cited = set(m.group(1).split('、'))
            bad = cited & ok
            tot += 1
            if bad:
                print(f"  !! {q['id']} 排除{cited}含正确项{ok} 解析:{m.group(0)}")
print('含整串枚举的题:', tot)
