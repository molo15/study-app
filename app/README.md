# 考研刷题

本地离线刷题应用，学习数据不出设备。面向考研专业课（古代汉语、现代汉语、中国文学史等），提供完整的刷题、复习、模拟考试、错题本和题库管理功能。

## 技术栈

- **Flutter** 3.47.x（Dart）
- **Riverpod** — 状态管理
- **SQLite**（sqflite）— 本地数据持久化
- **FSRS**（Free Spaced Repetitioner Scheduler）— 间隔复习调度算法
- **archive** — ZIP 题库包解析

## 项目结构

```
app/lib/
├── main.dart                          # 入口，edge-to-edge / 沉浸式 / 深色模式
├── models/models.dart                 # 数据模型（Question, QuestionType, Grade, MockPaper 等）
├── data/
│   ├── app_database.dart              # SQLite schema（v8）与迁移
│   ├── grading.dart                   # 判分逻辑（选择/多选/填空/简答/判断）
│   ├── srs_service.dart               # FSRS 调度封装
│   ├── seed_loader.dart               # 题库包 ZIP 解析与幂等导入（v0.9.1 内置）
│   ├── quiz_repository.dart           # Repository 统一入口（mixin 组合）
│   ├── quiz_repository_questions.dart # 题库管理（浏览/编辑/隐藏/删除/user_edited 保护）
│   ├── quiz_repository_srs.dart       # 到期队列/新题/错题本/连续正确计数
│   ├── quiz_repository_settings.dart  # 设置持久化（含刷题进度/答题卡结果）
│   ├── quiz_repository_export.dart    # 导出/恢复 JSON 备份 + 审题标记
│   └── quiz_repository_mock.dart      # 模拟卷会话 + 学习统计（含饼图/章节分布）
├── services/
│   ├── app_log.dart                   # 应用日志
│   └── export_helper.dart             # 审题标记导出辅助
└── ui/
    ├── root_page.dart                 # 底部导航（首页 / 统计 / 设置）
    ├── home_page.dart                 # 今日任务 + 快捷入口 + 题库列表
    ├── practice_page.dart             # 刷题核心页（答题/评分/答题卡/恢复进度）
    ├── bank_page.dart                 # 题库详情（章节树/随机刷/合集/模拟卷入口）
    ├── question_manage_page.dart      # 题目浏览器 + 编辑表单（搜索/审题标记/还原）
    ├── mock_exam_list_page.dart       # 模拟卷列表
    ├── mock_exam_page.dart            # 模拟考试（限时/答题卡/交卷成绩单）
    ├── wrong_book_page.dart           # 错题本
    ├── stats_page.dart                # 学习统计（饼图/章节掌握度/近 7 日趋势）
    ├── settings_page.dart             # 设置（外观/复习节奏/题库包管理/备份）
    ├── theme_controller.dart          # 主题配置（主色/背景图/透明度/圆角/深色模式）
    ├── glass_app_bar.dart             # 毛玻璃 AppBar（全局复用）
    └── widgets/                       # 公共小组件（图标块/章节头/空态视图）
```

## 核心功能

### 刷题与复习

- **五种题型**：单选、多选、判断、填空、简答（含等价答案分组判分）
- **三种刷题模式**：顺序刷、随机刷（50/100/150 题）、章节/重点合集
- **FSRS 间隔复习**：四档评分（Again / Hard / Good / Easy），自动调度下次复习时间
- **今日任务**：首页显示待复习题数，一键开始
- **答题卡**：按题型分区，红绿灰三态（对 / 错 / 未答），点击格子二次确认跳题，完成页整轮回顾
- **中途退出恢复**：固定顺序刷题自动保存进度，退出后再进入可从上次位置继续（弹窗确认）
- **审题标记**：刷题时标记待修改题目，支持备注和 JSON 导出
- **练习计时器**：可选显示，后台暂停
- **进度持久化**：答题卡结果跨 session 保存

### 错题本

- 答错自动归集
- 连续答对达阈值自动移出
- 支持手动移出

### 模拟考试

- 限时作答（倒计时）
- 交卷统一判分，生成成绩单存档
- 答题卡跳题

### 题库管理

- **内置题库**：5 科共 5000+ 题（v0.9.1），启动时自动版本检测与增量导入
- **题库包管理**：编辑题目 / 清理归档 / 隐藏（保数据）/ 彻底删除（需输入库名确认）
- **题目编辑**：完整表单（题干/选项/答案/解析/章节/等价答案）
- **用户修改保护**：编辑过的题打 `user_edited` 标记，内置题库更新时跳过覆盖，可还原为官方版

### 外观与个性化

- 主色 / 背景图（本地图片 + 渐变遮罩）/ 透明度 / 圆角
- 深色模式
- 隐藏状态栏（沉浸全屏）

### 数据

- **全部离线**：数据存储在本地 SQLite，无网络请求
- **导出/恢复**：设置页导出全量 JSON 备份，支持恢复导入
- **系统栏适配**：深色模式自动切换状态栏/导航栏图标亮度

## 构建

```bash
# 正式版
flutter build apk --release

# 调试版
flutter build apk --debug
```

产物路径：`app/build/app/outputs/flutter-apk/app-release.apk`

签名配置见 `android/key.properties`（release: `kaoyan-release.keystore`，debug: `~/.android/debug.keystore`）。

## 环境注意事项

- flutter `bin/cache` 写权限：被杀后删 `flutter.bat.lock` / `engine.realm` / `libimobiledevice.stamp` 再重试
- gradle daemon 随机挂：`gradlew --stop` 后重试；`gradle.properties` 已配置 `inprocess` 模式
- `flutter analyze` 在本环境偶发静默被杀，可用 `dart.exe analyze` 稳定替代

## 包名与版本

| 项 | 值 |
|---|---|
| 包名 | `dev.kaoyan.quiz_app` |
| versionName | 1.0.0 |
| versionCode | 1 |

## 依赖

| 包 | 用途 |
|---|---|
| flutter_riverpod | 状态管理 |
| sqflite | SQLite 数据库 |
| fsrs | 间隔复习调度 |
| archive | ZIP 题库包解析 |
| fl_chart | 统计饼图/趋势图 |
| file_picker | 导出备份文件选择 |
| path_provider | 应用目录路径 |
