# -*- coding: utf-8 -*-
"""工程卫生：归档 pipeline 一次性脚本，保留核心可复用脚本"""
import io, sys, os, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
d = r'D:\study_app\tools\seed-builder\pipeline'
archive = r'D:\study_app\tools\seed-builder\archive'
os.makedirs(archive, exist_ok=True)

# 保留：核心可复用的打包/验证/报告/通用导入/合并脚本 + 说明
keep = {
    'README.md', 'pack_v4.py', 'pack_v012.py', 'pack_v013.py',
    'verify_v011.py', 'verify_v012.py', 'verify_v013.py',
    'coverage_report.py', 'gen_report.py', 'gen_bank_report.py',
    'import_docx_common.py', 'parse_docx.py',
    'merge_knowledge.py', 'merge_knowledge_all.py', 'analyze_banks.py',
    'audit_knowledge_v2.py', 'fill_kid_all.py', 'gen_basic_from_knowledge.py',
    'overview_bank.py',
}
files = os.listdir(d)
moved = []
for f in sorted(files):
    if f in keep:
        continue
    src = os.path.join(d, f)
    if not os.path.isfile(src):
        continue
    dst = os.path.join(archive, f)
    shutil.move(src, dst)
    moved.append(f)

print('归档文件数:', len(moved))
print('保留文件数:', len(keep))
# 写 README 说明归档
readme = '''# archive：一次性历史脚本（归档）

本目录存放 seed-builder 历史开发过程中产生的**一次性脚本**，仅供回溯与复用参考，
不参与当前题库构建流程。当前构建仅使用 `../pipeline/` 中的核心脚本。

常见脚本族说明：
- `_fix_*` / `_patch_*`：历次数据修复、功能补丁（均已合并入产物，勿重复执行）
- `_siyuan_*`：思源笔记 API 操作（建目录/双链/抓取/校验，多为一次性）
- `mc2q_*_manual*` / `rebuild_*` / `refine_*`：分批出题、重建、精修脚本
- `_tmp_*` / `_check_*` / `_show_*` / `_probe_*` / `_dump_*` 等：临时探查与校验

如需复用其中逻辑，请拷贝到 pipeline 或 tools 根目录再修改，勿直接在此执行。
'''
with open(os.path.join(archive, 'README.md'), 'w', encoding='utf-8') as f:
    f.write(readme)
print('archive README 已写入')
