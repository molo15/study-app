# -*- coding: utf-8 -*-
"""修复现代汉语质量警告：删损坏题、清括号选项、加长短解析"""
import io, sys, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json'
KP = json.load(open(P, encoding='utf-8'))

def norm(s): return re.sub(r'[（）()。，、；：""“”\'  ]', '', s)

# 1) 删除损坏题（“只要”“即使”复句题）
removed = 0
for k in KP['knowledge']:
    keep = []
    for q in k.get('basicQuestions', []):
        if q['stem'].startswith('“只要') or q['stem'].startswith('“即使'):
            removed += 1
            continue
        keep.append(q)
    k['basicQuestions'] = keep
print('删除损坏题', removed)

# 2) 清理选项中的括号（如“-i（前）”）
for k in KP['knowledge']:
    for q in k.get('basicQuestions', []):
        if q['type'] == 'choice':
            q['options'] = [re.sub(r'[（(][^（）()]*[）)]', '', o).strip() for o in q['options']]

# 3) 加长短解析
EXT = {
    '语素是____的结合体。': '语素是语音和意义结合的最小语言单位，是构词的材料，如“人”“蝴蝶”。',
    '词的感情色彩分为褒义、贬义和____。': '词的感情色彩分褒义、贬义、中性三类，如“英雄”褒义、“叛徒”贬义、“桌子”中性。',
    '“台上坐着主席团”是____句。': '“台上坐着主席团”表存在，是存现句。存现句表示人或事物的存在、出现或消失，如“教室里坐着学生”“天上飘来一朵云”。',
    '普通话共有____个辅音声母。': '普通话有21个辅音声母（b p m f d t n l g k h j q x zh ch sh r z c s），另有零声母。',
    '标示书名、篇名、报刊名的标号是（　）': '书名号《》标示书名、篇名、报刊名、文件名等，如《现代汉语》。',
}
for k in KP['knowledge']:
    for q in k.get('basicQuestions', []):
        if q['stem'] in EXT:
            q['explanation'] = EXT[q['stem']]

json.dump(KP, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('修复完成')
