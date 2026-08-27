# -*- coding: utf-8 -*-
"""Generate dispositions JSON for 语法 chapter (249 questions)."""
import json, io

D = {}

def kb(i, reason, variants=None):
    D[i] = {"action": "keep_basic", "reason": reason}
    if variants: D[i]["answerVariants"] = variants

def kt(i, reason, variants=None):
    D[i] = {"action": "keep_test", "reason": reason}
    if variants: D[i]["answerVariants"] = variants

def de(i, reason):
    D[i] = {"action": "delete", "reason": reason}

def rw(i, reason, suggestion, variants=None):
    D[i] = {"action": "rewrite", "reason": reason, "rewriteSuggestion": suggestion}
    if variants: D[i]["answerVariants"] = variants

# ============ q_ series (exercise source, 21 题) ============
rw("bank-xiandai-hanyu:q_000005",
   "题干硬伤：引文「他跳下了车」中并没有「下来」（只有趋向补语「下」），引文与所问词不符，自相矛盾（规则e）",
   "把引文改为「他从车上跳下来了」或「他跳下车来」，仍问「下来」「起来」属于哪种补语，答案 C 趋向补语不变；解析中「跳下来」与题干保持一致。",
   ["趋向补语=趋向动词作补语"])
kb("bank-xiandai-hanyu:q_000006", "用「看关系」提问法辨认补语/宾语（V什么=V得怎么样），核心考点，题干规范")
kb("bank-xiandai-hanyu:q_000007", "存现句识别（主语方所性），特殊句式核心考点（w_000365/w_000423 同考点已删）")
kb("bank-xiandai-hanyu:q_000015", "句型主谓句/非主谓句二分（w_000316 同考点已删）")
kb("bank-xiandai-hanyu:q_000016", "双宾句近宾语/远宾语（w_000353 同考点已删）")
kb("bank-xiandai-hanyu:q_000017", "数量短语的构成与功能，基础")
kb("bank-xiandai-hanyu:q_000025", "虚词特征（依附实词、不单独成句）")
kb("bank-xiandai-hanyu:q_000026", "把字句宾语有定，教材要点")
kb("bank-xiandai-hanyu:q_000035", "虚词范围多选（w_000377 同考点已删）")
kb("bank-xiandai-hanyu:q_000063", "「与其…不如…」已定选择复句，区分度好")
kb("bank-xiandai-hanyu:q_000064", "多义短语（结构关系不同），基础")
kb("bank-xiandai-hanyu:q_000065", "兼语句与主谓短语作宾语句的辨析，考点价值高")
kb("bank-xiandai-hanyu:q_000066", "语法性质三性（抽象/稳固/民族）")
kb("bank-xiandai-hanyu:q_000067", "破折号/省略号表语音中断的区别")
kb("bank-xiandai-hanyu:q_000068", "语法单位四级")
kb("bank-xiandai-hanyu:q_000069", "句类四类（祈使句）")
kb("bank-xiandai-hanyu:q_000070", "层次分析法首次切分（别忘了带雨伞），与素材易错题一致")
kb("bank-xiandai-hanyu:q_000071", "程度副词很/极作补语的标记（很+得，极+了）")
kb("bank-xiandai-hanyu:q_000072", "连谓句前一动作表方式")
kb("bank-xiandai-hanyu:q_000073", "被字句受事有定")
kb("bank-xiandai-hanyu:q_000077", "偏正复句范围多选（w_000389 同考点已删）")

# ============ z_ 真题 series (34 题) ============
kb("bank-xiandai-hanyu:z_000133", "真题：划分词类三大标准（w_000301 同考点已删，保留真题）")
kb("bank-xiandai-hanyu:z_000134", "真题：副词语法特征")
kb("bank-xiandai-hanyu:z_000135", "真题：短语结构分类 vs 功能分类")
kb("bank-xiandai-hanyu:z_000136", "真题：偏正短语（美丽南京）")
kb("bank-xiandai-hanyu:z_000137", "真题：同位短语（国庆那天）")
kb("bank-xiandai-hanyu:z_000138", "真题：偏正短语（人口调查）")
kb("bank-xiandai-hanyu:z_000139", "真题：兼语短语（有人报名）", ["兼语短语=兼语式=动宾与主谓套合"])
kb("bank-xiandai-hanyu:z_000140", "真题：只有…才…条件复句", ["条件复句=必要条件复句"])
kb("bank-xiandai-hanyu:z_000141", "真题：名词语法特征（不能带宾语）")
kb("bank-xiandai-hanyu:z_000142", "真题：结构助词「的」（w_000396 镜像题已删，保留真题方）")
kb("bank-xiandai-hanyu:z_000143", "真题：句类 vs 句型（兼语句属句型）")
kb("bank-xiandai-hanyu:z_000144", "真题：短语功能类型分类")
kb("bank-xiandai-hanyu:z_000145", "真题：动宾短语（加强学习）")
kb("bank-xiandai-hanyu:z_000146", "真题：偏正短语（高贵品质）")
rw("bank-xiandai-hanyu:z_000147",
   "答案与解析矛盾：答案标 A 同位短语，解析却说「坐车上上班」是连谓短语（连动短语），且选项中没有连谓项，属答案硬伤（规则e）",
   "将选项改为包含「连谓短语（连动短语）」项并把正确答案定为连谓短语；或直接重设四个选项（如 A 连谓 B 偏正 C 主谓 D 动宾），答案为连谓短语。",
   ["连谓短语=连动短语"])
