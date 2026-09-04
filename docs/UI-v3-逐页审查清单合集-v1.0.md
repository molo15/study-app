# UI-v3 逐页审查清单合集 v1.0

> 审查对象：Flutter 考研刷题 App（应用根 `D:\study_app\app`），V3 iOS 风格迭代现状
> 审查方式：静态代码走查（Read/命令行按行读取），未做任何代码修改
> 审查日期：2026-09-04
> 验收基线：`flutter analyze --no-pub` 0 issues + 代码审查 + 真机（iPad mini5）目检
> 关联文档：`docs/prototype/ui-v3-ios.html`、`docs/UI-v3-iOS风格实施方案-v1.0.md`、`app/lib/ui/theme/ios_tokens.dart`

---

## 0. 审查范围与分级口径

### 覆盖页面

| # | 页面 | 文件 | 状态 |
|---|---|---|---|
| 1 | 设置页 | `app/lib/ui/pages/v3/settings_v3_page.dart` | 已审查 |
| 2 | 功能层交互 | `app/lib/ui/root_page.dart` 等 | 已审查 |
| 3 | 统计页 | `app/lib/ui/pages/v3/stats_v3_page.dart` + `data/quiz_repository_mock.dart` | 已审查 |
| 4 | 做题页 | `app/lib/ui/practice_page.dart` | 已审查 |
| 5 | 答题卡 | `app/lib/ui/practice_answer_sheet.dart` + `practice_question_view.dart` | 已审查 |
| 6 | 主界面（今日） | `app/lib/ui/pages/v3/home_v3_page.dart` | 已审查 |
| 7 | 背题模式 | `app/lib/ui/pages/v3/memorize_v3_page.dart` + `knowledge_memorize_page.dart` | 已审查 |
| 8 | 全局问题 | `theme/ios_page_route.dart`、`widgets/floating_tab_bar.dart` 等 | 已审查 |

### 问题分级

| 级别 | 定义 | 处理策略 |
|---|---|---|
| **P0** | 数据错误 / 交互不可用 / 用户核心需求未达成 | 必须修，优先 |
| **P1** | 明显组件残留 / 交互缺口 / 体验明显劣化 | 应修 |
| **P2** | 一致性打磨 / 细节优化 / 可选增强 | 有余力再修 |

### 判定备注

- 触觉反馈：iPad mini 5 **无 Taptic Engine**，`HapticFeedback` 全项目 0 处命中，触觉接入无实际效果，不列入修复项。
- 原生 iOS 液态玻璃：Flutter 渲染绕开 UIKit，现有玻璃为 `BackdropFilter` 仿制；接入 iOS 26 原生玻璃需 SwiftUI bridge，不现实，不列入。
- 旧 V2 代码策略：**保留不删**，本清单仅针对被用户实际使用、需统一到 V3 风格的面。

---

## 1. 设置页（settings_v3_page.dart）

### Material 组件残留（P1，B2）

| 位置 | 问题 | 建议 |
|---|---|---|
| `_showMemorizeModeInfo` ~468 行 | `AlertDialog` | 改 `showIOSModalSheet` |
| `_showHelp` ~495 行 | `AlertDialog` | 改 `showIOSModalSheet` |
| `_showFeedback` ~525 行 | `AlertDialog` | 改 `showIOSModalSheet` |
| `_showAbout` ~554 行 | `AlertDialog` | 改 `showIOSModalSheet` |
| ~661 / 678 / 721 行 | Material `Switch` ×3 | 改 iOS `CupertinoSwitch` |
| 每日目标弹窗 ~257 行 | `SwitchListTile` | 改 iOS 开关行 |
| 每日目标弹窗 ~293 行 | `FilledButton` | 改 `IOSButton` |
| ~171 / 198 行 | `TextField` Material 下划线样式 | 改 iOS 圆角输入框 |

### 文案过时（P2，B4）

- "使用帮助"文案仍描述"中央圆钮"——底栏已改统一一行，文案需同步。

### 已就绪项

- 目标院校输入已加入（`StudyGoal.school` 字段，考试日期弹窗内）。
- 题库管理入口已加入（数据分组顶部"题库管理"IOSListItem）。

---

## 2. 功能层交互（root_page 等）

