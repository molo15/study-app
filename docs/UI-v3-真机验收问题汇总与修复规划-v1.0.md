# UI-v3 真机验收问题汇总与修复规划 v1.0

> 日期：2026-09-04
> 来源：iPad mini5（2026 系统，深色模式）真机截图 7 张 + 用户补充文字描述
> 对应版本：commit 0778ab6 / 6b0b26b（GitHub Actions #20/#21 构建 IPA）

---

## 一、问题总清单（按严重度 P0 / P1 / P2）

### P0 · 功能性故障（阻断使用或交互异常）

| 编号 | 页面 | 问题现象 | 根因（已定位） |
|---|---|---|---|
| P0-1 | 全局路由 | 部分界面向右慢滑会弹出"浮动卡片"（页面被跟手右移，露出黑色下层）；部分页面右滑后卡死无法返回 | `ios_page_route.dart` 的 `_FullScreenBackGestureDetector` 设置 `gestureWidthRatio=1.0` **全屏手势区域**，与页面内部横向交互（选项横滑/滚动）抢手势；`_isBackGesture` 锁定后若手势被内部组件取消，`onCancel` 只重置位移不清除锁定状态，导致卡死 |
| P0-2 | 设置页 · 深色模式 | 点击"深色模式"屏幕变灰（barrier 出现）但弹不出选项面板 | `settings_v3_page.dart:118` 用 `showIOSActionSheet`（showModalBottomSheet 实现），在全屏手势路由（P0-1）上弹出时，手势层 Listener 覆盖全屏拦截了底部面板的命中测试 |
| P0-3 | 今日页 · 背题入口 | 点击"背题"同样变灰弹不出科目选择面板 | 同 P0-2：`home_v3_page.dart:542` `_showBankPickerForMem` 用 `showIOSActionSheet`，被手势层拦截 |
| P0-4 | 背题导航 | 背题→科目→章节→知识概览，看似一层实际套了多层：右滑一次只回退一级，需多次返回才回主界面 | `memorize_v3_page.dart:60` 用 `Navigator.push(iosPageRoute(ChapterOverviewListPage))` 压栈；而 `chapter_overview_list_page.dart:65` `_openChapter` 用 `context.go('/bank/xx/chapter/xx')`——go_router 在栈底 RootPage 之上重建 `BankPage`+`ChapterOverviewPage` 两层，叠加 push 层形成"三层" |

### P1 · 深色模式适配缺陷（视觉严重违和）

| 编号 | 页面 | 问题现象 | 根因（已定位） |
|---|---|---|---|
| P1-1 | 刷题答题卡 | 深色模式下大量米黄/浅绿大色块、黄线、双黄线，极其突兀 | `practice_answer_sheet.dart:19-25` 三态底色 `_greenBg/_redBg/_greyBg` 是**硬编码浅色常量**（0xFFEAF3DE 等），深色模式不切换 |
| P1-2 | 主页底栏 | 胶囊左右两边各有一道黑边黑块 | `floating_tab_bar.dart:96` LiquidGlass + `IOSShadow.glass(dark:true)` 深色阴影 `Color(0x80000000)`（alpha 0.5 的纯黑）blur 32 过大，深色背景下在胶囊边缘形成黑晕；叠加 `glassBorder` 0x33FFFFFF 半透明白边框在深底上显得发黑 |

### P2 · 体验与一致性（视觉/布局打磨）

| 编号 | 页面 | 问题现象 | 根因（已定位） |
|---|---|---|---|
| P2-1 | 背题知识卡 | "知识点已掌握 10/0"与"已会 10/0"内容重复 | `knowledge_memorize_page.dart:270` 顶部只有一处"已会 x/y"；但 231 行 `masteredNow = _mastered.length + _preMastered` 语义即"已会"，另一处显示疑似来自 AppBar 标题区或卡片正面，需核对后去重；同时数字"10/0"（分母应为总数）疑似计算反转 |
| P2-2 | 模拟考答题卡 | 与刷题答题卡界面不统一，顶部大片空白、6 列固定布局 | `mock_exam_page.dart:496` DraggableScrollableSheet 套 showIOSModalSheet 双层容器；标题下方大量空白；GridView 固定 6 列（刷题答题卡已响应式 4-10 列）；格子用 InkWell 水波纹 |
| P2-3 | 使用帮助弹窗 | 空白太多、字体太小、排版不整齐 | `settings_v3_page.dart:514` showIOSModalSheet 默认 `maxHeightFactor=0.82`，内容少但容器被撑大；`footnote` 字号偏小；纯文本无层级 |
| P2-4 | 章节知识横屏页 | 内容挤在右侧、左侧大片空白、底部出现"73 无效" | `chapter_overview_page.dart:216` `Center`+`ConstrainedBox(maxWidth: effectiveContentWidth)` 在横屏 iPad 下 maxWidth 计算导致内容偏右；"73 无效"疑似章节知识点统计提示文案异常 |

