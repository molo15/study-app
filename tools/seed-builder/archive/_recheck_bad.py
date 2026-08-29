# -*- coding: utf-8 -*-
import json, importlib.util, random, os
spec = importlib.util.spec_from_file_location('p', 'pack_v012.py')
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
for bank, (name, cn, rel) in p.BANKS.items():
    know = json.load(open(os.path.join(p.BASE, f'out/knowledge/{cn}.knowledge.json'), encoding='utf-8'))['knowledge']
    know_ids = {k['id'] for k in know}; kp_by_id = {k['id']: k for k in know}
    qs = json.load(open(os.path.join(p.BASE, rel), encoding='utf-8'))
    for q in qs:
        q['id'] = p.norm_id(bank, q['id']); q['chapter'] = p.norm_chapter(bank, q['chapter'])
    basic = [q for q in qs if q.get('purpose') == 'basic' and q.get('knowledgeId')]
    rep = {'ids': set(), 'bad': []}
    for q in basic:
        nq = dict(q)
        p.pad_explanation(nq, kp_by_id.get(q.get('knowledgeId'), {}).get('name', ''))
        p.fix_single_options(nq)
        p.shuffle_options(nq, random.Random('v012_' + bank))
        p.encode_answer_v4(nq)
        for e in p.validate_basic(nq, know_ids, rep):
            rep['bad'].append(f"{nq['id']} [{e}]")
    test = [q for q in qs if q not in basic]
    for q in test:
        nq = dict(q)
        p.fix_single_options(nq)
        p.shuffle_options(nq, random.Random('v012_' + bank))
        p.encode_answer_v4(nq)
        if nq['id'] in rep['ids']:
            rep['bad'].append(f"{nq['id']} [id重复]")
        rep['ids'].add(nq['id'])
    if len(rep['ids']) != len(basic) + len(test):
        rep['bad'].append('id集合不一致')
    print(bank, '最终异常', len(rep['bad']))
    for b in rep['bad'][:8]:
        print('   ', b)
