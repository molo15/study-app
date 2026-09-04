# 考研刷题 App V3 — iOS 风格 UI 设计实现方案 v1.0

> 版本：v1.0　·　日期：2026-09-03　·　状态：待评审执行
> 依据：《iOS 风格 UI 重设计规格文档 v1.0》（下文简称"规格"）
> 配套设计参考：`docs/prototype/ui-v3-ios.html`（V3 设计稿，含 5 形态 × 12 页）
> 关联文档：`docs/设计理念.md`、`docs/设计稿-各端对应与iOS适配说明.md`、`docs/UI-v2-冷磨砂实施方案-v1.0.md`

---

## 0. 阅读指引

本文档是 V3 从"设计定稿"到"Flutter 落地"的唯一执行方案。它与规格文档 §9「Flutter 实现技术方案」直接衔接：规格给出**组件规格与主题代码基线**，本文档给出**页面级改造顺序、现有代码映射、多端（含 iPad mini/平板）落地细则与验收清单**。V3 设计参考 `ui-v3-ios.html` 是视觉与交互的逐像素依据，实现时以本文档 + HTML 为准。

---

## 1. 概述与目标

### 1.1 背景
- V2 冷磨砂已完成多端结构骨架（形态切换器 + 设备外框 + iOS 状态栏 + 侧边栏 + 13 页）。
- V3 目标：全面转向 iOS 原生设计语言——去 Material 化、内容纯白无阴影、液态玻璃只用于悬浮 UI、底部悬浮导航、iOS 分组列表、克制配色。
- **V3 独立成稿，不复用 V2 覆盖关系**：V2 保留，V3 在独立分支/独立页面推进，验收通过后决定是否替换。

### 1.2 与设计理念.md 的对齐
| 设计宪法条目 | V3 落地 |
|---|---|
| 知识点记忆迁移主线 | 背题双模式（知识卡片/题目）+ SRS 状态标签（新词/学习中/复习中/已掌握）贯穿背题链路 |
| 记忆-应用分层 | 「背题」（记忆层）与「答题/模拟考」（应用层）在 Tab 与页面结构上显式分层 |
| 流动 | 页面滑动切换、背题卡 3D 翻转、弹窗底部滑入、导航栏滚动渐变 |
| 沉浸 | 大标题 + 大留白 + 克制用色，内容区纯白无干扰 |
| 质感 | 液态玻璃仅限悬浮元素，0.5px 细分隔线，连续圆角 |

### 1.3 已确认软件事实（实现硬约束）
- 底部 5 Tab：**今日 / 题库 / [背题中央圆钮] / 统计 / 我的**（背题为中央突出圆钮，非普通 Tab）。
- 标记语义定稿：
  - **存疑 = ◆ 菱形**：仅模拟考、会话级（不落库，退出考试即失效）。
  - **审题 = 🚩 旗子**：仅练习、默认关闭，落库 `review_flags`。
- 背题模式：**知识卡片 / 题目** 双模式。
- 五科题库 4504 题（教育学 1280 / 心理学 980 / 古代汉语 860 / 文学理论 720 / 政治 664）。

---

## 2. 设计定稿（Design Tokens 落地清单）

> 全部令牌与规格 §2 一致，V3 HTML 中已按此实现并逐项审计通过。落地时统一收敛到 `lib/ui/theme/ios_tokens.dart`，禁止魔法数字。

