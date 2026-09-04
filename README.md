# 考研刷题 App（study_app）

> 当前版本：App **v1.4.0** · 题库包 **v0.14.1**（formatVersion=4）· 5 科 4500+ 题

## 项目总览

考研专业课刷题应用：内置 5 科题库（现代汉语 / 古代汉语 / 中国古代文学史 / 中国现代文学史 / 中国当代文学史），
Flutter 客户端 + Python/Node 题库生产线。核心机制：间隔重复（FSRS）+ 基础/测试双轨 +
知识点树（章节知识概览）+ 背题模式（不背单词式推送）+ 综合模拟卷（随机组卷）。

**多端方向**：以 Web 为核心，文件存档为数据中枢，后续封装 APK / EXE。当前 Flutter 客户端为主力交付物，Web spike 已启动。

## 目录结构

```
D:\study_app
├── app/                  # Flutter 客户端（当前主力交付物）
│   ├── lib/
│   │   ├── main.dart     # 入口（含全局 FrostBackground 背景层）
│   │   ├── models/       # 领域模型（Question/BankManifest/KnowledgePoint/StudyGoal...）
│   │   ├── data/         # 数据层（SQLite DB v9 + Repository + FSRS 调度 + 判分 + 题库导入）
│   │   ├── services/     # 日志、导出工具
│   │   ├── ui/           # 页面（首页/题库/章节概览/刷题/背题/错题本/统计/我的/模拟卷...）
│   │   │   └── widgets/  # 通用组件（FrostBackground/GlassCard/AppCard/GlassTabBar/CircularRing...）
│   │   ├── assets/banks/ # 内置题库包（5 库 zip，formatVersion=4，v0.14.1）
│   │   ├── test/         # 单元 + 组件测试
│   │   └── pubspec.yaml  # 依赖：riverpod/sqflite/fsrs/archive/fl_chart...
├── tools/seed-builder/   # 题库生产线（Python 为主，Node.js 辅助思源导出）
│   ├── pipeline/         # 活跃流水线脚本（打包/校验/覆盖率/出题）
│   ├── src/              # 历史脚本（清洗/打包旧版本）
│   ├── scripts/          # 出题/合并脚本
│   ├── out/              # 中间产物（materials/skeleton/knowledge/packages/reports...）
│   └── scratch/          # 一次性临时脚本
├── docs/                 # 设计文档（见下方「文档索引」）
│   ├── prototype/        # UI 设计稿（ui-v2-cold-frost.html — 四形态可交互原型）
│   └── archive/          # 归档：早期设计文档 / 过程性审查报告
├── resource/             # 未使用的设计素材
├── logs/                 # 构建/运行日志（归档）
├── screenshots/          # 开发期截图（归档）
├── release/              # 发布产物（APK / Web build）
└── archive/              # 历史备份文件（.bak 等）
```

## 技术链

```
素材（本地思源笔记）
   │  Node.js（extract.js / siyuan.js — 思源 API 导出章节/知识点素材）
   ▼
seed-builder（Python 生产线）
   ├─ 素材结构化：skeleton / materials JSON（章节 → 知识点）
   ├─ 出题生成：gen_*.py（基础题=知识直问直答；测试题=简答/名解）
   ├─ 打包：pack_v013.py → v0.14.x（选项洗牌 + answer 文本编码 + knowledge/overviews）
   └─ 校验：verify_*.py（模拟 App 解析：answer 文本→key 映射 / 覆盖率 / 强去重 / P0-P2 分级）
   ▼
app/assets/banks/*.zip（5 库题库包，随 APK 内置）
   ▼
Flutter App（当前主力）
   ├─ seed_loader → SQLite（questions/knowledge_points/chapter_overviews/answer_logs/card_scheduling）
   ├─ fsrs 包：间隔重复调度（desired_retention 可调）
   ├─ Riverpod：状态管理（databaseProvider / quizRepositoryProvider / srsProvider）
   └─ 页面：首页(考试倒计时·象征性) → 题库 → 章节概览(知识点树) → 刷题/背题/模拟卷
   ▼
Web 端（spike 进行中，未来核心）
   ├─ 以 Web 为核心构建，响应式适配手机/平板/桌面
   ├─ 文件存档为数据中枢（.zip 包含全部状态：做题记录/FSRS 状态/设置/统计）
   ├─ 自动存档 + 主动导出/导入，任意端互通
   └─ 后续封装为 APK（WebView）/ EXE（桌面容器）
```

## 多端与存档机制

- **数据中枢**：文件存档（.zip），包含做题记录、FSRS 调度状态、设置、统计、审题标记等全部状态
- **存档方式**：自动存档（开关）+ 主动导出/导入；覆盖压缩机制避免文件过多过大
- **端对应**：Web（核心）→ APK（WebView 封装）→ EXE（桌面容器）；当前 Flutter APK 为过渡主力
- **目标设备**：iPad mini 5 / iQOO 手机 / iQOO 平板 / 电脑

## 关键约定

- **题库包格式**：zip = `manifest.json` + `questions/基础-<章>.json` + `questions/测试-<章>.json`；
  `manifest.formatVersion=4`（knowledge 树 + overviews）；选择题 `answer` 为**正确项文本**（洗牌后重算），
  App 端 `Question.fromBankJson` 映射回 key（兼容旧包 key 编码）
