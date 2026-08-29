# -*- coding: utf-8 -*-
"""现代汉语多选扩充：基于思源笔记知识框架出题（purpose=test）
写入题库包 测试-*.json，重打包 v0.14.0
"""
import io, sys, json, zipfile, os, shutil, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BANK = 'bank-xiandai-hanyu'
SRC = r'D:\study_app\app\assets\banks\bank-xiandai-hanyu-v0.13.0.zip'
DST = r'D:\study_app\app\assets\banks\bank-xiandai-hanyu-v0.14.0.zip'
VERSION = '0.14.0'

random.seed(20260829)

# ---- 题目定义：answer 为正确项文本（v4） ----
def mc(stem, options, answer_idx, chapter, expl, tags=None):
    """options: [(text, is_correct)]；shuffle 后生成，answer 为文本列表"""
    items = list(options)
    random.shuffle(items)
    keys = 'ABCDEFGHIJKL'
    opts = [{'key': keys[i], 'text': t} for i, (t, _) in enumerate(items)]
    ans = [t for t, ok in items if ok]
    return {
        'id': None, 'type': 'multi_choice', 'stem': stem,
        'options': opts, 'answer': ans, 'explanation': expl,
        'chapter': chapter,
        'tags': ['多选扩充'] + (tags or []),
        'difficulty': 'medium', 'purpose': 'test',
        'answerFormat': '多选：选出所有符合题意的选项字母。',
    }

QS = []
def add(stem, options, chapter, expl, tags=None):
    QS.append(mc(stem, options, None, chapter, expl, tags))

# ============ 绪论 ============
add('下列方言中，属于现代汉语七大方言区的有（多选）',
    [('北方方言', True), ('吴方言', True), ('湘方言', True),
     ('赣方言', True), ('西南官话', False), ('粤方言', True)],
    '绪论',
    '现代汉语七大方言区：北方方言、吴方言、湘方言、赣方言、客家方言、闽方言、粤方言；"西南官话"是北方方言的一个分区，不是独立的方言区。')
add('现代汉民族共同语的标准包括（多选）',
    [('以北京语音为标准音', True), ('以北方话为基础方言', True),
     ('以典范的现代白话文著作为语法规范', True), ('以上海语音为标准音', False),
     ('以吴语为基础方言', False)],
    '绪论',
    '现代汉民族共同语（普通话）的三项标准：语音以北京语音为标准音、词汇以北方话为基础方言、语法以典范的现代白话文著作为规范。')
add('下列关于现代汉语特点的说法，正确的有（多选）',
    [('语音方面无复辅音', True), ('元音占优势', True), ('有声调', True),
     ('量词丰富', True), ('语法方面语序和虚词不重要', False)],
    '绪论',
    '现代汉语语音无复辅音、元音占优势、有声调；语法方面语序和虚词重要、词类多功能、量词丰富、有语气词。"语序和虚词不重要"与事实相反。')
add('汉民族共同语在其历史发展过程中出现过的称谓包括（多选）',
    [('雅言', True), ('通语', True), ('官话', True), ('国语', True),
     ('白话', False)],
    '绪论',
    '汉民族共同语演变：雅言（春秋）→通语（汉）→官话（明）→国语→普通话。"白话"指书面语形式，不是共同语称谓。')
add('下列属于北方方言（官话）分区的有（多选）',
    [('华北—东北', True), ('西北', True), ('西南', True), ('江淮', True),
     ('粤海', False)],
    '绪论',
    '北方方言分为华北—东北、西北、西南、江淮四个次方言区；"粤海"属粤方言区，不属于北方方言。')
add('下列关于现代汉语词汇特点的说法，正确的有（多选）',
    [('单音节语素为主', True), ('双音节词占优势', True),
     ('广泛运用词根复合法构成新词', True), ('多音节语素占优势', False)],
    '绪论',
    '现代汉语词汇以单音节语素为主、双音节词占优、多用词根复合法构词；"多音节语素占优势"不符合现代汉语实际。')