### 2.1 颜色（浅色 / 深色）
| 令牌 | 浅色 | 深色 | 用途 |
|---|---|---|---|
| `bg` | `#F2F2F7` | `#000000` | 分组背景 |
| `card` | `#FFFFFF` | `#1C1C1E` | 卡片/列表/分组 |
| `fill` | `#F2F2F7` | `#2C2C2E` | 分段控件/按压态/图标按钮底 |
| `fill2` | `#E9E9EA` | `#3A3A3C` | 进度轨道/开关轨道 |
| `text` | `#000000` | `#FFFFFF` | 主文字（纯黑，非深灰） |
| `text2` | `#8E8E93` | `#98989E` | 次文字 |
| `text3` | `#AEAEB2` | `#6E6E73` | 三级文字 |
| `placeholder` | `#C7C7CC` | `#48484A` | 占位符 |
| `primary` | `#007AFF` | `#0A84FF` | 主色（iOS 蓝） |
| `primaryPressed` | `#0066D6` | `#409CFF` | 主色按压 |
| `success` | `#34C759` | 同 | 正确/成功 |
| `warning` | `#FF9500` | 同 | 存疑/警告 |
| `danger` | `#FF3B30` | 同 | 错误/删除 |
| `separator` | `#C6C6C8` | `#38383A` | 0.5px 细分隔线 |
| `cardBorder` | `rgba(0,0,0,0.06)` | `rgba(255,255,255,0.08)` | 卡片极淡边框 |
| `glass` | `rgba(255,255,255,0.62)` | `rgba(28,28,30,0.62)` | 液态玻璃（regular） |
| `glassThin` | `rgba(255,255,255,0.55)` | `rgba(28,28,30,0.55)` | 液态玻璃（thin） |

> 主色使用原则：**只用于关键操作**（主按钮、选中态、链接、进度条、Tab 选中）。科目图标允许使用 Apple 系统功能色区分（教育学蓝 / 心理学橙 / 古代汉语绿 / 文学理论紫 / 政治红），属功能色而非装饰。

### 2.2 字号 / 行高
`34 bold`（大标题）→ `28 bold`（标题1）→ `22 bold`（标题2）→ `20 semibold`（标题3）→ `17 regular`（正文）→ `15`（次正文）→ `13`（小字）→ `12`（标签）。行高：大标题/标题 1.2，正文 1.5，小字 1.4。等宽数字（进度/倒计时/分数）用 SF Mono。

### 2.3 间距 / 圆角
- 间距：8 的倍数；页面左右 16/24/32（按断点），卡片内 16，列表项 14 上下，区块 24，列表组间距 20。
- 圆角（连续圆角）：大卡片/弹窗 18，内容卡片 16，小卡片/列表组 12，主按钮 12，标签 8，图标按钮 10，胶囊/分段 完全圆角。Flutter 用 `BorderRadius.circular()` 近似，进阶接 `continuous_radius` 包。

### 2.4 阴影（克制）
仅悬浮元素有阴影：Tab Bar `0 8px 32px rgba(0,0,0,0.12)`、玻璃容器 `0 8px 32px rgba(0,0,0,0.10)`、弹窗 `0 16px 48px rgba(0,0,0,0.15)`、主色 FAB `0 8px 24px rgba(0,122,255,0.30)`。**内容卡片/列表/按钮一律无阴影**。

### 2.5 液态玻璃（Liquid Glass）
| 变体 | 模糊 | 透明度 | 用途 |
|---|---|---|---|
| thin | sigma 18 | 0.55 | 导航栏、刷题/背题底部操作栏 |
| regular | sigma 24 | 0.62 | Tab Bar、侧边栏 |
| thick | sigma 32 | 0.75（实现取 0.62+高光） | 弹窗/ActionSheet |

结构：`BackdropFilter(blur) + 半透明底 + 0.5px 边框（顶部更亮 rgba(255,255,255,0.4)）+ 顶部 40% 高光渐变 + 阴影`。

---

## 3. 技术方案（Flutter 落地）

### 3.1 主题系统
按规格 §9.1 创建 `lib/ui/theme/ios_theme.dart`：`lightTheme()` / `darkTheme()` 两个工厂，输出 `ThemeData`（`useMaterial3:true`、`scaffoldBackgroundColor: bg`、`splashFactory: NoSplash.splashFactory`、`cardTheme.elevation=0`、`appBarTheme` 透明+无 elevation、`dividerTheme 0.5px`）。全部颜色通过 `Theme.of(context)` / 自定义 `IOSTheme` 取色，禁止硬编码。