kb("bank-xiandai-hanyu:z_000148", "真题：「跟」为介词（引进动作对象）")
kb("bank-xiandai-hanyu:z_000149", "真题：短语+语调=句子（w_000314 同考点已删，保留真题）", ["语调=句调"])
kb("bank-xiandai-hanyu:z_000150", "真题：介词由动词虚化而来")
kb("bank-xiandai-hanyu:z_000151", "真题：时间名词/方位名词可作状语")
kb("bank-xiandai-hanyu:z_000152", "真题：每侧重总括、各侧重分指")
kb("bank-xiandai-hanyu:z_000153", "真题：学习重要主谓 vs 学习时间偏正")
kb("bank-xiandai-hanyu:z_000154", "真题：只有…才…为条件复句非单句")
kb("bank-xiandai-hanyu:z_000155", "真题：并非所有形容词都能受副词修饰（区别词例外）")
kb("bank-xiandai-hanyu:z_000156", "真题：不及物动词可带施事/处所宾语")
kb("bank-xiandai-hanyu:z_000157", "真题：只有…才…条件复句判断")
kb("bank-xiandai-hanyu:z_000158", "真题：上得来的「得」是可能补语标志，非情态补语", ["可能补语=能性补语"])
kt("bank-xiandai-hanyu:z_000159", "真题名解：实词（2016）")
kt("bank-xiandai-hanyu:z_000160", "真题名解：复句（2022）")
kt("bank-xiandai-hanyu:z_000161", "真题名解：生成语法（2023）")
kt("bank-xiandai-hanyu:z_000162", "真题简答：符号法分析句子（13/15/16）")
kt("bank-xiandai-hanyu:z_000163", "真题简答：多重复句分析方法（13/15/16）")
kt("bank-xiandai-hanyu:z_000164", "真题简答：句类异同对比并说明原因（2024）")
kt("bank-xiandai-hanyu:z_000165", "真题简答：层次分析法切分短语（2024）")
kt("bank-xiandai-hanyu:z_000166", "真题简答：歧义短语分析（2023）")

