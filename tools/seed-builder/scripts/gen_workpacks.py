# -*- coding: utf-8 -*-
"""生成古代文学史多会话工作包：每个包自包含（任务/输入/规则/输出格式），可发给独立会话并行执行。

产物：out/v09gudaiwenxue/workpacks/
  00-公共规则.md          所有会话必读（判定规则 a-f、处置 JSON 格式）
  审查-<章>.md            10 个（9 章 + 论述题专题）
  出题-<章>.md            9 个（有素材 6 章 + 无素材 3 章模板区分）
"""
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'out', 'v09gudaiwenxue', 'workpacks')
os.makedirs(OUT, exist_ok=True)

# 章 | 存量题数 | 素材条数 | 基础目标 | 测试目标 | 核心考点提示
CHAPTERS = [
    ('先秦文学', 92, 85, '40-50', '8-12',
     '《诗经》（风雅颂/赋比兴/六义）、楚辞（屈原/离骚/九歌）、历史散文（左传/国语/战国策）、诸子散文（论语/孟子/庄子）'),
    ('秦汉文学', 66, 73, '30-40', '6-10',
     '《史记》（纪传体/司马迁）、汉赋（司马相如/子虚赋上林赋）、乐府诗（陌上桑/孔雀东南飞）、古诗十九首'),
    ('魏晋南北朝文学', 85, 70, '35-45', '8-12',
     '建安风骨（三曹/七子）、正始之音（阮籍/嵇康）、陶渊明田园诗、山水诗（谢灵运）、永明体、世说新语、文心雕龙'),
    ('隋唐五代文学', 113, 173, '50-65', '10-15',
     '初唐四杰、盛唐气象（李白/杜甫）、边塞诗派、山水田园诗派、韩柳古文运动、新乐府运动（白居易）、晚唐小李杜、唐传奇、花间词/李煜'),
    ('宋代文学', 91, 120, '45-55', '8-12',
     '宋词（柳永/苏轼/李清照/辛弃疾）、宋诗（江西诗派/黄庭坚）、唐宋八大家、话本小说、陆游/杨万里'),
    ('明代文学', 98, 132, '40-50', '8-12',
     '四大奇书（三国演义/水浒传/西游记/金瓶梅）、汤显祖临川四梦、公安派/竟陵派、前后七子、拟话本三言二拍'),
    ('元代文学', 35, 0, '20-28', '5-8',
     '元杂剧（关汉卿/窦娥冤/西厢记/王实甫）、元散曲（马致远/天净沙秋思）、四大南戏'),
    ('清代文学', 46, 0, '25-32', '6-10',
     '《红楼梦》/曹雪芹、聊斋志异/蒲松龄、儒林外史/吴敬梓、桐城派、纳兰性德、长生殿/桃花扇'),
    ('近代文学', 16, 0, '10-16', '3-5',
     '诗界革命/黄遵宪、小说界革命/梁启超、四大谴责小说（官场现形记/二十年目睹之怪现状/老残游记/孽海花）'),
]