### 3.2 组件清单（规格 §9.2 全量）
| 组件 | 文件建议 | 关键规格 | 优先级 |
|---|---|---|---|
| `LiquidGlass` | `widgets/liquid_glass.dart` | blur+高光+边框，`RepaintBoundary` 包裹 | P0 |
| `FloatingTabBar` | `widgets/floating_tab_bar.dart` | 底部悬浮 20px、**胶囊形（圆角 999px）**、**宽度自适应（宽−边距，max 680）**、5 Tab、中央背题圆钮 58×58 | P0 |
| `FloatingActionBar` | `widgets/floating_action_bar.dart` | 上一题/进度/下一题，52px 高，16px 圆角 | P0 |
| `LargeTitleScaffold` | `widgets/large_title_scaffold.dart` | 大标题 + 滚动渐变液态玻璃 | P0 |
| `IOSCard` | `widgets/ios_card.dart` | 纯白、16px 圆角、无阴影、0.5px 边框可选 | P0 |
| `IOSButton` | `widgets/ios_button.dart` | 主/次/危险/文本四态，无阴影 | P0 |
| `IOSListGroup / IOSListItem` | `widgets/ios_list.dart` | 分组列表，inset grouped，0.5px 分隔线 | P1 |
| `IOSAlert / IOSActionSheet` | `widgets/ios_dialog.dart` | 居中 Alert / 底部滑入 ActionSheet | P1 |
| `IOSSegmentedControl` | `widgets/ios_segmented.dart` | Cupertino 风格分段 | P1 |
| `IOSTag` | `widgets/ios_tag.dart` | 状态标签（蓝/绿/橙/红/灰） | P2 |
| `IOSProgressBar / IOSRing` | `widgets/ios_progress.dart` | 线性/环形进度 | P2 |
| `FAB` | `widgets/ios_fab.dart` | 答题卡入口等 | P2 |
| `HeatmapView / LineChartView` | `widgets/charts/` | 日历热力图 / 正确率折线（CustomPaint） | P2 |

### 3.3 底部悬浮系统（关键改造）
- 移除 `Scaffold.bottomNavigationBar`，改用 `Stack`：`body` 内容 + `Positioned(bottom: 20 + MediaQuery.padding.bottom, child: Center(...))` 承载悬浮栏。
- **宽度自适应规则（"屏幕宽 − 左右边距"，V3 HTML 已实现并逐形态验收）**：compact（<600）为 `宽 − 48px`（左右各 24px）；medium（600–1200）为 `宽 − 64px`（左右各 32px）并设 `maxWidth 680px` 居中——平板横屏 1024 下收敛为 680px 居中，避免过宽失真；桌面 expanded 隐藏 Tab Bar、改用侧边栏。
- **胶囊形（圆角 999px）**：底栏高 60，左右收窄后观感更"悬浮"；`FloatingActionBar` 同步采用同宽度规则（高 52，胶囊形）。
- 内容区统一底部 padding 常量 `kTContentBottomInset = 80 + MediaQuery.padding.bottom`，所有可滚动页面套用，保证最后一条内容不被悬浮栏遮挡（V3 HTML 中 `page padding-bottom:120px` 即为该常量的一次具象）。
- **背题中央圆钮（保证不被裁切）**：FloatingTabBar 中间项渲染为 **58×58** 主色圆角块（圆角 20），**向上凸起 32px**、`z-index 60` 置于底栏之上，容器**不设 `overflow:hidden`**（底栏 `::before` 高光用 `border-radius:inherit` 收角），中央 Tab `z-index 2`、标签 `margin-top:34px` 让位——保证 iPhone 竖屏（含 Home Indicator 安全区）与 iPad/平板形态完整可见、不被底栏或相邻 Tab 裁切。

