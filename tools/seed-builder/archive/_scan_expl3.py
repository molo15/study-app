# -*- coding: utf-8 -*-
import io, sys, json, zipfile, glob, os, re
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

banks = glob.glob(r'D:\study_app\app\assets\banks\bank-*.zip')

# 各类问题按科目统计
by_bank = defaultdict(Counter)
sample_store = defaultdict(list)

def add(bank, cat, q, snippet):
    by_bank[bank][cat] += 1
    if len(sample_store[cat]) < 20:
        sample_store[cat].append((bank, q.get('id'), (q.get('stem') or '')[:24], snippet))

tot = 0
for b in banks:
    bank = os.path.basename(b).replace('-v0.14.0.zip', '')
    z = zipfile.ZipFile(b)
    for n in z.namelist():
        if not n.startswith('questions/'):
            continue
        for q in json.loads(z.read(n)):
            tot += 1
            expl = q.get('explanation') or ''
            e = re.sub(r'\s+', '', expl)
            st = q.get('stem') or ''
            t = q.get('type', '')
            opts = q.get('options') or []
            ans = q.get('answer') or ''
            # 1. 素材块工作残留（无实质解析）
            if '素材块' in e:
                add(bank, 'E素材块残留(无实质解析)', q, e[:70])
            # 2. 纯提示语解析（简答无答案）
            if re.search(r'^(解析[:：]?\s*)?(须答出|本题考查|本题为|答题要点|须从|注意从|可从)', e):
                add(bank, 'B简答解析为提示语', q, e[:70])
            # 3. 出题底稿尾巴
            if '本题属于' in e and '常考' in e:
                add(bank, 'A出题底稿尾巴', q, e[-42:])
            # 4. 等级标注尾巴
            if re.search(r'[（(](基础|变式|拓展|提升|综合|识记|理解)[）)]$', e):
                add(bank, 'C等级标注尾巴', q, e[-20:])
            # 5. 解析冒号前缀
            if re.match(r'^解析[:：]', e):
                add(bank, 'D解析冒号前缀', q, e[:40])
            # 6. 选择题：解析明确指向选项字母 与 answer 冲突（硬错配）
            if t == 'single_choice' and opts:
                # 解析中提到“选X”“X项”“X正确”“X错误”
                letter_hits = re.findall(r'选\s*([ABCDEF])|([ABCDEF])\s*项(?:正确|错误|对|不对|符合|不符合)|([ABCDEF])\s*正确|([ABCDEF])\s*错误', e)
                ans_text = ans if isinstance(ans, str) else ''
                ans_key = None
                for o in opts:
                    if o.get('text') == ans_text:
                        ans_key = o.get('key')
                for m in letter_hits:
                    for lm in m:
                        if not lm: continue
                        if ans_key and lm != ans_key:
                            add(bank, 'F解析明示选项与答案冲突', q, f'答案={ans_key} 解析指向{lm} | {e[:60]}')

print('总题数:', tot)
print()
for bank in sorted(by_bank):
    print(f'== {bank}')
    for cat, cnt in by_bank[bank].most_common():
        print(f'    {cat}: {cnt}')
print()
for cat, samples in sample_store.items():
    print(f'### {cat} 样本:')
    for s in samples:
        print('   ', s[0], '|', s[1], '|', s[2], '|', s[3])
    print()
