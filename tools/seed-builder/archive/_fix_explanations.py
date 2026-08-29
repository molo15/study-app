# -*- coding: utf-8 -*-
"""补全解析缺口（112 题）+ 修复 2 个坏题 + 1 个答案错误。
解析基于题目语义与知识点，简明准确。"""
import json

# id -> 解析文本
EXPL = {
    # ============ 现汉 ============
    "bank-xiandai-hanyu:k_000153": "辞格的套用指一种辞格内部又包含其他辞格，形成大套小的包容关系，题干表述正确。",
    "bank-xiandai-hanyu:k_000164": "辞格连用指同类或异类辞格在一段文字中接连使用，题干表述正确。",
    "bank-xiandai-hanyu:k_000183": "比喻要求本体喻体是两个本质不同的事物，且只取一个相似点；比拟则物我不分，把拟体特征直接加给本体，字面上拟体不出现。题干表述正确。",
    "bank-xiandai-hanyu:k_000198": "反复是积极修辞手段，用以突出语意、增强感情；重复则是字面语意重复，属于语病，二者性质不同。题干表述正确。",
    "bank-xiandai-hanyu:k_000226": "拈连要借助甲乙两事物都出现才成立，比拟字面上只出现本体、拟体不出现。题干表述正确。",
    "bank-xiandai-hanyu:k_000086": "表音文字用数目不多的符号表示有限的音位或音节，作为标记词语声音的字母，题干表述正确。",
    "bank-xiandai-hanyu:z_000063": "“筚路蓝缕”字形正确，成语源自《左传》，“筚路”指柴车，“蓝缕”指破衣。",
    "bank-xiandai-hanyu:z_000037": "“上”“下”用抽象符号在象形字基础上标示方位，属指事造字法。",
    "bank-xiandai-hanyu:z_000039": "汉字规范化包括定量（确定字数）、定形（规范字形）、定音（规范读音）、定序（确定排序）四个方面。",
    "bank-xiandai-hanyu:z_000048": "正确写法为“铤而走险”，“铤”指快走的样子，故从“金”旁，而非“挺”。",
    "bank-xiandai-hanyu:z_000073": "“shàn养”的规范写法为“赡养”，赡有供给、供养义。",
    "bank-xiandai-hanyu:z_000088": "“角色”中“角”读jué（文读），不读jiǎo。",
    "bank-xiandai-hanyu:w_000240": "汉字字体演变的总趋势是简化，由繁到简、由图形到符号。",
    "bank-xiandai-hanyu:q_000032": "造字法主要有象形、指事、会意、形声四种，形声字占现代汉字绝大多数（约90%）。",
    "bank-xiandai-hanyu:z_000167": "客家方言的代表话是广东梅县话，使用人口分布赣南、闽西、粤东等地。",
    "bank-xiandai-hanyu:z_000168": "语言以语音为物质外壳、词汇为建筑材料、语法为结构规律，三者缺一不可。",
    "bank-xiandai-hanyu:z_000169": "现代汉民族共同语（普通话）以北京语音为标准音、北方话为基础方言，以典范的现代白话文著作为语法规范。",
    "bank-xiandai-hanyu:q_000031": "复合式合成词按语素间关系分：联合型（途径）、偏正型（热心）、中补型（提高）、动宾型（失业）、主谓型（地震）五种。",
    "bank-xiandai-hanyu:q_000060": "外来词类型：音译（咖啡）、半音译半意译（浪漫主义）、音译加汉语语素（芭蕾舞）、借形（MTV、景气等）。",
    "bank-xiandai-hanyu:q_000061": "语义场是既有共同义素又有区别义素的一组词的相关语义聚合，含类属、顺序、关系、同义、反义五种义场。",
    "bank-xiandai-hanyu:z_000142": "“胜利一定是我们的”中“的”表领属关系，是结构助词；其余三例“的”均用于句末表肯定语气，是语气词。",
    "bank-xiandai-hanyu:k_000135": "“那两边，你瞧……都是新法栽种的好庄稼”分句间无主次先后，属并列关系。",
    "bank-xiandai-hanyu:w_000336": "动词的主要语法功能是能带宾语（如“吃苹果”），名词、形容词、副词一般不能带宾语。",
    "bank-xiandai-hanyu:k_000092": "实词有词汇意义、能充当句法成分，虚词只有语法意义、不单独充当句法成分，题干表述正确。",
    "bank-xiandai-hanyu:z_000149": "短语加上语调（句调）即可形成句子，语调是短语和句子的重要区别之一。",
    "bank-xiandai-hanyu:z_000150": "介词多由动词虚化而来，如“把、被、从、对于”等原本多为动词。",
    "bank-xiandai-hanyu:z_000151": "时间名词、方位名词除作主语宾语外，常可充当状语，如“明天去”“屋里坐”。",
    "bank-xiandai-hanyu:z_000152": "“每”侧重总括（全体无一例外），“各”侧重分指（分别逐个）。",
    "bank-xiandai-hanyu:w_000172": "j、q、x 发音时舌面前部抬起接近硬腭，属舌面音（舌面前音），题干表述正确。",
    "bank-xiandai-hanyu:z_000001": "人类发音的共鸣器官包括口腔、鼻腔和咽腔。",
    "bank-xiandai-hanyu:z_000002": "决定音色的因素有发音体、共鸣器形状和发音方法。",
    "bank-xiandai-hanyu:z_000003": "舌尖后浊擦音是r，舌尖中不送气清塞音是d，舌根清擦音是h。",
    "bank-xiandai-hanyu:z_000004": "舌面后半高圆唇元音是o，舌面前高不圆唇元音是i，卷舌央不圆唇元音是er。",
    "bank-xiandai-hanyu:z_000006": "“巡”（xún）的韵母是ün，其韵腹为ü。",
    "bank-xiandai-hanyu:z_000007": "汉语音节最多可包含4个音素，如“壮”（zhuàng）含zh、u、a、ng四个音素。",
    "bank-xiandai-hanyu:z_000009": "舌尖中不送气清塞音是d，舌根清擦音是h。",
    "bank-xiandai-hanyu:z_000010": "舌面前高不圆唇元音是i，舌面后半高圆唇元音是o。",
    "bank-xiandai-hanyu:z_000011": "气流振动声带、在口腔咽喉不受阻碍形成的音叫浊音；不振动声带的是清音。",
    "bank-xiandai-hanyu:z_000013": "韵母结构分韵头、韵腹、韵尾三部分，韵腹是韵母的核心。",
    "bank-xiandai-hanyu:z_000014": "国际音标由国际语音学会（IPA）制定，是目前最通行的记音符号。",
    "bank-xiandai-hanyu:z_000015": "儿化音又叫儿化韵，指“儿”后缀与前一首节融合卷舌的音变现象。",
    "bank-xiandai-hanyu:z_000016": "音节由音素构成，音素是听话时感到的最小语音单位。",
    "bank-xiandai-hanyu:z_000017": "传统音节结构分声母、韵母、声调三部分。",
    "bank-xiandai-hanyu:z_000018": "辅音按阻碍方式分塞音擦音，按声带振动分清浊，按气流强弱分送气不送气；39个韵母主要由元音组成。",
    "bank-xiandai-hanyu:z_000021": "普通话中唯一一对清浊相对的音是sh和r（舌尖后擦音）。",
    "bank-xiandai-hanyu:z_000022": "“一块”中“一”在去声前读阳平35；“一毛”中“一”在阳平前读去声51。",
    # ============ 古汉 ============
    "bank-gudai-hanyu:z_000016": "《说文解字》为东汉许慎所著，通过分析字形结构探求字的本义，是我国第一部字典。题干表述正确。",
    "bank-gudai-hanyu:z_000013": "《汉语大词典》的特点：一是历史性，系统反映词语历史演变；二是科学性。",
    "bank-gudai-hanyu:z_000014": "《说文解字》的作者是东汉文字学家许慎。",
    "bank-gudai-hanyu:z_000015": "清代王念孙《广雅疏证》以整理《广雅》为主，是清代训诂学代表作。",
    "bank-gudai-hanyu:z_000022": "会意字由两个以上意符组合表示新义，选项中“止+羊”组合表意，属会意；其余为形声或非字。",
    "bank-gudai-hanyu:z_000024": "“上”“下”以抽象符号标示方位，属指事造字法。",
    "bank-gudai-hanyu:z_000031": "“歡”“嘆”是异体字，二字意义相同，分歧在意符（“欠”与“口”）。",
    "bank-gudai-hanyu:z_000036": "“五经”指《诗》《书》《礼》《易》《春秋》，此处“礼”以《礼记》为代表。",
    "bank-gudai-hanyu:z_000037": "孔颖达疏五经为《周易正义》《尚书正义》《毛诗正义》《礼记正义》《春秋左传正义》。",
    "bank-gudai-hanyu:z_000040": "“包曰”的“包”指注家包咸；“犹”是训诂术语，表“相当于、等于”义。",
    "bank-gudai-hanyu:z_000041": "“兵”本义是兵器，引申为士兵（拿兵器的人），“士兵”义属“兵”的引申义。",
    "bank-gudai-hanyu:z_000042": "由本义直接派生的是直接引申义，在此基础上辗转再引申的是间接引申义。",
    "bank-gudai-hanyu:z_000043": "“穷”本义是穷尽（极、尽），引申指困窘；“醒”本义是酒醒，后引申指睡醒。",
    "bank-gudai-hanyu:z_000044": "“门间”的“间”本义为缝隙，此指门缝。",
    "bank-gudai-hanyu:z_000045": "“于予与何诛”中“诛”为责备、谴责义，后引申为杀戮。",
    "bank-gudai-hanyu:m_000099": "“齐侯以诸侯之师侵蔡”中“以”为动词，义为率领。",
    "bank-gudai-hanyu:m_000100": "“遂伐楚”中“遂”为副词，义为接着、于是。",
    "bank-gudai-hanyu:z_000055": "近体诗平仄中，中古平声属平，上去入三声属仄。",
    "bank-gudai-hanyu:m_000098": "该句拗救中“归”为拗字，“不”为救字，以本句自救方式补救平仄。",
    "bank-gudai-hanyu:m_000121": "下联出句第二字须与上联对句第二字平仄相同，称为“粘”。",
    "bank-gudai-hanyu:m_000122": "同一联中对句与出句平仄相对（尤其双数字及句尾），称为“对”。",
    "bank-gudai-hanyu:m_000244": "“亟请于武公”中“亟”作状语修饰谓语，为副词，义为屡次、多次。",
    "bank-gudai-hanyu:m_000421": "“吾属今为之虏矣”中“为”字引进行为施事者，是被动句的典型标志词。",
    "bank-gudai-hanyu:z_000069": "五音指唇、舌、齿、牙、喉五类声母发音部位。",
    "bank-gudai-hanyu:z_000070": "以清塞音p、t、k收尾的韵母叫入声韵；以元音收尾或无韵尾的叫阴声韵。",
    "bank-gudai-hanyu:z_000071": "中古上声演变：全浊上声变去声，其余仍读上声，故上声演变成上声和去声。",
    # ============ 古文史 ============
    "bank-zhongguo-gudai-wenxue:t_000523": "王实甫《西厢记》在人物塑造、结构安排和曲辞上达到元代戏曲最高水平，明初贾仲明称“《西厢记》天下夺魁”。题干表述正确。",
    "bank-zhongguo-gudai-wenxue:t_000508": "词在宋代被视为“诗余”，意即诗之馀绪，地位低于诗。题干表述正确。",
    "bank-zhongguo-gudai-wenxue:t_000513": "姜夔清雅词派指以姜夔为代表的南宋格律词派，主张清空骚雅，讲究音律与琢句炼字。",
    "bank-zhongguo-gudai-wenxue:t_000546": "《桃花扇》以侯方域、李香君爱情离合反映南明兴亡，思想与艺术高度统一，是清代传奇杰作。题干表述正确。",
    "bank-zhongguo-gudai-wenxue:t_000500": "晚唐时局动荡，写现实政治与社会生活的诗作比重下降，作家创作热情减退，题干表述正确。",
    # ============ 当代 ============
    "bank-zhongguo-dangdai-wenxue:t_000107": "1956年4月，毛泽东在中共中央政治局扩大会议上提出“百花齐放、百家争鸣”方针。",
    "bank-zhongguo-dangdai-wenxue:t_000168": "文革文学特征是政治直接“美学化”、题材人物遵循“三突出”、文学接受政治化；“强调个人独创与艺术自由”恰与之相反，故为错误项。",
    "bank-zhongguo-dangdai-wenxue:t_000050": "《废都》中性描写用于展现西京城文化景观、反思欲望与现代人生存、表达知识分子精神迷茫；“完成对理想爱情的讴歌”不符题意，为错误项。",
    "bank-zhongguo-dangdai-wenxue:t_000358": "《马桥词典》打破文体界限，“打通”文史哲，综合故事、随笔、议论、考证释义、风俗调查等。",
    "bank-zhongguo-dangdai-wenxue:t_000364": "《马桥词典》的语言艺术在于让语言本身成为被展示的对象，马桥的世界活在马桥话里。",
    "bank-zhongguo-dangdai-wenxue:t_000132": "山药蛋派贡献在于复兴民间话语、映照农村变迁、体现“为农民服务”；“塑造阿Q、朱老忠式典型形象”是其他作家成就，为错误项。",
    "bank-zhongguo-dangdai-wenxue:t_000133": "赵树理是20世纪塑造新旧农民形象、最了解农民的作家，被视为“山药蛋派”代表。",
    "bank-zhongguo-dangdai-wenxue:t_000193": "80年代文学总体呈探索求新、潮流化、清算历史等特点；“文学完全脱离政治影响”不符合史实，为错误项。",
    "bank-zhongguo-dangdai-wenxue:t_000195": "新时期“文革叙述”类型包括伤痕、反思、寻根小说等；“改革小说”不属文革叙述，为错误项。",
    "bank-zhongguo-dangdai-wenxue:t_000201": "拉美魔幻现实主义对中国当代影响最明显的是寻根文学、西藏作家群与新笔记小说创作。",
    "bank-zhongguo-dangdai-wenxue:t_000338": "90年代文学潮流淡化、长篇与散文突出、诗歌边缘化；“先锋探索重新成为主流”与史实相反，为错误项。",
    "bank-zhongguo-dangdai-wenxue:t_000234": "朦胧诗对现实的批判包含追求人性回归、探索历史本质、尊重人的价值；“恢复古典格律”不是其贡献，为错误项。",
    "bank-zhongguo-dangdai-wenxue:t_000235": "朦胧诗得名因其多用总体象征手法，意象具有不透明性和多义性。",
    "bank-zhongguo-dangdai-wenxue:t_000236": "舒婷诗歌肯定自我价值、联系民族命运、以爱为基础；“追求宏大史诗叙事”不符合其抒情风格，为错误项。",
    "bank-zhongguo-dangdai-wenxue:t_000344": "“新生代”诗人力图反叛与超越朦胧诗，呈现反英雄、反崇高的特征。",
    "bank-zhongguo-dangdai-wenxue:t_000076": "《爸爸爸》中丙崽是民族文化“劣根性”的象征物，体现了寻根文学的文化批判。",
    "bank-zhongguo-dangdai-wenxue:t_000256": "汪曾祺小说追求“本色艺术”，写健康人性与乡土诗意；“以宏大叙事见长”不符合其风格，为错误项。",
    "bank-zhongguo-dangdai-wenxue:t_000273": "《小鲍庄》中捞渣之死象征“仁义”这一民族道德观念在现代社会走向消亡。",
    "bank-zhongguo-dangdai-wenxue:t_000274": "《棋王》中王一生“以不变应万变”体现老庄“无为而无不为”的传统哲学思想。",
    "bank-zhongguo-dangdai-wenxue:t_000276": "莫言小说常用儿童/弱智视角、创造“立体时空小说”、以想象见长；“坚持单一线性结构”不符，为错误项。",
    "bank-zhongguo-dangdai-wenxue:t_000297": "先锋文学形式变革包括元叙事、语言试验、叙事结构转变；“恢复章回体叙事”相反，为错误项。",
    "bank-zhongguo-dangdai-wenxue:t_000299": "“先锋小说”重视文体的自觉，即小说的“虚构性”与“叙述”在小说方法上的意义。",
    "bank-zhongguo-dangdai-wenxue:t_000301": "鲁迅《狂人日记》的狂人是战斗精神代表，余华《四月三日事件》的狂人是彻底怀疑精神代表。",
    "bank-zhongguo-dangdai-wenxue:t_000302": "池莉“人生三部曲”指《烦恼人生》《不谈爱情》《太阳出世》，是新写实代表作。",
    "bank-zhongguo-dangdai-wenxue:t_000304": "中国先锋小说出现后现代倾向、新写实呈零散化平面化、王朔作品最明显体现后现代文化特征，故该项正确。",
    "bank-zhongguo-dangdai-wenxue:t_000059": "莫言文学想象的源泉和题材来源是其故乡“高密东北乡”。",
    "bank-zhongguo-dangdai-wenxue:t_000060": "张承志记述哲合忍耶回族历史的长篇小说是《心灵史》。",
    "bank-zhongguo-dangdai-wenxue:t_000073": "海外华文文学在中国大陆学界的兴起命名始于20世纪70年代末80年代初，从台港文学这一“引桥”引发。",
    "bank-zhongguo-dangdai-wenxue:t_000055": "树下野狐《搜神记》体现架空历史、语言至上、背景宏大等“80后”特点；“坚持宏大叙事追求史诗品格”不符，为错误项。",
    "bank-zhongguo-dangdai-wenxue:t_000065": "“底层写作”成绩在叙事角度、细节真实与叙事者介入；“脱离现实主义传统完全依赖虚构”不符，为错误项。",
    "bank-zhongguo-dangdai-wenxue:t_000066": "“底层写作”不足在于缺乏理论指导、迎合市场扭曲苦难、审美脱离底层读者；“塑造过于高大的底层英雄”不符，为错误项。",
    "bank-zhongguo-dangdai-wenxue:t_000052": "杨绛散文对历史保持距离、文字简约含蓄、写大时代中的小插曲；“以雄辩议论见长喜作宏大叙事”不符，为错误项。",
    "bank-zhongguo-dangdai-wenxue:t_000326": "张中行散文题材分述学、记人和叙事三大类，是学者散文代表。",
    "bank-zhongguo-dangdai-wenxue:t_000328": "余秋雨散文特色是叙事小说化、有剧场效果、主题鲜明蕴含人文精神；“完全客观纪实无抒情”不符，为错误项。",
    "bank-zhongguo-dangdai-wenxue:t_000160": "《茶馆》以人物与时代的冲突形成独特结构，成就高于《龙须沟》；《龙须沟》结构处理不尽人意。",
}