# ============ k_ 课后题 series (57 题) ============
kb("bank-xiandai-hanyu:k_000091", "划分实词/虚词的依据（w_000304 同考点已删）")
kb("bank-xiandai-hanyu:k_000092", "实词/虚词区别判断（k_000093、w_000302 同考点已删）")
de("bank-xiandai-hanyu:k_000093", "与 k_000092 同考点（虚词只有语法意义不充当句法成分）跨题型复制（规则c）")
kb("bank-xiandai-hanyu:k_000094", "八大句法成分两两配对")
de("bank-xiandai-hanyu:k_000095", "与 k_000094 同考点（句法成分同一层次配对）跨题型复制（规则c）")
kb("bank-xiandai-hanyu:k_000096", "学好本领为动宾（动语—宾语）关系")
kb("bank-xiandai-hanyu:k_000097", "语法抽象性定义（k_000098 同考点已删）")
de("bank-xiandai-hanyu:k_000098", "与 k_000097 同考点（语法抽象性）跨题型复制（规则c）")
kb("bank-xiandai-hanyu:k_000099", "能做主语的词语一般能做宾语")
kb("bank-xiandai-hanyu:k_000100", "谓词性词语自由作谓语、名词性词语受限")
kb("bank-xiandai-hanyu:k_000101", "状语主要修饰谓词性中心语")
kb("bank-xiandai-hanyu:k_000102", "经常作补语成分多选")
kb("bank-xiandai-hanyu:k_000103", "定语主要修饰名词性中心语")
kb("bank-xiandai-hanyu:k_000104", "经常作状语成分多选（k_000105 同考点已删）")
de("bank-xiandai-hanyu:k_000105", "与 k_000104 同考点（介词短语自由作状语）跨题型复制（规则c）")
kb("bank-xiandai-hanyu:k_000106", "崭新的由形容词充当定语")
kb("bank-xiandai-hanyu:k_000107", "限制性定语（领有者）判断")
de("bank-xiandai-hanyu:k_000108", "与 k_000110 同考点（描写性定语）复制，保留单选 k_000110（规则c）")
kb("bank-xiandai-hanyu:k_000109", "定语意义类别（质料）")
kb("bank-xiandai-hanyu:k_000110", "描写性定语（勇敢的）判断")
kb("bank-xiandai-hanyu:k_000111", "病句：词性误用（见闻）")
kb("bank-xiandai-hanyu:k_000112", "病句：否定不当")
kb("bank-xiandai-hanyu:k_000113", "病句：数量减少不能用倍数（k_000114 同考点已删）")
de("bank-xiandai-hanyu:k_000114", "与 k_000113 同考点（数量减少不能用倍数）跨题型复制（规则c）")
kb("bank-xiandai-hanyu:k_000115", "病句：量词误用（山用座）（k_000116 同考点已删）")
de("bank-xiandai-hanyu:k_000116", "与 k_000115 同考点（量词误用）换例复制（规则a）")
kb("bank-xiandai-hanyu:k_000117", "状态形容词不能加程度副词（恶狠狠）")
kb("bank-xiandai-hanyu:k_000118", "病句：搭配不当（提高观念）（k_000128 同考点已删）")
kb("bank-xiandai-hanyu:k_000119", "病句：和/或加合与选择并列")
kb("bank-xiandai-hanyu:k_000120", "病句：被字句谓语须及物动词")
kb("bank-xiandai-hanyu:k_000121", "病句：语序不当（多层定语歧义）")
kb("bank-xiandai-hanyu:k_000122", "病句：方言句式（有收到）")
kb("bank-xiandai-hanyu:k_000123", "病句：的地得（听得清清楚楚）", ["得=结构助词，补语标记"])
kb("bank-xiandai-hanyu:k_000124", "病句：不及物动词不能带宾语（出发）")
kb("bank-xiandai-hanyu:k_000125", "病句：句式杂糅")
kb("bank-xiandai-hanyu:k_000126", "病句：宾语中心语残缺")
kb("bank-xiandai-hanyu:k_000127", "病句：动宾搭配不当")
de("bank-xiandai-hanyu:k_000128", "与 k_000118 同考点（搭配不当）换例复制（规则a）")
kb("bank-xiandai-hanyu:k_000129", "递进复句（不但…而且…）")
kb("bank-xiandai-hanyu:k_000130", "条件复句（只要…就…）（w_000367 同考点已删）")
kb("bank-xiandai-hanyu:k_000131", "因果复句（因为…所以…）")
de("bank-xiandai-hanyu:k_000132", "与 w_000370 同考点（特指问句识别）跨来源复制（规则c）")
kb("bank-xiandai-hanyu:k_000133", "反诘问句（难道…吗）")
kb("bank-xiandai-hanyu:k_000134", "顺承复句（动作先后承接）")
kb("bank-xiandai-hanyu:k_000135", "并列复句（分句间关系）")
de("bank-xiandai-hanyu:k_000136", "与 w_000359 同考点（名词谓语句）跨来源复制（规则c）")
de("bank-xiandai-hanyu:k_000137", "与 w_000364 同考点（兼语句）跨来源复制（规则c）")
de("bank-xiandai-hanyu:k_000138", "与 w_000364/w_000425 同考点（兼语句）换例复制（规则a）")
kb("bank-xiandai-hanyu:k_000139", "非主谓句兼语句（有字式），与主谓式兼语句形成区分")
de("bank-xiandai-hanyu:k_000140", "与 w_000363 同考点（连动/连谓句）跨来源复制（规则c）")
de("bank-xiandai-hanyu:k_000141", "与 w_000363/k_000140 同考点（连谓句）换例复制（规则a）")
kb("bank-xiandai-hanyu:k_000142", "单句：介词短语状语前置（与偏正复句区分）")
kb("bank-xiandai-hanyu:k_000143", "病句：关联词搭配（哪怕…也…）")
kb("bank-xiandai-hanyu:k_000144", "病句：关联词残缺（不但缺而且）")
kb("bank-xiandai-hanyu:k_000145", "多重复句分句间关系依次判断，综合性较强")
kb("bank-xiandai-hanyu:k_000146", "语法体系 vs 语法学体系（k_000147 同考点已删）")
de("bank-xiandai-hanyu:k_000147", "与 k_000146 同考点（语法体系）跨题型复制（规则c）")

