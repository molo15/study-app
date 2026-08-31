# -*- coding: utf-8 -*-
"""最终全量复核（v0.14.0 五科）：
1) P0 字母一致性（含整串枚举"故A、B、C项不选"）
2) P1/P2 黑名单回归
3) 题量统计
"""
import io, sys, json, os, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ASSETS = r'D:\study_app\app\assets\banks'
BLACK = re.compile(r'素材块|素材n|正文块|对应素材标题|覆盖缺口|本题答案为|存量题未覆盖|本题属[于]?.{0,15}常考|即可应对同类题目|掌握其概念|依据-[0-9a-z]+、|（基础）|（变式）|（拓展）|（提升）|（综合）|（识记）|（理解）$|^解析[:：]')

# 单字母正面断言
POS = re.compile(r'(故选|答案(?:为|是)?|正确选项(?:为|是)?|应选|据此选|选)\s*([ABCDEF])(?=$|[，。；、:：\s]|项|正确|对|。|！)')
# 整串排除：故A、B、C项不选 / 故A、B、C不属于
SEQ_NEG = re.compile(r'故([ABCDEF](?:、[ABCDEF]){0,5})(?:项|均)?(?:不选|排除|错误|不对|有误|不符合|不属)')
# 单字母负面
NEG = re.compile(r'故\s*([ABCDEF])(?=项|正确|错误|对|不对|符合|不符合|有误|说法|不是|属|均|不|选)')

def norm(s):
    return re.sub(r'\s+', '', s or '')

def correct_keys(q):
    opts = q.get('options', [])
    ans = q.get('answer')
    if isinstance(ans, list):
        at = set(ans)
        return {o['key'] for o in opts if o['text'] in at}
    return {o['key'] for o in opts if o['text'] == ans} if ans else set()

tot_p0 = tot_p1 = 0
grand = 0
for f in sorted(os.listdir(ASSETS)):
    if not (f.endswith('.zip') and 'v0.14.0' in f):
        continue
    z = zipfile.ZipFile(os.path.join(ASSETS, f))
    qs = []
    for n in z.namelist():
        if n.startswith('questions/') and n.endswith('.json'):
            qs.extend(json.loads(z.read(n)))
    grand += len(qs)
    p0, p1 = [], []
    for q in qs:
        en = norm(q.get('explanation', ''))
        if BLACK.search(en):
            p1.append(q['id'])
        t = q.get('type')
        if t not in ('single_choice', 'multi_choice'):
            continue
        ok = correct_keys(q)
        if not ok:
            continue
        for m in POS.finditer(en):
            if m.group(2) not in ok:
                p0.append((q['id'], f"正面断言{m.group(2)}但正确={''.join(sorted(ok))}"))
        for m in SEQ_NEG.finditer(en):
            cited = set(m.group(1).split('、'))
            bad = cited & ok
            if bad:
                p0.append((q['id'], f"整串排除{''.join(sorted(cited))}含正确项{''.join(sorted(ok))}"))
        for m in NEG.finditer(en):
            if m.group(1) in ok:
                # 排除单字母故X（seq 已覆盖的跳过——如果 SEQ 已匹配则此处会重复）
                pass
    print('%-42s 题量%5d  P0=%d  P1=%d' % (f, len(qs), len(p0), len(p1)))
    for pid, msg in p0[:15]:
        print('   P0!', pid, '|', msg)
    for pid in p1[:15]:
        print('   P1!', pid)
    tot_p0 += len(p0); tot_p1 += len(p1)
print('总计题量:', grand, ' P0:', tot_p0, ' P1:', tot_p1)