# ============ 语音 ============
add('普通话声调系统包括的调类有（多选）',
    [('阴平', True), ('阳平', True), ('上声', True), ('去声', True),
     ('入声', False)],
    '语音',
    '普通话有阴平（55）、阳平（35）、上声（214）、去声（51）四个调类；入声是古代调类，普通话中已派人四声。')
add('语音的物理属性（四要素）包括（多选）',
    [('音高', True), ('音强', True), ('音长', True), ('音色', True),
     ('音位', False)],
    '语音',
    '语音的物理属性包括音高、音强、音长、音色；音位是按社会属性归纳出来的语音单位，不属于物理属性。')
add('下列韵母中，属于前响复元音韵母的有（多选）',
    [('ai', True), ('ei', True), ('ao', True), ('ou', True),
     ('ia', False)],
    '语音',
    '前响复元音韵母有 ai、ei、ao、ou 四个，韵腹在前；ia、ue 等是后响复元音，韵腹在后。')
add('普通话声母按发音部位划分，属于舌尖中音的有（多选）',
    [('d', True), ('t', True), ('n', True), ('l', True),
     ('z', False)],
    '语音',
    '舌尖中音是舌尖抵住上齿龈成阻的 d、t、n、l；z 是舌尖前音，与舌尖中音不同部位。')
add('普通话韵母的结构成分包括（多选）',
    [('韵头', True), ('韵腹', True), ('韵尾', True), ('声调', False),
     ('声母', False)],
    '语音',
    '韵母由韵头、韵腹、韵尾构成，韵腹是主干；声母和声调不属于韵母的结构成分。')
add('下列现象中，属于普通话语流音变的有（多选）',
    [('轻声', True), ('儿化', True), ('上声变调', True),
     ('语气词"啊"的音变', True), ('押韵', False)],
    '语音',
    '语流音变包括轻声、儿化、变调（如上声变调、一/不/七八变调）以及语气词"啊"的音变；押韵是韵文用韵规则，不属于语流音变。')
add('归纳音位（音位系统的建立）所依据的标准包括（多选）',
    [('辨义功能', True), ('互补分布', True), ('音感差异', True),
     ('发音方法必须相同', False)],
    '语音',
    '归纳音位依据辨义功能、互补分布和音感差异三条标准；发音方法相同与否不是归纳音位的主要标准。')

# ============ 文字 ============
add('汉字的造字法（传统"四书"）包括（多选）',
    [('象形', True), ('指事', True), ('会意', True), ('形声', True),
     ('假借', False)],
    '文字',
    '传统四书指象形、指事、会意、形声四种造字法；假借、转注属"六书"中用字之法，不是造字法。')
add('现行汉字形体的前身（历史演变序列）包括（多选）',
    [('甲骨文', True), ('金文', True), ('篆书', True), ('隶书', True),
     ('楷书', True)],
    '文字',
    '汉字形体演变：甲骨文→金文→篆书→隶书→楷书，楷书是现行汉字的标准形体。')
add('汉字的印刷体（印刷字形）包括（多选）',
    [('宋体', True), ('仿宋体', True), ('黑体', True), ('楷体', True),
     ('行书体', False)],
    '文字',
    '汉字印刷体常见宋体、仿宋体、黑体、楷体；行书是手写体，不属于印刷体。')
add('汉字标准化的"四定"包括（多选）',
    [('定量', True), ('定形', True), ('定音', True), ('定序', True),
     ('定数', False)],
    '文字',
    '汉字标准化要求定量、定形、定音、定序；"定数"不是规范提法。')
add('现行汉字的基本笔画包括（多选）',
    [('横', True), ('竖', True), ('撇', True), ('点', True), ('折', True),
     ('提', False)],
    '文字',
    '现行汉字五种基本笔画是横、竖、撇、点、折；"提"是派生笔画而非基本笔画。')