COMMON = '''# 古代文学史多会话工作包 · 公共规则（所有会话必读）

> 项目根：D:\\study_app。所有路径用绝对路径。产物统一写 JSON，主会话会合并。

## 双轨分类
- **基础题**（purpose=basic，贵多不贵精，辅助记忆）：单选/填空/判断/多选等客观题为主；纯记忆型简答（列举/名解）也可归基础。
- **测试题**（purpose=test，贵精不贵多，检验回忆与答案组织）：简答/论述/名解为主，可含精选综合性选填判。

## 逐题处置四选一（delete 命中任一）
- **keep_basic**：客观题且考点正常无重复；或纯记忆型简答。
- **keep_test**：简答/论述/名解，或综合辨析强的客观题。
- **delete**：
  - a.模板簇同壳题：同壳换词反复考同一考点，整簇只留 1-2 个代表；
  - b.镜像倒装/套娃："属于/不属于"、"A是B吗/B是A吗"互为倒装，保留真题或更标准方；
  - c.跨来源同考点复制：同一考点仅表述不同重复出现，保留最优 1 题；
  - d.偏怪冷门/过细：非教材主干、过细数字、残缺题干（如"题干空缺处应填入的内容是？"）；
  - e.题干硬伤：答案与解析矛盾、引文与题干不符、答案错误；
  - f.低质复制粘贴：机械复制无考察价值。
- **rewrite**：考点有价值但题干有硬伤/表述不清，给改写建议（含具体改法）。

## 覆盖缺口
对照素材（h 标题块★越多考点越高频），列出素材有明确考点但存量题完全没覆盖的清单（含素材证据）。

## 等价答案 answerVariants
对填空/简答/名解题，判断是否存在"可等价表述"的答案（如 建安风骨=建安风力、诗三百=诗经），写成分组 `[["词1","词2"]]`。这用于判分时"答任一等价表述即判对"。

## 机器处置 JSON 统一格式（Write 到指定路径，UTF-8）
```json
{
  "bank-zhongguo-gudai-wenxue:q_000001": {
    "action": "keep_basic|keep_test|delete|rewrite",
    "reason": "一句话理由（写明 a-f 哪条）",
    "answerVariants": [["等价词1","等价词2"]],   // 可选
    "rewriteSuggestion": "改写建议文本",          // 可选
    "suggestedChapter": "归属章节"                // 仅论述题专题需要
  },
  "_gaps": [{"考点": "...", "素材证据": "素材原文摘录"}]
}
```

## 硬性要求
1. **每道题必须有记录**（全覆盖，可脚本校验：action 合法、reason 非空）；
2. 删除理由必须写清属于判定规则哪一条；
3. **不修改任何输入文件**（只写输出文件）；
4. 完成后报告各处置计数。

## 输出目录（不存在先创建）
- 报告（人类可读）：D:\\study_app\\tools\\seed-builder\\out\\v09gudaiwenxue\\reports\\
- 机器处置（JSON）：D:\\study_app\\tools\\seed-builder\\out\\v09gudaiwenxue\\dispositions\\
- 出题产物（JSON）：D:\\study_app\\tools\\seed-builder\\out\\v09gudaiwenxue\\draft\\
'''


def review_pack(ch, n, mat, tips):
    has_mat = mat > 0
    mat_lines = f'- 素材：D:\\study_app\\tools\\seed-builder\\out\\v09gudaiwenxue\\materials\\{ch}.txt（{mat} 条，h 标题块★越多考点越高频，正文块行首 [blockId] 是思源笔记块 id）' if has_mat else '- 素材：**本章无笔记素材**（按教材标准考点判定质量，重点把关外部题库题的准确性）'
    return f'''# 审查工作包：{ch}（{n} 题）

## 任务
逐题审查 D:\\study_app\\tools\\seed-builder\\out\\v09gudaiwenxue\\existing\\{ch}.json（{n} 题，JSON 数组），判定 keep_basic / keep_test / delete / rewrite，并标注覆盖缺口与等价答案。

## 输入
- 存量题：D:\\study_app\\tools\\seed-builder\\out\\v09gudaiwenxue\\existing\\{ch}.json（{n} 题）
{mat_lines}

## 核心考点（教材主干，判定质量时对照）
{tips}

## 判定规则
先读《00-公共规则.md》（若该文件在会话中不可见，规则如下）：
- keep_basic / keep_test / delete（a-f）/ rewrite，定义见公共规则；
- 覆盖缺口：对照素材列素材有考点但存量未覆盖的清单；无素材章按教材标准考点判断缺口；
- 等价答案：填空/简答/名解有等价表述（如 建安风骨=建安风力）就写 answerVariants。

## 输出（Write，UTF-8，目录不存在先创建）
1. 报告：D:\\study_app\\tools\\seed-builder\\out\\v09gudaiwenxue\\reports\\{ch}.md
   结构：## 处置汇总；## 逐题处置表格（| id | type | stem摘要 | 处置 | 理由 |）；## 覆盖缺口；## 等价答案建议。
2. 机器处置：D:\\study_app\\tools\\seed-builder\\out\\v09gudaiwenxue\\dispositions\\{ch}.json
   格式：JSON 对象 key=题id，value={{"action":"keep_basic|keep_test|delete|rewrite","reason":"理由","answerVariants":[...]可选,"rewriteSuggestion":"..."可选}}；"_gaps":[{{"考点":"...","素材证据":"..."}}]

## 要求
{n} 题全覆盖；删除理由写明判定规则（a-f 哪一条）；不修改输入文件；完成后报告各处置计数。
'''