# ============ w_ 试题库 series ============
# --- 填空题 w_000301-330 ---
de("bank-xiandai-hanyu:w_000301", "与 z_000133 同考点（划分词类以语法功能为依据）跨来源复制，保留真题（规则c）")
de("bank-xiandai-hanyu:w_000302", "与 k_000092 同考点（虚词不能单独充当句法成分）跨来源复制（规则c）")
kb("bank-xiandai-hanyu:w_000303", "词的语法功能=词与词组合能力")
de("bank-xiandai-hanyu:w_000304", "与 k_000091/z_000133 同考点（词分实词虚词）跨来源复制（规则c）")
kb("bank-xiandai-hanyu:w_000305", "普通话常见语气词")
kb("bank-xiandai-hanyu:w_000306", "副词只能充当状语")
de("bank-xiandai-hanyu:w_000307", "与 w_000376 同考点（代词三类）跨题型复制（规则c）")
kb("bank-xiandai-hanyu:w_000308", "助词分类（结构/动态/比况等）")
de("bank-xiandai-hanyu:w_000309", "与 w_000380 同考点（五种基本短语按结构关系）跨题型复制（规则c）")
kb("bank-xiandai-hanyu:w_000310", "偏正短语=修饰语+中心语")
kb("bank-xiandai-hanyu:w_000311", "兼语=动宾短语+主谓短语套合", ["兼语短语=兼语式"])
de("bank-xiandai-hanyu:w_000312", "短语结构填空壳（今天春节→主谓），同壳换词，主谓短语由 z_000153 覆盖（规则a）")
de("bank-xiandai-hanyu:w_000313", "短语结构填空壳（从黄河游泳→状中偏正），同壳换词（规则a）")
de("bank-xiandai-hanyu:w_000314", "与 z_000149 同考点（句子具有语调）跨来源复制，保留真题（规则c）")
de("bank-xiandai-hanyu:w_000315", "与 w_000382 同考点（主语语义类型）跨题型复制（规则c）")
de("bank-xiandai-hanyu:w_000316", "与 q_000015 同考点（单句分主谓句/非主谓句）跨来源复制（规则c）")
de("bank-xiandai-hanyu:w_000317", "与 w_000387 同考点（主谓句四类）跨题型复制（规则c）")
kb("bank-xiandai-hanyu:w_000318", "连谓句定义（连动短语作谓语）", ["连谓句=连动句", "连谓短语=连动短语"])
kb("bank-xiandai-hanyu:w_000319", "复句由两个以上分句组成")
kb("bank-xiandai-hanyu:w_000320", "关联词语统称")
de("bank-xiandai-hanyu:w_000321", "与 q_000069、w_000392 同考点（语气四类）重复（规则c）")
kb("bank-xiandai-hanyu:w_000322", "疑问句四类（是非/特指/选择/正反）", ["正反问=反复问"])
kb("bank-xiandai-hanyu:w_000323", "突然为形容词、忽然为副词（真题相关辨析）")
kb("bank-xiandai-hanyu:w_000324", "正在为副词、现在为名词")
de("bank-xiandai-hanyu:w_000325", "同位短语识别填空，与 z_000137 真题同考点且属短语结构填空壳（规则a/c）")
kb("bank-xiandai-hanyu:w_000326", "学校管理部门同志的想法→定语")
kb("bank-xiandai-hanyu:w_000327", "补语七类（含时地补语）", ["时地补语=时间处所补语=介词短语补语"])
kb("bank-xiandai-hanyu:w_000328", "「是」判断动词/副词判别")
kb("bank-xiandai-hanyu:w_000329", "被字句用介词被引进施事", ["施事=施动者"])
kb("bank-xiandai-hanyu:w_000330", "除非…才…条件复句")