add('下列属于掌握和使用规范汉字要求的有（多选）',
    [('掌握简化字', True), ('不用异体字', True), ('区别新旧字形', True),
     ('掌握异形词的规范词形', True), ('恢复使用繁体字', False)],
    '文字',
    '使用规范汉字要求掌握简化字、不用异体字、区别新旧字形、掌握异形词规范词形；恢复繁体字与规范用字方向相反。')

# ============ 词汇 ============
add('合成词的结构类型包括（多选）',
    [('复合式', True), ('重叠式', True), ('附加式', True), ('联绵式', False)],
    '词汇',
    '合成词分复合式、重叠式、附加式三类；联绵词是单纯词（如"参差""仿佛"），不是合成词结构类型。')
add('下列各组词中，属于单纯词的有（多选）',
    [('联绵词', True), ('叠音词', True), ('音译外来词', True),
     ('拟声词', True), ('复合词', False)],
    '词汇',
    '单纯词包括联绵词（双声/叠韵等）、叠音词、音译外来词、拟声词；复合词由两个以上语素构成，是合成词。')
add('一般词汇（相对于基本词汇）包括（多选）',
    [('古语词', True), ('方言词', True), ('外来词', True), ('行业语', True),
     ('隐语', True), ('基本词汇', False)],
    '词汇',
    '一般词汇包括古语词、方言词、外来词、行业语、隐语等；基本词汇与一般词汇相对，不属一般词汇。')
add('汉语外来词的类型包括（多选）',
    [('音译', True), ('音译加意译', True), ('音译兼意译', True),
     ('借形', True), ('字母词', True), ('纯意译', False)],
    '词汇',
    '外来词类型有音译（沙发）、音译加意译（啤酒）、音译兼意译（可口可乐）、借形（AA制）、字母词（WTO）；纯意译（如"电话"）一般不算外来词。')
add('下列关于词义性质的说法，正确的有（多选）',
    [('词义具有概括性', True), ('词义具有模糊性', True),
     ('词义具有民族性', True), ('词义具有具体性', False)],
    '词汇',
    '词义的性质是概括性、模糊性、民族性；"具体性"与词义概括性的本质属性相矛盾。')
add('词的色彩义（附属义）包括（多选）',
    [('感情色彩', True), ('语体色彩', True), ('形象色彩', True),
     ('理性色彩', False)],
    '词汇',
    '色彩义包括感情色彩（褒/贬/中）、语体色彩（口语/书面）、形象色彩；理性色彩即概念义，是词义的核心，不属于附属色彩义。')
add('语义场的类型包括（多选）',
    [('类属义场', True), ('顺序义场', True), ('关系义场', True),
     ('同义义场', True), ('反义义场', True), ('组合义场', False)],
    '词汇',
    '语义场分类属、顺序、关系、同义、反义五类；"组合义场"不是语义场的类型划分。')

# ============ 语法 ============
add('现代汉语短语的结构类型包括（多选）',
    [('主谓', True), ('动宾', True), ('偏正', True), ('中补', True),
     ('联合', True), ('连谓', True), ('兼语', True), ('同位', True),
     ('陈述', False)],
    '语法',
    '短语结构类型有主谓、动宾、偏正（定中/状中）、中补、联合、连谓、兼语、同位八类；"陈述"是主谓短语的语义关系而非结构类型名。')
add('下列属于现代汉语特殊句式（特殊动词谓语句）的有（多选）',
    [('把字句', True), ('被字句', True), ('连谓句', True),
     ('兼语句', True), ('双宾句', True), ('存现句', True),
     ('陈述句', False)],
    '语法',
    '特殊句式包括把字句、被字句、连谓句、兼语句、双宾句、存现句、比较句等；陈述句是按语气划分的句类，不是特殊句式。')
add('下列属于联合复句关系类型的有（多选）',
    [('并列', True), ('顺承', True), ('解说', True), ('选择', True),
     ('递进', True), ('因果', False)],
    '语法',
    '联合复句包括并列、顺承、解说、选择、递进五类；因果属于偏正复句。')
