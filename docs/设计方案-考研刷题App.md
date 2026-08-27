# 考研刷题 App —— 设计方案（v1.0）

> 设计日期：2026-08-15
> 一句话定位：**本地优先的考研刷题器**——开发期用「思源笔记 + AI」把个人知识库加工成内置题库，运行时是一部完全离线、数据全在手机上的纯刷题 App。
>
> 核心洞察：题库 App（粉笔/万题库）有海量公共题但消化不了你的私有笔记；卡片工具（Anki/RemNote）能把笔记变卡片但缺"题目结构 + 判分 + 错题本 + 统计"。**"思源笔记 → 结构化题目 → 刷题闭环"是真实空白**，本方案填补它。

---

## 0. 需求与决策回顾

| 决策点 | 结论 | 依据 |
|---|---|---|
| 应用形态 | 安卓手机 App，离线优先 | 用户明确：手机刷题、本地刷题器 |
| 题库内容 | 用户自己的思源笔记加工成内置题库 | 用户明确 |
| AI 用途 | 仅开发期内容生产，运行时不需要 AI/网络 | 用户明确："mcp 只为开发服务" |
| 技术栈 | Flutter（沿用 schedule_app 约定） | 用户已在 D:\richeng\schedule_app 配置好 Flutter |
| 复用策略 | 自建骨架 + 满配开源依赖：依赖层直接用成熟开源包（全 MIT/BSD/Apache 许可），算法与数据模型借鉴已验证实现，不重复造轮子、不整体 fork（详见 §6） | 用户确认，规避 GPL 强制开源约束 |
| 交付物 | 本设计文档 | 用户明确 |

**已核实的本地环境**：
- 思源笔记 3.8.0 正在运行（127.0.0.1:6806，≥3.7.2 已修复 MCP 未授权漏洞）；
- Android SDK 就绪（API 35，模拟器可用，已有 AVD `zcode_test`）；
- Node v24 / Python 3.11 可用（开发期工具链可选）；
- schedule_app（Flutter）确立的工程约定：**sqflite 原生 SQL + 版本化迁移、Repository 层、Riverpod 3、中文注释、docs/ 设计文档文化**——本 App 完全沿用。

---

## 1. 系统全景：两阶段架构

整个产品分两个阶段，**职责严格分离**。这是本方案最重要的架构决策。

```
┌─────────────────────────────────────────────────────────────┐
│ 阶段一：内容生产线（开发期，跑在 PC，一次性/按需执行）            │
│                                                             │
│   思源笔记          素材筛选          AI 生成         人工审核   │
│   (6806 内核 API) ─→ (SQL 检索) ─→ (LLM 批量) ─→ (审核工具)   │
│                                                     │        │
│                                                     ▼        │
│                                          题库包 (JSON + 校验和) │
└─────────────────────────────────────────────────────────────┘
                              │ 随 App 打包 / 作为扩展包导入
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 阶段二：运行时 App（跑在安卓手机，完全离线）                     │
│                                                             │
│   Flutter UI ─→ ViewModel (Riverpod Notifier)               │
│                     │                                       │
│                     ▼                                       │
│              Repository ─→ 本地 SQLite (sqflite)             │
│              （题库/作答/错题/复习调度/统计）                    │
│                                                             │
│   功能：题库浏览 · 刷题 · 判分 · 错题本 · 间隔重复 · 统计        │
└─────────────────────────────────────────────────────────────┘
```

- **阶段一产出的题库包是阶段二的唯一输入**。App 不依赖思源、不依赖 AI、不依赖网络。
- 好处：思源版本升级、AI 模型更换、笔记变动，都只影响开发期，不影响已发布的 App；用户隐私（笔记原文）永不进 App 运行时。

---

## 2. 阶段一：内容生产线（开发期工具链）

形态：**Node.js CLI 工具**（本机已有 Node 24），放在新 Flutter 项目的 `tools/` 目录（沿用 schedule_app 的 tools 约定）。建议做成 `tools/seed-builder/`，独立 package，不参与 App 构建。

### 2.1 思源笔记接入：直接调内核 HTTP API，不走 MCP

