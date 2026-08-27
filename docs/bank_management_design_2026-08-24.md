# 题库包管理功能设计（删除 + 直接编辑）

> 日期：2026-08-24 · 状态：待确认后实施
> 现状：题库包只有"导入"（设置页）与"清除归档"（purgeArchived），无整库删除、无题目编辑。

## 1. 目标

- 能**删除/卸载**手动导入的题库包（内置 5 库可隐藏）；
- 能**直接编辑**已导入题库的题目（题面/选项/答案/解析），即时生效；
- 全程保护作答数据：删除分"卸载（保数据）"与"彻底删除（清数据）"两级。

## 2. 数据关系（删除时的连带范围）

| 表 | 关联键 | 说明 |
|---|---|---|
| questions | bank_id | 题库题（active/archived） |
| mock_papers | bank_id | 模拟卷定义 |
| answer_logs | question_id | 作答历史 |
| card_scheduling | question_id | FSRS 复习状态 |
| wrong_book_exclusions | question_id | 错题本手动移出 |
| review_flags | question_id, bank_id | 审题标记 |
| mock_sessions | paper_id | 模拟卷成绩 |
| settings | bank_{id}_version/name/groups + practice_progress:* | 元数据与练习进度 |

## 3. 功能一：删除题库包（两级语义）

### 3.1 卸载（默认，安全，可恢复）
- 题库从首页/设置列表**消失**；该库题目全部软归档（status=archived，不再出现在刷题范围）；
- **作答记录/FSRS/错题本/审题标记/练习进度全部保留**；
- 重新导入同 bank_id 包 → 题目恢复 active，历史数据自动接续。
- 内置库特殊处理：卸载 = 写入 `bank_{id}_hidden` 标记，首页自动导入（现逻辑 `importedVersion==null` 才导）改为同时检查 hidden 标记跳过。

### 3.2 彻底删除（高级，红字警告，不可恢复）
- 在卸载基础上，物理删除：该库全部 question_id 的 questions / answer_logs / card_scheduling / wrong_book_exclusions / review_flags，以及 mock_papers / mock_sessions / settings 元数据（bank_* 键 + 相关 practice_progress:*）。
- 防误触：确认框要求**手动输入题库包名称**后才可执行。

### 3.3 后端（quiz_repository 新增，均走事务）
```dart
Future<int> uninstallBank(String bankId);          // active→archived + hidden 标记
Future<int> deleteBankCompletely(String bankId);   // 全量物理删除（含作答数据）
Future<List<BankInfo>> banks();                    // 现有方法加 hidden 过滤
```

### 3.4 UI（设置 → 题库包管理 → 每库 trailing 菜单）
- 菜单项：卸载题库包（确认框）｜彻底删除（输入库名）｜编辑题目（功能二入口）
- 归档数>0 时保留现有"清除归档"。

## 4. 功能二：直接编辑题目

### 4.1 题目浏览器（题库包管理 → 某库 → 编辑题目）
- 按章节分组 + 按题型筛选 + 关键词搜索（题干/答案）；
- 显示审题标记（review_flags）题，一键跳转编辑（与现有"审题标记"联动）；
- 列表项：题型标签 + 题干摘要 + 状态（已修改/待审）。

### 4.2 编辑页（表单式，非刷题样式）
- 可编辑字段：题干 stem、选项 options（单选/多选/判断）、答案 answer、解析 explanation、章节 chapter、answerVariants、answerFormat；
- 保存校验：答案非空；选择题答案必须存在于选项（缺失则提示）；
- 保存 = `UPDATE questions SET ... WHERE id`（`updateQuestion(q)`），**只影响后续作答，不回溯历史记录**；
- 编辑的是 SQLite 库内数据，**不改 assets 源 zip**（如需"导出编辑后的库"另行决定）。