# 坏题修复：id -> (题干, 新answer)
BAD_FIX = {
    "bank-zhongguo-gudai-wenxue:t_000513":
        ("姜夔清雅词派主张清空骚雅，是南宋格律词派的代表。", "正确"),
    "bank-zhongguo-gudai-wenxue:t_000546":
        ("清代传奇《桃花扇》是一部思想和艺术达到完美结合的杰出作品。", "正确"),
}

# 答案错误修复：id -> 正确答案文本
ANS_FIX = {
    "bank-xiandai-hanyu:z_000142": "胜利一定是我们的",
}

files = {
    '现汉': (r'D:\study_app\tools\seed-builder\out\refined\bank-xiandai-hanyu.refined2.json', []),
    '古汉': (r'D:\study_app\tools\seed-builder\out\refined\bank-gudai-hanyu.v012.json', []),
    '古文史': (r'D:\study_app\tools\seed-builder\out\refined\bank-zhongguo-gudai-wenxue.v012.json', []),
    '当代': (r'D:\study_app\tools\seed-builder\out\refined\bank-zhongguo-dangdai-wenxue.refined2.json', []),
}
done_e = done_b = done_a = 0
for name, (f, _) in files.items():
    qs = json.load(open(f, encoding='utf-8'))
    for q in qs:
        if q['id'] in EXPL:
            q['explanation'] = EXPL[q['id']]
            done_e += 1
        if q['id'] in BAD_FIX:
            q['stem'], q['answer'] = BAD_FIX[q['id']]
            done_b += 1
        if q['id'] in ANS_FIX:
            q['answer'] = ANS_FIX[q['id']]
            done_a += 1
    json.dump(qs, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'补解析 {done_e} | 坏题修复 {done_b} | 答案修复 {done_a}')
