# seed-builder 题库生产线

Python 为主的题库构建流水线。素材来自本地思源笔记（Node.js 导出），产物为 App 内置题库包（zip）。

## 流水线阶段

```
① 素材导出（Node.js）     思源 API → 章节/知识点结构化素材
   extract.js / siyuan.js（tools/seed-builder/src/）
   ↓
② 素材结构化（Python）    materials.json / skeleton.json（章节 → 知识点）
   ↓
③ 出题生成（Python）      基础题（知识直问直答）+ 测试题（简答/名解/论述）
   gen_basic_from_knowledge.py（按知识点生成基础题）
   输出到 out/v010/basic、out/v09*/ 等
   ↓
④ 打包（Python）         formatVersion=4 zip → app/assets/banks/
   pack_v4.py            （knowledge 树 + overviews 进 manifest；
                          选项洗牌 + answer 文本编码；强去重 + 解析门禁）
   ↓
⑤ 校验（Python）         模拟 App 端解析，产出报告
   verify_v011.py         answer 文本→key 映射 / 覆盖率 / overview 题数一致性
   coverage_report.py     基础题覆盖率报告
   analyze_banks.py       题库结构分析
```

## 关键脚本

| 脚本 | 职责 |
|---|---|
| `pack_v4.py` | v4 打包主入口：5 库 → out/packages/v011 + assets/banks/（版本 0.11.0）。运行：`python pack_v4.py` |
| `verify_v011.py` | v4 包 App 解析模拟校验，报告 → out/reports/verify_v011.md |
| `coverage_report.py` | 基础题覆盖率报告（知识点 × 题型 × 章节） |
| `gen_basic_from_knowledge.py` | 按知识点清单批量生成基础题（P1 内容再造核心） |
| `analyze_banks.py` | 题库结构统计 |
| `overview_bank.py` | 章节概览生成辅助 |
| `merge_knowledge.py` / `merge_knowledge_all.py` | 知识点清单合并 |

## 输出与数据

- 题库包：`out/packages/v011/{bank}-v0.11.0.zip` → 部署 `app/assets/banks/`
- 中间产物：`out/v09*`（v3 清洗数据）、`out/knowledge/`（知识点树）、`out/materials|skeleton/`
- 报告：`out/reports/`
- 历史脚本（旧版打包/清洗）：`src/`（保留参考，勿直接运行）
- 历史备份：`out/legacy_banks_backup/`

## 数据约定

- 题库包格式：zip = `manifest.json` + `questions/基础-<章>.json` + `questions/测试-<章>.json`
- `manifest.formatVersion=4`；选择题 `answer` = 正确项文本（App 端映射回 key）
- 章节分组映射 `GROUPS` 与思源素材目录严格对应（见 pack_v4.py）

> 说明：一次性补丁/分析脚本（patch_*.py / dump_*.py / scan_*.py）是历史工作脚本，留在 `D:\study_app\.workbuddy\`，不进入本流水线目录。
