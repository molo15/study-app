# -*- coding: utf-8 -*-
"""全量扫描 v0.14.0 最终 zip：
1) P0：解析内明确字母引用 vs 实际正确选项字母 的一致性
2) P1/P2：工作残留/模板尾巴/冒号前缀黑名单
3) 统计各科题量
"""
import io, sys, json, os, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ASSETS = r'D:\study_app\app\assets\banks'
BLACK = re.compile(r'素材块|素材n|正文块|对应素材标题|覆盖缺口|本题答案为|存量题未覆盖|本题属[于]?.{0,15}常考|即可应对同类题目|掌握其概念|依据-[0-9a-z]+、|（基础）|（变式）|（拓展）|（提升）|（综合）|（识记）|（理解）$|^解析[:：]')
EXPL_LETTER = re.compile(r'(选|故选|答案|正确选项(?:为|是)?|应为|应选|故|仅|据此选|根据)([ABCDEF])(?=$|[，。；、:： ]|项|正确|错误|对|不对|符合|不符合|有误|表述正确|表述错误|说法|不是|属|均)')

def norm(s):
    return re.sub(r'\s+', '', s or '')

def check_letter_consistency(q):
    """选择题：解析中明示的选项字母若存在，须与答案一致。"""
    t = q.get('type')
    if t not in ('single_choice', 'multi_choice'):
        return []
    expl = norm(q.get('explanation', ''))
    opts = q.get('options', [])
    if not opts:
        return []
    ans = q.get('answer')
    # answer 可能是文本（v4）或 key 列表
    if isinstance(ans, list):
        ans_texts = set(ans)
    else:
        ans_texts = {ans}
    # 正确字母
    correct_keys = {o['key'] for o in opts if o.get('text') in ans_texts}
    if not correct_keys:
        return []
    # 解析中明示的字母
    cited = set()
    for m in EXPL_LETTER.finditer(expl):
        cited.add(m.group(2))
    errs = []
    for c in cited:
        if c not in correct_keys:
            errs.append(f"解析引用{c}但正确项为{''.join(sorted(correct_keys))}")
    return errs

def scan_zip(path):
    z = zipfile.ZipFile(path)
    names = z.namelist()
    qs = []
    for n in names:
        if n.startswith('questions/') and n.endswith('.json'):
            qs.extend(json.loads(z.read(n)))
    return qs

total_p0 = total_p1 = 0
print('%-42s %6s %6s %6s' % ('bank', '题量', 'P0', 'P1/P2'))
for f in sorted(os.listdir(ASSETS)):
    if not f.endswith('.zip'):
        continue
    qs = scan_zip(os.path.join(ASSETS, f))
    p0 = []
    p1 = []
    for q in qs:
        p0.extend((q['id'], e) for e in check_letter_consistency(q))
        en = norm(q.get('explanation', ''))
        if BLACK.search(en):
            p1.append(q['id'])
    print('%-42s %6d %6d %6d' % (f, len(qs), len(p0), len(p1)))
    for pid, e in p0[:10]:
        print('   P0:', pid, e)
    for pid in p1[:10]:
        print('   P1:', pid)
    total_p0 += len(p0)
    total_p1 += len(p1)
print('合计 P0:', total_p0, ' P1/P2:', total_p1)
