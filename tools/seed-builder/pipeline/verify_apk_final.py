# -*- coding: utf-8 -*-
"""APK 内最终全量扫描（P0 字母一致性 + P1 黑名单）。"""
import io, sys, json, os, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

APK = r'D:\study_app\app\build\app\outputs\flutter-apk\app-release.apk'
z = zipfile.ZipFile(APK)
BLACK = re.compile(r'素材块|素材n|正文块|对应素材标题|覆盖缺口|本题答案为|存量题未覆盖|本题属[于]?.{0,15}常考|即可应对同类题目|掌握其概念|依据-[0-9a-z]+、|（基础）|（变式）|（拓展）|（提升）|（综合）|（识记）|（理解）$|^解析[:：]')
POS = re.compile(r'(故选|答案(?:为|是)?|正确选项(?:为|是)?|应选|据此选|选)\s*([ABCDEF])(?=$|[，。；、:：\s]|项|正确|对|。|！)')
SEQ_NEG = re.compile(r'故([ABCDEF](?:、[ABCDEF]){0,5})(?:项|均)?(?:不选|排除|错误|不对|有误|不符合|不属)')

def norm(s):
    return re.sub(r'\s+', '', s or '')

def correct_keys(q):
    opts = q.get('options', [])
    ans = q.get('answer')
    if isinstance(ans, list):
        at = set(ans)
        return {o['key'] for o in opts if o['text'] in at}
    return {o['key'] for o in opts if o['text'] == ans} if ans else set()

banks = sorted(n for n in z.namelist() if 'assets/flutter_assets/assets/banks/' in n and n.endswith('.zip'))
tot_p0 = tot_p1 = grand = 0
for bn in banks:
    zz = zipfile.ZipFile(io.BytesIO(z.read(bn)))
    qs = []
    for n in zz.namelist():
        if n.startswith('questions/') and n.endswith('.json'):
            qs.extend(json.loads(zz.read(n)))
    grand += len(qs)
    p0, p1 = [], []
    for q in qs:
        en = norm(q.get('explanation', ''))
        if BLACK.search(en):
            p1.append(q['id'])
        if q.get('type') not in ('single_choice', 'multi_choice'):
            continue
        ok = correct_keys(q)
        if not ok:
            continue
        for m in POS.finditer(en):
            if m.group(2) not in ok:
                p0.append((q['id'], f"正面断言{m.group(2)}但正确={''.join(sorted(ok))}"))
        for m in SEQ_NEG.finditer(en):
            cited = set(m.group(1).split('、'))
            if cited & ok:
                p0.append((q['id'], f"整串排除含正确项"))
    print('%-40s 题量%5d P0=%d P1=%d' % (os.path.basename(bn), len(qs), len(p0), len(p1)))
    for pid, msg in p0[:12]:
        print('   P0!', pid, msg)
    for pid in p1[:12]:
        print('   P1!', pid)
    tot_p0 += len(p0); tot_p1 += len(p1)
print('APK 内总计: 题量', grand, 'P0:', tot_p0, 'P1:', tot_p1)