add('下列属于偏正复句关系类型的有（多选）',
    [('因果', True), ('条件', True), ('假设', True), ('转折', True),
     ('让步', True), ('目的', True), ('并列', False)],
    '语法',
    '偏正复句包括因果、条件、假设、转折、让步、目的等；并列是联合复句关系。')
add('下列属于句类（按语气划分）的有（多选）',
    [('陈述句', True), ('疑问句', True), ('祈使句', True),
     ('感叹句', True), ('主谓句', False)],
    '语法',
    '句类按语气分为陈述句、疑问句、祈使句、感叹句；主谓句是按结构划分的句型。')
add('单句常见的语病类型包括（多选）',
    [('搭配不当', True), ('残缺与多余', True), ('语序不当', True),
     ('句式杂糅', True), ('修辞不生动', False)],
    '语法',
    '单句语病主要有搭配不当、残缺与多余、语序不当、句式杂糅；"修辞不生动"不属于语法语病。')
add('下列词类中，属于虚词的有（多选）',
    [('介词', True), ('连词', True), ('助词', True), ('语气词', True),
     ('叹词', True), ('副词', False)],
    '语法',
    '现代汉语虚词包括介词、连词、助词、语气词、叹词等；副词在教材中一般归入实词（半实词），不列为虚词。')

# ============ 修辞 ============
add('比喻的基本类型包括（多选）',
    [('明喻', True), ('暗喻', True), ('借喻', True), ('拟人', False)],
    '修辞',
    '比喻分明喻、暗喻、借喻三种基本类型；拟人是比拟的一种，与比喻是不同辞格。')
add('下列辞格中，属于常用修辞格的有（多选）',
    [('比喻', True), ('比拟', True), ('借代', True), ('夸张', True),
     ('标点', False)],
    '修辞',
    '比喻、比拟、借代、夸张都是常用辞格；"标点"是书面符号系统，不是修辞格。')
add('夸张的类型包括（多选）',
    [('扩大夸张', True), ('缩小夸张', True), ('超前夸张', True),
     ('比喻夸张', False)],
    '修辞',
    '夸张分扩大夸张、缩小夸张、超前夸张三类；"比喻夸张"不是夸张的类型。')
add('对偶的类型包括（多选）',
    [('正对', True), ('反对', True), ('串对', True), ('平对', False)],
    '修辞',
    '对偶按内容分正对、反对、串对（流水对）；"平对"不是对偶类型的规范名称。')
add('词语的锤炼包括的内容有（多选）',
    [('意义的锤炼', True), ('声音的锤炼', True), ('结构的锤炼', False)],
    '修辞',
    '词语锤炼包括意义的锤炼（准确、鲜明、生动）和声音的锤炼（音节匀称、声调和谐、韵律协调）；"结构的锤炼"不是规范提法。')
add('下列属于现代汉语书面语体类型的有（多选）',
    [('公文语体', True), ('科技语体', True), ('政论语体', True),
     ('文艺语体', True), ('口头语体', False)],
    '修辞',
    '书面语体分公文语体、科技语体、政论语体、文艺语体；口头语体与书面语体相对，是语体的大类，不属于书面语体之列。')
add('下列句式类型中，属于"句式的选择"所涉及的有（多选）',
    [('长句和短句', True), ('整句和散句', True), ('主动句和被动句', True),
     ('肯定句和否定句', True), ('口语句式和书面语句式', True),
     ('主谓句和非主谓句', False)],
    '修辞',
    '句式选择涉及长句/短句、整句/散句、主动/被动、肯定/否定、口语/书面语等；主谓句与非主谓句是句型分类，不是句式选择的范畴。')

# ============ 标点符号 ============
add('下列标点符号中，属于句末点号的有（多选）',
    [('句号', True), ('问号', True), ('叹号', True), ('逗号', False),
     ('顿号', False)],
    '标点符号',
    '句末点号包括句号、问号、叹号；逗号、顿号是句中点号。')
