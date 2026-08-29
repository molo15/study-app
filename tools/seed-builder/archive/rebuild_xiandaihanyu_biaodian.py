# -*- coding: utf-8 -*-
"""现代汉语·标点符号 4→6 点重拆 + 全库答案错配检查"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = r"D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json"

NEW = [
    {"id": "k_xdyy_biaodian_01", "name": "标点符号的性质与分类", "parent": "k_xdyy_biaodian", "chapter": "标点符号", "hot": True,
     "summary": "标点符号是辅助文字记录语言的符号，用来表示语句的停顿、语气或标示词语。分为点号（7种）和标号（9种）两大类：点号主要表示语句的各种停顿，标号有标明词语或句子性质的作用。",
     "basicQuestions": [
        {"stem": "标点符号分为____和____两大类，其中点号有____种，标号有____种。", "type": "blank", "answer": "点号；标号；7；9",
         "explanation": "点号7种（句号问号叹号分号逗号顿号冒号），标号9种（引号括号破折号省略号着重号连接号间隔号书名号专名号）。",
         "options": []},
        {"stem": "下列全部属于点号的一组是（　）", "type": "choice", "answer": "句号、逗号、顿号、分号、冒号、问号、叹号",
         "explanation": "点号7种：句号、问号、叹号、分号、逗号、顿号、冒号，主要表示语句的各种停顿。",
         "options": ["句号、逗号、顿号、分号、冒号、问号、叹号", "引号、括号、破折号、省略号、着重号", "书名号、专名号、间隔号、连接号", "句号、叹号、引号、书名号、着重号"]},
     ]},
    {"id": "k_xdyy_biaodian_02", "name": "句末点号：句号、问号、叹号", "parent": "k_xdyy_biaodian", "chapter": "标点符号", "hot": True,
     "summary": "句号主要表示陈述句末尾的停顿和舒缓的语气，语气舒缓的祈使句末尾也用句号；问号表示疑问句末尾的停顿和疑问语气；叹号主要表示感叹句末尾的停顿和强烈语气，语气强烈的祈使句、反问句末尾也用叹号。",
     "basicQuestions": [
        {"stem": "语气舒缓的祈使句末尾也可以用（　）", "type": "choice", "answer": "句号",
         "explanation": "语气舒缓的祈使句末尾也用句号。",
         "options": ["句号", "问号", "叹号", "分号"]},
        {"stem": "语气强烈的反问句，末尾要用（　）", "type": "choice", "answer": "叹号",
         "explanation": "语气强烈的祈使句、反问句末尾要用叹号。",
         "options": ["句号", "问号", "叹号", "逗号"]},
        {"stem": "主要表示疑问句末尾的停顿和疑问语气的是（　）", "type": "choice", "answer": "问号",
         "explanation": "问号表示疑问句末尾的停顿和疑问语气。",
         "options": ["句号", "问号", "叹号", "冒号"]},
     ]},
    {"id": "k_xdyy_biaodian_03", "name": "句内点号：逗号、顿号、分号、冒号", "parent": "k_xdyy_biaodian", "chapter": "标点符号", "hot": True,
     "summary": "逗号表示句子内部的一般性停顿；顿号表示语句内部较短的并列短语之间的停顿；分号用于多重复句中起分组作用、主要表示并列关系分句之间的停顿；冒号表示提示性话语后或总括语前的停顿，一般管到句终。",
     "basicQuestions": [
        {"stem": "用于多重复句中起分组作用、主要表示并列分句之间停顿的是（　）", "type": "choice", "answer": "分号",
         "explanation": "分号用于多重复句中起分组作用，主要表示并列关系分句之间的停顿。",
         "options": ["分号", "顿号", "逗号", "冒号"]},
        {"stem": "表示句子内部的一般性停顿的是（　）", "type": "choice", "answer": "逗号",
         "explanation": "逗号表示句子内部的一般性停顿。",
         "options": ["顿号", "分号", "逗号", "冒号"]},
        {"stem": "表示提示性话语后或总括语前的停顿的是（　）", "type": "choice", "answer": "冒号",
         "explanation": "冒号表示提示性话语后或总括语前的停顿，一般管到句终。",
         "options": ["分号", "逗号", "冒号", "破折号"]},
     ]},
    {"id": "k_xdyy_biaodian_04", "name": "标号（一）：引号、括号、破折号、省略号", "parent": "k_xdyy_biaodian", "chapter": "标点符号", "hot": True,
     "summary": "引号表示文中直接引语或特别指出的词语；括号表示文中注释性的话；破折号表示文中解释说明的语句，还表示语意的转换、跃进或语句的中断、延长；省略号表示文中省略了的话、沉默、语言中断，共六个小圆点，省略整段时用十二个小圆点单独成行。",
     "basicQuestions": [
        {"stem": "表示文中直接引语或特别指出的词语的是（　）", "type": "choice", "answer": "引号",
         "explanation": "引号表示文中直接引语或特别指出的词语。",
         "options": ["引号", "括号", "破折号", "着重号"]},
        {"stem": "省略号一共____个小圆点；省略一整段或几段文字时用____个小圆点。", "type": "blank", "answer": "六；十二",
         "explanation": "省略号共六个小圆点；省略一整段或几段文字时用十二个小圆点，单独成行。",
         "options": []},
        {"stem": "表示文中注释性的话的是（　）", "type": "choice", "answer": "括号",
         "explanation": "括号表示文中注释性的话。",
         "options": ["引号", "括号", "省略号", "破折号"]},
     ]},
    {"id": "k_xdyy_biaodian_05", "name": "标号（二）：着重号、连接号、间隔号、书名号、专名号", "parent": "k_xdyy_biaodian", "chapter": "标点符号", "hot": False,
     "summary": "着重号表示要求读者特别注意的字词短语句子；连接号把密切相关的名词连接起来，只占一个字符位置；间隔号用在月份和日期、音译的名和姓、书名和篇名等的中间；书名号表示书籍、篇章、报刊、剧作、歌曲等名称；专名号表示人地名等专有名称，一般只用在古籍或文史著作中。",
     "basicQuestions": [
        {"stem": "表示书籍、篇章、报刊、剧作、歌曲等名称的标号是（　）", "type": "choice", "answer": "书名号",
         "explanation": "书名号表示书籍、篇章、报刊、剧作、歌曲等名称。",
         "options": ["书名号", "引号", "着重号", "专名号"]},
        {"stem": "表示要求读者特别注意的字、词、短语、句子的标号是（　）", "type": "choice", "answer": "着重号",
         "explanation": "着重号表示要求读者特别注意的字、词、短语、句子。",
         "options": ["连接号", "着重号", "间隔号", "省略号"]},
        {"stem": "用在月份和日期、音译的名和姓、书名和篇名中间的标号是（　）", "type": "choice", "answer": "间隔号",
         "explanation": "间隔号表示间隔或边界，用在月份和日期、音译的名和姓、书名和篇名等中间。",
         "options": ["间隔号", "连接号", "破折号", "分号"]},
     ]},
    {"id": "k_xdyy_biaodian_06", "name": "易混淆标点的辨析", "parent": "k_xdyy_biaodian", "chapter": "标点符号", "hot": True,
     "summary": "破折号和省略号都可表示语音中断，区别是破折号表示语音戛然而止、省略号表示余音未尽；逗号表一般停顿、顿号表并列词语间短停顿、分号表并列分句间停顿；冒号一般管到句终，没有比较大的停顿不要用冒号。",
     "basicQuestions": [
        {"stem": "破折号和省略号都可表示语音中断，二者的区别是：破折号表示语音____，省略号则表示____。", "type": "blank", "answer": "戛然而止；余音未尽",
         "explanation": "破折号表示语音戛然而止，省略号则表示余音未尽。",
         "options": []},
        {"stem": "冒号一般管到____。", "type": "blank", "answer": "句终",
         "explanation": "冒号一般管到句终，没有比较大的停顿不要用冒号。",
         "options": []},
     ]},
]

def main():
    d = json.load(open(PATH, encoding="utf-8"))
    keep = [k for k in d["knowledge"] if k["chapter"] != "标点符号"]
    d["knowledge"] = keep + NEW
    json.dump(d, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    from collections import Counter
    print("重拆后各章知识点数:", dict(Counter(k["chapter"] for k in d["knowledge"])))

    # 全库答案错配检查
    bad = []
    for k in d["knowledge"]:
        for q in k.get("basicQuestions", []):
            if q["type"] == "choice":
                if len(q.get("options", [])) != 4:
                    bad.append(f"{k['id']} 选项数!={len(q.get('options',[]))}: {q['stem'][:20]}")
                if q["answer"] not in q.get("options", []):
                    bad.append(f"{k['id']} 答案错配: {q['stem'][:25]} ans={q['answer']!r}")
    print("现代汉语全库答案错配/异常:", len(bad))
    for b in bad:
        print("  ", b)

if __name__ == "__main__":
    main()
