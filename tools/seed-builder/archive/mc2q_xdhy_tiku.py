# -*- coding: utf-8 -*-
"""现代汉语试题库 → 挂载到知识库：单选映射挂载 + 语音单空填空"""
import io, sys, re, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SPLIT = r'D:\study_app\tools\seed-builder\out\xiandai-tiku-split'
KP = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json', encoding='utf-8'))

def norm(s):
    return re.sub(r'[（）()。，、；：""“”\'  ]', '', s)

def load(path):
    with open(path, encoding='utf-8') as f:
        return f.read()

def find_answer_start(text):
    pos = [i for kw in ['答案略', '答案参见教材', '（答案略'] if (i := text.find(kw)) >= 0]
    return min(pos) if pos else -1

def split_q(block):
    items = []
    for p in re.split(r'(?=\n\s*\d{1,3}[\.．、])', block):
        m = re.match(r'\s*(\d{1,3})[\.．、]\s*(.*)', p, re.S)
        if m:
            items.append({'num': int(m.group(1)), 'body': m.group(2)})
    return items

def parse_options(body):
    opts = {}
    for letter, txt in re.findall(r'([A-E])\s*[\.、．]?\s*([^\nA-E]{1,40})', body):
        if letter not in opts:
            opts[letter] = re.sub(r'^[\.、．、\s]+|[、，。；;]+$', '', txt).strip()
    stem = body
    m = re.search(r'\s*[A-E]\s*[\.、．]?\s*\S', body)
    if m:
        stem = body[:m.start()]
    stem = re.sub(r'[\s　]+', ' ', stem).strip(' 　')
    stem = re.sub(r'[_—＿]+$', '', stem).strip()
    return stem, opts

def parse_letter_ans(block):
    ans = {}
    for m in re.finditer(r'(\d{1,3})\s*[\.、．]\s*([A-E])', block):
        ans.setdefault(int(m.group(1)), m.group(2))
    return ans

def parse_num_ans(block):
    ans = {}
    for m in re.finditer(r'(\d{1,3})[\.、．]\s*(.+?)(?=\n\s*\d{1,3}[\.、．]|\n\s*[一二三四五六]|$)', block, re.S):
        ans[int(m.group(1))] = m.group(2).strip()
    return ans

# ---------- 各章单选题干 ----------
def parse_choices(fn):
    text = load(os.path.join(SPLIT, fn + '.txt'))
    apos = find_answer_start(text)
    q_part = text[:apos] if apos > 0 else text
    a_part = text[apos:] if apos > 0 else ''
    cm = list(re.finditer(r'单项选择题', q_part))
    if not cm:
        return []
    seg_q = q_part[cm[0].start():]
    seg_q = re.split(r'\n\s*[一二三四五六]、', seg_q)[0]
    items = split_q(seg_q)
    am = re.search(r'单项选择题\s*[（(]?[^\n]*\n?\s*(.*)', a_part, re.S)
    if not am:
        # 修辞：答案区"三、"无标题
        am = re.search(r'\n\s*三、\s*\n?(.*)', a_part, re.S) if fn == '修辞' else None
    ans_map = parse_letter_ans(am.group(1)) if am else {}
    out = []
    for it in items:
        if it['num'] in ans_map:
            stem, opts = parse_options(it['body'])
            if len(opts) >= 4 and stem:
                out.append({'stem': stem, 'options': [opts.get(l, '') for l in 'ABCD'],
                            'ans': ans_map[it['num']]})
    return out

# ---------- 语音单空填空 ----------
def parse_voice_blanks():
    text = load(os.path.join(SPLIT, '语音.txt'))
    apos = find_answer_start(text)
    q_part = text[:apos]; a_part = text[apos:]
    bm = list(re.finditer(r'填空题', q_part))
    seg_b = q_part[bm[0].start():]
    seg_b = re.split(r'\n\s*[一二三四五六]、', seg_b)[0]
    items = split_q(seg_b)
    bm2 = re.search(r'填空题\s*\n(.*)', a_part, re.S)
    bans = parse_num_ans(bm2.group(1)) if bm2 else {}
    out = []
    for it in items:
        if it['num'] in bans:
            stem = re.sub(r'[\s　]+', ' ', it['body']).strip()
            ans = bans[it['num']]
            # 只取空数<=2且答案简短
            n_blank = len(re.findall(r'[_＿]+', stem))
            if n_blank <= 2 and len(ans) <= 16 and '\n' not in ans:
                out.append({'stem': stem, 'ans': ans})
    return out