add('下列标点符号中，属于句中点号的有（多选）',
    [('逗号', True), ('顿号', True), ('分号', True), ('冒号', True),
     ('句号', False)],
    '标点符号',
    '句中点号包括逗号、顿号、分号、冒号；句号是句末点号。')
add('下列标点符号中，属于标号的有（多选）',
    [('引号', True), ('括号', True), ('破折号', True), ('省略号', True),
     ('书名号', True), ('逗号', False)],
    '标点符号',
    '标号包括引号、括号、破折号、省略号、着重号、书名号、间隔号、连接号；逗号是点号。')
add('下列标点符号中，属于标号的有（多选）',
    [('着重号', True), ('间隔号', True), ('连接号', True),
     ('顿号', False), ('分号', False)],
    '标点符号',
    '着重号、间隔号、连接号都是标号；顿号、分号是点号。')

print('现代汉语多选扩充题数:', len(QS))

# ---- 分配 id 并合并进题库包 ----
with zipfile.ZipFile(SRC) as z:
    names = z.namelist()
    # 读取 manifest 和现有测试章节
    manifest = json.loads(z.read('manifest.json'))
    chapter_files = [n for n in names if n.startswith('questions/测试-') and n.endswith('.json')]
    # 现有 id 集合
    existing_ids = set()
    for n in names:
        if n.startswith('questions/') and n.endswith('.json'):
            for q in json.loads(z.read(n)):
                existing_ids.add(q.get('id'))
    # 收集现有测试文件内容
    chap_data = {}
    for n in chapter_files:
        chap_data[n] = json.loads(z.read(n))
    # 分配 id：mc_000001 起，避免冲突
    seq = 1
    prefix = f'{BANK}:mc_'
    for q in QS:
        while f'{prefix}{seq:06d}' in existing_ids:
            seq += 1
        q['id'] = f'{prefix}{seq:06d}'
        existing_ids.add(q['id'])
        seq += 1
    # 按 chapter 归入对应测试章节文件
    for q in QS:
        # 章节文件映射
        key = None
        for n in chapter_files:
            ch_name = n.split('测试-')[-1].replace('.json', '')
            if q['chapter'] == ch_name:
                key = n
                break
        if key is None:
            # 语法里的标点符号归入 测试-标点符号.json
            if q['chapter'] == '标点符号':
                key = 'questions/测试-标点符号.json'
        if key is None:
            raise RuntimeError(f'章节文件未找到: {q["chapter"]}')
        chap_data.setdefault(key, []).append(q)

    # 更新 manifest 版本
    manifest['version'] = VERSION
    # questionCount = 现有总题数 + 新增（与原包口径一致：总题数）
    existing_total = 0
    for n in names:
        if n.startswith('questions/') and n.endswith('.json'):
            existing_total += len(json.loads(z.read(n)))
    manifest['questionCount'] = existing_total + len(QS)
    manifest['updatedAt'] = '2026-08-29'

    with zipfile.ZipFile(DST, 'w', zipfile.ZIP_DEFLATED) as zout:
        for n in names:
            if n == 'manifest.json':
                zout.writestr(n, json.dumps(manifest, ensure_ascii=False, indent=1))
            elif n in chap_data and n.startswith('questions/测试-'):
                zout.writestr(n, json.dumps(chap_data[n], ensure_ascii=False, indent=1))
            else:
                zout.writestr(n, z.read(n))

print('已生成:', DST)
print('manifest 版本:', manifest['version'], '题数:', manifest['questionCount'])
# 验证
with zipfile.ZipFile(DST) as z:
    tot_mc = 0
    for n in z.namelist():
        if n.startswith('questions/测试-'):
            for q in json.loads(z.read(n)):
                if q.get('type') == 'multi_choice':
                    tot_mc += 1
    print('测试章节多选总数:', tot_mc)
