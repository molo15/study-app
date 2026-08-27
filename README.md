# 考研刷题 App（study_app）

## 项目总览

考研专业课刷题应用：内置 5 科题库（现代汉语 / 古代汉语 / 中国古代文学史 / 中国现代文学史 / 中国当代文学史），
Flutter 客户端 + Python/Node 题库生产线。核心机制：间隔重复（FSRS）+ 基础/测试双轨 +
知识点树（章节知识概览）+ 背题模式 + 模拟卷。

## 目录结构

```
D:\study_app
├── app/                  # Flutter 客户端（唯一对外交付物）
│   ├── lib/
│   │   ├── main.dart     # 入口
│   │   ├── models/       # 领域模型（Question/BankManifest/KnowledgePoint/StudyGoal...）
│   │   ├── data/         # 数据层（SQLite DB v9 + Repository + FSRS 调度 + 判分 + 题库导入）
│   │   ├── services/     # 日志、导出工具
│   │   └── ui/           # 页面（首页/题库/章节概览/刷题/背题/错题本/统计/设置/模拟卷...）
│   │       └── widgets/  # 通用小组件
│   ├── assets/banks/     # 内置题库包（5 库 zip，formatVersion=4，v0.11.0）
│   ├── test/             # 单元 + 组件测试（52 个）
│   └── pubspec.yaml      # 依赖：riverpod/sqflite/fsrs/archive/fl_chart...
├── tools/seed-builder/   # 题库生产线（Python 为主，Node.js 辅助思源导出）
│   ├── pipeline/         # 活跃流水线脚本（打包/校验/覆盖率/出题，见其 README）
│   ├── src/              # 历史脚本（清洗/打包旧版本）
│   ├── scripts/          # 出题/合并脚本
│   ├── out/              # 中间产物（materials/skeleton/knowledge/packages/reports...）
│   └── scratch/          # 一次性临时脚本
├── resource/             # 未使用的设计素材
├── docs/                 # 设计文档（总设计/题库规划/重新设计方案等）
├── logs/                 # 构建/运行日志（归档）
├── screenshots/          # 开发期截图（归档）
└── archive/              # 历史备份文件（.bak 等）
```

## 技术链

```
素材（本地思源笔记）
   │  Node.js（extract.js / siyuan.js — 思源 API 导出章节/知识点素材）
   ▼
seed-builder（Python 生产线）
   ├─ 素材结构化：skeleton / materials JSON（章节 → 知识点）
   ├─ 出题生成：gen_*.py（基础题=知识直问直答；测试题=简答/名解/论述）
   ├─ 打包：pack_v4.py（formatVersion=4：选项洗牌 + answer 文本编码 + knowledge/overviews）
   └─ 校验：verify_v011.py（模拟 App 解析：answer 文本→key 映射 / 覆盖率 / 强去重）
   ▼
app/assets/banks/*.zip（5 库题库包，随 APK 内置）
   ▼
Flutter App
   ├─ seed_loader → SQLite（questions/knowledge_points/chapter_overviews/answer_logs/card_scheduling）
   ├─ fsrs 包：间隔重复调度（desired_retention 可调）
   ├─ Riverpod：状态管理（databaseProvider / quizRepositoryProvider / srsProvider）
   └─ 页面：首页(倒计时/今日任务) → 题库 → 章节概览(知识点树) → 刷题/背题
```

## 关键约定

- **题库包格式**：zip = `manifest.json` + `questions/基础-<章>.json` + `questions/测试-<章>.json`；
  `manifest.formatVersion=4`（knowledge 树 + overviews）；选择题 `answer` 为**正确项文本**（洗牌后重算），
  App 端 `Question.fromBankJson` 映射回 key（兼容旧包 key 编码）
- **判分**：集合判分 + `answerVariants` 要点分组；填空/简答部分得分（全部命中 correct / 部分 partial / 零命中 wrong）
- **背题模式**：不背单词式推送（不会的卡每隔 5 张推回），不进 FSRS/错题本
- **数据库**：`app_database.dart` 版本 v9，升级走 `onUpgrade` 增量迁移
- **Repository**：单一 `QuizRepository` + 多个 `part` mixin（settings/questions/knowledge/srs/mock/export）

## 常用命令

```bash
# App
cd app && flutter analyze
cd app && flutter test
cd app && flutter build apk --debug

# 题库打包（v4）
cd tools/seed-builder/pipeline && python pack_v4.py   # 打包 5 库 → assets/banks
python verify_v011.py                                # v4 包 App 解析校验
python coverage_report.py                            # 基础题覆盖率报告
```