### 3.4 去 Material 化改造清单
1. 全局 `ThemeData.splashFactory = NoSplash.splashFactory`。
2. 所有 `InkWell`/`GestureDetector` 点击反馈改为 `highlightColor: transparent` + 自定义浅灰 `#F2F2F7` 高亮（100ms），保留 `InkResponse` 仅用于命中区域。
3. `Card` → 自绘 `IOSCard`（Container 纯白圆角，`elevation:0`）。
4. `showDialog` → `IOSAlert`；`showModalBottomSheet` → `IOSActionSheet`（底部滑入 + 弹簧）。
5. `CupertinoSwitch`、`CupertinoSegmentedControl`、`CupertinoSlider` 等原生组件按规格接入。

### 3.5 多端断点与形态适配（含 iPad mini / 平板）
用 `LayoutBuilder` + 断点常量实现三档，**与 V3 HTML 的 container 查询一一对应**：
| 断点 | 判定 | 页面边距 | 内容最大宽 | 底部导航 | 说明 |
|---|---|---|---|---|---|
| compact | `<600` | 16 | 100% | 悬浮 Tab Bar | iPhone 竖屏（390×844） |
| medium | `600–1200` | 24 | 760 | 悬浮 Tab Bar | iPad mini 竖屏（744×1133）、iPad 竖屏（768×1024）、平板横屏（1024×768） |
| expanded | `>=1200` | 32 | 920 | 桌面侧边栏 | 桌面（1280×800 起） |

**桌面侧边栏**：宽屏时底部 Tab Bar 自动隐藏，左侧出现 66px 图标栏，可展开为 232px（展开显示文字，收起仅图标）；用 `AnimatedContainer` 宽度切换。
**iPad mini 专属要点**：
- 744 逻辑宽度属 medium，但偏窄，卡片列数保持 1–2 列（`minmax` 自适应，不强制 3 列）。
- 背题卡翻转卡、答题卡弹窗在 744 宽下居中 480 固定宽，左右留白。
- 分屏/悬浮窗（Slide Over 约 375pt）时自动落入 compact，所有页面三档可退化（`LayoutBuilder` 天然支持，无需额外分支）。
**平板横屏（1024×768）**：属 medium 但横向充裕，首页英雄区可 2 列、统计页五科环形 1 行排开；题库科目卡 2 列。
**刷题页双栏**（规格 §8.2）：仅 expanded（>=1200）启用「题目左 + 答题卡右 280px」。

### 3.6 深色模式（三段切换）
- `theme_controller.dart` 提供 **三态**：`跟随系统（auto）/ 浅色（light）/ 深色（dark）`。`auto` 监听 `MediaQuery.platformBrightness`（HTML 侧对应 `prefers-color-scheme` + `matchMedia('change')` 自动跟随）；`light/dark` 为自定义强制覆盖（设置页 `我的·外观` 开关在强制浅/深间切换）。
- 深色令牌按规格 §8.5：背景 `#000000`（次级填充/按压 `#1C1C1E`）、卡片 `#2C2C2E`、分隔线 `#38383A`、液态玻璃 `rgba(28,28,30,0.62)`、主色 `#0A84FF`。所有页面颜色走令牌，逐页验收防黑底黑字。

### 3.7 标记语义与数据落库
- **存疑 ◆**：模拟考答题模型新增会话级字段 `doubted: Set<int>`（题目 id），仅存内存/会话作用域，交卷或退出即清空。答题卡网格中 ◆ 题显示橙色菱形角标。
- **审题 🚩**：练习答题模型新增 `reviewFlagged: Set<int>`，默认关闭（设置页开关），答题卡网格右上角 🚩 角标；落库 `review_flags` 表，进入错题/收藏链路。
- 背题双模式：`KnowledgeMemorizePage` 增加模式分段控件（知识卡片 / 题目），卡片正面/背面渲染随模式切换（知识卡片显示知识点，题目模式显示题干→答案+解析）。

### 3.8 动效
按规格 §7：页面切换（右滑入+淡入 300ms）、Tab 切换内容淡入 150ms、弹窗底部弹簧滑入 350ms、背题卡 3D 翻转 500ms、导航栏滚动渐变（跟随滚动）、按钮 scale 0.96→1.0 150ms、进度条 300ms ease-out。接入 `MediaQuery.disableAnimations` 尊重"减少动态效果"。

