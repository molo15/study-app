# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open(r'D:\study_app\tools\seed-builder\out\knowledge\古代汉语.knowledge.json', encoding='utf-8'))
targets = ["k_gdyy_wenzi_xia_08", "k_gdyy_cihui_02", "k_gdyy_cihui_05", "k_gdyy_yufa_shang_04",
           "k_gdyy_yufa_shang_05", "k_gdyy_yufa_xia_03", "k_gdyy_yufa_xia_04", "k_gdyy_yufa_xia_06",
           "k_gdyy_yufa_xia_08", "k_gdyy_yufa_xia_08"]
seen = set()
for k in d['knowledge']:
    for q in k.get('basicQuestions', []):
        # 通过知识点id定位（题目没有独立id，用知识点id+序号）
        pass
for k in d['knowledge']:
    if k['id'] in targets:
        print('###', k['id'], k['name'])
        for q in k.get('basicQuestions', []):
            if q['type'] == 'choice' and q['answer'] not in q.get('options', []):
                print('  STEM:', q['stem'])
                print('  ANSWER:', q['answer'])
                print('  OPTIONS:', q['options'])
                print()