# --- 单选 w_000331-371 ---
de("bank-xiandai-hanyu:w_000331", "与 w_000372 同考点（语法三含义）跨题型复制（规则c）")
kb("bank-xiandai-hanyu:w_000332", "人百个均属体词")
kb("bank-xiandai-hanyu:w_000333", "名词能用数量短语修饰")
kb("bank-xiandai-hanyu:w_000334", "名词不能用不修饰")
kb("bank-xiandai-hanyu:w_000335", "动量词表示动作的量")
kb("bank-xiandai-hanyu:w_000336", "动词能带宾语")
kb("bank-xiandai-hanyu:w_000337", "上来是趋向动词")
kb("bank-xiandai-hanyu:w_000338", "区别词（国营/民用/大型）")
kb("bank-xiandai-hanyu:w_000339", "不没是否定副词")
kb("bank-xiandai-hanyu:w_000340", "很挺十分为程度副词")
kb("bank-xiandai-hanyu:w_000341", "我你他是人称代词")
kb("bank-xiandai-hanyu:w_000342", "在字介词判别（他在黑板上写字）")
kb("bank-xiandai-hanyu:w_000343", "着了过是动态助词")
kb("bank-xiandai-hanyu:w_000344", "哎哟是叹词")
de("bank-xiandai-hanyu:w_000345", "短语结构单选壳（今天星期日→主谓），同壳换词，主谓短语由 z_000153 覆盖（规则a）")
de("bank-xiandai-hanyu:w_000346", "短语结构单选壳（彻底解决→偏正），同壳换词，偏正由 z_000136/138/146 真题覆盖（规则a）")
de("bank-xiandai-hanyu:w_000347", "短语结构单选壳（去打电话→连动），同壳换词，连动由 z_000147 覆盖（规则a）")
de("bank-xiandai-hanyu:w_000348", "短语结构单选壳（明代医药家李时珍→同位），同壳换词，同位由 z_000137 真题覆盖（规则a）")
kb("bank-xiandai-hanyu:w_000349", "你的到来为体词性句法结构")
kb("bank-xiandai-hanyu:w_000350", "小张为施事主语")
kb("bank-xiandai-hanyu:w_000351", "跑跑为谓词性主语")
kb("bank-xiandai-hanyu:w_000352", "赶快去为谓词性宾语")
de("bank-xiandai-hanyu:w_000353", "与 q_000016 同考点（双宾句近/远宾语）跨来源复制（规则c）")
kb("bank-xiandai-hanyu:w_000354", "要命为程度补语")
kb("bank-xiandai-hanyu:w_000355", "那位连长为复说语", ["复说语=复指成分=称代式复说"])
kb("bank-xiandai-hanyu:w_000356", "往少里说是插说语（独立语）", ["插说语=插入语=独立成分"])
kb("bank-xiandai-hanyu:w_000357", "非主谓句：名词句（春天）（w_000358 同壳已删）")
de("bank-xiandai-hanyu:w_000358", "与 w_000357 同壳（下列句子中的( )是X句）换词，形容句考点由 w_000386 覆盖（规则a）")
kb("bank-xiandai-hanyu:w_000359", "名词谓语句（明天国庆节）")
kb("bank-xiandai-hanyu:w_000360", "形容词谓语句（今天冷极了）")
kb("bank-xiandai-hanyu:w_000361", "动词谓语句（山上都是苹果树）")
kb("bank-xiandai-hanyu:w_000362", "主谓谓语句（你的想法我认为很奇怪）")
kb("bank-xiandai-hanyu:w_000363", "连动句（他推开门走了出去）")
kb("bank-xiandai-hanyu:w_000364", "兼语句（老张介绍我去见局长）")
de("bank-xiandai-hanyu:w_000365", "与 q_000007 同考点（存现句）跨来源复制（规则c）")
kb("bank-xiandai-hanyu:w_000366", "把字句（老张把他叫走了）", ["把字句=处置式"])
de("bank-xiandai-hanyu:w_000367", "与 k_000130 同考点（只要…就…条件复句）跨来源复制（规则c）")
kb("bank-xiandai-hanyu:w_000368", "即使…也…让步性假设条件复句")
kb("bank-xiandai-hanyu:w_000369", "越…越…为紧缩句", ["紧缩句=紧缩复句"])
kb("bank-xiandai-hanyu:w_000370", "特指问句（小张为什么没有来）")
kb("bank-xiandai-hanyu:w_000371", "选择问句（我去还是不去）")