---

## 4. 现有页面 → V3 设计稿映射

| 现有代码（`lib/ui/`） | V3 设计稿页面 | 改造要点 |
|---|---|---|
| `home_page.dart` | 首页 | 大标题 + 今日任务卡 + 五科分组列表 + 悬浮 Tab Bar |
| `bank_page.dart` | 题库 | 搜索框 + 科目卡（带进度）+ 快捷入口（错题本/模拟考/背题） |
| —（新增） | 章节概览 | 总体进度卡 + 章节分组列表（每章内联进度） |
| `knowledge_memorize_page.dart` | 背题总览 / 背题卡 | SRS 队列卡 + 四象限 + 3D 翻转卡 + 悬浮操作栏（忘记/环形进度/记住） |
| `practice_question_view.dart` | 答题 | 液态玻璃导航 + 题目卡 + 选项选中态 + 解析折叠 + 悬浮操作栏 + 答题卡弹窗 |
| —（新增） | 答题卡 | 悬浮弹窗（已答/未答/◆存疑/🚩审题）网格 + 交卷 |
| `mock_exam_list_page.dart` | 模拟考 | 设置卡（科目/题量/时间/难度）+ 开始 + 历史记录 + 考试中视图（倒计时/进度/交卷） |
| —（新增） | 结果 | 成绩环形 + 用时/正确率/排名 + 题型正确率 + 错题回顾 |
| `stats_page.dart` | 统计 | 概览 4 项 + 热力图 + 五科环形 + 正确率折线（分段控件 今日/本周/本月/全部） |
| `root_page.dart` | （Tab 容器） | 改为悬浮 Tab Bar + 中央背题圆钮 + 页面栈管理 |
| —（新增） | 错题本 | 统计卡 + 错题分组列表（我的答案/正确答案/重做） |
| —（新增） | 我的 | 用户卡 + 学习/背题/外观/数据/关于 分组列表（深色模式开关、审题🚩开关、存疑◆开关） |

> 说明：规格 §6 定义的页面结构为本表设计稿内容；`bank_page` 等页面若含原 13 页体系中未在此列出的页（如收藏/设置二级页），沿用同一组件体系补齐。

---

## 5. 分阶段实施计划

### 阶段 1：设计系统落地（1–2 天）
任务：`ios_theme.dart`（浅/深）、`LiquidGlass`、`FloatingTabBar`、`IOSButton/IOSCard`、`main.dart` 全局挂主题；`NoSplash` 全局限波纹。
验收：主题切换正常；玻璃组件渲染正确；Tab Bar 悬浮不遮挡；`flutter analyze` 0 issues。

### 阶段 2：核心四页重做（3–5 天）
任务：首页、答题（含答题卡弹窗）、背题（总览+卡+双模式+SRS）、统计。
验收：四页视觉对齐 V3 HTML；交互正常；无涟漪/无塑料感；analyze 0。

### 阶段 3：次级页面 + 组件完善（2–3 天）
任务：题库、章节概览、模拟考（设置+考试中）、结果、错题本、我的；`IOSAlert/IOSActionSheet/IOSListGroup` 全量替换。
验收：全部页面视觉统一；弹窗/列表全 iOS 风。

### 阶段 4：动效 + 多端适配（2–3 天）
任务：页面切换/翻转/弹窗弹簧动效；断点三档；**桌面侧边栏 66↔232**；**iPad mini 744 与平板 1024 专项适配**；深色模式完善；分屏退化；Reduce Motion。
验收：三档断点逐形态（iPhone/iPad mini/iPad/平板横屏/桌面）截图对比 V3 HTML，无遮挡无溢出。

### 阶段 5：性能 + 全量验收（1 天）
任务：液态玻璃 RepaintBoundary/缓存、列表 item 缓存、滚动 60fps；全流程回归（含 SRS、存档、review_flags）；真机多尺寸。
验收：规格 §11 全量 checklist。

