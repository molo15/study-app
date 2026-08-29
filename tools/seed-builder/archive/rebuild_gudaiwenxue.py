# -*- coding: utf-8 -*-
"""古代文学史 元代5→8、清代5→8、近代4→6 重拆扩充
注意：思源笔记无元/清/近代独立文档，知识点依据通行古代文学史教材常识（考研标准考点）扩充。
保留原有好题，补充知识点与题目。
"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = r"D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json"

YUAN = [
    {"id": "k_wxs_yuandai_01", "name": "元杂剧的体制与关汉卿", "parent": "k_wxs_yuandai", "chapter": "元代文学", "hot": True,
     "summary": "元杂剧结构体制一般为四折一楔子，剧本由曲词、宾白、科范（科介）三部分组成，一般由一人主唱。关汉卿是元杂剧的奠基人、元曲四大家之首，代表作《窦娥冤》写窦娥蒙冤及血溅白练、六月飞雪、大旱三年三桩誓愿，另有《救风尘》《单刀会》等。",
     "basicQuestions": [
        {"stem": "元杂剧的结构体制一般为____一楔子。", "type": "blank", "answer": "四折",
         "explanation": "元杂剧结构体制一般为四折一楔子。",
         "options": []},
        {"stem": "关汉卿的代表作《____》写窦娥蒙冤及三桩誓愿。", "type": "blank", "answer": "窦娥冤",
         "explanation": "关汉卿《窦娥冤》写窦娥蒙冤，临刑前发下血溅白练、六月飞雪、大旱三年三桩誓愿。",
         "options": []},
        {"stem": "元杂剧剧本一般由曲词、宾白、____三部分组成。", "type": "blank", "answer": "科范（科介）",
         "explanation": "元杂剧剧本由曲词（唱）、宾白（白）、科范（科）三部分组成。",
         "options": []},
     ]},
    {"id": "k_wxs_yuandai_02", "name": "王实甫与《西厢记》", "parent": "k_wxs_yuandai", "chapter": "元代文学", "hot": True,
     "summary": "王实甫《西厢记》写张生与崔莺莺的爱情，题材源于元稹《莺莺传》，直接继承董解元《西厢记诸宫调》。“愿天下有情人终成眷属”由张生之口喊出；红娘是性格最光彩的婢女形象；《西厢记》被称为“天下夺魁”之作，是元杂剧中以多本连演的长篇。",
     "basicQuestions": [
        {"stem": "《西厢记》中“愿天下有情人____”这一口号由王实甫借人物之口喊出。", "type": "blank", "answer": "都成了眷属",
         "explanation": "“愿天下有情人终成眷属”由王实甫借张生之口喊出。",
         "options": []},
        {"stem": "《西厢记》中性格最为光彩的婢女形象是____。", "type": "blank", "answer": "红娘",
         "explanation": "红娘是《西厢记》中性格最光彩的婢女形象，撮合张生与莺莺。",
         "options": []},
        {"stem": "《西厢记》题材的直接渊源是（　）", "type": "choice", "answer": "董解元《西厢记诸宫调》",
         "explanation": "《西厢记》题材源于元稹《莺莺传》，直接继承董解元《西厢记诸宫调》。",
         "options": ["董解元《西厢记诸宫调》", "元稹《莺莺传》", "白朴《墙头马上》", "关汉卿《拜月亭》"]},
     ]},
    {"id": "k_wxs_yuandai_03", "name": "元代散曲", "parent": "k_wxs_yuandai", "chapter": "元代文学", "hot": True,
     "summary": "散曲是元代新兴的诗体，包括小令与套数（套曲）两种主要形式。马致远《天净沙·秋思》“枯藤老树昏鸦”被称为“秋思之祖”，是散曲中的绝唱。散曲语言俚俗活泼、押韵灵活，可加衬字。",
     "basicQuestions": [
        {"stem": "“散曲”包括小令与____。", "type": "blank", "answer": "套数",
         "explanation": "散曲包括小令与套数（套曲）两种主要形式。",
         "options": []},
        {"stem": "被称“秋思之祖”的散曲《天净沙·秋思》的作者是（　）", "type": "choice", "answer": "马致远",
         "explanation": "马致远《天净沙·秋思》“枯藤老树昏鸦，小桥流水人家”被称为“秋思之祖”。",
         "options": ["马致远", "关汉卿", "张养浩", "白朴"]},
        {"stem": "散曲在格律上可在曲律规定之外增加____字。", "type": "blank", "answer": "衬",
         "explanation": "散曲语言俚俗活泼，可以加衬字，比词更灵活。",
         "options": []},
     ]},
    {"id": "k_wxs_yuandai_04", "name": "南戏与《琵琶记》", "parent": "k_wxs_yuandai", "chapter": "元代文学", "hot": True,
     "summary": "南戏是宋元时期流行于南方的戏曲形式。被称为“南戏之祖”的元代作品是高明的《琵琶记》，写蔡伯喈与赵五娘的故事；四大南戏为“荆刘拜杀”（《荆钗记》《白兔记》《拜月亭记》《杀狗记》）。",
     "basicQuestions": [
        {"stem": "被称为“南戏之祖”的元代作品是高明的《____》。", "type": "blank", "answer": "琵琶记",
         "explanation": "高明《琵琶记》被称为“南戏之祖”。",
         "options": []},
        {"stem": "《琵琶记》中的女主人公是____。", "type": "blank", "answer": "赵五娘",
         "explanation": "《琵琶记》写蔡伯喈与赵五娘的故事，赵五娘是女主人公。",
         "options": []},
        {"stem": "“荆刘拜杀”指的是（　）", "type": "choice", "answer": "《荆钗记》《白兔记》《拜月亭记》《杀狗记》",
         "explanation": "四大南戏简称“荆刘拜杀”：《荆钗记》《白兔记》《拜月亭记》《杀狗记》。",
         "options": ["《荆钗记》《白兔记》《拜月亭记》《杀狗记》", "《窦娥冤》《汉宫秋》《梧桐雨》《赵氏孤儿》", "《西厢记》《墙头马上》《倩女离魂》《汉宫秋》", "《琵琶记》《牡丹亭》《长生殿》《桃花扇》"]},
     ]},
    {"id": "k_wxs_yuandai_05", "name": "元诗四大家与元代诗文", "parent": "k_wxs_yuandai", "chapter": "元代文学", "hot": True,
     "summary": "“元诗四大家”指虞集、杨载、范梈、揭傒斯四人，以虞集成就最高。元代后期杨维桢创“铁崖体”，诗风奇诡；元代还出现了话本、讲史等通俗文学，如《三国志平话》。",
     "basicQuestions": [
        {"stem": "“元诗四大家”是指____、杨载、范梈、揭傒斯四人。", "type": "blank", "answer": "虞集",
         "explanation": "元诗四大家为虞集、杨载、范梈、揭傒斯，以虞集成就最高。",
         "options": []},
        {"stem": "元代后期创“铁崖体”、诗风奇诡的诗人是（　）", "type": "choice", "answer": "杨维桢",
         "explanation": "杨维桢号铁崖，创“铁崖体”，诗风奇诡，是元代后期诗坛代表。",
         "options": ["杨维桢", "虞集", "揭傒斯", "范梈"]},
     ]},
    {"id": "k_wxs_yuandai_06", "name": "元杂剧的四大悲剧", "parent": "k_wxs_yuandai", "chapter": "元代文学", "hot": True,
     "summary": "元杂剧四大悲剧：关汉卿《窦娥冤》、白朴《梧桐雨》（李隆基杨玉环故事）、马致远《汉宫秋》（王昭君出塞）、纪君祥《赵氏孤儿》。另有四大爱情剧：《西厢记》《墙头马上》《拜月亭》《倩女离魂》。",
     "basicQuestions": [
        {"stem": "元杂剧四大悲剧中，写王昭君出塞故事的是马致远的《____》。", "type": "blank", "answer": "汉宫秋",
         "explanation": "马致远《汉宫秋》写王昭君出塞故事，是元杂剧四大悲剧之一。",
         "options": []},
        {"stem": "元杂剧四大悲剧中，写李隆基与杨玉环爱情悲剧的是白朴的《____》。", "type": "blank", "answer": "梧桐雨",
         "explanation": "白朴《梧桐雨》写唐明皇李隆基与杨贵妃的爱情悲剧。",
         "options": []},
        {"stem": "下列不属于元杂剧四大悲剧的是（　）", "type": "choice", "answer": "《西厢记》",
         "explanation": "四大悲剧为《窦娥冤》《梧桐雨》《汉宫秋》《赵氏孤儿》；《西厢记》属四大爱情剧。",
         "options": ["《西厢记》", "《窦娥冤》", "《赵氏孤儿》", "《汉宫秋》"]},
     ]},
    {"id": "k_wxs_yuandai_07", "name": "白朴与马致远的杂剧", "parent": "k_wxs_yuandai", "chapter": "元代文学", "hot": False,
     "summary": "白朴代表作《梧桐雨》（李杨故事）、《墙头马上》（写裴少俊与李千金的爱情）；马致远《汉宫秋》写王昭君，其散曲成就亦高；郑光祖《倩女离魂》写张倩女离魂追爱的故事。元曲四大家为关汉卿、白朴、马致远、郑光祖。",
     "basicQuestions": [
        {"stem": "元曲四大家指关汉卿、白朴、马致远和（　）", "type": "choice", "answer": "郑光祖",
         "explanation": "元曲四大家：关汉卿、白朴、马致远、郑光祖。",
         "options": ["郑光祖", "王实甫", "纪君祥", "张养浩"]},
        {"stem": "白朴写裴少俊与李千金爱情故事的杂剧是《____》。", "type": "blank", "answer": "墙头马上",
         "explanation": "白朴《墙头马上》写裴少俊与李千金的爱情故事，属四大爱情剧之一。",
         "options": []},
     ]},
    {"id": "k_wxs_yuandai_08", "name": "元杂剧的繁荣与形式", "parent": "k_wxs_yuandai", "chapter": "元代文学", "hot": False,
     "summary": "元杂剧兴盛于北方，形成一本四折、一人主唱的体制，角色有末、旦、净、杂等，主唱角色为“正末”或“正旦”，分别称“末本”“旦本”；剧本语言称“本色当行”。元代还产生《三国志平话》等讲史话本。",
     "basicQuestions": [
        {"stem": "元杂剧中由正旦主唱的剧本称（　）", "type": "choice", "answer": "旦本",
         "explanation": "元杂剧一般一人主唱，由正旦主唱称“旦本”，由正末主唱称“末本”。",
         "options": ["旦本", "末本", "净本", "杂本"]},
        {"stem": "元杂剧的语言讲究“本色当行”，其意是（　）", "type": "choice", "answer": "语言朴素自然、符合人物身份",
         "explanation": "“本色当行”指元杂剧语言朴素自然、贴近生活、符合舞台与人物身份。",
         "options": ["语言朴素自然、符合人物身份", "语言典雅华丽、辞采富丽", "多用典故、晦涩难懂", "讲究格律、平仄严格"]},
     ]},
]

QING = [
    {"id": "k_wxs_qingdai_01", "name": "《聊斋志异》与文言短篇小说", "parent": "k_wxs_qingdai", "chapter": "清代文学", "hot": True,
     "summary": "蒲松龄（字留仙，号柳泉居士）《聊斋志异》是清代文言短篇小说的集大成之作，鲁迅评其“用传奇法，而以志怪”；全书近五百篇，借花妖狐魅写人间百态，寄托孤愤。",
     "basicQuestions": [
        {"stem": "清代文言短篇小说集大成之作是蒲松龄的《____》。", "type": "blank", "answer": "聊斋志异",
         "explanation": "蒲松龄《聊斋志异》是清代文言短篇小说的集大成之作。",
         "options": []},
        {"stem": "鲁迅评《聊斋志异》的艺术特点是“用传奇法，而以____”。", "type": "blank", "answer": "志怪",
         "explanation": "鲁迅评《聊斋志异》“用传奇法，而以志怪”。",
         "options": []},
        {"stem": "《聊斋志异》的作者蒲松龄号（　）", "type": "choice", "answer": "柳泉居士",
         "explanation": "蒲松龄字留仙，号柳泉居士。",
         "options": ["柳泉居士", "随园主人", "香山居士", "六一居士"]},
     ]},
    {"id": "k_wxs_qingdai_02", "name": "《儒林外史》", "parent": "k_wxs_qingdai", "chapter": "清代文学", "hot": True,
     "summary": "吴敬梓《儒林外史》是我国古代讽刺小说的典范，鲁迅概括其结构特点为“虽云长篇，颇同短制”；塑造了范进、严监生等科举制度下的士人形象，讽刺科举与功名富贵。",
     "basicQuestions": [
        {"stem": "鲁迅概括《____》的结构特点为“虽云长篇，颇同短制”。", "type": "blank", "answer": "儒林外史",
         "explanation": "鲁迅评《儒林外史》“虽云长篇，颇同短制”，全书由众多相对独立的故事连缀而成。",
         "options": []},
        {"stem": "《儒林外史》的作者是（　）", "type": "choice", "answer": "吴敬梓",
         "explanation": "《儒林外史》作者吴敬梓，是我国古代讽刺小说的典范。",
         "options": ["吴敬梓", "李宝嘉", "蒲松龄", "曹雪芹"]},
        {"stem": "《儒林外史》中因中举喜极而疯的人物是（　）", "type": "choice", "answer": "范进",
         "explanation": "范进中举后喜极而疯，是《儒林外史》中科举制度毒害下的典型形象。",
         "options": ["范进", "严监生", "匡超人", "周进"]},
     ]},
    {"id": "k_wxs_qingdai_03", "name": "《红楼梦》", "parent": "k_wxs_qingdai", "chapter": "清代文学", "hot": True,
     "summary": "曹雪芹《红楼梦》前八十回为曹雪芹所著，后四十回一般认为高鹗续补；版本有脂评本（抄本）与程高本（刻本）两个系统；“满纸荒唐言，一把辛酸泪”是作者自题诗。小说以贾宝玉林黛玉的爱情悲剧为主线，展现封建大家族由盛而衰。",
     "basicQuestions": [
        {"stem": "《红楼梦》有____与程高本两个版本系统。", "type": "blank", "answer": "脂评本",
         "explanation": "《红楼梦》版本分脂评本（带脂砚斋评的抄本）与程高本（程伟元高鹗刻本）两个系统。",
         "options": []},
        {"stem": "一般认为《红楼梦》后四十回的作者是（　）", "type": "choice", "answer": "高鹗",
         "explanation": "《红楼梦》前八十回为曹雪芹著，后四十回一般认为高鹗续补。",
         "options": ["高鹗", "脂砚斋", "吴敬梓", "李汝珍"]},
        {"stem": "“满纸荒唐言，一把辛酸泪”出自《红楼梦》的（　）", "type": "choice", "answer": "作者自题诗",
         "explanation": "“满纸荒唐言，一把辛酸泪”是曹雪芹题《红楼梦》的自题诗。",
         "options": ["作者自题诗", "贾宝玉题咏", "林黛玉咏诗", "判词"]},
     ]},
    {"id": "k_wxs_qingdai_04", "name": "清代戏曲（《长生殿》《桃花扇》）", "parent": "k_wxs_qingdai", "chapter": "清代文学", "hot": True,
     "summary": "清代传奇双璧：洪昇《长生殿》写唐明皇与杨贵妃的爱情；“借离合之情，写兴亡之感”是孔尚任《桃花扇》的独特结构方式，写侯方域与李香君的爱情，反映南明兴亡。",
     "basicQuestions": [
        {"stem": "“借离合之情，写兴亡之感”是《____》的独特结构方式。", "type": "blank", "answer": "桃花扇",
         "explanation": "孔尚任《桃花扇》“借离合之情，写兴亡之感”，借侯李爱情写南明兴亡。",
         "options": []},
        {"stem": "李香君是《____》中的人物。", "type": "blank", "answer": "桃花扇",
         "explanation": "李香君是《桃花扇》中的女主人公，与侯方域的爱情贯穿全剧。",
         "options": []},
        {"stem": "洪昇《长生殿》写的是（　）的爱情故事。", "type": "choice", "answer": "唐明皇与杨贵妃",
         "explanation": "《长生殿》写唐明皇李隆基与杨贵妃的爱情故事。",
         "options": ["唐明皇与杨贵妃", "侯方域与李香君", "张生与崔莺莺", "裴少俊与李千金"]},
     ]},
    {"id": "k_wxs_qingdai_05", "name": "清代诗文词派", "parent": "k_wxs_qingdai", "chapter": "清代文学", "hot": True,
     "summary": "清词有阳羡派（陈维崧）、浙西派（朱彝尊）、常州词派（张惠言开山、周济发扬光大）。诗坛有王士禛“神韵说”、袁枚“性灵说”（《随园诗话》）、沈德潜“格调说”、翁方纲“肌理说”。",
     "basicQuestions": [
        {"stem": "常州词派由张惠言开山，至____发扬光大，蔚为宗派。", "type": "blank", "answer": "周济",
         "explanation": "常州词派由张惠言开山，至周济发扬光大。",
         "options": []},
        {"stem": "提出“性灵说”、《随园诗话》的诗人是（　）", "type": "choice", "answer": "袁枚",
         "explanation": "袁枚（随园主人）提出“性灵说”，著《随园诗话》。",
         "options": ["袁枚", "王士禛", "沈德潜", "翁方纲"]},
        {"stem": "清初词坛中，朱彝尊是（　）的代表。", "type": "choice", "answer": "浙西词派",
         "explanation": "朱彝尊是浙西词派代表，与阳羡派（陈维崧）并峙清初词坛。",
         "options": ["浙西词派", "阳羡词派", "常州词派", "云间词派"]},
     ]},
    {"id": "k_wxs_qingdai_06", "name": "桐城派与清代散文", "parent": "k_wxs_qingdai", "chapter": "清代文学", "hot": False,
     "summary": "桐城派是清代影响最大的散文流派，代表人物方苞（首创“义法”说）、刘大櫆、姚鼐（集大成，主张义理、考据、辞章三者统一），因三人皆安徽桐城人得名。",
     "basicQuestions": [
        {"stem": "清代散文影响最大的流派是（　）", "type": "choice", "answer": "桐城派",
         "explanation": "桐城派是清代影响最大的散文流派，因代表作家皆安徽桐城人得名。",
         "options": ["桐城派", "公安派", "竟陵派", "唐宋派"]},
        {"stem": "桐城派中首创散文“义法”说的是（　）", "type": "choice", "answer": "方苞",
         "explanation": "方苞首创“义法”说，是桐城派奠基人。",
         "options": ["方苞", "刘大櫆", "姚鼐", "曾国藩"]},
        {"stem": "姚鼐主张文章应做到义理、____、辞章三者统一。", "type": "blank", "answer": "考据",
         "explanation": "姚鼐集桐城派大成，主张义理、考据、辞章三者统一。",
         "options": []},
     ]},
    {"id": "k_wxs_qingdai_07", "name": "纳兰性德与清词", "parent": "k_wxs_qingdai", "chapter": "清代文学", "hot": False,
     "summary": "纳兰性德（字容若）是清代最杰出的词人之一，词集《饮水词》，风格凄婉深挚、自然真切，“以自然之眼观物，以自然之舌言情”，王国维称其“北宋以来，一人而已”。",
     "basicQuestions": [
        {"stem": "清代词人纳兰性德的词集是《____》。", "type": "blank", "answer": "饮水词",
         "explanation": "纳兰性德词集名《饮水词》。",
         "options": []},
        {"stem": "王国维称其“北宋以来，一人而已”的清词代表是（　）", "type": "choice", "answer": "纳兰性德",
         "explanation": "王国维《人间词话》评纳兰性德“北宋以来，一人而已”。",
         "options": ["纳兰性德", "朱彝尊", "陈维崧", "张惠言"]},
        {"stem": "纳兰性德词的风格特点是（　）", "type": "choice", "answer": "凄婉深挚、自然真切",
         "explanation": "纳兰词凄婉深挚、自然真切，“以自然之舌言情”。",
         "options": ["凄婉深挚、自然真切", "豪放雄健、气势磅礴", "典丽精工、绵密含蓄", "旷达疏朗、清丽明快"]},
     ]},
    {"id": "k_wxs_qingdai_08", "name": "清代其他小说", "parent": "k_wxs_qingdai", "chapter": "清代文学", "hot": False,
     "summary": "清代长篇小说除四大名著外，有李汝珍《镜花缘》（才学小说）、李绿园《歧路灯》（教育小说）等；讽刺小说《儒林外史》之外，还有晚清谴责小说（详见近代）。章回小说在清代进一步发展。",
     "basicQuestions": [
        {"stem": "清代李汝珍的小说《镜花缘》属于（　）", "type": "choice", "answer": "才学小说",
         "explanation": "《镜花缘》是清代才学小说，借海外奇谈展示作者的博学。",
         "options": ["才学小说", "谴责小说", "神魔小说", "公案小说"]},
        {"stem": "清代李绿园的长篇小说是（　）", "type": "choice", "answer": "《歧路灯》",
         "explanation": "李绿园《歧路灯》写教育兴家主题，是清代教育小说。",
         "options": ["《歧路灯》", "《镜花缘》", "《醒世姻缘传》", "《儿女英雄传》"]},
     ]},
]

JINDAI = [
    {"id": "k_wxs_jindai_01", "name": "龚自珍与近代初期诗文", "parent": "k_wxs_jindai", "chapter": "近代文学", "hot": True,
     "summary": "龚自珍是近代文学的开山作家，诗作《己亥杂诗》“我劝天公重抖擞，不拘一格降人才”，《夜坐》有“春夜伤心坐画屏，不如放眼入青冥”；其诗思想深刻、瑰丽奇肆，开一代风气。",
     "basicQuestions": [
        {"stem": "“春夜伤心坐画屏，不如放眼入青冥”出自近代诗人____的《夜坐》。", "type": "blank", "answer": "龚自珍",
         "explanation": "此句出自龚自珍《夜坐》，龚自珍是近代文学的开山作家。",
         "options": []},
        {"stem": "“我劝天公重抖擞，不拘一格降人才”出自龚自珍的（　）", "type": "choice", "answer": "《己亥杂诗》",
         "explanation": "“我劝天公重抖擞，不拘一格降人才”出自龚自珍《己亥杂诗》。",
         "options": ["《己亥杂诗》", "《夜坐》", "《病梅馆记》", "《咏史》"]},
        {"stem": "龚自珍借梅喻人、批判束缚人才的是散文《____》。", "type": "blank", "answer": "病梅馆记",
         "explanation": "《病梅馆记》以梅喻人才，批判封建礼教对人才的束缚。",
         "options": []},
     ]},
    {"id": "k_wxs_jindai_02", "name": "诗界革命与黄遵宪、梁启超", "parent": "k_wxs_jindai", "chapter": "近代文学", "hot": True,
     "summary": "近代后期梁启超鲜明提出“诗界革命”口号；黄遵宪是诗界革命旗帜性诗人，主张“我手写吾口”，其诗被称为“诗史”；梁启超著《饮冰室诗话》宣传诗界革命。",
     "basicQuestions": [
        {"stem": "近代后期鲜明提出“诗界革命”口号的是____。", "type": "blank", "answer": "梁启超",
         "explanation": "梁启超提出“诗界革命”口号，并著《饮冰室诗话》加以宣传。",
         "options": []},
        {"stem": "诗界革命中主张“我手写吾口”的旗帜性诗人是（　）", "type": "choice", "answer": "黄遵宪",
         "explanation": "黄遵宪主张“我手写吾口，古岂能拘牵”，是诗界革命的旗帜性诗人。",
         "options": ["黄遵宪", "梁启超", "谭嗣同", "夏曾佑"]},
        {"stem": "梁启超宣传诗界革命的理论著作是《____》。", "type": "blank", "answer": "饮冰室诗话",
         "explanation": "梁启超《饮冰室诗话》系统宣传诗界革命主张。",
         "options": []},
     ]},
    {"id": "k_wxs_jindai_03", "name": "小说界革命", "parent": "k_wxs_jindai", "chapter": "近代文学", "hot": True,
     "summary": "1902年梁启超发表《论小说与群治之关系》，将小说提高到“新国新民”的高度，掀起小说界革命；《新中国未来记》是其政治小说代表作。",
     "basicQuestions": [
        {"stem": "1902年梁启超发表《____》，将小说提高到新国新民的高度。", "type": "blank", "answer": "论小说与群治之关系",
         "explanation": "《论小说与群治之关系》将小说提高到新国新民的高度，是小说界革命的纲领。",
         "options": []},
        {"stem": "梁启超的政治小说代表作是（　）", "type": "choice", "answer": "《新中国未来记》",
         "explanation": "梁启超《新中国未来记》是近代政治小说的开山之作。",
         "options": ["《新中国未来记》", "《官场现形记》", "《孽海花》", "《老残游记》"]},
     ]},
    {"id": "k_wxs_jindai_04", "name": "四大谴责小说", "parent": "k_wxs_jindai", "chapter": "近代文学", "hot": True,
     "summary": "晚清四大谴责小说：李宝嘉《官场现形记》、吴趼人《二十年目睹之怪现状》、刘鹗《老残游记》、曾朴《孽海花》，皆以暴露社会黑暗、抨击官场腐败为指归，与鲁迅所说“谴责小说”命名相符。",
     "basicQuestions": [
        {"stem": "晚清四大谴责小说不包括（　）", "type": "choice", "answer": "《镜花缘》",
         "explanation": "四大谴责小说为《官场现形记》《二十年目睹之怪现状》《老残游记》《孽海花》。《镜花缘》是清代李汝珍的才学小说。",
         "options": ["《镜花缘》", "《官场现形记》", "《老残游记》", "《孽海花》"]},
        {"stem": "《官场现形记》的作者是（　）", "type": "choice", "answer": "李宝嘉",
         "explanation": "《官场现形记》作者李宝嘉（李伯元），是谴责小说的代表作。",
         "options": ["李宝嘉", "吴趼人", "刘鹗", "曾朴"]},
        {"stem": "《老残游记》的作者是（　）", "type": "choice", "answer": "刘鹗",
         "explanation": "《老残游记》作者刘鹗，借老残游历揭露晚清社会弊端。",
         "options": ["刘鹗", "李宝嘉", "曾朴", "吴趼人"]},
     ]},
    {"id": "k_wxs_jindai_05", "name": "近代翻译文学与林纾", "parent": "k_wxs_jindai", "chapter": "近代文学", "hot": True,
     "summary": "林纾（琴南）是近代翻译西方小说最多、影响最大的翻译家，代表作译作《巴黎茶花女遗事》，世称“林译小说”；近代翻译文学对晚清文学观念变革产生了深远影响。",
     "basicQuestions": [
        {"stem": "近代翻译西方小说最多、影响最大的翻译家是____。", "type": "blank", "answer": "林纾",
         "explanation": "林纾翻译西方小说最多、影响最大，世称“林译小说”。",
         "options": []},
        {"stem": "林纾的第一部翻译小说、轰动文坛的是《____》。", "type": "blank", "answer": "巴黎茶花女遗事",
         "explanation": "林纾与人合作翻译《巴黎茶花女遗事》，“林译小说”由此得名。",
         "options": []},
     ]},
    {"id": "k_wxs_jindai_06", "name": "南社与近代戏剧改良", "parent": "k_wxs_jindai", "chapter": "近代文学", "hot": False,
     "summary": "南社是近代革命文学团体，由陈去病、高旭、柳亚子等创立，主张“鼓吹新学思潮，标榜爱国主义”；秋瑾是辛亥革命时期著名女诗人，有“秋风秋雨愁煞人”名句；近代戏剧改良推动京剧改良与话剧（新剧）的诞生。",
     "basicQuestions": [
        {"stem": "南社是近代（　）文学团体，以柳亚子、陈去病、高旭为代表。", "type": "choice", "answer": "革命",
         "explanation": "南社是近代革命文学团体，主张鼓吹新学思潮、标榜爱国主义。",
         "options": ["革命", "改良", "复古", "唯美"]},
        {"stem": "“秋风秋雨愁煞人”出自近代女诗人（　）", "type": "choice", "answer": "秋瑾",
         "explanation": "秋瑾绝笔“秋风秋雨愁煞人”，她是辛亥革命时期著名女诗人。",
         "options": ["秋瑾", "苏曼殊", "陈去病", "吕碧城"]},
     ]},
]

def main():
    d = json.load(open(PATH, encoding="utf-8"))
    keep = [k for k in d["knowledge"] if k["chapter"] not in ("元代文学", "清代文学", "近代文学")]
    d["knowledge"] = keep + YUAN + QING + JINDAI
    json.dump(d, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    from collections import Counter
    print("重拆后各章知识点数:")
    for c, n in Counter(k["chapter"] for k in d["knowledge"]).items():
        print(f"  {c}: {n}")

    bad = []
    for k in d["knowledge"]:
        for q in k.get("basicQuestions", []):
            if q["type"] == "choice":
                if len(q.get("options", [])) != 4:
                    bad.append(f"{k['id']} 选项数: {q['stem'][:20]}")
                if q["answer"] not in q.get("options", []):
                    bad.append(f"{k['id']} 错配: {q['stem'][:25]}")
    print("校验异常:", len(bad))
    for b in bad:
        print("  ", b)

if __name__ == "__main__":
    main()
