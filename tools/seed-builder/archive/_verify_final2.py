# -*- coding: utf-8 -*-
"""仅扫 v0.14.0 最终 zip；P0 字母一致性做更精确判断：
解析中明示字母，若该字母对应选项文本是「错误项」则解析说"不选/排除"属正常；
只有「解析断言该字母为正确答案却对应错误项」或「解析断言该字母为错误却对应正确项」才算错配。
"""
import io, sys, json, os, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ASSETS = r'D:\study_app\app\assets\banks'
BLACK = re.compile(r'素材块|素材n|正文块|对应素材标题|覆盖缺口|本题答案为|存量题未覆盖|本题属[于]?.{0,15}常考|即可应对同类题目|掌握其概念|依据-[0-9a-z]+、|（基础）|（变式）|（拓展）|（提升）|（综合）|（识记）|（理解）$|^解析[:：]')

# 解析中的字母断言模式：分「正面断言正确」与「反面断言不选」两类
POS = re.compile(r'(故选|答案(?:为|是)?|正确选项(?:为|是)?|应选|据此选|选)([ABCDEF])(?=$|[，。；、:： ]|项|正确|对|。)|故([ABCDEF])正确|([ABCDEF])项正确')
NEG = re.compile(r'((?:故|即|因此|所以)?)([ABCDEF])项?(?:不选|错误|不对|有误|不符合|不属|排除)')
# 简版：列出所有引用字母供人工复核

def norm(s):
    return re.sub(r'\s+', '', s or '')

def scan(path):
    z = zipfile.ZipFile(path)
    qs = []
    for n in z.namelist():
        if n.startswith('questions/') and n.endswith('.json'):
            qs.extend(json.loads(z.read(n)))
    p0 = []
    p1 = []
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
        # 正面断言：解析说"选X/答案X/正确" 的字母必须∈正确项
        for m in POS.finditer(en):
            cited = next((g for g in m.groups() if g in 'ABCDEF'), None)
            if cited and cited not in correct_keys:
                p0.append((q['id'], f"正面断言{cited}但正确={''.join(sorted(correct_keys))}", expl[:70]))
        # 反面断言：解析说"X项不选/错误" 的字母必须∈错误项
        for m in NEG.finditer(en):
            cited = m.group(2)
            if cited in correct_keys:
                p0.append((q['id'], f"反面断言{cited}不选但它是正确项", expl[:70]))
    return qs, p0, p1

tot_p0 = tot_p1 = 0
for f in sorted(os.listdir(ASSETS)):
    if not (f.endswith('.zip') and 'v0.14.0' in f):
        continue
    qs, p0, p1 = scan(os.path.join(ASSETS, f))
    print('%-42s 题量%5d  P0=%d  P1=%d' % (f, len(qs), len(p0), len(p1)))
    for pid, msg, expl in p0[:12]:
        print('   P0!', pid, '|', msg, '|', expl)
    for pid in p1[:12]:
        print('   P1!', pid)
    tot_p0 += len(p0); tot_p1 += len(p1)
print('TOTAL P0:', tot_p0, ' P1:', tot_p1)