def lunsu_pack():
    return f'''# 审查工作包：论述题专题（170 题，拆归）

## 任务
170 道论述题（全 short_answer）需**按内容归入 9 个真实章节**并判定保留/删除/改写。伪章节将取消。

## 输入
- 待拆归题：D:\\study_app\\tools\\seed-builder\\out\\v09gudaiwenxue\\existing\\论述题专题.json（170 题）
- 各章素材（判断归属）：D:\\study_app\\tools\\seed-builder\\out\\v09gudaiwenxue\\materials\\ 下 6 个 txt（先秦/秦汉/魏晋南北朝/隋唐五代/宋代/明代；元代/清代/近代无素材按教材常识判断）

## 目标章节（suggestedChapter 从这些里选）
先秦文学、秦汉文学、魏晋南北朝文学、隋唐五代文学、宋代文学、明代文学、元代文学、清代文学、近代文学

## 判定
每题输出：归属章节 + 处置（四选一）：
- keep_test：论述题归测试题，考点属教材主干且论述价值高 → 保留。
- delete：偏怪/过时/低质/与教材主干无关；**重复考同一话题的只留最优 1-2 道**（如多道"李白诗歌艺术特色"论述题）。
- rewrite：考点有价值但题干需优化（给改写建议）。
- keep_basic 一般不适用，个别记忆型列举简答可例外。

注意：170 题量大，重点删重复考同一话题的（同一作家/作品/流派保留最优 1-2 道）与偏怪冷门题。元代/清代/近代的标准考点（元杂剧、关汉卿、汤显祖、曹雪芹《红楼梦》等）属教材主干，有价值的保留。

## 等价答案
对保留论述题，判断答案是否存在可等价表述的关键术语（如 建安风骨=建安风力、江西诗派=江西宗派），写 answerVariants 组。

## 输出（Write，UTF-8）
1. 报告：D:\\study_app\\tools\\seed-builder\\out\\v09gudaiwenxue\\reports\\论述题专题.md
   结构：## 处置汇总（各处置+各归属计数）；## 逐题拆归表格（| id | 归属章节 | 处置 | stem摘要 | 理由 |）；## 等价答案建议。
2. 机器处置：D:\\study_app\\tools\\seed-builder\\out\\v09gudaiwenxue\\dispositions\\论述题专题.json
   格式：JSON 对象 key=题id，value={{"action":"keep_basic|keep_test|delete|rewrite","suggestedChapter":"归属章节","reason":"理由","answerVariants":[...]可选,"rewriteSuggestion":"..."可选}}

## 要求
170 题全覆盖，每条含 suggestedChapter；删除理由写清类别；不修改输入文件；完成后报告各处置计数与归属分布。
'''