调研结论（详见附录 A）：思源已官方内置 MCP（`POST /mcp`，v3.7.x）也有社区 MCP server，但 **MCP 是给 AI Agent / LLM 工具调用设计的协议封装**；本项目的应用代码是确定性业务逻辑（读块 → 解析 → 出题 → 写回），**直接调内核 HTTP API 更简单、稳定、可控**：

| 维度 | 直接调内核 API（推荐） | 走 MCP |
|---|---|---|
| 依赖 | 零额外依赖，curl/Node 即可 | 需 MCP 客户端 SDK / 子进程 |
| 权限 | 读类接口普通 token 即可；`/api/query/sql` 需管理员 | 官方 /mcp 强制管理员 + 受暴露策略影响 |
| 能力 | 完整公开 API，文档化稳定 | 封装子集，官方注释明示"不承诺全部兼容" |
| 调试 | curl 直调，异常直接 `{code,msg}` | 多一层协议 |

**接入要点**（已验证）：
- 端点：`http://127.0.0.1:6806`，全部 `POST` + JSON body；
- 鉴权头：`Authorization: Token <token>`（注意 `Token` 大写 T + 空格，不是 Bearer）；
- token 获取：`<工作空间>/conf/conf.json` 的 `api.token` 字段（或思源 设置→鉴权→API token）；
- 开发期工具在本地跑，直接用管理员 token 即可（含 SQL 检索权限）；
- 返回结构统一 `{"code":0,"msg":"","data":...}`，code 非 0 为异常。

**用到的关键接口**：

| 功能 | 接口 | 说明 |
|---|---|---|
| 列笔记本 | `POST /api/notebook/lsNotebooks` | 选择要出题的笔记本 |
| 列出文档树 | `POST /api/filetree/getDocByPath` | 按章节浏览 |
| SQL 检索块 | `POST /api/query/sql` | 核心素材筛选（见 2.2） |
| 读块内容 | `POST /api/block/getBlockKramdown` | 取块 markdown 原文 |
| 全文搜索 | `POST /api/search/fullTextSearchBlock` | 关键词定位素材（可选） |
| 写入（可选） | `POST /api/block/insertBlock`、`/api/attr/setBlockAttrs` | 把生成的题/错题写回笔记（增强功能） |

### 2.2 素材筛选（SQL 策略）

思源数据在 SQLite 中，核心表 `blocks` 关键列：`id, parent_id, root_id(所属文档), box(笔记本), path, hpath(文档路径), name, type(块类型), tag, content(纯文本), markdown(kramdown), ial(自定义属性), created, updated`。

**筛选策略**：以"块"为素材单元，过滤规则：
- 只选内容型块：`type IN ('p','h','l','li')`（段落/标题/列表项），排除 `c`(代码)、`tb`(数据库) 等；
- 按笔记本/文档过滤：`box = ?` 或 `root_id = ?`；
- 按内容长度：`length BETWEEN 20 AND 800`（过短无信息量，过长需切分）；
- 可选按标签：`tag LIKE '%真题%'` 或 ial 自定义属性。

示例：
```sql
SELECT id, type, content, hpath, markdown
FROM blocks
WHERE box = '<boxID>'
  AND type IN ('p','h','l','li')
  AND length BETWEEN 20 AND 800
  AND hpath NOT LIKE '%模板%'
ORDER BY hpath, sort
```

**上下文组装**：每块生成题目前，向上拼取父标题链（hpath）作为"章节语境"，必要时拼接相邻块——提升 AI 出题相关性。

### 2.3 AI 题目生成管线

**流程**：素材块 → 文本清洗（去 kramdown 语法、公式转义、超长切分）→ LLM 批量生成（严格 JSON）→ 本地规则校验 → 人工审核 → 入库。

**模型选型**（国内可用，成本可忽略）：
- 批量草稿：**GLM-4.5-Flash / GLM-4.7-Flash（免费）** 或 DeepSeek v4-flash（约 $0.0004/次）；
- 精生成（简答/解析质量要求高时）：DeepSeek / GLM-5；
- **统一走 OpenAI 兼容端点**（用户自配 base_url + API Key），供应商可替换。