| 优先级 | 位置 | 问题 |
|---|---|---|
| P1 | `root_page.dart` | 背题 Tab（index2）**未配 GlobalKey refresh**——home/bank/stats 均有、memorize 独缺，切 Tab 回来背题页不刷新 |
| P1 | `bank_home_page.dart` | 题库页大标题**顶到状态栏**（无 SafeArea 顶部） |
| P2 | 全局 | toast 仍是 Material `SnackBar` |
| P2 | `bank_manage_v3_page.dart` | 用 Material `BackButton` |
| P2 | `quiz_repository_mock.dart` | `_calcStreak` 依赖 `daily.day` 的 `YYYY-MM-DD` 格式契约未验证 |

---

## 3. 统计页（stats_v3_page.dart + quiz_repository_mock.dart）

### 数据口径（P0，B1）

| # | 问题 | 影响 |
|---|---|---|
| 1 | 总览 `totalAnswered/correct/wrong` 统计**全部** `answer_logs`（含归档题）；题型分布 SQL 却只统计 `q.status='active'` | 归档过题目后，总览合计与题型分布合计**对不上** |
| 2 | 章节统计 SQL 只算 correct/wrong，**partial 既不进对也不进错** | 有半对题时"X 对 / Y 错 / Z 题"中 **X+Y < Z** |

### 展示/计分（P1-P2）

| 优先级 | 位置 | 问题 |
|---|---|---|
| P1 | `_DailyBars` ~330 行 | 近 7 日柱状图**时间轴反了**：`daily[0]`=今天在最左（应最右） |
| P2 | `StudyStats.accuracy` ~680 行 | partial 一律算错（多选漏选拉低正确率）——**口径需用户拍板** |
| P2 | ~75 / 428 行 | `CircularProgressIndicator` / `LinearProgressIndicator` Material 残留 |
| P2 | `studyStats` 查询 | `resultDistribution` 查了但 UI 未展示（冗余） |
| P2 | 薄弱章节 | 按 accuracy 升序取前 8，样本量小时噪声大 |

---

## 4. 做题页（practice_page.dart）

### 交互逻辑——健壮，无 P0

- 三种模式取题 ✓；中断恢复（进度续刷 + 答题卡结果按题 id 恢复）✓
- 恢复竞态已处理（先恢复再放行作答）✓
- 恢复点落在已答题上自动续到下一道未答，全答完直接落结算页 ✓
- 恢复弹窗不可外部关闭、返回键拦截、计时暂停 ✓
- `logAnswerAndSchedule` 单事务原子写入（日志与 FSRS 调度一致）✓
- 单选/判断选完即判分、多选 toggle、计数从结果表重算 ✓
- 错题重刷连续答对达阈值静默移出错题本 ✓
- `reduceMotion` 全链路支持、选项抖动/弹性动效用 IOSColors + IOSRadius ✓

> 结论：做题页交互层无需修复，是本项目最健壮的一层。

---

## 5. 答题卡（practice_answer_sheet.dart + practice_question_view.dart）

### 容器动效——已达标 ✓

- compact：`showIOSModalSheet` 玻璃底部弹层 + 入场动画
- 平板/桌面：`showGeneralDialog` + `SlideTransition` 右侧滑入 320ms easeOutCubic（入场+收起反向）

### Material 残留 / 一致性缺口（P1，B2）

| 位置 | 问题 |
|---|---|
| `_confirmJump` ~289 行 | 跳转确认是 `showDialog + AlertDialog + FilledButton`——**做题流程最后一个 Material 弹窗** |
| `_Cell` ~343 行 | 格子用 **InkWell 水波纹**——iOS 应为无涟漪按压变暗 |
| 顶栏 ~51/57 行 | 用 `theme.textTheme` / `theme.colorScheme.outline`——非 IOSTypography |
| 平板浮层 ~606 行 | 遮罩 `Colors.black 0.25` 平铺黑——与 compact 玻璃遮罩质感不一致 |
| `GridView.count` ~267 行 | `crossAxisCount: 6` **写死**——桌面 280 宽/平板 300 宽格子偏小，未响应式 |

### 可选打磨（P2，B4）

- 题型分组整体一次性渲染，无逐组/逐格入场 stagger（对比背题科目页 `IOSListGroup(animate:true)`）。
- 三态底色为**静态浅色常量**（深浅通用设计，可读性好）——合理决策，真机确认后再定是否深色微调。

---