### 4.3 后端（quiz_repository 新增）
```dart
Future<List<Question>> questionsForManage(String bankId,
    {String? chapter, String? keyword, QuestionType? type, int limit = 200});
Future<void> updateQuestion(Question q);
Future<List<ChapterGroup>> chaptersForBank(String bankId);  // 章节分组（复用现有）
```

## 5. 边界与限制
- 内置 5 库删除后，`_bundledBanks` 源包仍在 assets——隐藏后随时可重新显示，不会"消失"；
- 手动导入库彻底删除后，源 zip 需用户自行保留（App 不存源包）；
- 编辑保存失败（如答案非法）给出明确提示且不落库；
- 删除操作全部先确认后执行，与现有"先扫后做"协作习惯一致。

## 6. 审题标记常驻化（不再按构建隐藏）

- 现状：`reviewModeEnabled = bool.fromEnvironment('REVIEW_MODE', defaultValue: kDebugMode)`（`services/export_helper.dart`）——正式 release 不传参即隐藏刷题页旗子按钮与设置页导出入口。
- 决策：**改为常驻功能**（用户确认），刷题页"标记为待修改"旗子 + 设置页"导出审题标记"入口始终可见；
- 与题目编辑联动：审题标记的题在题目浏览器中置顶/角标显示，一键跳转编辑——"发现问题 → 标记 → 修复"闭环；
- 保留导出：`导出审题标记` 仍按 review_flags 输出清单，便于批量核对。

## 7. 用户修改保护（内置式更新的覆盖问题）

### 7.1 问题
内置式题库更新：新 APK 携带新题库 zip，启动时 `SeedLoader.import` 按 id `INSERT OR REPLACE`。
**用户手动编辑过的题，会被新包同 id 的题覆盖**（REPLACE 全字段覆盖）——必须解决。

### 7.2 方案：`user_edited` 本地修改标记
- **DB v8 迁移**：`ALTER TABLE questions ADD COLUMN user_edited INTEGER DEFAULT 0`（`app_database.dart` bump `_dbVersion` 8 + onUpgrade）；
- `updateQuestion()`（题目编辑保存）→ `user_edited = 1`；
- `SeedLoader.import` 导入逻辑调整（**合并策略**）：
  - 库中已存在且 `user_edited = 1` 的题 → **跳过 REPLACE，保留用户版本**（同 id 新内容丢弃）；
  - 库中不存在 / `user_edited = 0` 的题 → 照常 upsert（新题插入、官方修复生效）；
  - 新包中已删除的题 → 仍软归档（不变）；
- 可见性：设置页题库包管理显示"本库有 X 题被本地修改（更新时保留）"；
- 导出备份：备份 JSON 中题目带 `user_edited` 字段，恢复后标记不丢。

### 7.3 边界
- 用户改过的题，后续官方修复不会自动到达（除非用户主动"还原为官方版"——编辑页提供**还原按钮**，置回 `user_edited = 0` 并刷新为最新包内容）；
- 冲突提示不阻断导入（静默保留本地版，管理页可见计数）。

## 8. 实施步骤（确认后按序执行）
1. DB v8 迁移（user_edited 列）+ `SeedLoader.import` 合并策略；
2. 后端：`uninstallBank` / `deleteBankCompletely` / `updateQuestion` / `questionsForManage` / `restoreQuestionToOfficial`；
3. 设置页：题库包管理 UI（菜单、卸载/彻底删除、输入库名确认、本地修改计数）；
4. 题目浏览器 + 编辑表单页（含审题标记联动、还原按钮）；
5. 审题标记常驻化（去掉构建开关条件）；
6. `flutter analyze` + 编译验证 → 打包正式版。

## 9. 待拍板
1. **更新保护粒度**：采用"`user_edited` 跳过覆盖"（官方修复不自动到用户改过的题，管理页可见）是否可接受？还是需要"三向合并提示"（弹窗逐题选择本地/官方）？
2. **还原按钮**：编辑页是否提供"还原为官方版"（丢弃本地修改，刷成最新包内容）？