**提示词策略**：
- **直接复用成熟提示词模板**：借鉴 Chat-GPT-Flashcards-To-Anki-Converter（MIT）的**"你是只从给定来源取材的机器人，禁止引入外部常识"** 约束——这正是考研出题"仅依据笔记原文、不掺外部知识"的关键技巧；
- 结构化输出用 **Instructor**（MIT，13.7k star）：Pydantic/Schema 强制 LLM 输出严格 JSON + 校验失败自动重试，替代手写 JSON 校验与正则修复；不依赖 LLM 自由输出 JSON 再猜；
- 系统提示固定 JSON Schema，要求 `answer` 可校验（选择题答案必须能在 options 中严格对应；填空答案须能在原文中找到依据）；
- 每块默认生成 2~5 题（可配"知识密度"）；
- 分题型提示：单选/多选要求干扰项同域不重复；填空挖空点选关键术语/数据；简答给参考答案 + 2~3 个评分关键词。

**本地规则校验**（Instructor Schema 之外的第二道闸）：
- 去重：`(stem 归一化哈希)` 与已有题比对；
- 答案可验证：选择题答案索引必须落在 options 内；填空答案非空且短；
- 题干非空、不含 AI 痕迹词、不与原块逐字相同（防纯复制）；
- 不通过的题标记 `draft` 进入人工审核，不直接入库。

**人工审核**：审核工具（本地 Web 页面或简单 TUI）列出 draft 题，逐题"通过 / 修改 / 删除"，支持批量通过；审核后状态 `published`。

### 2.4 题库包格式（阶段一与阶段二的接口契约）

**容器**：题库包 = **zip 文件**（骨架参照 opentdb 的极简 JSON + 吸收 GIFT 的反馈标记思想），随 App 打包为 asset，也可作为外部扩展包导入。内部结构：

```
bank-gaoshu-2026.zip
├── manifest.json        # 包元数据：formatVersion / bankId / name / version / 章节列表 / 作者 / 生成时间
├── questions.json       # 全部题目（或 questions/ 目录按章节分文件，大包推荐）
└── media/               # 题目引用的图片等资源（一期可缺省，纯文字题不需要）
```

`manifest.json` 与 `questions.json` 的字段定义如下（题目结构即下方示例的 `questions[]` 项）：

```json
{
  "formatVersion": 1,
  "bankId": "bank-gaoshu-2026",
  "name": "考研 · 高等数学",
  "version": "1.0.0",
  "generatedAt": "2026-08-15T10:00:00+08:00",
  "chapters": ["第一章 函数与极限", "第二章 导数与微分"],
  "questions": [
    {
      "id": "bank-gaoshu-2026:q_000001",
      "type": "single_choice",
      "stem": "当 $x \\to 0$ 时，下列无穷小量中阶数最高的是：",
      "options": [
        { "key": "A", "text": "$x^2$" },
        { "key": "B", "text": "$1-\\cos x$" },
        { "key": "C", "text": "$\\sin x - x$" },
        { "key": "D", "text": "$\\ln(1+x)$" }
      ],
      "answer": "C",
      "explanation": "……（含解题思路，可引用笔记原文片段）",
      "tags": ["极限", "无穷小"],
      "chapter": "第一章 函数与极限",
      "difficulty": "medium",
      "source": {
        "blockId": "20240101120000-abc1234",
        "docPath": "/高数笔记/第一章 函数与极限",
        "note": "衍生自笔记：无穷小比较"
      }
    }
  ]
}
```

**题目 id 规则**：`id = "{bank_id}:{序号}"`（如 `bank-gaoshu-2026:q_000001`）。`bank_id` 前缀保证多题库包导入时**全局唯一**（DB 主键是全局的），`seed_loader` 也据此识别题目归属、做包内增量比对。

**answer 编码约定**：答案一律为 JSON 值——单选/判断是字符串（`"C"`），多选/填空是字符串数组（`["A","C"]` / `["极限"]`），简答是参考答案文本。Dart 侧统一解析为 `Set<String>` 参与判分（集合比较，单选天然单元素），避免字符串与数组混用导致的类型分支。

**chapters 与题目 chapter 的关系**：实际章节以题目上的 `chapter` 为准（App 浏览页用 `SELECT DISTINCT chapter` 动态生成），顶层 `chapters` 数组仅供元数据展示与导入时一致性告警，不参与页面构建。

**formatVersion 兼容**：导入器只接受 `formatVersion ≤ 当前支持的最大版本`，更高版本直接拒绝并提示"题库包版本过新，请升级 App"，避免静默解析出错。

