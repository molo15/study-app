# -*- coding: utf-8 -*-
import io, sys, json, os, random, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

spec = importlib.util.spec_from_file_location('pv', r'D:\study_app\tools\seed-builder\pipeline\pack_v013.py')
pv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pv)

# q_000163 源数据
q = {
    'type': 'multi_choice',
    'options': [
        {'key': 'A', 'text': '强烈的主观抒情性，是重感情、重情绪的“情绪剧”'},
        {'key': 'B', 'text': '富有想象力与传奇性，多写少有的事件'},
        {'key': 'C', 'text': '开放式结构，时空安排比较自由'},
        {'key': 'D', 'text': '诗化的语言，人物独白可当抒情诗朗诵'},
        {'key': 'E', 'text': '严格遵循“三一律”，冲突高度集中'},
    ],
    'answer': ['A', 'B', 'C', 'D'],
    'explanation': '田汉前期浪漫剧具有强烈的主观抒情性、传奇色彩、开放式结构和诗化的语言等特点，他的剧“重象征、重哲理、重（主观）抒情”；其时空安排自由，并不遵循“三一律”，故E不选',
}
# 用 pack 相同 seed
rng = random.Random('v4_bank-zhongguo-xiandai-wenxue')
pv.shuffle_options(q, rng)
pv.encode_answer_v4(q)
print('answer:', q['answer'])
for o in q['options']:
    m = ' <==正确' if o['text'] in q['answer'] else ''
    print('   ', o['key'], o['text'][:20], m)
print('expl tail:', q['explanation'][-30:])
