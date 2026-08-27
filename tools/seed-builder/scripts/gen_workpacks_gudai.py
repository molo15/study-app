# -*- coding: utf-8 -*-
"""生成古代汉语多会话工作包：每个包自包含，可发给独立会话并行执行。

产物：out/v09gudaihanyu/workpacks/
  00-公共规则.md          所有会话必读
  审查-<章>.md            14 个（13 章 + 论述题专题）
  出题-<章>.md            13 个
"""
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'out', 'v09gudaihanyu', 'workpacks')
os.makedirs(OUT, exist_ok=True)

# 章 | 存量题数 | 素材条数 | 基础目标 | 测试目标 | 核心考点提示
CHAPTERS = [
    ('修辞', 10, 39, '25-32', '4-6',
     '古汉语修辞格：互文（秦时明月汉时关）、借代（诸葛亮代智慧）、夸张、婉曲、双关、顶真、排偶、用典；与现代汉语修辞的异同'),
    ('古书的文体', 8, 38, '20-28', '4-6',
     '文体分类：论说/序跋/奏议/书牍/碑志/哀祭/传状；骈文与散文；文体与语体特征；文体演变'),
    ('古书的标点', 36, 13, '12-18', '3-5',
     '句读与标点：断句原则、标点致误原因（词义不明/语法不通/上下文失照）、标点正确性判断'),
    ('工具书简介', 24, 81, '35-45', '5-8',
     '《说文解字》（许慎/540部首/9353字）、《尔雅》（训诂/19篇）、《广韵》（206韵）、《康熙字典》（214部首）、类书（艺文类聚/太平御览/永乐大典）、政书、书目、索引；查检方法'),
    ('文字（上）', 162, 90, '40-50', '6-10',
     '六书（象形/指事/会意/形声/转注/假借）、汉字结构分析（独体/合体）、形声字声符形符、汉字形体演变（甲骨文→金文→篆→隶→楷）'),
    ('文字（下）', 22, 66, '30-40', '5-8',
     '古今字（然—燃）、异体字（泪—涙）、繁简字、通假字（蚤—早）、隶变、六书与用字关系'),
    ('绪论', 8, 34, '20-28', '4-6',
     '古代汉语研究对象、文言与白话、古今汉语的继承与发展、古汉语学习的意义'),
    ('训诂', 34, 54, '30-38', '5-8',
     '训诂方法（形训/声训/义训）、训诂术语（曰/为/谓之/犹/之言/貌/属/别）、传注笺疏（毛传/郑笺/孔疏）、训诂著作、随文释义与通释语义'),
    ('词汇', 221, 91, '40-50', '6-10',
     '本义/引申义/假借义、词义引申方式（辐射/链条）、古今异义、同义词辨析、连绵词（联绵字）、偏义复词、单音词为主'),
    ('诗词格律', 51, 40, '25-32', '4-6',
     '平仄（平上去入/平分阴阳）、近体诗格律（粘对/拗救/押韵）、对仗（工对/宽对）、词牌与词律、五言七言律诗绝句'),
    ('语法（上）', 43, 143, '50-60', '8-12',
     '词类活用（名词动化/形容词动化）、使动用法、意动用法、名词作状语、虚词（之其而于以与为）、兼词（诸/焉/盍）、固定结构（何以/奈何/孰与）'),
    ('语法（下）', 97, 221, '60-75', '10-14',
     '判断句（者也/乃/即）、被动句（于/见/为/被）、宾语前置（疑问代词/否定句代词/之是标志）、定语后置、状语后置、省略句、疑问代词与疑问语气词'),
    ('音韵', 22, 53, '30-38', '5-8',
     '中古音（三十六字母/声母）、反切、四声（平上去入）、韵部、上古音（阴阳入对转/古无轻唇音）、音韵学与古书阅读'),
]

