# -*- coding: utf-8 -*-
"""给 pack_v013.py 加：解析黑名单校验（对基础轨+保留轨全部题目生效）。"""
import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\study_app\tools\seed-builder\pipeline\pack_v013.py'
src = open(P, encoding='utf-8').read()

# 1. 在 validate_basic 中加入黑名单检查
old_validate = '''    expl = q.get("explanation", "")
    if not expl or len(expl.strip()) < 20:
        errs.append(f"解析过短({len(expl.strip())}字)")
    if PLACEHOLDER.search(expl.strip()):
        errs.append("解析占位")'''

new_validate = '''    expl = q.get("explanation", "")
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

assert old_validate in src
src = src.replace(old_validate, new_validate)

# 2. 保留轨循环也调用黑名单校验
old_keep = '''        for q in keep:
            nq = dict(q)
            nq.pop("source", None)
            shuffle_options(nq, rng)
            encode_answer_v4(nq)
            keep_out.append(nq)
            if nq["id"] in report["ids"]:
                report["bad"].append(f"{nq['id']} [id重复]")
            report["ids"].add(nq["id"])'''

new_keep = '''        for q in keep:
            nq = dict(q)
            nq.pop("source", None)
            shuffle_options(nq, rng)
            encode_answer_v4(nq)
            keep_out.append(nq)
            if nq["id"] in report["ids"]:
                report["bad"].append(f"{nq['id']} [id重复]")
            report["ids"].add(nq["id"])
            # 保留轨解析黑名单校验（不含 id/knowledgeId 等基础校验）
            _en = re.sub(r"\\s+", "", nq.get("explanation", ""))
            if re.search(r"素材块|素材n|正文块|对应素材标题|覆盖缺口|本题答案为|存量题未覆盖|本题属[于]?.{0,12}常考", _en):
                report["bad"].append(f"{nq['id']} [保留轨解析含工作残留]")
            if re.search(r"[（(](基础|变式|拓展|提升|综合|识记|理解)[）)]$", _en):
                report["bad"].append(f"{nq['id']} [保留轨解析带等级尾巴]")
            if re.match(r"^解析[:：]", _en):
                report["bad"].append(f"{nq['id']} [保留轨解析冒号前缀]")'''

assert old_keep in src
src = src.replace(old_keep, new_keep)

open(P, 'w', encoding='utf-8').write(src)
import py_compile
py_compile.compile(P, doraise=True)
print('打包脚本黑名单校验已注入，语法 OK')
