# UI 与动效优化设计方案 v1

- 项目：考研刷题 App（Flutter，v1.3.0+14）
- 日期：2026-08-29
- 状态：待确认后分阶段实施

---

## 0. 设计目标与原则

**目标**：在不增加学习干扰的前提下，让 App 从"能用"升级到"有质感、有手感"——视觉更统一、反馈更清晰、导航更顺滑。

**核心原则**（贯穿所有改动）：

1. **学习工具优先**：所有美化服务于专注与反馈，不做纯装饰性炫技
2. **动效克制**：时长 150~300ms，统一 `easeOut` 曲线，可全局降级
3. **可配置**：主题/动效都走现有 `AppThemeConfig` 体系，用户可关可调
4. **零新依赖**：全部用 Flutter 自带组件 + CustomPaint 自绘，不引入第三方 UI/动画库
5. **不碰数据层**：本方案只改 UI/动效层，题库、判分、调度逻辑不动

---

## 1. UI 优化方案

### 1.1 主题预设一键切换（P1）

**现状**：只有手动调色盘（主色/背景/圆角/透明度），用户得自己调。

**方案**：内置 4 套预设，设置页顶部加一行「主题预设」横向卡片，点一下整套切换：

| 预设名 | 主色 | 背景 | 卡片 | 圆角 | 适用 |
|---|---|---|---|---|---|
| 墨绿（默认） | `#00696D` | `#F4F7F6` | 白 | 16 | 当前默认，延续 |
| 纸米 | `#8B6F47` | `#F5EFE3` | `#FBF7EE` | 18 | 笔记/手账感，护眼 |
| 经典蓝 | `#1A56DB` | `#F5F7FA` | 白 | 14 | 清爽工具感 |
| 夜间 | `#4DB6AC` | `#101418` | `#1E2428` | 16 | 深色模式（现有） |

**实现**：在 `AppThemeConfig` 加 `static const presets`，设置页加预设选择器；选中后写入持久化配置（复用现有机制）。

**涉及文件**：`theme_controller.dart`、`settings_theme_panel.dart`

### 1.2 统一卡片组件与层次（P1）

**现状**：各页面卡片样式不统一（有的用 Card、有的用 Container 手搓），阴影偏平，层次感弱。

**方案**：新建 `ui/widgets/app_card.dart` 统一卡片组件：

- 圆角走主题 `cornerRadius`
- 阴影：`BoxShadow(blurRadius: 12, spreadRadius: -4, color: 黑 6%)`（柔和不突兀）
- 内边距统一 16
- 支持 `onTap`（自带点按微动效，见 §2.2）

所有章节卡、统计卡、设置项卡、答题卡统一替换为 `AppCard`。

**涉及文件**：新建 `app_card.dart`；`bank_page.dart`、`home_page.dart`、`stats_page.dart`、`settings_page.dart`、`mock_exam_list_page.dart` 等替换。

### 1.3 首页信息重排（P1）

**现状**：首页信息密度偏高，入口平铺，重点不突出。

**方案**：首页改为「三主卡 + 快捷区」结构：

```
┌─────────────────────────┐
│  顶部：问候 + 考试倒计时（象征性）  │
├─────────────────────────┤
│  【今日进度主卡】           │
│   进度环 + 今日已刷/目标    │
│   正确率迷你趋势（近7天）    │
├─────────────────────────┤
│  【模拟考主卡】  【背题主卡】  │
│   两栏并排，点击进入         │
├─────────────────────────┤
│  快捷入口：错题本 / 统计 / 设置 │
└─────────────────────────┘
```

- 进度环用 CustomPaint 自绘（带动画，见 §2.5）
- 今日进度卡是视觉焦点，尺寸最大

**涉及文件**：`home_page.dart`

### 1.4 统计页可视化（P2）

**现状**：纯数字列表。

**方案**：加两个轻量图表（CustomPaint 自绘，零依赖）：

- **正确率趋势迷你折线图**：近 7/14/30 天切换，点按显示当日数值
- **章节掌握度雷达图**：5 科或某科各章节的正确率分布，一眼看出薄弱章节

数字保留，图表作为补充，不替代。