# --- 多选 w_000372-399 ---
kb("bank-xiandai-hanyu:w_000372", "语法三含义多选（规律/科学/教材）")
kb("bank-xiandai-hanyu:w_000373", "实词分体词/谓词/加词")
kb("bank-xiandai-hanyu:w_000374", "起附着作用的虚词（介词/助词/语气词）")
kb("bank-xiandai-hanyu:w_000375", "加词=区别词+副词", ["加词=只作修饰语、不作主语谓语的词"])
kb("bank-xiandai-hanyu:w_000376", "代词三类（人称/指示/疑问）")
de("bank-xiandai-hanyu:w_000377", "与 q_000035 同考点（虚词范围）跨来源复制（规则c）")
kb("bank-xiandai-hanyu:w_000378", "报告兼名词/动词")
kb("bank-xiandai-hanyu:w_000379", "和跟同与兼连词/介词")
kb("bank-xiandai-hanyu:w_000380", "五种基本短语结构类型")
kb("bank-xiandai-hanyu:w_000381", "句法结构功能分类", ["体词性短语=名词性短语", "谓词性短语=动词性/形容词性短语"])
kb("bank-xiandai-hanyu:w_000382", "主语语义类型（施事/受事/中性）")
kb("bank-xiandai-hanyu:w_000383", "宾语功能分类（体词性/谓词性）")
kb("bank-xiandai-hanyu:w_000384", "结果补语识别多选")
kb("bank-xiandai-hanyu:w_000385", "句子特殊成分（复说语/插说语）")
kb("bank-xiandai-hanyu:w_000386", "非主谓句类型")
kb("bank-xiandai-hanyu:w_000387", "主谓句类型（按谓语性质）")
kb("bank-xiandai-hanyu:w_000388", "联合复句（并列/连贯/递进/选择）")
de("bank-xiandai-hanyu:w_000389", "与 q_000077 同考点（偏正复句范围）跨来源复制（规则c）")
kb("bank-xiandai-hanyu:w_000390", "假设条件复句类型多选")
kb("bank-xiandai-hanyu:w_000391", "句子变化（倒装/省略/紧缩）")
kb("bank-xiandai-hanyu:w_000392", "语气四类多选")
de("bank-xiandai-hanyu:w_000393", "与 w_000322 同考点（疑问句四类）跨题型复制（规则c）")
kb("bank-xiandai-hanyu:w_000394", "搭配不当类型多选")
kb("bank-xiandai-hanyu:w_000395", "偏正结构短语多选")
de("bank-xiandai-hanyu:w_000396", "镜像题：与 z_000142（属于结构助词）正反互换，保留真题方（规则b）")
kb("bank-xiandai-hanyu:w_000397", "了字语气词/动态助词判别多选")
kb("bank-xiandai-hanyu:w_000398", "在字介词/动词/副词判别多选")
kb("bank-xiandai-hanyu:w_000399", "跟字介词/连词/动词判别多选")

# --- 词类分析壳 w_000400-410 (Cluster A, keep 2) ---
kb("bank-xiandai-hanyu:w_000400", "词类分析壳代表题：了为动态助词")
de("bank-xiandai-hanyu:w_000401", "词类分析壳（渐渐→副词）同壳换词（规则a）")
de("bank-xiandai-hanyu:w_000402", "词类分析壳（正在→副词）同壳换词，且与 w_000324 同考点（规则a/c）")
de("bank-xiandai-hanyu:w_000403", "词类分析壳（出去→趋向动词）同壳换词，且与 w_000337 同考点（规则a/c）")
de("bank-xiandai-hanyu:w_000404", "词类分析壳（着→动态助词）同壳换词，且与 w_000343 同考点（规则a/c）")
de("bank-xiandai-hanyu:w_000405", "词类分析壳（吗→语气词）同壳换词（规则a）")
de("bank-xiandai-hanyu:w_000406", "词类分析壳（刚才→时间名词）同壳换词，与 z_000151 相关（规则a）")
de("bank-xiandai-hanyu:w_000407", "词类分析壳（上面→方位词）同壳换词（规则a）")
de("bank-xiandai-hanyu:w_000408", "词类分析壳（袖珍→区别词）同壳换词，且与 w_000338 同考点（规则a/c）")
de("bank-xiandai-hanyu:w_000409", "词类分析壳（无论→连词）同壳换词（规则a）")
kb("bank-xiandai-hanyu:w_000410", "词类分析壳代表题：突然为形容词（区分突然/忽然，真题相关）")

# --- 短语结构壳 w_000411-419 (Cluster B, keep 2) ---
kb("bank-xiandai-hanyu:w_000411", "短语结构壳代表题：坐在床上为中补短语", ["中补短语=述补短语"])
de("bank-xiandai-hanyu:w_000412", "短语结构壳（来了三位→动宾）同壳换词，动宾由 z_000145 真题覆盖（规则a）")
de("bank-xiandai-hanyu:w_000413", "短语结构壳（敢想敢说→联合）同壳换词（规则a）")
de("bank-xiandai-hanyu:w_000414", "短语结构壳（领导带头→主谓）同壳换词，主谓由 z_000153 覆盖（规则a）")
de("bank-xiandai-hanyu:w_000415", "短语结构壳（放学之前→方位短语）同壳换词，方位短语属较冷小类（规则a/d）")
de("bank-xiandai-hanyu:w_000416", "短语结构壳（派他完成→兼语）同壳换词，兼语由 z_000139/w_000311 覆盖（规则a）")
kb("bank-xiandai-hanyu:w_000417", "短语结构壳代表题：卖菜的为的字短语", ["的字短语=的字结构"])
de("bank-xiandai-hanyu:w_000418", "短语结构壳（拍着手笑→连谓）同壳换词，连谓由 z_000147/w_000363 覆盖（规则a）")
de("bank-xiandai-hanyu:w_000419", "短语结构壳（我们三个人→同位）同壳换词，同位由 z_000137 覆盖（规则a）")