COMMON = '''# 古代汉语多会话工作包 · 公共规则（所有会话必读）

> 项目根：D:\\study_app。所有路径用绝对路径。产物统一写 JSON，主会话会合并。

## 双轨分类
- **基础题**（purpose=basic，贵多不贵精，辅助记忆）：单选/填空/判断/多选等客观题为主；纯记忆型简答（列举/名解）也可归基础。
- **测试题**（purpose=test，贵精不贵多，检验回忆与答案组织）：简答/论述/名解/古文翻译/断句为主，可含精选综合性选填判。

## 逐题处置四选一（delete 命中任一）
- **keep_basic**：客观题且考点正常无重复；或纯记忆型简答。
- **keep_test**：简答/论述/名解/翻译/断句，或综合辨析强的客观题。
- **delete**：
  - a.模板簇同壳题：同壳换词反复考同一考点，整簇只留 1-2 个代表（古汉典型：如"「X」中加点词的意义是"系列、"下列各组属于古今字的一组是"穷举系列、"「X」在句中的词性是"系列）；
  - b.镜像倒装/套娃："属于/不属于"、"A是B吗/B是A吗"互为倒装，保留真题或更标准方；
  - c.跨来源同考点复制：同一考点仅表述不同重复出现，保留最优 1 题；
  - d.偏怪冷门/过细：非教材主干、过细数字、残缺题干（如"题干空缺处应填入的内容是？"）；
  - e.题干硬伤：答案与解析矛盾、引文与题干不符、答案错误；
  - f.低质复制粘贴：机械复制无考察价值。
- **rewrite**：考点有价值但题干有硬伤/表述不清，给改写建议（含具体改法）。

## 覆盖缺口
对照素材（h 标题块★越多考点越高频），列出素材有明确考点但存量题完全没覆盖的清单（含素材证据）。

## 等价答案 answerVariants
对填空/简答/名解/翻译题，判断是否存在"可等价表述"的答案（如 连绵词=联绵字、使动用法=使动、说文解字=说文、通假字=通假），写成分组 `[["词1","词2"]]`。这用于判分时"答任一等价表述即判对"。**古文翻译/字词释义尤其要查等价表述**。

## 机器处置 JSON 统一格式（Write 到指定路径，UTF-8）
```json
{
  "bank-gudai-hanyu:q_000001": {
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
- 报告（人类可读）：D:\\study_app\\tools\\seed-builder\\out\\v09gudaihanyu\\reports\\
- 机器处置（JSON）：D:\\study_app\\tools\\seed-builder\\out\\v09gudaihanyu\\dispositions\\
- 出题产物（JSON）：D:\\study_app\\tools\\seed-builder\\out\\v09gudaihanyu\\draft\\
'''


def review_pack(ch, n, mat, tips):
    return f'''# 审查工作包：{ch}（{n} 题）

## 任务
逐题审查 D:\\study_app\\tools\\seed-builder\\out\\v09gudaihanyu\\existing\\{ch}.json（{n} 题，JSON 数组），判定 keep_basic / keep_test / delete / rewrite，并标注覆盖缺口与等价答案。

## 输入
- 存量题：D:\\study_app\\tools\\seed-builder\\out\\v09gudaihanyu\\existing\\{ch}.json（{n} 题）
- 素材：D:\\study_app\\tools\\seed-builder\\out\\v09gudaihanyu\\materials\\{ch}.txt（{mat} 条，h 标题块★越多考点越高频，正文块行首 [blockId] 是思源笔记块 id）

## 核心考点（教材主干，判定质量时对照）
{tips}

## 判定规则
先读《00-公共规则.md》（若该文件在会话中不可见，规则如下）：
- keep_basic / keep_test / delete（a-f）/ rewrite，定义见公共规则；
- 覆盖缺口：对照素材列素材有考点但存量未覆盖的清单；
- 等价答案：填空/简答/名解/翻译有等价表述（如 连绵词=联绵字）就写 answerVariants。

## 输出（Write，UTF-8，目录不存在先创建）
1. 报告：D:\\study_app\\tools\\seed-builder\\out\\v09gudaihanyu\\reports\\{ch}.md
   结构：## 处置汇总；## 逐题处置表格（| id | type | stem摘要 | 处置 | 理由 |）；## 覆盖缺口；## 等价答案建议。
2. 机器处置：D:\\study_app\\tools\\seed-builder\\out\\v09gudaihanyu\\dispositions\\{ch}.json
   格式：JSON 对象 key=题id，value={{"action":"keep_basic|keep_test|delete|rewrite","reason":"理由","answerVariants":[...]可选,"rewriteSuggestion":"..."可选}}；"_gaps":[{{"考点":"...","素材证据":"..."}}]

## 要求
{n} 题全覆盖；删除理由写明判定规则（a-f 哪一条）；不修改输入文件；完成后报告各处置计数。
'''