# ---------- 知识点映射 ----------
# 每章：[(关键词正则, 知识点名子串)]
MAP = {
    '语音': [
        (r'声调', '声调'), (r'调值|调类', '声调'),
        (r'音素', '音素'), (r'音节', '音节结构'),
        (r'元音|辅音', '元音与辅音'),
        (r'声母', '声母'), (r'发音部位', '发音部位'), (r'发音方法', '发音方法'),
        (r'韵母|韵头|韵腹|韵尾|韵身', '韵母'), (r'单韵母', '单韵母'), (r'复韵母', '复韵母'), (r'鼻韵母', '鼻韵母'),
        (r'四呼|开口呼|合口呼|齐齿呼|撮口呼', '四呼'),
        (r'拼写|拼音|声调符号|隔音', '拼写规则'),
        (r'轻声', '轻声'), (r'儿化', '儿化'), (r'变调|“一”|“不”', '变调'),
        (r'音高|音强|音长|音色', '语音四要素'),
        (r'发音|语音', '语音的性质'),
        (r'汉语拼音方案', '《汉语拼音方案》'),
        (r'元音|辅音', '元音与辅音'),
    ],
    '语法': [
        (r'这一术语', '语法的性质'),
        (r'能用数量短语|不能用“不”修饰|表示动作的量|能带宾语的是', '实词'),
        (r'“国营|“不、没|“很、挺|“我、你|“着、了、过|“哎哟|“上来|这三个词都是', '词类的划分'),
        (r'“他在黑板上写字”的“在”', '虚词'),
        (r'句子中的（ ）是', '句类'),
        (r'今天星期日|明天国庆节|今天冷极了', '单句与句型'),
        (r'彻底解决|去打电话|明代医药家|你的到来', '短语'),
        (r'“小张写了|“跑跑|“主张|“问他一件事|“累得要命|“我认识他|“这条鱼', '句子成分'),
        (r'推开门|介绍我去见|教室里坐着|老张把他|你的想法，我认为|山上都是苹果树', '特殊句式'),
        (r'只要|即使|越学越爱学', '复句'),
        (r'为什么没有来|我去还是不去', '句类'),
    ],
    '修辞': [
        (r'比喻|明喻|暗喻|借喻|博喻', '比喻'),
        (r'借代', '借代'), (r'比拟|拟人|拟物', '比拟'), (r'夸张', '夸张'),
        (r'对偶|对比', '对偶与对比'), (r'排比', '排比'), (r'反复|顶真', '反复与顶真'),
        (r'反问|设问', '反问与设问'), (r'双关', '双关'), (r'通感', '通感'),
        (r'修辞|语境', '修辞与语境'),
    ],
}

def mount(chapter, q, match_kw):
    kps = [k for k in KP['knowledge'] if k['chapter'] == chapter]
    best = None
    for k in kps:
        if match_kw and match_kw in k['name']:
            best = k
            break
    if best is None:
        for k in kps:
            if '真题补充' in k['name']:
                best = k
                break
    if best is None:
        best = {"id": "k_zhen_xdhy_" + chapter, "name": chapter + "（真题补充）",
                "parent": "root", "chapter": chapter, "hot": False,
                "summary": "考研真题补充知识点，覆盖该章重要考点。", "basicQuestions": []}
        KP['knowledge'].append(best)
    for e in best.get('basicQuestions', []):
        if norm(e['stem']) == norm(q['stem']):
            return False
    if len(best.get('basicQuestions', [])) >= 6:
        return False
    best['basicQuestions'].append(q)
    return True

def match_kp(chapter, stem):
    for pat, name in MAP[chapter]:
        if re.search(pat, stem):
            return name
    return None

def to_choice(q):
    al = q['ans'].upper().replace('Ａ', 'A').replace('Ｂ', 'B').replace('Ｃ', 'C').replace('Ｄ', 'D')
    idx = 'ABCD'.index(al)
    return {'stem': q['stem'], 'type': 'choice', 'answer': q['options'][idx],
            'explanation': '', 'options': q['options']}

def to_blank(q):
    return {'stem': q['stem'], 'type': 'blank', 'answer': q['ans'],
            'explanation': '', 'options': []}

# ---------- 执行 ----------
stats = {}
total = 0
for fn, ch in [('语音', '语音'), ('语法', '语法'), ('修辞', '修辞')]:
    qs = parse_choices(fn)
    n_ok = 0
    for q in qs:
        if q['ans'].upper().replace('Ａ', 'A') not in 'ABCD':
            continue
        kw = match_kp(ch, q['stem'])
        if not kw:
            continue
        ok = mount(ch, to_choice(q), kw)
        n_ok += ok
    stats[fn + '单选'] = (len(qs), n_ok)
    total += n_ok

blanks = parse_voice_blanks()
n_b = 0
for q in blanks:
    kw = match_kp('语音', q['stem'])
    if not kw:
        continue
    ok = mount('语音', to_blank(q), kw)
    n_b += ok
stats['语音填空'] = (len(blanks), n_b)
total += n_b

json.dump(KP, open(r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in stats.items():
    print(f'{k}: 解析{ v[0]} 挂载{v[1]}')
print(f'合计挂载 {total}')
