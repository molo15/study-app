# -*- coding: utf-8 -*-
"""修复模拟卷失效引用：用同库同章同题型活跃题替换，保持结构。"""
import json, os, collections
BASE = r'D:\study_app\tools\seed-builder'
refined = {
 'bank-gudai-hanyu':'out/refined/bank-gudai-hanyu.v012.json',
 'bank-xiandai-hanyu':'out/refined/bank-xiandai-hanyu.refined2.json',
 'bank-zhongguo-gudai-wenxue':'out/refined/bank-zhongguo-gudai-wenxue.v012.json',
 'bank-zhongguo-xiandai-wenxue':'out/refined/bank-zhongguo-xiandai-wenxue.quota.json',
 'bank-zhongguo-dangdai-wenxue':'out/refined/bank-zhongguo-dangdai-wenxue.refined2.json',
}
# 失效题元信息（type, chapter）来自 backup
stale_meta = {
 'bank-gudai-hanyu:m_000539':('single_choice','诗词格律'),
 'bank-gudai-hanyu:m_000524':('multi_choice','语法（上）'),
 'bank-gudai-hanyu:q_000026':('true_false','音韵'),
 'bank-gudai-hanyu:q_000132':('true_false','语法（上）'),
 'bank-xiandai-hanyu:q_000010':('single_choice','文字'),
 'bank-xiandai-hanyu:z_000141':('single_choice','语法'),
 'bank-xiandai-hanyu:w_000049':('single_choice','语音'),
 'bank-xiandai-hanyu:w_000279':('single_choice','词汇'),
 'bank-xiandai-hanyu:k_000224':('single_choice','修辞'),
 'bank-xiandai-hanyu:w_000050':('single_choice','语音'),
 'bank-xiandai-hanyu:w_000138':('single_choice','语音'),
 'bank-xiandai-hanyu:w_000452':('blank','修辞'),
 'bank-xiandai-hanyu:w_000093':('blank','语音'),
 'bank-xiandai-hanyu:k_000227':('short_answer','修辞'),
 'bank-zhongguo-gudai-wenxue:q_000116':('multi_choice','魏晋南北朝文学'),
 'bank-zhongguo-xiandai-wenxue:q_000061':('single_choice','文学思潮与运动（一）'),
 'bank-zhongguo-xiandai-wenxue:q_000102':('single_choice','市民通俗小说（一）'),
 'bank-zhongguo-xiandai-wenxue:q_000001':('single_choice','鲁迅（一）'),
 'bank-zhongguo-xiandai-wenxue:q_000005':('single_choice','郭沫若'),
 'bank-zhongguo-xiandai-wenxue:q_000140':('blank','文学思潮与运动（二）'),
 'bank-zhongguo-xiandai-wenxue:q_000052':('blank','老舍'),
 'bank-zhongguo-xiandai-wenxue:q_000120':('short_answer','小说（一）'),
 'bank-zhongguo-dangdai-wenxue:q_000072':('single_choice','第二章 50、60 年代小说'),
 'bank-zhongguo-dangdai-wenxue:q_000053':('single_choice','第九章 80、90 年代戏剧'),
 'bank-zhongguo-dangdai-wenxue:q_000094':('single_choice','第五章 80、90 年代文学思潮'),
 'bank-zhongguo-dangdai-wenxue:q_000114':('single_choice','第八章 80、90 年代新诗'),
 'bank-zhongguo-dangdai-wenxue:q_000111':('multi_choice','第七章 90 年代小说'),
 'bank-zhongguo-dangdai-wenxue:q_000130':('multi_choice','第十章 80、90 年代散文'),
 'bank-zhongguo-dangdai-wenxue:q_000017':('true_false','第三章 50、60 年代新诗'),
 'bank-zhongguo-dangdai-wenxue:q_000036':('short_answer','第三章 50、60 年代新诗'),
}

# 建活跃题索引
active = {}
for b, f in refined.items():
    qs = json.load(open(f'{BASE}/{f}', encoding='utf-8'))
    active[b] = {}
    for q in qs:
        active[b].setdefault(q['type'], collections.defaultdict(list))
        active[b][q['type']][q.get('chapter','')].append(q['id'])
    # 记录题id全集
    active[b]['_all'] = {q['id'] for q in qs}

p = json.load(open(f'{BASE}/out/papers/papers.json', encoding='utf-8'))
replacements = {}
for pp in p['papers']:
    b = pp['bankId']
    existing = set(pp['questionIds'])
    new_ids = []
    for sid in pp['questionIds']:
        if sid not in active[b]['_all']:
            t, ch = stale_meta.get(sid, (None, None))
            cand = []
            if t and ch:
                cand = [i for i in active[b][t][ch] if i not in existing and i not in new_ids]
            if not cand and t:
                for ch2, ids in active[b][t].items():
                    cand += [i for i in ids if i not in existing and i not in new_ids]
            if not cand:
                # 兜底：任意 active 题
                cand = [i for i in active[b]['_all'] if i not in existing and i not in new_ids]
            rep = cand[0] if cand else None
            if rep:
                replacements[sid] = rep
                new_ids.append(rep)
                existing.add(rep)
            else:
                new_ids.append(sid)  # 无法替换则保留（不应发生）
        else:
            new_ids.append(sid)
    pp['questionIds'] = new_ids

json.dump(p, open(f'{BASE}/out/papers/papers.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('替换映射（失效 → 新题）：')
for k, v in replacements.items():
    print(f'  {k} -> {v}')
print('共替换', len(replacements), '个失效引用')
