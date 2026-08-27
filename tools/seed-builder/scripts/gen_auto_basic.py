# -*- coding: utf-8 -*-
"""从笔记素材自动生成基础题（填空/单选为主）。

策略：素材块多为"概念/作品/人物 = 定义"式文本，提取可模板化的知识点：
  1. 含"XX是/即/又称/指"的定性句 → 挖空生成填空（答案是概念词）
  2. 含"第一部/代表作/作者是"的要点句 → 生成填空/单选
生成结果写入 draft/基础-<章>.json，供主会话人工复核后合并。

不追求完美：脚本只作"贵多不贵精"的基础题主力，测试题与人工润色由主会话补充。
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(BASE, 'out', 'v09gudaiwenxue')
MAT = os.path.join(WORK, 'materials')
DRAFT = os.path.join(WORK, 'draft')
os.makedirs(DRAFT, exist_ok=True)

# 概念词库：用于"XX是……"句式的概念抽取（各章通用 + 文学史术语）
CONCEPT_WORDS = [
    '编年体史书', '历史散文', '叙事散文', '说理散文', '第一部', '现存最早', '总集', '诗集',
    '乐府诗', '赋', '骈文', '小说', '传奇', '话本', '杂剧', '南戏', '散曲', '词集',
    '词派', '诗派', '文体', '文论', '批评著作', '诗歌理论', '民歌', '寓言', '神话',
    '山水诗', '田园诗', '咏史诗', '边塞诗', '宫体诗', '玄言诗', '新体诗',
]


def extract_concept_questions(ch, blocks):
    """从素材块提取可模板化知识点，生成填空/单选。"""
    qs = []
    seq = 0
    for block in blocks:
        block_id = block['blockId']
        content = block['content']
        if not content or len(content) < 20:
            continue
        # 1. "XX是……/即……/又称……" 定性句 → 填空
        # 匹配 "《XX》是……" 或 "XX是……" 首部定性
        for m in re.finditer(r'[《“]?([^《》“，。；]{2,8})[》”]?是(?:我国|中国|世界上|现存)?第?[一二三四五六七八九十0-9]*[部种个本]?[^，。；]{2,20}', content):
            concept = m.group(1).strip()
            # 过滤明显不是概念的词
            if len(concept) < 2 or concept in ('它', '其', '他们', '这里', '这'):
                continue
            rest = m.group(0)[m.start(1):]
            # 生成填空：____是……（填概念词）
            qs.append({
                'id': f'tmp-auto:{ch}:b{seq:03d}',
                'type': 'blank',
                'stem': f'＿＿＿是{rest[len(concept):]}',
                'answer': [concept],
                'explanation': f'依据素材：{content[:80]}',
                'chapter': ch,
                'purpose': 'basic',
                'tags': ['基础'],
                'difficulty': 'easy',
                'source': {'blockId': block_id, 'kind': 'exercise'},
            })
            seq += 1
            if seq > 15:  # 每章最多 15 道，控制量
                break
        if seq > 15:
            break
    return qs


def main(ch):
    mat_path = os.path.join(MAT, f'{ch}.txt')
    if not os.path.exists(mat_path):
        print(f'{ch}: 无素材，跳过自动生成')
        return
    # 解析素材 txt：行首 [blockId] 正文
    blocks = []
    cur_id = None
    for line in open(mat_path, encoding='utf-8'):
        line = line.strip()
        m = re.match(r'^\[([0-9]{14}-[a-z0-9]+)\] (.*)', line)
        if m:
            cur_id = m.group(1)
            content = m.group(2)
            if content and not content.startswith('#'):
                blocks.append({'blockId': cur_id, 'content': content})
    print(f'{ch}: {len(blocks)} 素材块')

    qs = extract_concept_questions(ch, blocks)
    out = os.path.join(DRAFT, f'基础-{ch}.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(qs, f, ensure_ascii=False, indent=1)
    print(f'  -> 生成 {len(qs)} 道基础题: {out}')


if __name__ == '__main__':
    for ch in ['先秦文学', '秦汉文学', '魏晋南北朝文学', '隋唐五代文学', '宋代文学', '明代文学']:
        main(ch)
