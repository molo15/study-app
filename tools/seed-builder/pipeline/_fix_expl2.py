# -*- coding: utf-8 -*-
"""为 43 题扩写解析（内容正确前提下补足 >20 字，避免 pad 低质占位）。"""
import json

EXPL2 = {
    # ===== 现汉 =====
    "bank-xiandai-hanyu:k_000150":
        "整句形式整齐、气势贯通、富有节奏感；散句结构参差不同但语意贯通、散而不乱，长短错落更显自然灵活。",
    "bank-xiandai-hanyu:k_000174":
        "设问是自问自答或明知故问，目的在于引起注意、强调观点；一般疑问句是有疑而问、期待对方回答，二者性质不同。",
    "bank-xiandai-hanyu:w_000440":
        "词语修辞就是对词语进行选择和锤炼，包括词语的选用（选词）与加工（炼字），使表达更准确、生动、富有表现力。",
    "bank-xiandai-hanyu:w_000449":
        "借喻只出现喻体，本体和喻词都不出现，如“银鹰在天空翱翔”即以银鹰代飞机，因借喻最简练，故最常用。",
    "bank-xiandai-hanyu:w_000242":
        "五十年代制定的“约定俗成、稳步前进”的简化汉字方针，尊重汉字使用习惯、循序渐进推进规范，至今仍有指导意义。",
    "bank-xiandai-hanyu:w_000010":
        "方言是民族共同语（普通话）的地域分支，现代汉语方言是普通话在不同地域分化发展的结果。",
    "bank-xiandai-hanyu:w_000513":
        "同义词包括等义词（意义完全相同，如“演讲—讲演”）和近义词（意义相近但有细微差别）两种类型。",
    "bank-xiandai-hanyu:w_000521":
        "惯用语多为三字格，以动宾结构居多（如“开倒车”“唱高调”），口语色彩浓、形象生动，意义多具整体性。",
    "bank-xiandai-hanyu:w_000337":
        "「上来」表示动作趋向，是趋向动词，常作趋向补语（如“爬上来”），也可单独作谓语（如“他上来了”）。",
    "bank-xiandai-hanyu:w_000341":
        "「我、你、他」指代人，是人称代词，在句中常作主语、宾语、定语，是代词中的典型一类。",
    "bank-xiandai-hanyu:w_000342":
        "「在」引出动作发生的处所，是介词，与处所名词构成介词短语作状语（“在黑板上写字”）。",
    "bank-xiandai-hanyu:w_000344":
        "「哎哟」独立成句表示感叹、应答，是叹词，通常不与其他词组合，位置灵活。",
    "bank-xiandai-hanyu:w_000357":
        "名词句指由名词或名词短语单独构成的非主谓句，如“春天。”“好大的雪！”以名词直接成句。",
    "bank-xiandai-hanyu:w_000370":
        "用疑问代词「为什么」等提问、要求对方就特定处所作答的句子是特指问，句中必含疑问代词。",
    "bank-xiandai-hanyu:w_000371":
        "用「还是」列出两项或多项供选择、要求对方择一的句子是选择问，如“你去还是我去？”",
    "bank-xiandai-hanyu:w_000391":
        "句子的变化包括倒装（成分移位）、省略（成分承前省）、紧缩（分句压缩为单句）等，使表达更灵活简练。",
    "bank-xiandai-hanyu:w_000306":
        "副词的主要语法功能是充当状语，如“很漂亮”的“很”，一般不能单独回答问题、不能修饰名词。",
    "bank-xiandai-hanyu:w_000310":
        "偏正短语由修饰语（定语/状语）加中心语构成，被修饰限制的是中心语，如“伟大祖国”的中心语是“祖国”。",
    "bank-xiandai-hanyu:w_000318":
        "连动短语（两个动词性成分连用）充当谓语的句子称连谓句，如“他推开门走了出去”。",
    "bank-xiandai-hanyu:z_000025":
        "m 是双唇、浊、鼻音，发音时双唇闭合、气流从鼻腔通过，属于双唇浊鼻音。",
    "bank-xiandai-hanyu:k_000047":
        "语音具有物理属性（音高音强音长音色）、生理属性（发音器官活动）、社会属性（表义功能，本质属性）。",
    "bank-xiandai-hanyu:w_000158":
        "说话快慢即声音持续的长短，属于语音四要素（音高、音强、音长、音色）中的音长。",
    "bank-xiandai-hanyu:w_000166":
        "旧称母音、子音，分别对应元音、辅音；元音气流不受阻碍，辅音气流受阻碍。",
    "bank-xiandai-hanyu:w_000181":
        "一个或两个元音后面带上鼻辅音韵尾（n/ng）组成的韵母必然是鼻韵母，如“an”“ang”。",
    "bank-xiandai-hanyu:z_000017":
        "传统音节结构分声母、韵母、声调三部分，与现代语音学从音素角度分析互补。",
    # ===== 古汉 =====
    "bank-gudai-hanyu:z_000014":
        "《说文解字》的作者是东汉文字学家许慎，全书按540部首编排，是我国第一部系统分析字形的字典。",
    "bank-gudai-hanyu:m_000416":
        "“画成其物，随体诘诎”指描摹事物形状的造字法，即象形，如“日”“月”之形。",
    "bank-gudai-hanyu:m_000242":
        "「辟」与「避」是一对古今字，「辟」为本字、后加形旁分化出「避」表躲避义。",
    "bank-gudai-hanyu:m_000392":
        "『徼』在此义为“求取、祈求”，‘君惠徼福’即请求赐福，属古汉语常用义。",
    "bank-gudai-hanyu:m_000395":
        "『绥』义为“安抚”，‘以德绥诸侯’即以德行安抚诸侯，是《左传》常见用义。",
    "bank-gudai-hanyu:z_000044":
        "“门间”的“间”本义为缝隙，此指门缝，从门缝窥视丈夫，是名词本义用法。",
    "bank-gudai-hanyu:m_000387":
        "“歧”字拗、“在”字救，属本句自救的拗救方式，使诗句合于平仄格律。",
    "bank-gudai-hanyu:m_000247":
        "疑问代词有“谁”“何”“奚”“安”等，选项中“谁”“奚”均为疑问代词。",
    "bank-gudai-hanyu:m_000110":
        "「之」在此为代词，代指诸侯，“女实征之”即你确实征伐他们。",
    "bank-gudai-hanyu:m_000375":
        "“古之人不余欺也”是否定句中代词“余”作宾语前置，否定词“不”后宾语前移。",
    "bank-gudai-hanyu:m_000376":
        "“惟余马首是瞻”用代词“是”复指前置宾语“马首”，属宾语用代词复指而前置。",
    "bank-gudai-hanyu:m_000379":
        "“蔓草犹不可除”无形式标志，靠语意表被动，属语意上的被动句（意念被动）。",
    "bank-gudai-hanyu:m_000420":
        "“吾属今为之虏矣”以“为”引进行为施事者，是带形式标志的被动句。",
    "bank-gudai-hanyu:m_000243":
        "具有使动用法的词类有名词、动词、形容词，如“臣活之”的“活”为使动用法。",
    # ===== 古文史 =====
    "bank-zhongguo-gudai-wenxue:b_000004":
        "元散曲包括小令（单支曲）和套数（套曲，多支同宫调曲联缀）两种形式，还有带过曲。",
    "bank-zhongguo-gudai-wenxue:b_000028":
        "《桃花扇》以侯方域与李香君的爱情离合贯穿明末兴亡，即“借离合之情，写兴亡之感”。",
    "bank-zhongguo-gudai-wenxue:b_000049":
        "晚唐李商隐、杜牧并称“小李杜”，以别于盛唐李白、杜甫的“李杜”。",
    # ===== 当代 =====
    "bank-zhongguo-dangdai-wenxue:t_000169":
        "文革文学最流行的批评方法是以写作小组署名开展批判，常用署名有“初澜”“江天”，体现政治化批评模式。",
}

files = {
    '现汉': r'D:\study_app\tools\seed-builder\out\refined\bank-xiandai-hanyu.refined2.json',
    '古汉': r'D:\study_app\tools\seed-builder\out\refined\bank-gudai-hanyu.v012.json',
    '古文史': r'D:\study_app\tools\seed-builder\out\refined\bank-zhongguo-gudai-wenxue.v012.json',
    '当代': r'D:\study_app\tools\seed-builder\out\refined\bank-zhongguo-dangdai-wenxue.refined2.json',
}
done = 0
for name, f in files.items():
    qs = json.load(open(f, encoding='utf-8'))
    for q in qs:
        if q['id'] in EXPL2:
            q['explanation'] = EXPL2[q['id']]
            done += 1
    json.dump(qs, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('扩写解析', done, '题')
