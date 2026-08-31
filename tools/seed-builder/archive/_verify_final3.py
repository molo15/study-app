# -*- coding: utf-8 -*-
"""修正扫描脚本：避免 None in 字符串崩溃；改进字母断言判断。"""
import io, sys, json, os, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ASSETS = r'D:\study_app\app\assets\banks'
BLACK = re.compile(r'素材块|素材n|正文块|对应素材标题|覆盖缺口|本题答案为|存量题未覆盖|本题属[于]?.{0,15}常考|即可应对同类题目|掌握其概念|依据-[0-9a-z]+、|（基础）|（变式）|（拓展）|（提升）|（综合）|（识记）|（理解）$|^解析[:：]')

# 更精准：只匹配解析中「明确结论」的字母，不匹配"A. 胆怯"列举
# 正面：选X / 故选X / 答案X / 应选X / 正确选项为X
POS = re.compile(r'(故选|答案(?:为|是)?|正确选项(?:为|是)?|应选|据此选|选)([ABCDEF])(?=$|[，。；、:： ]|项|正确|对|。|！)')
# 负面：X项不选 / 故X不选 / X错误 / X不对
NEG = re.compile(r'([ABCDEF])项?(?:不选|排除|错误|不对|有误|不符合|不属)|(?:故|即|因此)([ABCDEF])项?不选')

def norm(s):
    return re.sub(r'\s+', '', s or '')

def scan(path):
    z = zipfile.ZipFile(path)
    qs = []
    for n in z.namelist():
        if n.startswith('questions/') and n.endswith('.json'):
            qs.extend(json.loads(z.read(n)))
    p0, p1 = [], []
    for q in qs:
        t = q.get('type')
        expl = q.get('explanation', '')
        en = norm(expl)
        if BLACK.search(en):
            p1.append(q['id'])
        if t not in ('single_choice', 'multi_choice'):
            continue
        opts = q.get('options', [])
        ans = q.get('answer')
        if isinstance(ans, list):
            ans_texts = set(ans)
        else:
            ans_texts = {ans} if ans else set()
        if not opts:
            continue
        correct_keys = {o['key'] for o in opts if o.get('text') in ans_texts}
        if not correct_keys:
            continue
        for m in POS.finditer(en):
            cited = m.group(2)
            if cited not in correct_keys:
                p0.append((q['id'], f"正面断言{cited}但正确={''.join(sorted(correct_keys))}", expl[:80]))
        for m in NEG.finditer(en):
            cited = m.group(1) or m.group(2)
            if cited in correct_keys:
                p0.append((q['id'], f"负面断言{cited}不选但它是正确项", expl[:80]))
    return qs, p0, p1

tot_p0 = tot_p1 = 0
for f in sorted(os.listdir(ASSETS)):
    if not (f.endswith('.zip') and 'v0.14.0' in f):
        continue
    qs, p0, p1 = scan(os.path.join(ASSETS, f))
    print('%-42s 题量%5d  P0=%d  P1=%d' % (f, len(qs), len(p0), len(p1)))
    for pid, msg, expl in p0[:15]:
        print('   P0!', pid, '|', msg, '|', expl)
    for pid in p1[:15]:
        print('   P1!', pid)
    tot_p0 += len(p0); tot_p1 += len(p1)
print('TOTAL P0:', tot_p0, ' P1:', tot_p1)