**题型枚举**：`single_choice`（单选）/ `multi_choice`（多选）/ `blank`（填空）/ `short_answer`（简答）/ `true_false`（判断）。

**公式与图片**：
- 公式：题干/选项/解析存 LaTeX（`$...$`），App 端用 `flutter_math_fork` 离线渲染（不依赖网络）；
- 图片：笔记中的图片按 `assets/` 目录随包走（`source.blockId` 关联图名），一期可先跳过图片题。

---

## 3. 阶段二：运行时 App 架构

### 3.1 技术栈

| 层 | 选型 | 说明 |
|---|---|---|
| 框架 | Flutter | 沿用 schedule_app 已配置环境 |
| 状态管理 | Riverpod 3（flutter_riverpod） | 与 schedule_app 一致 |
| 本地数据库 | sqflite + 版本化迁移 | 与 schedule_app 一致（PRAGMA foreign_keys ON） |
| 间隔重复 | **`fsrs`（dart-fsrs，MIT）** | FSRS-4/5 官方 Dart 移植，直接依赖不造轮子（见 §3.6） |
| 公式渲染 | flutter_math_fork（Apache-2.0） | 离线 LaTeX，不支持时回退纯文本 |
| 题库包解压 | archive（MIT） | zip 题库包导入 |
| 文件选择 | file_picker（BSD-3） | 外部题库包导入 |
| 卡片翻转（可选） | flip_card（MIT） | 背题模式动画 |
| 统计图表（可选） | fl_chart（MIT） | 知识点掌握度图表 |
| 通知（可选） | flutter_local_notifications | 每日复习提醒（二期） |

> 依赖许可证纪律：**全部依赖限定 MIT / BSD / Apache 宽松许可**，零 copyleft 传染（详见 §6）。

新项目建议目录：`D:\study_app\app\`（Flutter 工程根），与设计文档、开发期工具分开。

### 3.2 分层架构

```
lib/
├── main.dart
├── models/            # 领域模型：Question, AnswerLog, CardState, BankMeta, Stats…
├── data/
│   ├── app_database.dart    # sqflite 建表/迁移（沿用 schedule_app 模式）
│   ├── seed_loader.dart     # 内置题库包 → DB 导入（幂等、按版本增量）
│   ├── quiz_repository.dart # 题目/作答/错题/收藏读写
│   ├── scheduler.dart       # 间隔重复调度（SM-2，接口预留 FSRS）
│   └── stats.dart           # 统计聚合查询
├── ui/
│   ├── home_page.dart       # 今日概览（待复习数/今日目标/快捷入口）
│   ├── bank_page.dart       # 题库浏览（按章节/知识点）
│   ├── practice/            # 刷题引擎（题干/选项/作答/判分/解析）
│   ├── wrong_book_page.dart # 错题本
│   ├── stats_page.dart      # 统计报表
│   └── settings_page.dart   # 设置（复习参数/导入包/备份）
└── services/          # 通知、备份、包导入
```

**依赖方向**：UI → ViewModel(Riverpod Notifier) → Repository → DB。ViewModel 不碰 SQL，Repository 集中所有数据库读写（沿用 schedule_app 约定）。

### 3.3 数据模型（SQLite）

```
questions(
  id TEXT PRIMARY KEY,            -- 全局唯一：{bank_id}:{序号}（如 bank-gaoshu-2026:q_000001）
  bank_id TEXT NOT NULL,          -- 所属题库包
  status TEXT NOT NULL DEFAULT 'active',  -- active / archived（题包更新时软归档）
  type TEXT NOT NULL,             -- single_choice / multi_choice / blank / short_answer / true_false
  stem TEXT NOT NULL,
  options TEXT,                   -- JSON: [{key,text}]
  answer TEXT NOT NULL,           -- JSON 统一编码（见 §2.4）："C" / ["A","C"] / ["答案"] / "参考答案"
  explanation TEXT,
  chapter TEXT,                   -- 章节（冗余，加速按章刷题）
  tags TEXT,                      -- JSON 数组
  difficulty TEXT,                -- easy/medium/hard
  source_block_id TEXT,           -- 来源思源块 id（容错字段，非 FK）
  source_doc_path TEXT,           -- 来源文档路径（块被删后仍可定位/纯文本降级）
  collected INTEGER DEFAULT 0,    -- 收藏
  flagged INTEGER DEFAULT 0,      -- 存疑标记
  created_at INTEGER, updated_at INTEGER
)
CREATE INDEX idx_questions_chapter ON questions(chapter);
CREATE INDEX idx_questions_bank ON questions(bank_id);

