# -*- coding: utf-8 -*-
import io, sys, json, os, random, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 加载 pack_v013 模块
spec = importlib.util.spec_from_file_location('pv', r'D:\study_app\tools\seed-builder\pipeline\pack_v013.py')
pv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pv)

# 构造 z_000109 测试
q = {
    'type': 'single_choice',
    'options': [
        {'key': 'A', 'text': '胆怯'},
        {'key': 'B', 'text': '笔直'},
        {'key': 'C', 'text': '报考'},
        {'key': 'D', 'text': '悦耳'},
    ],
    'answer': 'A',
    'explanation': '主谓式即名词/代词+动词/形容词。\n- A. 胆怯（胆+怯，主谓）——是\n- B. 笔直（偏正）——否\n- C. 报考（连动）——否\n- D. 悦耳（动宾）——否\n- 故选 A',
}
rng = random.Random('test')
pv.shuffle_options(q, rng)
pv.encode_answer_v4(q)
print('answer:', q['answer'])
print('options:', [(o['key'], o['text']) for o in q['options']])
print('expl:', q['explanation'][-40:])
