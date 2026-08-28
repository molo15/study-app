# -*- coding: utf-8 -*-
"""挂载文字/词汇/语法填空 → 现代汉语知识库"""
import io, sys, re, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SPLIT = r'D:\study_app\tools\seed-builder\out\xiandai-tiku-split'
P = r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json'
KP = json.load(open(P, encoding='utf-8'))

def norm(s): return re.sub(r'[（）()。，、；：""“”\'  ]', '', s)
def load(path):
    with open(path, encoding='utf-8') as f: return f.read()
def find_answer_start(text):
    pos = [i for kw in ['答案略', '答案参见教材', '（答案略'] if (i := text.find(kw)) >= 0]
    return min(pos) if pos else -1
def split_q(block):
    items = []
    for p in re.split(r'(?=\n\s*\d{1,3}[\.．、])', block):
        m = re.match(r'\s*(\d{1,3})[\.．、]\s*(.*)', p, re.S)
        if m: items.append({'num': int(m.group(1)), 'body': m.group(2)})
    return items
def parse_num_ans(block):
    ans = {}
    for m in re.finditer(r'(\d{1,3})[\.．、]\s*(.+?)(?=\n\s*\d{1,3}[\.．、]|\n\s*[一二三四五六]|$)', block, re.S):
        ans[int(m.group(1))] = m.group(2).strip()
    return ans

MAP = {
    '文字': [
        (r'甲骨文|金文|篆|隶|楷|草|行|形体|演变', '汉字的形体演变'),
        (r'象形|指事|会意|形声|转注|假借|六书', '六书'),
        (r'形声', '形声字'),
        (r'独体|合体', '独体字与合体字'),
        (r'笔画|笔顺', '笔画与笔顺'),
        (r'偏旁|部首', '偏旁与部首'),
        (r'简化|繁体', '简化字与繁体字'),
        (r'异体|异读', '异体字与异读词'),
        (r'定量|定形|定音|定序|标准化', '汉字标准化（四定）'),
        (r'文字|汉字|性质', '文字的性质与汉字的性质'),
    ],
    '词汇': [
        (r'语素', '语素'),
        (r'单纯词|联绵|双声|叠韵', '单纯词与合成词'),
        (r'双声|叠韵', '联绵词'),
        (r'合成词|并列|偏正|动宾|主谓|补充', '合成词的结构'),
        (r'词根|词缀|前缀|后缀', '词根与词缀'),
        (r'理性义|色彩|感情|语体|形象', '词义（理性义与色彩义）'),
        (r'义项|义素|语义场', '义项、义素与语义场'),
        (r'同义|反义', '同义词与反义词'),
        (r'基本词汇|一般词汇', '基本词汇与一般词汇'),
        (r'成语|惯用语|歇后语|谚语|熟语', '熟语'),
        (r'扩大|缩小|转移|演变', '词义的演变'),
        (r'词', '词'),
    ],
    '语法': [
        (r'复句|分句|关联', '复句'),
        (r'语素', '语法的性质'),
        (r'词类|实词|虚词|名词|动词|形容词', '词类的划分'),
        (r'实词', '实词'),
        (r'虚词|介词|连词|助词|语气', '虚词'),
        (r'短语|词组|结构', '短语'),
        (r'主语|谓语|宾语|定语|状语|补语', '句子成分'),
        (r'句型|主谓|非主谓|连动|兼语', '特殊句式'),
        (r'句类|疑问|祈使|感叹|陈述', '句类'),
        (r'单句|句子', '单句与句型'),
    ],
}

def match_kp(ch, stem):
    for pat, name in MAP[ch]:
        if re.search(pat, stem): return name
    return None

def mount(ch, q, kw):
    kps = [k for k in KP['knowledge'] if k['chapter'] == ch]
    best = None
    for k in kps:
        if kw and kw in k['name']:
            best = k; break
    if best is None:
        for k in kps:
            if '真题补充' in k['name']:
                best = k; break
    if best is None:
        best = {"id": "k_zhen_xdhy_" + ch, "name": ch + "（真题补充）", "parent": "root",
                "chapter": ch, "hot": False, "summary": "考研真题补充知识点。", "basicQuestions": []}
        KP['knowledge'].append(best)
    for e in best.get('basicQuestions', []):
        if norm(e['stem']) == norm(q['stem']): return False
    if len(best.get('basicQuestions', [])) >= 6: return False
    best['basicQuestions'].append(q); return True

total = 0
for fn, ch in [('文字', '文字'), ('词汇', '词汇'), ('语法', '语法')]:
    text = load(os.path.join(SPLIT, fn + '.txt'))
    apos = find_answer_start(text)
    q_part = text[:apos]; a_part = text[apos:]
    bm = list(re.finditer(r'填空题', q_part))
    seg_b = q_part[bm[0].start():]
    seg_b = re.split(r'\n\s*[一二三四五六]、', seg_b)[0]
    items = split_q(seg_b)
    bm2 = re.search(r'填空题\s*\n(.*)', a_part, re.S)
    bans = parse_num_ans(bm2.group(1)) if bm2 else {}
    n = 0
    for it in items:
        if it['num'] not in bans: continue
        stem = re.sub(r'[\s　]+', ' ', it['body']).strip()
        ans = bans[it['num']]
        if len(re.findall(r'[_＿]+', stem)) > 2 or len(ans) > 18 or '\n' in ans: continue
        kw = match_kp(ch, stem)
        if not kw: continue
        q = {'stem': stem, 'type': 'blank', 'answer': ans, 'explanation': '', 'options': []}
        if mount(ch, q, kw): n += 1
    total += n
    print(f'{fn}填空 挂载{n}')

json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'合计 {total}')
