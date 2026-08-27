# -*- coding: utf-8 -*-
"""把 _parsed_wenxue.json 的 93 道真题论述题转换为题库格式（chapter=论述题专题）。

- 按内容把 93 道题归类到 古代文学史 / 现代文学史 / 当代文学史
- 清洗题干：去掉行首编号、末尾 "[学校XXXX年研]"、"相关试题：..." 冗余
- 生成符合 v3 包格式的 question dict（type=short_answer, answerFormat=论述）
- 输出 staging json 供人工核对；--write 时写入 tools/seed-builder/out/lunshu/<bank>.json
"""
import json
import re
import sys

SRC = 'tools/seed-builder/out/zhenti/_parsed_wenxue.json'
OUT_DIR = 'tools/seed-builder/out/lunshu'

# 93 道题的下标 → 归属题库（其余为古代文学史）
BANK_OF = {
    'bank-zhongguo-xiandai-wenxue': {0, 9, 13},
    'bank-zhongguo-dangdai-wenxue': {1, 3, 6},
}
ANCIENT = 'bank-zhongguo-gudai-wenxue'

ANSWER_FORMAT = '论述题：分条作答，先摆论点再给论据，结合作品/原文例证论证充分。'

# 年份归属标记（用于 difficulty 提示 / explanation 备注）
def _clean_stem(parts):
    """parts: list[str]；返回 (stem, school_tag)。"""
    raw = '\n'.join(str(p) for p in parts)
    raw = raw.strip()
    # 去掉行首编号 "1." "2." 等
    m = re.match(r'^\s*\d+[\.、．]\s*', raw)
    if m:
        raw = raw[m.end():]
    # 截断末尾 "相关试题：..."（含"相关试题"及其后全部）
    idx = raw.find('相关试题')
    if idx != -1:
        raw = raw[:idx].rstrip('。；;，, \n')
    # 去掉题干任意位置出现的「（学校XXXX年研）」/「[学校XXXX年研]」标记
    schools = re.findall(r'[\[【（(][^\]】）)]{1,40}?研[\]】）)]', raw)
    school = '；'.join(s.strip('[]【】（）()') for s in schools)
    raw = re.sub(r'[\[【（(][^\]】）)]{1,40}?研[\]】）)]', '', raw)
    raw = raw.rstrip('。；;，, \n')
    # 仅给出原文/诗而无设问的题，补一个统一设问
    if not re.search(r'[试论析述评]|比较|谈谈|结合|如何|为什么|怎样|关系|意义|影响|成就|特点|特征|内容|形象|贡献|发展|作用|评价|分析', raw):
        raw += '。请结合这首诗分析其思想内容与艺术特色，并展开论述。'
    raw = re.sub(r'\s*\n\s*', '\n', raw).strip()
    return raw, school


def convert():
    data = json.load(open(SRC, encoding='utf-8'))
    qs = data if isinstance(data, list) else data.get('questions', [])
    lun = [q for q in qs if q.get('type') == '论述题']
    if len(lun) != 93:
        print(f'警告：论述题数量 {len(lun)} != 93')

    banks = {ANCIENT: [], 'bank-zhongguo-xiandai-wenxue': [], 'bank-zhongguo-dangdai-wenxue': []}
    for i, q in enumerate(lun):
        bank = ANCIENT
        for b, idxs in BANK_OF.items():
            if i in idxs:
                bank = b
                break
        stem, school = _clean_stem(q.get('stem', []))
        answer = re.sub(r'\n{3,}', '\n\n', str(q.get('answer', '')).strip())
        # tags：取题干前若干主题词（简单启发式：保留 2-4 个词）
        words = re.findall(r'[\u4e00-\u9fa5]{2,6}', stem)
        seen, tags = set(), []
        for w in words:
            if w in seen or w in ('相关试题', '试述', '试论', '简述', '分析', '结合作品'):
                continue
            seen.add(w)
            tags.append(w)
            if len(tags) >= 3:
                break
        tags = tags or ['论述题']
        note = f'（真题·{school}）' if school else '（真题）'
        newq = {
            'id': f'{bank}:lun_{i+1:03d}',
            'type': 'short_answer',
            'stem': stem,
            'answer': answer,
            'explanation': note + ' 参考答案为历年考研真题标准作答，供对照自评。',
            'answerFormat': ANSWER_FORMAT,
            'chapter': '论述题专题',
            'tags': tags,
            'difficulty': 'medium',
            'source': {
                'docPath': f'试题题库/论述题/{"·".join(tags[:2])}',
                'blockId': f'line_{q.get("line")}',
            },
        }
        banks[bank].append(newq)

    import os
    os.makedirs(OUT_DIR, exist_ok=True)
    for bank, items in banks.items():
        with open(os.path.join(OUT_DIR, bank + '.json'), 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=1)
        print(f'{bank}: {len(items)} 道')
    # 打印每科前 2 条题干核对
    for bank, items in banks.items():
        print(f'\n== {bank} ({len(items)}) 示例:')
        for x in items[:2]:
            print('  题干:', x['stem'][:70].replace('\n', ' / '))
            print('  答案前60:', x['answer'][:60].replace('\n', ' '))


if __name__ == '__main__':
    convert()
