# -*- coding: utf-8 -*-
import io, sys, json, zipfile, glob, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

banks = glob.glob(r'D:\study_app\app\assets\banks\bank-*.zip')

# 扩大检测：解析中出现 "选X / X项 / 故X正确 / X正确 / 故选X / 答案X / X项(有误|不符)" 且 X 与答案 key 不一致
pat = re.compile(r'(?:选|故选|答案|故答案为|正确选项(?:为|是)?|应为|应选)\s*([ABCDEF])\b|([ABCDEF])\s*项(?:正确|错误|对|不对|符合|不符合|有误|表述正确|表述错误)|故\s*([ABCDEF])\s*(?:正确|对)|只有([ABCDEF])\s*(?:正确|对)|应(?:该|当)?选([ABCDEF])')

conflicts = []
for b in banks:
    bank = os.path.basename(b).replace('-v0.14.0.zip', '')
    z = zipfile.ZipFile(b)
    for n in z.namelist():
        if not n.startswith('questions/'):
            continue
        for q in json.loads(z.read(n)):
            if q.get('type') != 'single_choice':
                continue
            expl = re.sub(r'\s+', '', q.get('explanation') or '')
            opts = q.get('options') or []
            ans = q.get('answer') or ''
            ans_key = None
            for o in opts:
                if o.get('text') == ans:
                    ans_key = o.get('key')
            if not ans_key:
                continue
            hits = set()
            for m in pat.finditer(expl):
                for g in m.groups():
                    if g:
                        hits.add(g)
            for h in hits:
                if h != ans_key:
                    conflicts.append((bank, q.get('id'), f'答案key={ans_key}', f'解析指向={h}', (q.get('stem') or '')[:26], expl[:70]))

print('解析明确引用字母与答案不一致:', len(conflicts))
for c in conflicts:
    print('  ', c)
