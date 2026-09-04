# UI-v3 修复规划案 v1.0

> 依据：《UI-v3-逐页审查清单合集-v1.0.md》
> 目标：在**不删旧代码**前提下，按"数据正确性 → 组件一致性 → 交互缺口 → 体验打磨 → 深水区"顺序修复审查发现的全部问题
> 执行方式：多 agent 分工 + 每批验收（analyze 0 + 代码走查 + 真机目检）+ 逐批 git 提交
> 关联文档：`docs/UI-v3-逐页审查清单合集-v1.0.md`

---

## 1. 规划原则

1. **数据先行**：统计口径 bug（P0）先修——用户能直接感知数字对错，且影响后续统计相关改动的基线。
2. **组件收口**：Material 残留统一换 iOS 组件，一次改完一处入口（新建 `CupertinoSwitch` 包装等）。
3. **不删旧代码**：只改被用户实际使用、需统一到 V3 风格的页面；V2 保留。
4. **多 agent 分工**：每批一个执行 agent + 一个独立审查 agent，审查不通过不入下一批。
5. **逐批提交**：每批验收通过后 `git commit` + push（自动触发 GitHub Actions iOS 构建），保持 main 可构建。
6. **硬约束**：色用 `IOSColors.of(context)`、动效 `IOSAnimations.of(context)`、间距 `IOSSpacing`、圆角 `IOSRadius`、断点 `IOSBreakpoint`；禁用魔法数字。

---

## 2. 阶段总览

| 批次 | 主题 | 目标 | 工作量 | 依赖 |
|---|---|---|---|---|
| **B1** | 统计页数据口径 | 数字自洽 | 小 | 无 |
| **B2** | Material 残留收口 | 设置页+答题卡 iOS 化 | 中 | 无 |
| **B3** | 交互缺口 | 背题刷新、新题预取、SafeArea | 小 | B2（动效令牌复用） |
| **B4** | 体验打磨 | 柱状图方向、toast、按压反馈、stagger | 中 | B2 |
| **B5** | 深水区 | 全屏返回手势 + 背题翻卡页 V3 化 | 大 | B1-B4 全部完成 |

---

## 3. B1 — 统计页数据口径（P0）

### 目标
总览、题型分布、章节统计三处口径统一，partial 计分明确。

### 改动项（依据清单 §3）
| # | 改动 | 文件 | 要点 |
|---|---|---|---|
| B1-1 | 题型分布 SQL 与总览口径统一 | `quiz_repository_mock.dart` studyStats | 二选一：题型分布也含归档题（对齐总览）；或总览排除归档。**建议统一为"含归档"**（历史已答应计入总成绩，归档只隐藏题位不抹除答题记录） |
| B1-2 | 章节统计补 partial | `quiz_repository_mock.dart` 章节 SQL（~407-429） | partial 计入"已答"（半对半错），正确率按 B1-3 口径 |
| B1-3 | partial 计分口径 | `models.dart` `StudyStats.accuracy`（~680） | **决策点**：partial 按 0.5 计 / 按错计。建议 `accuracy=(correct + 0.5*partial)/total`，需用户拍板 |

### 验收
- 同一用户数据下：总览合计 = 题型分布合计 = 章节合计
- 有半对题时"X 对 / Y 错 / Z 题"满足 X+Y ≤ Z，且已答数 = Z - 未答
- `flutter analyze --no-pub` 0 issues

---

## 4. B2 — Material 残留收口（P1）

### 4.1 设置页（清单 §1）
| # | 改动 |
|---|---|
| B2-1 | 4 个 `AlertDialog`（~468/495/525/554）→ `showIOSModalSheet` |
| B2-2 | 3 个 `Switch`（~661/678/721）+ 每日目标弹窗 `SwitchListTile`（~257）→ iOS 开关（新建 `IOSSwitch` 包装 `CupertinoSwitch`，深色圆钮白色问题随动消失） |
| B2-3 | 每日目标弹窗 `FilledButton`（~293）→ `IOSButton` |
| B2-4 | 2 个 `TextField` 下划线（~171/198）→ iOS 圆角输入框（复用 ios_action_sheet 内输入样式） |
| B2-5 | "使用帮助"文案去"中央圆钮"过时描述 |

### 4.2 答题卡（清单 §5）
| # | 改动 |
|---|---|
| B2-6 | `_confirmJump`（~289）`AlertDialog` → `showIOSActionSheet` 或 `showIOSModalSheet`（统一动效） |
| B2-7 | `_Cell`（~343）`InkWell` → iOS 无涟漪按压（`GestureDetector` + 按压变暗 AnimatedContainer） |
| B2-8 | 顶栏 `theme.textTheme`（~51/57）→ `IOSTypography` |
| B2-9 | 平板浮层遮罩（~606）`Colors.black 0.25` → 玻璃遮罩统一 |
| B2-10 | `GridView.count(6)`（~267）→ 按断点响应式列数（compact 6 / medium 8 / expanded 10，格子最小 40pt） |

