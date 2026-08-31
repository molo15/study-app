# -*- coding: utf-8 -*-
"""调整 pack_v013 解析过短阈值：blank 类降到 5 字，其余保持 20 字。"""
import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\study_app\tools\seed-builder\pipeline\pack_v013.py'
src = open(P, encoding='utf-8').read()

old = '''    expl = q.get("explanation", "")
    if not expl or len(expl.strip()) < 20:
        errs.append(f"解析过短({len(expl.strip())}字)")
    if PLACEHOLDER.search(expl.strip()):
        errs.append("解析占位")
    # 解析黑名单（出题工作底稿/模板残留）
    _expl_norm = re.sub(r"\\s+", "", expl)
    if re.search(r"素材块|素材n|正文块|对应素材标题|覆盖缺口|本题答案为|存量题未覆盖|本题属[于]?.{0,12}常考", _expl_norm):
        errs.append("解析含工作底稿/模板残留")
    if re.search(r"[（(](基础|变式|拓展|提升|综合|识记|理解)[）)]$", _expl_norm):
        errs.append("解析带等级标注尾巴")
    if re.match(r"^解析[:：]", _expl_norm):
        errs.append("解析冒号前缀")'''

new = '''    expl = q.get("explanation", "")
    _expl_len = len(re.sub(r"\\s+", "", expl))
    _min_len = 5 if q["type"] in ("blank", "short_answer") else 20
    if not expl or _expl_len < _min_len:
        errs.append(f"解析过短({_expl_len}字)")
    if PLACEHOLDER.search(expl.strip()):
        errs.append("解析占位")
    # 解析黑名单（出题工作底稿/模板残留）
    _expl_norm = re.sub(r"\\s+", "", expl)
    if re.search(r"素材块|素材n|正文块|对应素材标题|覆盖缺口|本题答案为|存量题未覆盖|本题属[于]?.{0,12}常考|即可应对同类题目|掌握其概念", _expl_norm):
        errs.append("解析含工作底稿/模板残留")
    if re.search(r"[（(](基础|变式|拓展|提升|综合|识记|理解)[）)]$", _expl_norm):
        errs.append("解析带等级标注尾巴")
    if re.match(r"^解析[:：]", _expl_norm):
        errs.append("解析冒号前缀")'''

assert old in src, "validate_basic 段未匹配"
src = src.replace(old, new)

# 保留轨也同步阈值 + 黑名单补全
old_keep = '''            # 保留轨解析黑名单校验（不含 id/knowledgeId 等基础校验）
            _en = re.sub(r"\\s+", "", nq.get("explanation", ""))
            if re.search(r"素材块|素材n|正文块|对应素材标题|覆盖缺口|本题答案为|存量题未覆盖|本题属[于]?.{0,12}常考", _en):
                report["bad"].append(f"{nq['id']} [保留轨解析含工作残留]")
            if re.search(r"[（(](基础|变式|拓展|提升|综合|识记|理解)[）)]$", _en):
                report["bad"].append(f"{nq['id']} [保留轨解析带等级尾巴]")
            if re.match(r"^解析[:：]", _en):
                report["bad"].append(f"{nq['id']} [保留轨解析冒号前缀]")'''

new_keep = '''            # 保留轨解析黑名单校验（不含 id/knowledgeId 等基础校验）
            _en = re.sub(r"\\s+", "", nq.get("explanation", ""))
            if re.search(r"素材块|素材n|正文块|对应素材标题|覆盖缺口|本题答案为|存量题未覆盖|本题属[于]?.{0,12}常考|即可应对同类题目|掌握其概念", _en):
                report["bad"].append(f"{nq['id']} [保留轨解析含工作残留]")
            if re.search(r"[（(](基础|变式|拓展|提升|综合|识记|理解)[）)]$", _en):
                report["bad"].append(f"{nq['id']} [保留轨解析带等级尾巴]")
            if re.match(r"^解析[:：]", _en):
                report["bad"].append(f"{nq['id']} [保留轨解析冒号前缀]")
            _el = len(_en)
            _ml = 5 if nq["type"] in ("blank", "short_answer") else 20
            if _el and _el < _ml:
                report["bad"].append(f"{nq['id']} [保留轨解析过短({_el}字)]")'''

assert old_keep in src, "保留轨段未匹配"
src = src.replace(old_keep, new_keep)

open(P, 'w', encoding='utf-8').write(src)
import py_compile
py_compile.compile(P, doraise=True)
print('阈值与黑名单已更新，语法 OK')
