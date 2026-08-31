# -*- coding: utf-8 -*-
import io, sys, random, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
spec = importlib.util.spec_from_file_location('pv', r'D:\study_app\tools\seed-builder\pipeline\pack_v013.py')
pv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pv)

# q_000088 场景
q = {
    'type': 'single_choice',
    'options': [
        {'key': 'A', 'text': '以绮丽精致的语言、繁复优美的意象和轻松玄妙的笔调传达内心的复杂情愫'},
        {'key': 'B', 'text': '语言朴实平淡，追求冲淡平和、舒徐自如'},
        {'key': 'C', 'text': '以幽默闲适为笔调，提倡性灵，独抒性灵'},
        {'key': 'D', 'text': '以报告体式迅速反映现实与战况'},
    ],
    'answer': 'A',
    'explanation': '何其芳《画梦录》注重情调和氛围的创造，文字运用上极其精致。周作人散文讲究冲淡平和，林语堂提倡幽默闲适，故B、C、D项不选',
}
rng = random.Random('v4_bank-zhongguo-xiandai-wenxue')
pv.shuffle_options(q, rng)
pv.encode_answer_v4(q)
print('answer:', q['answer'])
for o in q['options']:
    m = ' <==正确' if o['text'] == q['answer'] else ''
    print('   ', o['key'], o['text'][:20], m)
print('expl tail:', q['explanation'][-36:])