def lunsu_pack():
    return f'''# 审查工作包：论述题专题（34 题，拆归）

## 任务
34 道论述题（全 short_answer，含古文翻译/断句/论述）需**按内容归入 13 个真实章节**并判定保留/删除/改写。伪章节将取消。

## 输入
- 待拆归题：D:\\study_app\\tools\\seed-builder\\out\\v09gudaihanyu\\existing\\论述题专题.json（34 题）
- 各章素材（判断归属）：D:\\study_app\\tools\\seed-builder\\out\\v09gudaihanyu\\materials\\ 下 13 个 txt

## 目标章节（suggestedChapter 从这些里选）
修辞、古书的文体、古书的标点、工具书简介、文字（上）、文字（下）、绪论、训诂、词汇、诗词格律、语法（上）、语法（下）、音韵

## 判定
每题输出：归属章节 + 处置（四选一）：
- keep_test：论述/翻译/断句题归测试题，考点属教材主干且价值高 → 保留。
- delete：偏怪/过时/低质/与教材主干无关；**重复考同一话题的只留最优 1-2 道**。
- rewrite：考点有价值但题干需优化（给改写建议）。
- keep_basic 一般不适用，个别记忆型列举简答可例外。

## 等价答案
对保留的翻译/断句/论述题，判断答案是否存在可等价表述的关键术语（如 使动用法=使动、连绵词=联绵字），写 answerVariants 组。**翻译题务必给出参考译文并标注重点字词等价释义**。

## 输出（Write，UTF-8）
1. 报告：D:\\study_app\\tools\\seed-builder\\out\\v09gudaihanyu\\reports\\论述题专题.md
   结构：## 处置汇总（各处置+各归属计数）；## 逐题拆归表格（| id | 归属章节 | 处置 | stem摘要 | 理由 |）；## 等价答案建议。
2. 机器处置：D:\\study_app\\tools\\seed-builder\\out\\v09gudaihanyu\\dispositions\\论述题专题.json
   格式：JSON 对象 key=题id，value={{"action":"keep_basic|keep_test|delete|rewrite","suggestedChapter":"归属章节","reason":"理由","answerVariants":[...]可选,"rewriteSuggestion":"..."可选}}

## 要求
34 题全覆盖，每条含 suggestedChapter；删除理由写清类别；不修改输入文件；完成后报告各处置计数与归属分布。
'''


def gen_pack(ch, n, mat, b_target, t_target, tips):
    return f'''# 出题工作包：{ch}

## 任务
基于笔记素材生成两道文件：
1. 新增**基础题 {b_target} 道**：以单选题、填空题为主（可少量判断/多选），贵多不贵精，同一核心知识点允许不同题型重复考。
2. 新增**测试题 {t_target} 道**：以简答题/名词解释/古文翻译/断句为主（必带 answerFormat），贵精不贵多。

另外：审查报告中标记 rewrite 的存量题，须按"改写建议"产出改写版（id 保持原 id，放对应 purpose 的文件里）。

## 输入
- 笔记素材：D:\\study_app\\tools\\seed-builder\\out\\v09gudaihanyu\\materials\\{ch}.txt（{mat} 条，h 标题块★越多考点越高频；正文块行首 [blockId] 是思源笔记块 id，出题时必须引用）
- 审查处置：D:\\study_app\\tools\\seed-builder\\out\\v09gudaihanyu\\dispositions\\{ch}.json（_gaps=缺口清单优先覆盖；rewriteSuggestion=改写建议）
- 审查报告：D:\\study_app\\tools\\seed-builder\\out\\v09gudaihanyu\\reports\\{ch}.md

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
  "answerFormat": "作答格式：……",   // 仅 short_answer 必填（翻译题填：①先句读断句 ②重点字词释义（句中〔〕标注）③整句通译）
  "answerVariants": [["等价词1","等价词2"], ...],   // 存在等价表述必填（如 连绵词=联绵字、使动用法=使动）
  "chapter": "{ch}",
  "purpose": "basic | test",
  "tags": ["六书", "古今字", ...],   // 2-5 个
  "difficulty": "easy | medium | hard",
  "source": {{"blockId": "素材中引用的块id", "kind": "exercise"}}
}}
- 新增题 id 用 tmp-<章关键词>:两位序号（基础与测试错开）；rewrite 题 id 保持原 id。
- source.blockId 必须取自素材文件中的真实块 id。

## 数量与质量要求
- 基础题贵多不贵精：核心知识点（古今字组、词类活用类型、六书归类、虚词用法）可多题型多角度重复考，覆盖 _gaps 全部缺口。
- 测试题贵精不贵多：覆盖核心论述/名解/翻译考点，每题带 answerFormat。
- 不得与存量保留题重复（处置文件 action=keep_*；可读 D:\\study_app\\tools\\seed-builder\\out\\v09gudaihanyu\\existing\\{ch}.json 对照）。
- 题干原创改写，不逐字照抄素材长句；每题 explanation 必须写清依据；**古汉填空/简答的答案注意列等价表述**（如 本义/本意）。

## 输出（Write，UTF-8，目录不存在先创建）
1. D:\\study_app\\tools\\seed-builder\\out\\v09gudaihanyu\\draft\\基础-{ch}.json —— 数组：新增基础题 + 归基础的 rewrite 改写版
2. D:\\study_app\\tools\\seed-builder\\out\\v09gudaihanyu\\draft\\测试-{ch}.json —— 数组：新增测试题 + 归测试的 rewrite 改写版
写完自检：字段齐全、id 规则正确、answer 编码符合、source.blockId 存在于素材。完成后报告各文件题数与 rewrite 处理情况。
'''


def main():
    with open(os.path.join(OUT, '00-公共规则.md'), 'w', encoding='utf-8') as f:
        f.write(COMMON)
    print('00-公共规则.md')

    for ch, n, mat, b, t, tips in CHAPTERS:
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