answer_logs(                     -- append-only，永不修改
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  question_id TEXT NOT NULL,
  mode TEXT NOT NULL,            -- learn / review / wrong_rework / mock / browse
  result TEXT NOT NULL,          -- correct / wrong / partial / skip
  rating INTEGER,                -- SRS 评分 1..4（Again/Hard/Good/Easy），仅 review/learn 有
  time_ms INTEGER,               -- 单题用时
  answered_at INTEGER NOT NULL   -- epoch ms
)
CREATE INDEX idx_logs_qid ON answer_logs(question_id);
CREATE INDEX idx_logs_time ON answer_logs(answered_at);

card_scheduling(                 -- 每道题的 FSRS 状态，字段对齐 dart-fsrs 的 Card.toMap()
  question_id TEXT PRIMARY KEY,
  state TEXT NOT NULL,           -- new / learning / review / relearning（dart-fsrs CardState）
  due INTEGER NOT NULL,          -- 到期时间（epoch ms）
  stability REAL,                -- FSRS 记忆稳定性 S
  difficulty REAL,               -- FSRS 难度 D
  elapsed_days INTEGER,
  scheduled_days INTEGER,
  reps INTEGER DEFAULT 0,
  lapses INTEGER DEFAULT 0,
  last_review INTEGER,           -- epoch ms
  updated_at INTEGER
)

settings(key TEXT PRIMARY KEY, value TEXT)   -- desired_retention、每日新题数、learning_steps…
```

**设计要点**（对齐 Anki 的 notes/cards/revlog 分离哲学，结构借鉴 AnkiDroid 数据模型、自行实现）：
1. 调度状态与题目内容分离——调度逻辑完全交给 dart-fsrs 包，表字段与其 `Card` 序列化一一对应，包升级（如 FSRS-5→6）只动字段映射，不迁移题目表与作答日志；
2. `answer_logs` append-only——统计与 FSRS 参数优化器都依赖它；
3. `source_block_id` 容错：块被删/改名时降级为纯文本解析，不影响刷题。

### 3.4 题库包导入（seed）

- **内置题库**：题库包作为 Flutter asset 打包；App 首次启动（或检测到 bank 版本更新时）由 `seed_loader` 幂等导入 DB。导入按 `(bank_id, version)` 比对，只增量导入变更题（按稳定 `id` upsert，不重建表）。
- **题目删除语义**：新包中不存在、且属于该 `bank_id` 的旧题**软归档**为 `archived`（保留作答历史与统计），UI 默认不展示；设置页提供"彻底清理已归档题"入口。默认不做物理删除——删题会丢统计。
- **外部扩展包**：设置页"导入题库包"（file_picker 选 .json），导入流程与内置一致；支持个人后续追加题目包。
- **回滚**：内置题库的"已导入版本"存 settings，异常导入可重置重导。

### 3.5 刷题状态机

所有刷题模式共用一个状态机，**模式只决定"取哪些题"，SRS 只负责"到期队列"**（调研中最重要的解耦决策）：

```
选择模式/范围 → 取题队列(questions queue)
  → 展示题目(题干/选项/输入)
  → 提交作答
  → 判分(对/错/部分对) → 展示解析(含来源出处展示)
  → 写 answer_logs → 更新 card_scheduling
  → 下一题 → 队列耗尽 → 结算页(正确率/用时/知识点分布)