**涉及文件**：`stats_page.dart`，新建 `ui/widgets/mini_charts.dart`

### 1.5 内置纹理背景（P2）

**现状**：背景图功能已支持，但用户得自己找图。

**方案**：内置 2~3 张浅色纸纹/水墨纹理（PNG，每张 < 200KB），主题预设里可选；透明度走现有 `backgroundOpacity` 滑块。

**素材来源**：可用纯色 + 噪点自生成（Python 生成 PNG），或用你笔记的水墨风格。**需要你确认风格**。

**涉及文件**：`assets/textures/`、`theme_controller.dart`、`settings_theme_panel.dart`

---

## 2. 动效优化方案

### 2.1 判题反馈动效（P0，最核心）

**现状**：选完答案后纯颜色变化，无过渡。

**方案**：

| 场景 | 动效 | 时长 |
|---|---|---|
| 答对 | 正确选项背景 150ms 渐变绿 + 缩放 1.0→1.03→1.0（弹性）+ 勾号淡入 | 250ms |
| 答错 | 选中项 150ms 渐变红 + 水平抖动 3 次（±4px）；同时正确项变绿提示 | 300ms |
| 解析卡片 | 判题后从底部滑入 + 淡入（SlideTransition + FadeTransition） | 250ms |
| 多选提交 | 同上，按最终结果统一反馈 | — |

**实现**：在 `practice_question_view.dart` 用 `AnimationController` + `AnimatedBuilder`；抖动用 `TweenSequence`。

**涉及文件**：`practice_question_view.dart`、`practice_page.dart`

### 2.2 全局点按微动效（P0）

**现状**：卡片/按钮按下无反馈（或只有水波纹）。

**方案**：新建 `PressableCard`（基于 `AnimatedScale` + `GestureDetector`）：

- 按下：缩放 1.0 → 0.97，阴影减弱，100ms `easeOut`
- 抬起：回弹 0.97 → 1.0，150ms `easeOut`
- 所有 `AppCard`、选项按钮、主卡、设置项统一使用

选项按钮额外：选中时缩放 1.0→1.02 + 边框高亮，150ms。

**涉及文件**：新建 `ui/widgets/pressable_card.dart`；全局替换。

### 2.3 切题过渡（P1）

**现状**：题目卡片硬切换。

**方案**：下一题/上一题时，题目卡片做 120ms 横向微滑入（方向跟随前进/后退）+ 淡入；用 `AnimatedSwitcher` + `SlideTransition`，key 用题目 id。

**涉及文件**：`practice_question_view.dart`

### 2.4 导航过渡补全（P1）

**现状**：页面级已有 iOS 横向滑动，但无 Hero、无列表交错。

**方案**：

- **Hero 共享元素**：章节卡 → 章节详情页时，章节标题/封面"飞"过去（`Hero` tag 用章节 id）。仅对章节卡启用，避免滥用。
- **列表交错入场**：首页/章节列表/统计页首次进入时，条目逐个 fade+上滑，间隔 40ms，总时长 ≤ 400ms（`SlideTransition` + 错峰 `Interval`）。返回时不重播（用 `AutomaticKeepAliveClientMixin` 或状态标记）。
- **Tab 指示条**：底部导航/章节 Tab 的指示器做平滑横移（`AnimatedPositioned` 或 `TabBar` 自带 indicator animation）。

**涉及文件**：`bank_page.dart`、`chapter_overview_page.dart`、`home_page.dart`、`root_page.dart`

### 2.5 数据动效（P2）

- **进度环动画**：首页进度环首次进入/数值变化时，从 0 动画到目标值（`AnimationController` + CustomPaint），600ms `easeOut`。
- **数字 count-up**：统计页正确率/刷题数从 0 滚动到目标值，500ms。
- **模拟考交卷结算**：交卷后成绩卡做放大淡入 + 正确率环动画，800ms（克制，不做撒花）。

**涉及文件**：`home_page.dart`、`stats_page.dart`、`mock_review_page.dart`

### 2.6 动效统一与降级（P0 配套）