def gen_pack(ch, n, mat, b_target, t_target, tips):
    has_mat = mat > 0
    src_line = f'- 笔记素材：D:\\study_app\\tools\\seed-builder\\out\\v09gudaiwenxue\\materials\\{ch}.txt（{mat} 条，h 标题块★越多考点越高频；正文块行首 [blockId] 是思源笔记块 id，出题时必须引用）' if has_mat else '- 笔记素材：**本章无素材**，按教材标准考点出题；source.blockId 填 "textbook-standard"，docPath 填 "教材标准考点"'
    rewrite_line = '另外：审查报告中标记 rewrite 的存量题，须按"改写建议"产出改写版（id 保持原 id，放对应 purpose 的文件里）。' if True else ''
    return f'''# 出题工作包：{ch}

## 任务
基于笔记素材生成两道文件：
1. 新增**基础题 {b_target} 道**：以单选题、填空题为主（可少量判断/多选），贵多不贵精，同一核心知识点允许不同题型重复考。
2. 新增**测试题 {t_target} 道**：以简答题/名词解释为主（必带 answerFormat），贵精不贵多。
{rewrite_line}

## 输入
{src_line}
- 审查处置：D:\\study_app\\tools\\seed-builder\\out\\v09gudaiwenxue\\dispositions\\{ch}.json（_gaps=缺口清单优先覆盖；rewriteSuggestion=改写建议）
- 审查报告：D:\\study_app\\tools\\seed-builder\\out\\v09gudaiwenxue\\reports\\{ch}.md

## 核心考点（出题围绕）
{tips}

## 字段规范（每道题）
{{
  "id": "tmp-<章关键词>:01",
  "type": "single_choice | blank | true_false | multi_choice | short_answer",
  "stem": "题干（选择题带（　）或问号；填空用＿＿＿或____占位）",
  "options": [{{"key": "A", "text": "选项"}}, ...],   // 选择类必填；填空/简答/判断 = []
  "answer": "A" | ["A","B"] | ["答案词"] | "正确/错误",
  "explanation": "解析（结合素材内容，写清依据）",
  "answerFormat": "作答格式：……",   // 仅 short_answer 必填
  "answerVariants": [["等价词1","等价词2"], ...],   // 存在等价表述必填（如 建安风骨=建安风力）
  "chapter": "{ch}",
  "purpose": "basic | test",
  "tags": ["作家/作品/流派名", ...],   // 2-5 个
  "difficulty": "easy | medium | hard",
  "source": {{"blockId": "素材中引用的块id", "kind": "exercise"}}
}}
- 新增题 id 用 tmp-<章关键词>:两位序号（基础 01-{b_target.replace('-','')}，测试错开）；rewrite 题 id 保持原 id。
- source.blockId 必须取自素材文件中的真实块 id；无素材章用 "textbook-standard" 占位。

## 数量与质量要求
- 基础题贵多不贵精：核心知识点（作家作品对应、流派特征、名句出处）可多题型多角度重复考，覆盖 _gaps 全部缺口。
- 测试题贵精不贵多：覆盖核心论述/名解考点（艺术特色、人物形象、思潮意义），每题带 answerFormat。
- 不得与存量保留题重复（处置文件 action=keep_*；可读 D:\\study_app\\tools\\seed-builder\\out\\v09gudaiwenxue\\existing\\{ch}.json 对照）。
- 题干原创改写，不逐字照抄素材长句；每题 explanation 必须写清依据。

## 输出（Write，UTF-8，目录不存在先创建）
1. D:\\study_app\\tools\\seed-builder\\out\\v09gudaiwenxue\\draft\\基础-{ch}.json —— 数组：新增基础题 + 归基础的 rewrite 改写版
2. D:\\study_app\\tools\\seed-builder\\out\\v09gudaiwenxue\\draft\\测试-{ch}.json —— 数组：新增测试题 + 归测试的 rewrite 改写版
写完自检：字段齐全、id 规则正确、answer 编码符合、source.blockId 存在于素材（无素材章除外）。完成后报告各文件题数与 rewrite 处理情况。
'''


def main():
    with open(os.path.join(OUT, '00-公共规则.md'), 'w', encoding='utf-8') as f:
        f.write(COMMON)
    print('00-公共规则.md')

    for ch, n, mat, b, t, tips in CHAPTERS:
        if ch == '先秦文学' or True:
            with open(os.path.join(OUT, f'审查-{ch}.md'), 'w', encoding='utf-8') as f:
                f.write(review_pack(ch, n, mat, tips))
            print(f'审查-{ch}.md')

    with open(os.path.join(OUT, '审查-论述题专题.md'), 'w', encoding='utf-8') as f:
        f.write(lunsu_pack())
    print('审查-论述题专题.md')

    for ch, n, mat, b, t, tips in CHAPTERS:
        with open(os.path.join(OUT, f'出题-{ch}.md'), 'w', encoding='utf-8') as f:
            f.write(gen_pack(ch, n, mat, b, t, tips))
        print(f'出题-{ch}.md')


if __name__ == '__main__':
    main()
