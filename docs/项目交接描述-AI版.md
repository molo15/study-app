# 项目交接描述（AI 版）—— 考研刷题 App

> 以下内容可直接整体复制给任意 AI 助手，用于接手本项目的开发、维护或答疑。

---

## 一句话定位

一个 Android 考研刷题 App（Flutter 开发），内置 5 科语文类考研题库，支持分章节刷题、综合模拟考试、背题/知识点卡片、错题与审题标记、备份导入导出，题库由本地思源笔记素材经脚本构建打包进 APK。

## 技术栈

- **客户端**：Flutter（Dart），Android 端；本地数据库 SQLite（sqflite）；无后端，纯本地运行
- **题库构建**：Python 脚本 + 思源笔记 API（本地 SiYuan 服务，http://127.0.0.1:6806）
- **版本管理**：Git（仓库根目录 `D:\study_app`）

## 目录结构

```
D:\study_app
├─ app\                      # Flutter App 工程（唯一客户端代码）
│  ├─ lib\                   # Dart 源码
│  │  ├─ data\               # 数据层：seed_loader(题库包导入)、quiz_repository(作答/复习)、
│  │  │                      #   quiz_repository_knowledge(知识点卡)、quiz_repository_srs(背题调度)等
│  │  ├─ models\             # 数据模型（Question/Manifest/KnowledgePoint/ChapterOverview 等）
│  │  ├─ ui\                 # 页面：home、章节/练习、模拟考、背题、设置、备份等
│  │  └─ main.dart
│  ├─ assets\banks\          # 5 个题库包 zip（v0.14.0，App 启动自动发现最高版本导入）
│  ├─ test\                  # 单元/widget 测试（61 个，判分/组卷/回归）
│  └─ pubspec.yaml           # 版本号 version: 1.3.0+14
├─ tools\seed-builder\       # 题库构建流水线（Python）
│  ├─ pipeline\              # 核心可复用脚本：pack_v4/verify/coverage/gen_report/audit/mc_expand_*×5
│  ├─ archive\               # 265 个一次性脚本归档（勿直接执行，参考用）
│  └─ README.md
├─ tools\mc_assets\          # 思源笔记 5 科素材（markdown，供扩充题库复用）
└─ docs\                     # 方案、审核报告、题库报告
```

## 题库与数据约定（重要）

- **5 科**：现代汉语、古代汉语、中国现代文学史、中国当代文学史、中国古代文学史
- 当前版本 **v0.14.0**，共 **4506 题**：单选 1653 / 多选 282 / 填空 1614 / 简答 895 / 判断 63
- 每科按章节分文件：`questions/基础-{章}.json`（基础题）+ `questions/测试-{章}.json`（测试题）
- 题库包是 **zip**，内含 `manifest.json`（formatVersion=4，含 knowledge 知识点树 + overviews 章节概览 + questionCount）+ `questions/` 多文件
- **判断题在包内 options 为空数组**，App 加载时自动补「正确/错误」——不是缺陷，勿改
- 题目 id 必须带 `{bankId}:` 前缀（如 `bank-xiandai-hanyu:q_000001`），否则 App 拒绝导入
- 知识点卡/章节概览数据存在 manifest 的 `knowledge`/`overviews` 字段，**不在独立目录**
- 题库升级走「幂等导入」：同 id 覆盖、库中不再出现的题**软归档**（保留作答记录）

## 当前版本状态

- App 版本 **v1.3.0+14**（正式发行第一版），git tag `v1.3.0`
- Release APK：`app\build\app\outputs\flutter-apk\app-release.apk`（53.9MB，**debug 签名**，未配置正式 keystore）
- 已验证：`flutter analyze` 0 issues、`flutter test` 61 个全绿
- git 历史 10 个语义化提交，工作区干净

## 核心功能清单

1. **章节刷题**：基础题/测试题分开，支持多种题型（单选/多选/填空/简答/判断），逐题解析
2. **综合模拟考**：5 科随机组卷 68 题（单选30/多选10/填空20/简答8，150 分制，以现汉+古汉为主），有历史成绩回看、逐题解析（只看错题切换）
3. **背题模式**：知识点卡 + 章节知识概览（数据来自 manifest.knowledge/overviews），SRS 调度
4. **审题标记**：主题定制里的开关（默认关），联动旗标
5. **备份**：导出/导入、题库包管理（5 个默认包可编辑）
6. **考试倒计时**：仅首页象征性展示，无计划倒排

## 常用命令

```powershell
cd D:\study_app\app
D:\flutter\bin\flutter.bat analyze    # 静态检查
D:\flutter\bin\flutter.bat test       # 跑测试
D:\flutter\bin\flutter.bat build apk --release   # 构建 release
# 题库重建（改数据后）：
python tools\seed-builder\pipeline\pack_v4.py
python tools\seed-builder\archive\_verify_packs.py   # 校验题库包
```

## 已知约定与注意事项

- 平台是 **Windows + PowerShell**，Python 脚本用 `python -X utf8` 跑避免中文乱码
- 命令用 `;` 分隔，**PowerShell 不支持 `&&`**
- 思源笔记是素材源（改题/扩充时 `_pull_notebook.py` 拉取），本地服务需开启
- 题库改动后必须跑 verify 校验（重复 id / 答案错位 / 声称题数），并同步 bump manifest.version
- 正式分发前建议补 release keystore（当前是 debug 签名）