- 在 `AppThemeConfig` 加 `reduceMotion` 开关（默认关），开启后：所有非必要动效时长减半或直接跳过，仅保留判题颜色反馈。
- 所有动效时长集中定义在 `ui/widgets/animation_constants.dart`：
  ```dart
  class Durations {
    static const fast = 120;   // 点按
    static const normal = 200; // 判题/切题
    static const slow = 300;   // 页面/列表
  }
  class Curves {
    static const standard = Curves.easeOutCubic;
  }
  ```

**涉及文件**：新建 `animation_constants.dart`；`theme_controller.dart` 加字段；全局引用。

---

## 3. 实施优先级与分阶段

| 阶段 | 内容 | 预估改动量 | 价值 |
|---|---|---|---|
| **P0 手感** | 判题反馈动效 + 全局点按微动效 + 动效统一/降级 | 中（2 个新组件 + 做题页改造） | ★★★★★ 每次做题都感知 |
| **P1 视觉** | 主题预设 + 统一卡片层次 + 首页重排 + 切题过渡 + 导航过渡（Hero/交错/Tab） | 大（多页面替换 + 首页重构） | ★★★★ 整体观感升级 |
| **P2 数据/氛围** | 统计可视化 + 进度环/数字动效 + 内置纹理背景 + 模拟考结算 | 中 | ★★★ 锦上添花 |

**建议执行顺序**：P0 → P1 → P2，每阶段独立可发布、可回退。

---

## 4. 涉及文件总览

**新建**：
- `ui/widgets/app_card.dart`（统一卡片）
- `ui/widgets/pressable_card.dart`（点按微动效）
- `ui/widgets/animation_constants.dart`（时长曲线常量）
- `ui/widgets/mini_charts.dart`（P2 迷你图/雷达）
- `assets/textures/`（P2 纹理图）

**修改**：
- `theme_controller.dart`（预设 + reduceMotion）
- `settings_theme_panel.dart`（预设选择器 + 动效开关）
- `practice_question_view.dart`（判题动效 + 切题过渡 + 选项动画）
- `practice_page.dart`（配合）
- `home_page.dart`（重排 + 进度环 + 交错）
- `bank_page.dart`（AppCard + Hero + Tab 指示）
- `chapter_overview_page.dart`（Hero 目标）
- `stats_page.dart`（可视化 + count-up）
- `mock_review_page.dart`（结算动效）
- `root_page.dart`（Tab 指示）
- 其他页面：AppCard 替换（`settings_page.dart`、`mock_exam_list_page.dart`、`wrong_book_page.dart`、`memorize_page.dart` 等）

---

## 5. 验收标准

1. `flutter analyze`：0 issues
2. `flutter test`：61 个用例全绿（动效不影响判分逻辑）
3. P0 验收：做题时答对/答错有明确动效反馈，所有卡片点按有缩放反馈
4. P1 验收：4 套主题预设可一键切换且持久化；首页三主卡结构；章节卡→详情有 Hero
5. 性能：中低端机（骁龙 6 系）动效不丢帧，`reduceMotion` 开启后动效明显减弱
6. 不破坏现有功能：刷题、模拟考、背题、备份、审题标记全部回归正常

---

## 6. 风险与权衡

| 风险 | 应对 |
|---|---|
| 首页重排可能影响你已习惯的入口位置 | 重排前先出首页线框图给你确认，不直接改 |
| 全局替换 AppCard 可能引入样式回归 | 逐页面替换 + 每页面手动过一遍，analyze+test 兜底 |
| 判题动效与现有答题状态机耦合 | 动效只挂在 UI 层，不碰 `practice_page` 的状态逻辑 |
| 纹理背景素材风格不确定 | P2 阶段先出 2~3 张样图给你挑，不直接定 |
| 动效过量干扰学习 | 统一 150~300ms + reduceMotion 开关，默认克制 |

---

## 7. 需要你确认的点

1. **执行范围**：按 P0→P1→P2 全做，还是先只做 P0？
2. **主题预设风格**：4 套（墨绿/纸米/经典蓝/夜间）是否合适？要不要加/减？
3. **首页重排**：三主卡结构是否符合你的使用习惯？要不要先出线框图？
4. **纹理背景**：是否需要？想要什么风格（纸纹/水墨/纯色）？
5. **reduceMotion 开关**：放在主题定制页，默认关，是否 OK？