# --- 歧义短语 w_000420 ---
kt("bank-xiandai-hanyu:w_000420", "歧义短语综合多选（五个均可作不同层次切分），综合性强，可与 z_000166 测试题配套", ["多义短语=歧义短语"])

# --- 句型识别壳 w_000421-426 (同 w_000359-366 换例，全部删) ---
de("bank-xiandai-hanyu:w_000421", "与 w_000362 同考点（主谓谓语句）换例复制（规则a）")
de("bank-xiandai-hanyu:w_000422", "与 w_000366 同考点（把字句）换例复制（规则a）")
de("bank-xiandai-hanyu:w_000423", "与 q_000007 同考点（存现句）换例复制（规则a）")
de("bank-xiandai-hanyu:w_000424", "与 w_000363 同考点（连动句）换例复制（规则a）")
de("bank-xiandai-hanyu:w_000425", "与 w_000364 同考点（兼语句）换例复制（规则a）")
de("bank-xiandai-hanyu:w_000426", "与 w_000364 同考点（兼语句）换例复制（规则a）")

# --- 复句第一层壳 w_000427-429 (keep 1) ---
de("bank-xiandai-hanyu:w_000427", "复句第一层壳（并列），与 w_000428/429 同壳，保留 1 题（规则a）")
kb("bank-xiandai-hanyu:w_000428", "复句第一层代表题：因果（经过的年月一多…所以…）")
de("bank-xiandai-hanyu:w_000429", "复句第一层壳（转折），与 w_000428 同壳（规则a）")

# --- 没有语法错误壳 w_000430-433 (keep 2) ---
kb("bank-xiandai-hanyu:w_000430", "没有语法错误壳代表题：故障名词误用作谓语（词性误用）")
kb("bank-xiandai-hanyu:w_000431", "没有语法错误壳代表题：熟练形容词误带宾语（词性误用）")
de("bank-xiandai-hanyu:w_000432", "与 w_000430 同壳（他的工作很模范→名词误用）换词（规则a）")
de("bank-xiandai-hanyu:w_000433", "与 w_000431 同壳（比赛不及物带宾语）换词，且 k_000124 已覆盖（规则a）")

# --- 改错壳 w_000434-437 (keep 2) ---
kb("bank-xiandai-hanyu:w_000434", "改错壳代表题：刚刚应改为刚才（时间名词/副词辨析，真题相关）")
de("bank-xiandai-hanyu:w_000435", "改错壳（删很）同壳换词（规则a）")
kb("bank-xiandai-hanyu:w_000436", "改错壳代表题：防止不发生→删不（否定多余）")
de("bank-xiandai-hanyu:w_000437", "改错壳（删被）同壳换词（规则a）")

# ============ validate ============
import json as _json
with open("D:/study_app/tools/seed-builder/out/v09/existing/语法.json", "r", encoding="utf-8") as f:
    ids = [q["id"] for q in _json.load(f)]

missing = [i for i in ids if i not in D]
extra = [k for k in D if k not in ids]
print("total in file:", len(ids))
print("total in D:", len(D))
print("missing:", missing)
print("extra:", extra)
assert not missing and not extra, "mismatch!"

# counts
from collections import Counter
print(Counter(v["action"] for v in D.values()))