### 验收
- 设置页/答题卡截图走查无 Material 控件
- 按压/开关动效符合 iOS 习惯
- `flutter analyze --no-pub` 0 issues

---

## 5. B3 — 交互缺口（P1）

| # | 改动 | 文件 |
|---|---|---|
| B3-1 | 背题页补 `refresh()` + root_page 配 GlobalKey（对齐 home/bank/stats） | `memorize_v3_page.dart` / `root_page.dart` |
| B3-2 | "可新学"不再一次性预取全部，改为限单轮量（如 30）或传参让 PracticePage 内部按需取 | `home_v3_page.dart` ~251 |
| B3-3 | 题库页大标题 SafeArea 顶部 | `bank_home_page.dart` |

### 验收
- 切 Tab 背题页数据刷新；可新学点击响应 <100ms 无卡顿；题库页标题不与状态栏重叠

---

## 6. B4 — 体验打磨（P1-P2）

| # | 改动 | 文件 |
|---|---|---|
| B4-1 | 近 7 日柱状图时间轴反转为今天在右 | `stats_v3_page.dart` `_DailyBars` ~330 |
| B4-2 | 全局 toast 换 iOS 样式（悬浮胶囊，非 SnackBar） | 全局 |
| B4-3 | 视觉按压补齐：IOSCard / FloatingTabBar Tab / ios_action_sheet 选项加按压反馈 | `widgets/ios_card.dart` / `floating_tab_bar.dart` / `ios_action_sheet.dart` |
| B4-4 | 答题卡逐题型分组入场 stagger | `practice_answer_sheet.dart` |
| B4-5 | 深色硬编码 6 处 Switch 圆钮白（随 B2-2 自然消失）；核对余下 3 处白字蓝底 | 全项目 |
| B4-6 | 统计页 Material 进度指示器（~75/428）→ iOS 风格 | `stats_v3_page.dart` |
| B4-7 | `resultDistribution` 冗余查询：UI 补展示或删查询 | `stats_v3_page.dart` |

### 验收
- 柱状图时间序正确；toast 圆角悬浮；按压反馈全组件覆盖；动效一致（IOSAnimations 令牌）

---

## 7. B5 — 深水区（P0 手势 + 翻卡页 V3 化）

### 7.1 全屏返回手势补全（用户核心需求）
- 现状：`ios_page_route.dart` `_FullScreenBackGestureDetector` 半成品（onStart/onUpdate 空、仅 onEnd velocity 判断）
- 方案：复制/实现完整手势控制器——拖拽跟随（onUpdate 计算水平位移，页面随手指右移 + 背景渐显）、松手回弹（超阈值 pop / 未超回弹）、velocity 与位移双判据、与横向滚动冲突规避（透传优先、方向锁定后接管）
- 风险：手势与题目选项横向滑动/滑动删除冲突——需真机（iPad mini5）验证

### 7.2 背题翻卡页 V3 化
- `knowledge_memorize_page.dart`：硬编码色（`Colors.white`/`0xFF2B3646`/`config.accent`）→ `IOSColors.of(context)`；`theme.textTheme` → `IOSTypography`；卡片容器接液态玻璃/按压动效；深浅模式对齐 V3 背景
- 范围：只改视觉层，翻卡交互逻辑（会话队列/背会判定/状态持久化）不动

### 验收
- 任意二级页中部右滑可返回、跟手、松手回弹；背题翻卡页深色下与全局风格一致
- 回归：滑动删除/横向滚动无冲突

---

## 8. 风险与决策点

| 项 | 决策 | 影响 |
|---|---|---|
| partial 计分口径（B1-3） | 建议 `(correct+0.5*partial)/total` | 影响统计页正确率展示，需用户拍板 |
| 统计口径统一方向（B1-1） | 建议"含归档" | 归档后历史成绩保留 |
| 答题卡三态底色深浅通用 | 保持浅色（可读性好） | 深色玻璃容器内偏亮，真机确认 |
| 全屏返回与横向手势冲突 | 方向锁定后接管 | B5 真机验证 |
| 背题翻卡页 V3 化工作量 | 较大，独立 B5 批次 | 不阻塞 B1-B4 |

---

## 9. 验收基线（每批通用）

1. `cd D:\study_app\app; flutter analyze --no-pub` → **0 issues**
2. 代码走查：无新 Material 残留、无魔法数字、令牌引用正确
3. `flutter test`（受 sqlite3 native asset 下载超时限制，若不可跑则注明）
4. git 提交 + push → GitHub Actions Build iOS IPA 成功
5. iPad mini5 真机目检：横竖屏、深色模式、动效一致性

---

*本文档为规划案，执行顺序与决策点以用户确认为准；每批完成后更新《UI-v3-逐页审查清单合集》勾选状态。*