- **当前题库版本**：现汉/古汉/现文 **v0.14.1**，当代/古文 **v0.14.0**
- **判分**：集合判分 + `answerVariants` 要点分组；填空/简答部分得分（全部命中 correct / 部分 partial / 零命中 wrong）
- **背题模式**：不背单词式推送（不会的卡每隔 N 张推回），不进 FSRS/错题本；背题卡由基础题自动派生
- **审题标记**：旗子标记，可开关（默认关），用于标记存疑题目；非收藏功能
- **数据库**：`app_database.dart` 版本 v9，升级走 `onUpgrade` 增量迁移
- **Repository**：单一 `QuizRepository` + 多个 `part` mixin（settings/questions/knowledge/srs/mock/export）
- **通知功能**：当前未实现（无 local_notifications 依赖），不做

## UI 主题体系（冷磨砂 v2）

冷磨砂视觉改造（P0–P3 已完成并审查），核心是「模糊冷磨砂质感」：

- **主题预设**：`theme_controller.dart` 内置 3 档——冷磨砂（frost，默认）/ 夜间 / 复古纸。
  主题结构：`frost`（是否磨砂）+ `accent`（主色）+ `frostTop/frostBottom`（渐变端点）+
  `darkMode` + `cornerRadius` + `reduceMotion`；旧配置迁移时 `frost` 默认 false（保持旧观感）
- **全局背景**：`main.dart` 全局 `FrostBackground` 光斑渐变背景（含深色变体），所有页面共享一层，避免各自浮层
- **玻璃组件**：`GlassCard`（三档深度 strong/normal/light）/ `AppCard` / `GlassTabBar` / `CircularRing`，
  通过 `BackdropFilter` 实现毛玻璃；底部 5 Tab + 中央背题圆钮
- **动效**：页面横向滑入（iOS 式）、首页 Hero 环形进度生长、统计数值动画、背题卡 3D 翻转
- **深色模式**：冷磨砂 + darkMode 时自动切换深色渐变背景与深色玻璃（白底浅字会不可读，已审查修复）
- **已知观察**：冷磨砂下每屏多个 `BackdropFilter`，中低端机可能掉帧；如卡顿可将 `GlassCard.depth` 降为 `light`

### 审查结论（2026-08-31）

对 P0–P3 全量修改审查，发现并修复：

| 级别 | 问题 | 修复 |
|---|---|---|
| 严重 | 冷磨砂 + 深色模式对比度失效（白底 + 深色主题浅字不可读） | FrostBackground 深色渐变；GlassCard/AppCard/背题卡深色玻璃（#2B3646 渐变 + 弱白边 + 低高光） |
| 中 | 新建页面固定灰蓝小字（#56647C）深色模式对比度弱 | 改为主题自适应 `onSurfaceVariant` |

确认正常：GlassTabBar 深色处理、答题页选项玻璃（按明暗区分）、模拟考存疑标记/结果环、今日队列双卡、背题 3D 翻转。

**通知功能：当前未实现**（无 local_notifications 依赖、无推送/提醒），如需可后续以「本地通知 + FSRS 到期提醒」方向扩展。

## 文档索引（docs/）

### 核心设计文档（根目录，当前有效）

| 文档 | 内容 |
|---|---|
| `设计理念.md` | 产品核心设计理念（每个环节的设计核心） |
| `UI-v2-冷磨砂实施方案-v1.0.md` | 冷磨砂 UI 改造方案 + P0–P3 执行记录与验收 |
| `UI与动效优化设计方案-v1.md` | UI 与动效优化方向（手感/过渡/信息流） |
| `多端存档同步实施方案-v1.0.md` | 文件存档为核心的多端同步方案（Web→APK/EXE） |
| `设计稿-各端对应与iOS适配说明.md` | 四形态设计稿对应表 + 响应式断点 + iOS 适配清单 |
| `PROJECT_PROGRESS_2026-08-24.md` | 项目进度记录 |
| `项目交接描述-AI版.md` | 项目交接说明（给新 AI 会话的上下文） |

### 设计稿（prototype/）

| 文件 | 内容 |
|---|---|
| `prototype/ui-v2-cold-frost.html` | **UI v2 冷磨砂可交互原型**，四形态切换：手机竖屏 / iPad 竖屏 / 平板横屏 / 桌面。覆盖首页信息流、题库、背题卡 3D 翻转、答题、统计、模拟卷、我的等全页面。 |

### 协作提示词

| 文档 | 内容 |
|---|---|
| `审查提示词-分对话审查-v1.0.md` | 分对话审查用提示词（代码/题库/UI 审查） |
| `修理工程师提示词-分对话修复-v1.0.md` | 分对话修复用提示词（含 Ponytail 4 条代码精简纪律：梯子/根因/留痕/留证） |

### 归档（archive/）

- `archive/early-design/` — 早期设计文档（8 月题库分析、旧版 UI 方案等，已被新文档替代）
- `archive/reviews-2026-09/` — 2026 年 9 月过程性审查报告（PWA/Web 构建/全功能逻辑/性能基线等）

## 常用命令

```bash
# App
cd app && flutter analyze
cd app && flutter test
cd app && flutter build apk --debug

# 题库打包（v4 / v0.13→v0.14）
cd tools/seed-builder/pipeline && python pack_v013.py   # 打包 5 库 → assets/banks（v0.13.0）
python mc_expand_xdhy.py && python mc_expand_gdhy.py \
  && python mc_expand_gdwx.py && python mc_expand_xdwx.py && python mc_expand_ddwx.py  # 多选扩充 → v0.14.0
python verify_v013.py                                  # v4 包 App 解析校验
python coverage_report.py                              # 基础题覆盖率报告
```