```

> 一期离线运行：解析中的"来源"仅展示出处文本（`source.docPath`，如"衍生自：高数笔记/第一章"），不做笔记跳转；如后续需要回链思源，走"导出同步文件 → 手动导入"的弱链路。

**判分规则**：
- 基础机制：作答与答案都归一化为 `Set<String>` 做集合比较——单选天然单元素，单选/多选共用同一套集合判分逻辑；
- 单选/判断：即时判分；
- 多选：全中 = correct，部分 = partial；
- 填空：参考答案 + 关键词匹配（前端归一化比对），可"看答案后自评"；
- 简答：**看答案后自评对错**（Anki 方式，四档评分直接进 SRS）；
- 模拟考试：整卷交卷判分（限时 + 答题卡 + 成绩单）。

**模式清单**：

| 模式 | 取题范围 | 判分 | 是否进 SRS 统计 |
|---|---|---|---|
| 顺序刷 | 章节内题序 | 即时 | 是（learn） |
| 随机刷 | 范围内随机（可按标签/章节过滤） | 即时 | 是（learn） |
| 按知识点刷 | 选标签集合 | 即时 | 是（learn） |
| 错题重刷 | 错题本（按错误次数排序） | 即时 | 是，掌握后移出错题本 |
| 背题模式 | 任意范围 | 不判分 | **否**（mode=browse，不污染统计） |
| 模拟考试 | 固定题量+限时 | 交卷统一判 | 单独统计（mode=mock） |

**错题本逻辑**：答错自动入错题本（记录最近错误时间/次数）；"错题重刷"答对且连续正确达阈值（如连续 2 次正确）自动移出；也可手动移除。

### 3.6 间隔重复调度（直接用 dart-fsrs，不造轮子）

**选型**：直接 pub 依赖 **`fsrs`**（open-spaced-repetition/dart-fsrs，MIT，FSRS-4/5 官方 FSRS 组织的纯 Dart 移植）。FSRS 是 Anki、墨墨背单词、思源官方 Riff 组件现网主力的调度算法；包内提供完整 `Scheduler`——学习步骤、重学步骤、间隔模糊化、按到期排序取队列、可调 desired retention / 最大间隔 / 19 权重参数——**无需自写 SM-2 或任何调度逻辑**。

**接入方式**（薄适配，不重复实现）：
- `card_scheduling` 表字段 = dart-fsrs `Card.toMap()` 输出（见 §3.3）；`answer_logs.rating` 1..4 直接映射 FSRS Rating（Again/Hard/Good/Easy）；
- 每次作答：`scheduler.reviewCard(card, rating)` → 返回新 `Card` + `ReviewLog`，分别写 `card_scheduling` 与 `answer_logs`；
- 今日复习队列：按包内 `due` 排序取到期卡片（new 按学习步骤时间、review 按到期日），错题重刷等模式仍走 §3.5 的取题逻辑、与 SRS 队列解耦；
- 学习步进 / desired retention / 每日新题配额在包参数中配置，设置页可调：长期备考 retention 90%、冲刺期调低至 80% 并缩短学习步进——参数化切换，不是两套逻辑。注意方向：FSRS 中 **retention 越低复习间隔越长**（interval ∝ retention^(1/decay)−1，decay<0），冲刺期调低 retention 的目的是降低复习密度、把时间留给刷新题。

**数据自第一天就对齐 FSRS**：`state / due / stability / difficulty` 等随每次作答落库，即使一期不做完整复习页，调度状态也已就位；包升级只涉及字段映射与包版本，不动题目表与作答日志。

### 3.7 首页"今日概览"

```
┌─────────────────────────────┐
│  今日待复习 23  ·  新题 20   │  ← 到期队列 + 今日新题配额
│  [开始今日复习]  [开始刷题]  │
│  ───────────────────────    │
│  连续打卡 12 天 │ 今日正确率 68% │
│  快捷：按章节刷 / 随机刷 / 错题重刷(5) │
└─────────────────────────────┘
```

### 3.8 统计报表

数据来源：`answer_logs`（append-only）聚合：
- 今日/累计做题数、正确率、用时；
- 连续打卡天数（按日去重）；
- 各章节/知识点正确率（雷达/柱状，定位薄弱点）；
- 错题数量趋势；
- 到期未复习数（防队列堆积）。

---

## 4. 实施路线图

| 里程碑 | 内容 | 涉及页面 / 数据表 | 验收标准 |
|---|---|---|---|
| **M0 环境骨架** | `flutter create` 新项目（`D:\study_app\app`）；sqflite + Riverpod 接入；按 §6 依赖清单接入核心包（fsrs、archive 等）；题库包格式定稿 | main 壳；settings、questions（空表） | 空库可启动，目录结构与 schedule_app 一致 |
| **M1 题库加载 + 刷题闭环** | seed_loader 导入示例题库包（手写 10 题验证）；题库浏览页；顺序/随机刷；判分与解析 | bank_page、practice；questions、answer_logs | 手机上能完整刷一遍题并看到解析；每道题的判分结果与用时**持久化到 answer_logs**（M2 的错题本/SRS 以此为数据基石）；示例题**覆盖全部 5 种题型**（单选/多选/填空/判断/简答各 2 道），把判分逻辑一次做全 |
| **M2 错题本 + 间隔重复** | 错题本自动归集/重刷/移出；**接入 fsrs 包**调度 + 今日复习队列；四档评分 | home_page、wrong_book_page；card_scheduling | 错题自动入本，到期队列按调度出现 |
| **M3 统计 + 设置** | 统计报表页；设置（复习参数/导入扩展包/备份导出/清理归档） | stats_page、settings_page；settings、questions(status) | 统计数字与作答记录一致 |
| **M4 内容生产线** | tools/seed-builder CLI：思源 API 接入 → SQL 素材筛选（谓词构造参照思源 buildTypeFilter）→ AI 生成（Instructor 结构化输出）→ 校验 → 审核 → 打包含并 | 无（开发期工具链，不进 App） | 从真实思源笔记生成 ≥100 题内置题库 |
| **M5 打磨发布** | 公式渲染、背题/模考模式（mode=browse/mock）、空态/引导、APK 构建签名 | practice 模式补全；answer_logs(mode) | 生成可安装 APK |

> 建议 M1 就用手写小样本题库验证刷题体验，M4 再投入笔记/AI 管线——先验证"刷题本身"的价值，再放大内容。

---

## 5. 风险与开放问题

| 风险/问题 | 应对 |
|---|---|
| 公式渲染离线 | flutter_math_fork（Apache-2.0）；不支持时降级纯文本 + "查看原笔记"提示 |
| 笔记图片入包 | 图片随题库包 media/ 目录；一期可先只出文字题 |
| 题库包体积 | 按章节分包；zip 压缩；统计页可裁剪 |
| 简答/填空判分主观 | 自评模式（看答案后自评），符合 SRS 惯例 |
| 思源块被删/改名 | source 容错字段 + 纯文本降级 |
| 生成题质量 | Instructor 结构化校验 + 本地规则校验 + 人工审核兜底；draft 不直接进刷题队列 |
| 开源依赖许可传染 | 依赖全部限定 MIT/BSD/Apache（见 §6），规避 GPL/AGPL 传染；**不 fork 无许可证或 copyleft 项目** |
| 题库版权 | **绝不引入外部题库**（真题/市售题库/OpenTDB 均有版权或 Share-Alike 传染风险），坚持 AI 仅依据用户笔记生成原创题（见 §6） |
| 是否要云同步 | 一期明确不要；备份/导出文件作为可移植方案（二期可选） |
| 多设备/多账号 | 一期单机单用户；题库包本身就是内容分发单元 |

---

## 6. 拿来主义与复用清单（核心原则：能拿现成的不自研）

调研结论：**没有任何现成开源项目整体命中"本地刷题器 + 笔记加工题库"**（闪卡 SRS App 缺题目/判分/错题本，题库 App 不开源或带许可约束），但**每一层都有可直接拿来的积木**。策略：自建骨架 + 满配宽松许可依赖 + 借鉴已验证实现，**不整体 fork、不复制 copyleft 代码、不引入外部题库数据**。

### A) 直接 pub/GitHub 依赖（运行时 App）

| 包 | 许可证 | 用途 | 备注 |
|---|---|---|---|
| `fsrs`（dart-fsrs） | MIT | FSRS-4/5 间隔重复调度 | 官方 FSRS 组织纯 Dart 移植，`Scheduler.reviewCard` + `Card.toMap()`，无需自写调度 |
| `flutter_math_fork` | Apache-2.0 | 离线 LaTeX 公式渲染 | simpleclub 维护；勿用停维护的 katex_flutter（EUPL 传染） |
| `sqflite` | BSD-2 | 本地数据库 | 事实标准 |
| `archive` | MIT | zip 题库包解压 | |
| `file_picker` | BSD-3 | 扩展包文件选择 | |
| `flip_card` | MIT | 背题模式翻转动画 | 可选 |
| `fl_chart` | MIT | 统计图表 | 可选 |
| `flutter_local_notifications` | BSD-3 | 每日复习提醒 | 二期可选 |

### B) 开发期内容生产线复用（全 MIT/宽松许可）

| 项目 | 许可证 | 复用什么 |
|---|---|---|
| **Instructor** | MIT | LLM 强制结构化 JSON 输出 + 校验失败自动重试，替代手写 JSON 校验 |
| 思源 `kernel/model/search.go` 的 `buildTypeFilter` | AGPL（**借鉴实现**，不复制代码） | 按块类型/子类型筛选素材的 SQL 谓词构造（官方权威实现） |
| 思源 `kernel/model/flashcard.go` | AGPL（借鉴） | 题目↔块绑定业务逻辑（按文档树收集块、块属性标记归属） |
| 思源官方 Riff 组件 | AGPL（借鉴） | `{卡片ID, 块ID}` 绑定方式 + `custom-riff-decks` 属性机制 → 我们题目带 `sourceBlockID` + 块上写 `custom-quiz` 属性回标 |
| Chat-GPT-Flashcards-To-Anki-Converter | MIT | **"仅从给定来源取材、禁止引入外部常识"** 出题约束提示词 |
| md2anki / LearnKit | GPL / MIT（借鉴） | Markdown→AI→审核→导出 的管线形态参照 |
| AnkiDroid / Anki 数据模型 | GPL/AGPL（借鉴结构，自行实现） | notes/cards/revlog 三表分离 + 调度状态机（type/queue/due） |
| opentdb JSON / GIFT | CC BY-SA / 开放文本（仅参照格式） | 题库包 JSON 骨架（极简）+ 答案/干扰项分离 + 反馈标记思想；**不引入其题目数据** |
| QuizFlow / memo | GPL-3 / BSD-3（仅参照 UI 与流程） | 刷题交互流、导入导出流程、进程度量设计 |

### C) 明确不碰的（许可或版权红线）

| 项目 | 许可 | 原因 |
|---|---|---|
| QuizFlow / TubeCards fork | GPL-3.0 | fork 即整个 App 必须 GPL 开源，闭源受限 |
| Quiz-App-Flutter 等大量高 star 项目 | **无许可证** | 默认保留所有权利，法律上不能抄 |
| katex_flutter | EUPL-1.2 | copyleft + 6 年未维护 |
| OpenTDB 题目数据 | CC BY-SA 4.0 | Share-Alike 传染，且为欧美 trivia，与考研不匹配 |
| C-Eval / CMMLU 题库 | CC BY-NC-SA | 非商用许可 |
| 考研真题 / 市售题库 | 版权归属出题机构 | 传播/打包/商用均有版权风险 |

---

## 附录 A：思源接入调研摘要（关键结论与链接）

- 思源 v3.7.2+ 官方内置 MCP（`POST /mcp`），但本场景推荐直接调内核 HTTP API（理由见 2.1）；
- 坑点提醒：token 只放开发期工具配置，绝不进 App；开发期工具在本地跑，思源不发布到公网；
- 写入能力完备（建文档/插块/打属性），"错题写回笔记"可作为增强功能，但不进一期；
- 参考链接：
  - 内核 API 文档（中文）：https://github.com/siyuan-note/siyuan/blob/master/docs/API.zh-CN.md
  - 思源主仓库（表结构 kernel/sql/database.go）：https://github.com/siyuan-note/siyuan
  - 工作区/数据文档：https://github.com/siyuan-note/siyuan/blob/master/docs/WORKSPACE.zh-CN.md
  - 官方 SRS 组件 Riff：https://github.com/siyuan-note/riff
  - SM-2：https://super-memory.com/english/ol/sm2.htm ；FSRS：https://github.com/open-spaced-repetition/awesome-fsrs

## 附录 B：AI 生成参考（调研摘要）

- 成本：GLM-flash 免费档 ≈ 0；DeepSeek v4-flash 生成 10000 题 ≈ $4；瓶颈在质量与限流，不在成本；
- 生成题默认 draft + 人工审核；双模型分层（flash 草稿 / 旗舰精修）为可选优化。