---

## 6. 验收标准（Checklist）

### 6.1 视觉
- [ ] 内容卡片纯白、无阴影；液态玻璃仅出现在悬浮元素（Tab Bar/操作栏/FAB/弹窗/侧边栏）。
- [ ] 无 Material 涟漪；点击为浅灰高亮。
- [ ] 底部悬浮 Tab Bar：距底 20px、**胶囊形（圆角 999px）**、高 60、**宽度自适应（compact 宽−48、medium 宽−64 上限 680 居中）**、液态玻璃；**中央背题圆钮 58×58 凸起 32px 完整可见**。
- [ ] 大标题 + 滚动后液态玻璃导航；iOS 分组列表；0.5px 分隔线。
- [ ] 配色克制（主色只用于关键操作）；字号 34/28/22/20/17/15/13/12；连续圆角 12/16/18。

### 6.2 交互
- [ ] 页面 iOS 滑动切换、背题 3D 翻转、弹窗底部弹簧、按钮 scale、开关 CupertinoSwitch、分段 CupertinoSegmented。
- [ ] 深色模式三段切换（跟随系统 / 浅色 / 深色）：`auto` 随系统自动切换，浅/深为强制覆盖。

### 6.3 功能
- [ ] 首页五科 4504 题；答题选择/解析/答题卡；背题翻转/记住/忘记/SRS；统计图表；模拟考全流程；存疑◆会话级；审题🚩落库 review_flags。

### 6.4 多端
- [ ] iPhone 竖屏 / iPad mini 竖屏 / iPad 竖屏 / 平板横屏 / 桌面（侧边栏）五形态布局正常，逐形态截图对比 V3 HTML 无遮挡无溢出；底栏按"宽−边距"自适应（平板横屏 680 居中），中央背题圆钮各形态完整可见。
- [ ] 桌面侧边栏 66↔232 可折叠；expanded 刷题双栏；深色模式（含三段切换）全页面正常。

### 6.5 性能与代码质量
- [ ] 冷启动 <2s、滚动 60fps、液态玻璃无性能塌陷；`flutter analyze` 0、测试全绿；设计令牌统一管理；数据层/SRS/存档/条件导入架构不被破坏（规格 §12.2 硬约束）。

---

## 7. 风险与回退
- 液态玻璃性能：限制模糊区域、`RepaintBoundary` 隔离、避免嵌套大模糊。
- 大标题导航与路由冲突：统一 `LargeTitleScaffold`，逐页迁移。
- 悬浮栏遮挡：统一底部 padding 常量 + 逐页滚动到底验收。
- 深色遗漏：全部走令牌，逐页过深色。
- 回退：旧主题文件保留一键回退；UI 改造独立 git 分支，逐页合并。

---

## 8. 附录

### 8.1 多端视口清单（V3 HTML 已实现并验收）
| 形态 | 逻辑分辨率 | 断点 | 状态栏 | 底部导航 |
|---|---|---|---|---|
| iPhone 竖屏 | 390×844 | compact | 47px + 灵动岛 | 悬浮 Tab Bar |
| iPad mini 竖屏 | 744×1133 | medium | 24px | 悬浮 Tab Bar |
| iPad 竖屏 | 768×1024 | medium | 24px | 悬浮 Tab Bar |
| 平板横屏 | 1024×768 | medium | 24px | 悬浮 Tab Bar |
| 桌面 | 1280×800 | expanded | 无（窗口） | 侧边栏 66↔232px |

### 8.2 验收截图
`docs/prototype/verify/` 下为 V3 HTML 五形态 × 关键页面的 chromium 真实渲染截图（含深色模式），可作实现对照基准。

### 8.3 相关规格引用
规格 §2 令牌、§3 液态玻璃、§4 底部悬浮、§5 组件、§6 页面布局、§7 动效、§8 多端、§9 Flutter 技术方案、§10 里程碑、§11 验收、§12 风险。