## 6. 主界面（今日 home_v3_page.dart）

### 数据逻辑——健壮 ✓

- 内置题库自动发现（枚举 assets 最高版本）+ 幂等同步 + 隐藏库跳过 ✓
- 单题库自动设当前、多题库可切"全部"聚合 ✓
- 子页返回 `_push` 后自动 `_refresh` ✓

### 问题

| 优先级 | 位置 | 问题 |
|---|---|---|
| P1 | "可新学" onTap ~251 行 | **一次性预取全部新题**（`limit: _newCount` 全量加载后传 PracticePage）——首次新题多时点按钮瞬间卡、全驻内存；应让 PracticePage 内部按需取或限单轮量 |
| P2 | 快捷入口 ~284 行 | 导航策略混合：`context.go` 走 GoRouter `CupertinoPage`——转场 iOS ✓，但这些页面**无全屏滑动返回**（仅默认左边缘 40pt），与 iosPageRoute 二级页手势不一致 |
| P2 | `_init` ~85 行 | 冷启动每次扫全部 zip 读 manifest 比对版本——题库多时冷启动略慢 |
| P2 | ~179 行 | 加载态 `CircularProgressIndicator`（Material） |

---

## 7. 背题模式

### 科目选择页（memorize_v3_page.dart）——V3 化 ✓

- IOSListGroup 入场动效、IOSCard 说明卡、iosPageRoute 进章节 ✓
- **缺 `refresh()`**（P1，B3）：切 Tab 回来科目/可背数不刷新

### 翻卡核心页（knowledge_memorize_page.dart）——最大深水区

| 优先级 | 位置 | 问题 |
|---|---|---|
| P1 | 全页 | **V2 老界面**：`Theme.of(context)` + `theme.textTheme`，卡片色硬编码（浅 `Colors.white` / 深 `0xFF2B3646` 深蓝灰）、强调色走旧 `config.accent` |
| P1 | 全页 | **未接入 V3 令牌**（IOSColors/IOSSpacing/IOSTypography/液态玻璃）——深色下翻转卡"深蓝灰硬卡片"与 V3 深色近黑背景+玻璃风格明显不搭，全 App iOS 味最弱处 |
| — | 交互逻辑 | 会话队列/背会未背会重推/记忆状态持久化为 V2 久经验证，逻辑健壮，纯视觉落后 |

---

## 8. 全局问题

| 优先级 | 位置 | 问题 |
|---|---|---|
| **P0-D1** | `theme/ios_page_route.dart` | **全屏返回手势是半成品**：`_FullScreenBackGestureDetector` 的 onStart/onUpdate 为空、只在 onEnd 判 `velocity>300` 才 `maybePop`——无拖拽跟随、无松手回弹，注释自认"阶段1实现，阶段4待复制手势控制器"。**用户核心需求"非边界右滑返回"未真正达成**。全屏 Listener translucent 与横向滚动/滑动删除有冲突隐患 |
| P1-D2 | V3 自定义卡片列表（home_v3/memorize_v3/stats_v3/bank_home） | 无入场动效——`IOSAnimatedItem`/`StaggeredItem` 只在 V2 页和 `IOSListGroup` 内部使用 |
| P2-D3 | 视觉按压 | IOSButton/IOSListGroup 行/PressableCard ✓；**IOSCard / FloatingTabBar Tab / ios_action_sheet 选项缺按压反馈** |
| P2-D4 | 深色硬编码 | V3 页 9 处：3 处白字蓝底（设计正确），6 处 Switch 圆钮白色（换 CupertinoSwitch 后自然消失） |
| P2 | 导航一致性 | 三级页面两套体系：iosPageRoute（V3 二级页，全屏返回✓）+ GoRouter CupertinoPage（mock/wrongbook/bank 等，仅左边缘返回） |

---

## 9. 问题总数统计

| 级别 | 数量 | 归属批次 |
|---|---|---|
| P0 | 3 | B1（统计口径×2）、B5（全屏返回手势） |
| P1 | 12 | B2/B3/B5 分散 |
| P2 | 13 | B4 及可选 |

> 注：P0 中的"全屏返回手势"归入 **B5 深水区**（涉及手势控制器复制，独立评估）；统计口径 2 项归 B1。

---

*本文档为审查快照，仅记录问题不修改代码；修复动作以《UI-v3 修复规划案》为准。*