gaps = [
    {"考点": "句群（特征/与复句区别/十类/句群语病）",
     "素材证据": "素材整节「句群」：『句群大于复句，是介于复句和段落之间的语法单位』（块 20260725224153-e1a5ja9）、『句群与复句的区别：构成单位/关联词语/类型差异/所属范畴/划分目的』（块 20260725212124-tl0tfix 等）、『句群按句际关系分并列、顺承、解说、选择、递进、条件、假设、因果、目的、转折十类』（20260725212124-yqpf6of）、『句群语病常见类型』（20260725212124-z5h3ybl）。存量题 0 覆盖。"},
    {"考点": "标点符号分类：点号7种/标号9种；分号用于多重复句分组；冒号管到句终",
     "素材证据": "『标点符号分为点号和标号两类』（20260725212432-5tsy6mv）、『点号：有7种…句号、问号、叹号、分号、逗号、顿号和冒号』（20260725212432-4ec8w50）、『标号：有9种』（20260725212432-tgrmyfm）、『分号用于多重复句中起分组作用』（20260725212432-081rws0）、『冒号一般管到句终』（20260725212432-hr7e5x1）。存量题仅 q_000067 覆盖破折号/省略号一处。"},
    {"考点": "多层定语语序、多层状语语序",
     "素材证据": "『多层定语的顺序：领属+时间处所+数量短语指示代词+动词性词语或主谓短语+形容词词语+质料属性或范围的名词动词+中心语』（20260725211028-i6s9meb）、『多层状语的顺序：时间名词+处所+范围副词+情态形容词+对象介词短语+中心语』（20260725211028-vvfiyjf）。存量题无正向排序题（k_000121 仅为病句语序不当）。"},
    {"考点": "补语和宾语的辨认三法（看标记/看关系/看词性）及把字提宾法",
     "素材证据": "『补语和宾语的辨认：(1)看标记(有无「得」)(2)看关系(提问法V什么/V得怎么样)(3)看词性』（20260725211028-7twxzgh）、『可用「把」字提宾法来鉴别』。存量题仅 q_000006 覆盖「看关系」一法。"},
    {"考点": "双层补语及补语宾语顺序（动+补+宾/动+宾+补/动+补+宾+补/动+宾+补+宾）",
     "素材证据": "『补语和宾语的顺序及多层补语：(1)动+补+宾(2)动+宾+补(3)动+补+宾+补：拿出书来(4)动+宾+补+宾：给他三次钱』（20260725211028-ai9gscd）、『双层补语的结构：结果+动量、趋向+动量、趋向+趋向』（20260725211028-xycju2p）。存量题 0 覆盖。"},
    {"考点": "兼语句四种类型（使令式/爱恨式/选定式/有字式）",
     "素材证据": "『(1)使令式…请、使、叫、让、派…(2)爱恨式…称赞、表扬、骂、恨、嫌…(3)选定式…选举、称、认…(4)有字式…有、轮』（20260725211448-rzkh5p9/8nrmne4/ie06ne6/xq0mjaz）。存量题仅识别兼语句，无四式分类题。"},
    {"考点": "疑问代词任指/虚指用法",
     "素材证据": "『疑问代词可以不表疑问，引申为任指和虚指两种用法』（20260725205915-bzrxnyx）、『任指：谁也听不懂他的话…虚指：我好像在哪儿见过她』（20260725205915-yd19hh9/oll913p），且代词特征为陕师25年填空题考点。存量题 0 覆盖。"},
    {"考点": "变式句：省略句/倒装句（主谓倒装、定语后置、状语后置）",
     "素材证据": "『省略句：对话省/因上下文而省』（20260725211448-dz3frld）、『倒装句：包括主谓倒装、定语后置和状语后置』（20260725211448-zeob1fu）。存量题仅 w_000391 多选点到名称，无识别题。"},
    {"考点": "状态形容词 vs 性质形容词及其语法特征（状态形容词不能再受程度副词修饰、不能重叠）",
     "素材证据": "『性质形容词大都能受程度副词修饰…性质形容词的重叠式和状态形容词，不能再受程度副词修饰』（20260725205915-akclubb）、『状态形容词如雪白、漆黑、血红，不用加很或重叠』（20260725205915-slyn8x4）。存量题仅 z_000155/k_000117 两句判断，缺系统识别题。"},
    {"考点": "特殊句式之比较句",
     "素材证据": "素材概览明确列出特殊句式：『把字句、被字句、连谓句、兼语句、双宾句、存现句、比较句』（20260725214057-ahrbzdz）。存量题覆盖把/被/连谓/兼语/双宾/存现，比较句 0 覆盖。"},
    {"考点": "能愿动词（助动词）语法特征（V不V式、不V不式、可作谓语中心、不能重叠）",
     "素材证据": "『能愿动词…有「V 不 V」式和「不 V 不」式…还可以做谓语或谓语中心』（20260725205915-az8s8ui/fzd4j0h）。存量题 0 覆盖能愿动词专属题。"},
    {"考点": "语气词「的」与结构助词「的」的辨析方法（陕师16年选择题考点）",
     "素材证据": "『语气词「的」和助词「的」的区别』（20260725210126-58zsqlj）、『(1)看后面能不能添加上相应的名词…(3)用改为否定句的办法来检验』（20260725210126-pp574xc）。存量题 z_000142/w_000396 只考识别，未考辨析方法。"},
]
D["_gaps"] = gaps

out_path = "D:/study_app/tools/seed-builder/out/v09/dispositions/语法.json"
with io.open(out_path, "w", encoding="utf-8") as f:
    _json.dump(D, f, ensure_ascii=False, indent=1)
print("written:", out_path)