---

## 二、修复规划（按依赖排序）

### 批次 R1 · 手势路由重构（修 P0-1/2/3 之根，阻断一切弹窗/卡死问题）
**核心思路**：全屏手势改为"系统级返回与页面内横向交互共存"的方案：
1. `_FullScreenBackGestureDetector` 手势识别区域从全屏改为**左侧 1/3 屏宽**（iOS 真实惯例：全屏返回主要从屏幕左缘起手；用户需求"不需要边界右滑"可保留到 40%），并给内部横向滚动组件让路。
2. `onCancel` 时彻底复位 `_isBackGesture` + `_dragOffset` + `_snap`，杜绝卡死。
3. 弹窗问题根治：`showIOSActionSheet`/`showIOSModalSheet` 弹出时**临时禁用手势层**（手势层根据 route 的 `animation.isAnimating` 或 overlay 判定让位），或在手势层外层加 `IgnorePointer` 由 bottom sheet 的 barrier 接管。
4. 简化实现：不再手动 `Transform.translate` 跟手（这是"浮动卡片"来源），改由 `Navigator.pop` 前用原生转场，或保留跟手但限制位移到 1/4 屏宽且始终可被弹窗打断。

### 批次 R2 · 深色适配（修 P1-1/1-2）
1. 答题卡三态底色 `_greenBg/_redBg/_greyBg/_greenFg/_redFg/_greyFg` 改为**随主题切换**：浅色用现有浅色系，深色用 `IOSColors` 深色语义（successBg/dangerBg/fill2 + success/danger/text）。
2. 底栏黑边：深色阴影 `Color(0x80000000)` → 收窄到 `Color(0x40000000)` + blur 24 + 偏移 (0,6)；或深色下 `showShadow:false` 改用浅色边框区分。

### 批次 R3 · 背题导航层级修复（修 P0-4）
`memorize_v3_page.dart:60` 从 `Navigator.push` 改为与章节页一致的 `context.go('/bank/xx/chapters')`，让 go_router 统一管理嵌套栈，消除"push + go 混用"导致的额外层级。

### 批次 R4 · 答题卡统一（修 P2-2）+ 知识卡进度去重（修 P2-1）
1. mock 答题卡改为与刷题答题卡同一套视觉：响应式列数、无 InkWell 水波纹、紧凑布局（去掉 DraggableScrollableSheet 双层）。
2. 背题知识卡顶部进度只保留一处，修正"10/0"为"已会 x/total"。

### 批次 R5 · 弹窗与横屏打磨（修 P2-3/2-4）
1. 帮助/背题/反馈弹窗：`maxHeightFactor` 按内容自适应（内容少时收缩），字号 body、加列表层级。
2. 章节知识横屏：`effectiveContentWidth` 在横屏下改用 `maxWidth(720)` 且左右居中（`Center` 已居中，疑为 padding 不对称），核对底部统计文案。

---

## 三、验收标准
- 每批：`flutter analyze --no-pub` 0 issues；代码审查（无魔法数字、走 V3 令牌）
- R1 后：真机验证右滑返回正常、慢滑不再弹浮动卡片、设置/今日/背题弹窗正常弹出
- R2 后：深色模式答题卡无浅色块、底栏无黑边
- R3 后：背题→科目→章节→概览一次右滑逐级返回、无多余层级
- 全部完成后：统一 commit + push + GitHub Actions 构建 IPA + 爱思助手装机

---

## 四、附：真机截图存档
`docs/review-2026-09-04/01.png ~ 07.png`（本仓库已入库）
