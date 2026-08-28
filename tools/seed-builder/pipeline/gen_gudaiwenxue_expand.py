# -*- coding: utf-8 -*-
"""古文史扩充：袁行霈 205 填空 → 归章 → 映射知识点 → 生成基础题 → 合并现有库。

- 未分类（考研真题精选）填空按关键词归章
- 每个候选按关键词映射到具体知识点（knowledgeId）
- 生成基础题（type=blank），与现有题题干去重
- 现有元/清/近代 basic 题补 knowledgeId
输出：out/refined/bank-zhongguo-gudai-wenxue.v012.json（最终数据）
"""
import json, re, os
from collections import defaultdict, Counter

BASE = r"D:\study_app\tools\seed-builder\out"
BANK = "bank-zhongguo-gudai-wenxue"
SRC_CAND = os.path.join(BASE, "refined", "gudaiwenxue_expand_candidates.json")
SRC_CUR = os.path.join(BASE, "refined", f"{BANK}.refined2.json")
KP = os.path.join(BASE, "knowledge", "中国古代文学史.knowledge.json")
OUT = os.path.join(BASE, "refined", f"{BANK}.v012.json")

# ========== 归章关键词（未分类用） ==========
CH_KEYWORDS = {
    "先秦文学": ["诗经", "风雅颂", "楚辞", "离骚", "屈原", "宋玉", "左传", "战国策", "国语", "尚书", "论语", "孟子", "庄子", "老子", "诸子", "神话", "九辩", "寓言"],
    "秦汉文学": ["史记", "汉书", "汉赋", "乐府", "古诗十九首", "贾谊", "晁错", "司马相如", "扬雄", "班固", "王褒", "淮南子", "枚乘", "阿房宫赋", "过秦论", "咏史"],
    "魏晋南北朝文学": ["建安", "曹操", "曹丕", "曹植", "七子", "正始", "竹林七贤", "太康", "左思", "陶渊明", "谢灵运", "元嘉", "鲍照", "永明", "谢朓", "庾信", "宫体", "民歌", "搜神记", "世说新语", "文心雕龙", "志怪", "志人", "潘岳", "陆机"],
    "隋唐五代文学": ["初唐", "四杰", "王勃", "杨炯", "卢照邻", "骆宾王", "陈子昂", "王维", "孟浩然", "高适", "岑参", "王昌龄", "李白", "杜甫", "韩愈", "孟郊", "贾岛", "大历", "元稹", "白居易", "新乐府", "李贺", "李商隐", "杜牧", "温庭筠", "古文运动", "唐传奇", "变文", "李煜", "花间", "师说", "三戒", "柳宗元", "刘禹锡", "三十六体"],
    "宋代文学": ["柳永", "苏轼", "周邦彦", "李清照", "辛弃疾", "姜夔", "欧阳修", "黄庭坚", "江西诗派", "杨万里", "范成大", "陆游", "永嘉四灵", "江湖诗派", "宋初", "话本", "秦观", "张炎", "六一", "稼轩", "易安", "淮海", "山中白云", "吴船录", "临江", "工尺谱"],
    "元代文学": ["元杂剧", "关汉卿", "西厢记", "王实甫", "窦娥冤", "散曲", "小令", "套数", "南戏", "琵琶记", "高明", "元诗四大家", "虞集", "元好问", "马致远", "张养浩", "赵五娘", "墙头马上", "白朴", "倩女离魂"],
    "明代文学": ["三国", "水浒", "西游记", "金瓶梅", "三言", "二拍", "喻世明言", "警世通言", "醒世恒言", "汤显祖", "临川四梦", "牡丹亭", "徐渭", "昆腔", "复古派", "公安派", "竟陵派", "前七子", "后七子", "李贽", "焚书", "刘基", "诚意伯", "梼杌闲评"],
    "清代文学": ["聊斋", "蒲松龄", "儒林外史", "吴敬梓", "红楼梦", "曹雪芹", "长生殿", "桃花扇", "洪昇", "孔尚任", "桐城", "常州词派", "张惠言", "周济", "汪中", "哀盐船文", "李渔", "无声戏", "十二楼", "脂评本", "水浒后传"],
    "近代文学": ["龚自珍", "诗界革命", "黄遵宪", "梁启超", "小说界革命", "谴责小说", "官场现形记", "二十年目睹", "老残游记", "孽海花", "林纾", "天演论", "春柳社", "夜坐", "我手写我口"],
}

# ========== 章→知识点 关键词映射（长词优先） ==========
# 结构：{chapter: [(关键词, knowledgeId), ...]}，顺序即优先级
KP_MAP = {
    "先秦文学": [
        ("赋比兴", "k_wxs_xianqin_02"), ("诗经", "k_wxs_xianqin_01"), ("风雅颂", "k_wxs_xianqin_01"), ("采薇", "k_wxs_xianqin_01"), ("七月", "k_wxs_xianqin_01"), ("芣苢", "k_wxs_xianqin_01"), ("弃妇", "k_wxs_xianqin_01"), ("王风", "k_wxs_xianqin_01"),
        ("左传", "k_wxs_xianqin_05"), ("尚书", "k_wxs_xianqin_04"), ("历史文献总集", "k_wxs_xianqin_04"), ("春秋", "k_wxs_xianqin_04"), ("战国策", "k_wxs_xianqin_06"), ("画蛇添足", "k_wxs_xianqin_06"), ("狐假虎威", "k_wxs_xianqin_06"), ("国语", "k_wxs_xianqin_05"),
        ("论语", "k_wxs_xianqin_07"), ("三人行", "k_wxs_xianqin_07"), ("岁寒", "k_wxs_xianqin_07"), ("诸子散文", "k_wxs_xianqin_07"), ("老子", "k_wxs_xianqin_07"), ("孟子", "k_wxs_xianqin_08"), ("十三经", "k_wxs_xianqin_08"), ("庄子", "k_wxs_xianqin_09"), ("望洋兴叹", "k_wxs_xianqin_09"), ("小说一词", "k_wxs_xianqin_09"), ("儒以", "k_wxs_xianqin_09"), ("强本", "k_wxs_xianqin_07"), ("荀子", "k_wxs_xianqin_07"), ("韩非", "k_wxs_xianqin_07"),
        ("离骚", "k_wxs_xianqin_10"), ("楚辞", "k_wxs_xianqin_10"), ("屈原", "k_wxs_xianqin_10"), ("路漫漫", "k_wxs_xianqin_10"), ("上下而求索", "k_wxs_xianqin_10"), ("九歌", "k_wxs_xianqin_11"), ("九章", "k_wxs_xianqin_11"), ("九辩", "k_wxs_xianqin_11"), ("宋玉", "k_wxs_xianqin_11"),
        ("神话", "k_wxs_xianqin_01"), ("乐府", "k_wxs_xianqin_01"), ("巫舞", "k_wxs_xianqin_01"), ("风雅颂", "k_wxs_xianqin_01"),
    ],
    "秦汉文学": [
        ("史记", "k_wxs_qinhan_03"), ("司马", "k_wxs_qinhan_03"), ("报任安", "k_wxs_qinhan_03"), ("报任少卿", "k_wxs_qinhan_03"),
        ("汉书", "k_wxs_qinhan_08"), ("贾谊", "k_wxs_qinhan_08"), ("晁错", "k_wxs_qinhan_08"), ("过秦论", "k_wxs_qinhan_08"), ("阿房宫", "k_wxs_qinhan_08"), ("论衡", "k_wxs_qinhan_08"), ("吴越春秋", "k_wxs_qinhan_08"), ("越绝书", "k_wxs_qinhan_08"),
        ("汉赋", "k_wxs_qinhan_01"), ("司马相如", "k_wxs_qinhan_02"), ("扬雄", "k_wxs_qinhan_02"), ("班固", "k_wxs_qinhan_02"), ("张衡", "k_wxs_qinhan_02"), ("王褒", "k_wxs_qinhan_02"), ("洞箫", "k_wxs_qinhan_02"), ("枚乘", "k_wxs_qinhan_01"), ("七发", "k_wxs_qinhan_01"), ("京都赋", "k_wxs_qinhan_02"), ("首写京都赋", "k_wxs_qinhan_02"),
        ("乐府", "k_wxs_qinhan_06"), ("孔雀东南飞", "k_wxs_qinhan_06"), ("焦仲卿", "k_wxs_qinhan_06"), ("古诗十九首", "k_wxs_qinhan_07"), ("五言之冠冕", "k_wxs_qinhan_07"), ("忧伤以终老", "k_wxs_qinhan_07"), ("同心而离居", "k_wxs_qinhan_07"), ("淮南子", "k_wxs_qinhan_08"), ("咏史", "k_wxs_qinhan_07"),
    ],
    "魏晋南北朝文学": [
        ("建安", "k_wxs_weijin_01"), ("七子", "k_wxs_weijin_01"), ("曹操", "k_wxs_weijin_02"), ("曹丕", "k_wxs_weijin_02"), ("曹植", "k_wxs_weijin_02"), ("烈士暮年", "k_wxs_weijin_02"), ("视死忽如归", "k_wxs_weijin_02"), ("捐躯赴国难", "k_wxs_weijin_02"), ("岂不罹凝寒", "k_wxs_weijin_02"), ("松柏有本性", "k_wxs_weijin_02"),
        ("正始", "k_wxs_weijin_03"), ("竹林七贤", "k_wxs_weijin_03"), ("阮籍", "k_wxs_weijin_03"), ("嵇康", "k_wxs_weijin_03"), ("玄言", "k_wxs_weijin_03"), ("孙绰", "k_wxs_weijin_03"),
        ("太康", "k_wxs_weijin_04"), ("左思", "k_wxs_weijin_04"), ("潘岳", "k_wxs_weijin_04"), ("陆机", "k_wxs_weijin_04"),
        ("陶渊明", "k_wxs_weijin_05"), ("田园", "k_wxs_weijin_05"), ("五柳先生", "k_wxs_weijin_05"), ("谢灵运", "k_wxs_weijin_06"), ("元嘉", "k_wxs_weijin_06"), ("山水", "k_wxs_weijin_06"), ("池塘生春草", "k_wxs_weijin_06"), ("园柳变鸣禽", "k_wxs_weijin_06"),
        ("鲍照", "k_wxs_weijin_07"), ("永明", "k_wxs_weijin_07"), ("谢朓", "k_wxs_weijin_08"), ("谢脁", "k_wxs_weijin_08"), ("庾信", "k_wxs_weijin_08"), ("宫体", "k_wxs_weijin_08"),
        ("民歌", "k_wxs_weijin_09"), ("西曲", "k_wxs_weijin_09"), ("子夜", "k_wxs_weijin_09"), ("搜神记", "k_wxs_weijin_10"), ("世说新语", "k_wxs_weijin_10"), ("志怪", "k_wxs_weijin_10"), ("志人", "k_wxs_weijin_10"), ("干宝", "k_wxs_weijin_10"), ("刘义庆", "k_wxs_weijin_10"), ("水经注", "k_wxs_weijin_10"),
        ("文心雕龙", "k_wxs_weijin_11"), ("诗品", "k_wxs_weijin_11"), ("典论", "k_wxs_weijin_11"), ("文选", "k_wxs_weijin_11"), ("萧统", "k_wxs_weijin_11"), ("刘勰", "k_wxs_weijin_11"), ("郦道元", "k_wxs_weijin_11"),
    ],
    "隋唐五代文学": [
        ("初唐", "k_wxs_suitang_01"), ("四杰", "k_wxs_suitang_01"), ("王勃", "k_wxs_suitang_01"), ("杨炯", "k_wxs_suitang_01"), ("卢照邻", "k_wxs_suitang_01"), ("骆宾王", "k_wxs_suitang_01"), ("上官", "k_wxs_suitang_01"),
        ("陈子昂", "k_wxs_suitang_02"), ("王维", "k_wxs_suitang_03"), ("孟浩然", "k_wxs_suitang_03"), ("山水田园", "k_wxs_suitang_03"),
        ("高适", "k_wxs_suitang_04"), ("岑参", "k_wxs_suitang_04"), ("王昌龄", "k_wxs_suitang_04"), ("边塞", "k_wxs_suitang_04"),
        ("李白", "k_wxs_suitang_05"), ("杜甫", "k_wxs_suitang_06"), ("杜工部", "k_wxs_suitang_06"),
        ("韩愈", "k_wxs_suitang_07"), ("孟郊", "k_wxs_suitang_07"), ("贾岛", "k_wxs_suitang_07"), ("大历", "k_wxs_suitang_07"), ("韩孟", "k_wxs_suitang_07"),
        ("元稹", "k_wxs_suitang_08"), ("白居易", "k_wxs_suitang_08"), ("新乐府", "k_wxs_suitang_08"), ("长恨歌", "k_wxs_suitang_08"), ("琵琶行", "k_wxs_suitang_08"), ("曾经沧海", "k_wxs_suitang_08"),
        ("李贺", "k_wxs_suitang_09"), ("李商隐", "k_wxs_suitang_09"), ("三十六体", "k_wxs_suitang_09"),
        ("杜牧", "k_wxs_suitang_10"), ("晚唐", "k_wxs_suitang_10"),
        ("古文运动", "k_wxs_suitang_11"), ("唐宋八大家", "k_wxs_suitang_11"), ("师说", "k_wxs_suitang_11"), ("柳宗元", "k_wxs_suitang_11"), ("三戒", "k_wxs_suitang_11"),
        ("唐传奇", "k_wxs_suitang_12"), ("传奇", "k_wxs_suitang_12"), ("游仙窟", "k_wxs_suitang_12"), ("变文", "k_wxs_suitang_12"),
        ("花间", "k_wxs_suitang_13"), ("李煜", "k_wxs_suitang_13"), ("温庭筠", "k_wxs_suitang_13"), ("南唐", "k_wxs_suitang_13"), ("鸡声茅店月", "k_wxs_suitang_13"), ("人迹板桥霜", "k_wxs_suitang_13"),
        ("春江花月夜", "k_wxs_suitang_01"), ("张若虚", "k_wxs_suitang_01"), ("诗中之诗", "k_wxs_suitang_01"), ("明月松间照", "k_wxs_suitang_03"), ("清泉石上流", "k_wxs_suitang_03"), ("诗中有画", "k_wxs_suitang_03"), ("独坐幽篁", "k_wxs_suitang_03"), ("空翠湿人衣", "k_wxs_suitang_03"), ("山路元无雨", "k_wxs_suitang_03"), ("野旷天低树", "k_wxs_suitang_03"), ("江清月近人", "k_wxs_suitang_03"), ("边塞", "k_wxs_suitang_04"), ("岭树重遮", "k_wxs_suitang_04"), ("江流曲似九回肠", "k_wxs_suitang_04"),
    ],
    "宋代文学": [
        ("宋初", "k_wxs_songdai_01"), ("西昆", "k_wxs_songdai_01"), ("杨亿", "k_wxs_songdai_01"), ("白体", "k_wxs_songdai_01"), ("晚唐体", "k_wxs_songdai_01"),
        ("江西诗派", "k_wxs_songdai_02"), ("黄庭坚", "k_wxs_songdai_02"), ("一祖三宗", "k_wxs_songdai_02"), ("陈师道", "k_wxs_songdai_02"),
        ("杨万里", "k_wxs_songdai_03"), ("范成大", "k_wxs_songdai_03"), ("陆游", "k_wxs_songdai_03"), ("永嘉四灵", "k_wxs_songdai_03"), ("江湖诗派", "k_wxs_songdai_03"),
        ("柳永", "k_wxs_songdai_04"), ("苏轼", "k_wxs_songdai_05"), ("东坡", "k_wxs_songdai_05"), ("豪放", "k_wxs_songdai_05"),
        ("周邦彦", "k_wxs_songdai_06"), ("清真", "k_wxs_songdai_06"), ("李清照", "k_wxs_songdai_07"), ("易安", "k_wxs_songdai_07"),
        ("辛弃疾", "k_wxs_songdai_08"), ("稼轩", "k_wxs_songdai_08"), ("姜夔", "k_wxs_songdai_09"), ("白石", "k_wxs_songdai_09"), ("张炎", "k_wxs_songdai_09"), ("山中白云", "k_wxs_songdai_09"),
        ("欧阳修", "k_wxs_songdai_10"), ("六一", "k_wxs_songdai_10"), ("醉翁", "k_wxs_songdai_10"),
        ("话本", "k_wxs_songdai_11"), ("说话", "k_wxs_songdai_11"), ("秦观", "k_wxs_songdai_04"), ("淮海", "k_wxs_songdai_04"),
        ("武林旧事", "k_wxs_songdai_03"), ("三十功名", "k_wxs_songdai_03"), ("八千里路", "k_wxs_songdai_03"), ("沧浪诗话", "k_wxs_songdai_02"), ("诗有别材", "k_wxs_songdai_02"), ("诗有别趣", "k_wxs_songdai_02"), ("词中老杜", "k_wxs_songdai_06"), ("创用词调最多", "k_wxs_songdai_04"),
        ("严羽", "k_wxs_songdai_02"), ("王维吴道子", "k_wxs_songdai_05"),
    ],
    "元代文学": [
        ("关汉卿", "k_wxs_yuandai_01"), ("窦娥", "k_wxs_yuandai_01"), ("元杂剧", "k_wxs_yuandai_01"), ("救风尘", "k_wxs_yuandai_01"),
        ("西厢", "k_wxs_yuandai_02"), ("王实甫", "k_wxs_yuandai_02"), ("红娘", "k_wxs_yuandai_02"),
        ("散曲", "k_wxs_yuandai_03"), ("小令", "k_wxs_yuandai_03"), ("套数", "k_wxs_yuandai_03"), ("马致远", "k_wxs_yuandai_03"), ("张养浩", "k_wxs_yuandai_03"), ("山坡羊", "k_wxs_yuandai_03"), ("天净沙", "k_wxs_yuandai_03"),
        ("南戏", "k_wxs_yuandai_04"), ("琵琶记", "k_wxs_yuandai_04"), ("高明", "k_wxs_yuandai_04"), ("赵五娘", "k_wxs_yuandai_04"), ("蔡伯喈", "k_wxs_yuandai_04"),
        ("元诗四大家", "k_wxs_yuandai_05"), ("虞集", "k_wxs_yuandai_05"), ("元好问", "k_wxs_yuandai_05"), ("白朴", "k_wxs_yuandai_02"), ("墙头马上", "k_wxs_yuandai_02"), ("倩女离魂", "k_wxs_yuandai_04"), ("元曲四大家", "k_wxs_yuandai_01"),
    ],
    "明代文学": [
        ("三国", "k_wxs_mingdai_01"), ("水浒", "k_wxs_mingdai_02"), ("西游记", "k_wxs_mingdai_03"), ("金瓶梅", "k_wxs_mingdai_04"), ("世情", "k_wxs_mingdai_04"),
        ("三言", "k_wxs_mingdai_05"), ("二拍", "k_wxs_mingdai_05"), ("喻世明言", "k_wxs_mingdai_05"), ("警世通言", "k_wxs_mingdai_05"), ("醒世恒言", "k_wxs_mingdai_05"), ("古今小说", "k_wxs_mingdai_05"), ("拟话本", "k_wxs_mingdai_05"), ("李渔", "k_wxs_mingdai_05"),
        ("复古", "k_wxs_mingdai_06"), ("公安", "k_wxs_mingdai_06"), ("竟陵", "k_wxs_mingdai_06"), ("前七子", "k_wxs_mingdai_06"), ("后七子", "k_wxs_mingdai_06"), ("文必秦汉", "k_wxs_mingdai_06"), ("独抒性灵", "k_wxs_mingdai_06"), ("李贽", "k_wxs_mingdai_06"), ("焚书", "k_wxs_mingdai_06"),
        ("汤显祖", "k_wxs_mingdai_07"), ("临川四梦", "k_wxs_mingdai_07"), ("牡丹亭", "k_wxs_mingdai_07"), ("玉茗堂四梦", "k_wxs_mingdai_07"), ("良辰美景", "k_wxs_mingdai_07"), ("赏心乐事", "k_wxs_mingdai_07"), ("徐渭", "k_wxs_mingdai_08"), ("昆腔", "k_wxs_mingdai_08"), ("浣纱记", "k_wxs_mingdai_08"), ("昆山派", "k_wxs_mingdai_08"), ("宝剑记", "k_wxs_mingdai_08"), ("刘基", "k_wxs_mingdai_06"), ("诚意伯", "k_wxs_mingdai_06"), ("梼杌闲评", "k_wxs_mingdai_04"), ("宣和遗事", "k_wxs_mingdai_02"), ("项脊轩", "k_wxs_mingdai_06"), ("挂枝儿", "k_wxs_mingdai_05"), ("剪灯新话", "k_wxs_mingdai_05"),
    ],
    "清代文学": [
        ("聊斋", "k_wxs_qingdai_01"), ("蒲松龄", "k_wxs_qingdai_01"), ("儒林外史", "k_wxs_qingdai_02"), ("吴敬梓", "k_wxs_qingdai_02"), ("范进", "k_wxs_qingdai_02"), ("虽云长篇", "k_wxs_qingdai_02"), ("戚而能谐", "k_wxs_qingdai_02"),
        ("红楼梦", "k_wxs_qingdai_03"), ("曹雪芹", "k_wxs_qingdai_03"), ("脂评", "k_wxs_qingdai_03"), ("焦大", "k_wxs_qingdai_03"), ("水浒后传", "k_wxs_qingdai_03"),
        ("长生殿", "k_wxs_qingdai_04"), ("桃花扇", "k_wxs_qingdai_04"), ("洪昇", "k_wxs_qingdai_04"), ("孔尚任", "k_wxs_qingdai_04"), ("李香君", "k_wxs_qingdai_04"), ("借离合", "k_wxs_qingdai_04"),
        ("桐城", "k_wxs_qingdai_05"), ("常州词派", "k_wxs_qingdai_05"), ("张惠言", "k_wxs_qingdai_05"), ("周济", "k_wxs_qingdai_05"), ("汪中", "k_wxs_qingdai_05"), ("哀盐船", "k_wxs_qingdai_05"), ("神韵说", "k_wxs_qingdai_05"), ("王士祯", "k_wxs_qingdai_05"), ("桐城中兴", "k_wxs_qingdai_05"), ("乾隆三大家", "k_wxs_qingdai_05"), ("赵翼", "k_wxs_qingdai_05"), ("袁枚", "k_wxs_qingdai_05"), ("曾国藩", "k_wxs_qingdai_05"), ("被常州派推为", "k_wxs_qingdai_05"), ("有词以来成就最高", "k_wxs_qingdai_05"), ("无声戏", "k_wxs_qingdai_01"), ("十二楼", "k_wxs_qingdai_01"),
    ],
    "近代文学": [
        ("龚自珍", "k_wxs_jindai_01"), ("夜坐", "k_wxs_jindai_01"), ("己亥", "k_wxs_jindai_01"), ("我劝天公", "k_wxs_jindai_01"), ("不拘一格", "k_wxs_jindai_01"),
        ("诗界革命", "k_wxs_jindai_02"), ("黄遵宪", "k_wxs_jindai_02"), ("梁启超", "k_wxs_jindai_02"), ("我手写我口", "k_wxs_jindai_02"), ("人境庐", "k_wxs_jindai_02"),
        ("小说界革命", "k_wxs_jindai_03"), ("谴责小说", "k_wxs_jindai_03"), ("官场现形记", "k_wxs_jindai_03"), ("二十年目睹", "k_wxs_jindai_03"), ("老残游记", "k_wxs_jindai_03"), ("孽海花", "k_wxs_jindai_03"), ("论小说与群治", "k_wxs_jindai_03"),
        ("林纾", "k_wxs_jindai_04"), ("天演论", "k_wxs_jindai_04"), ("春柳社", "k_wxs_jindai_04"), ("翻译", "k_wxs_jindai_04"), ("戏剧团体", "k_wxs_jindai_04"), ("南社", "k_wxs_jindai_04"),
    ],
}

def norm(s):
    return re.sub(r"[\s，。、；：？！“”‘’（）()·—…《》<>0-9A-Za-z]","", s or "")

def classify_ch(stem):
    """按关键词归章"""
    for ch, kws in CH_KEYWORDS.items():
        for kw in kws:
            if kw in stem:
                return ch
    return None

# ========== 答案反推：作者名/作品名 → 知识点（跨章） ==========
ANS_MAP = [
    ("杜甫", "k_wxs_suitang_06"), ("王维", "k_wxs_suitang_03"), ("孟浩然", "k_wxs_suitang_03"),
    ("李白", "k_wxs_suitang_05"), ("高适", "k_wxs_suitang_04"), ("岑参", "k_wxs_suitang_04"),
    ("王昌龄", "k_wxs_suitang_04"), ("白居易", "k_wxs_suitang_08"), ("元稹", "k_wxs_suitang_08"),
    ("韩愈", "k_wxs_suitang_07"), ("柳宗元", "k_wxs_suitang_07"), ("李贺", "k_wxs_suitang_09"),
    ("李商隐", "k_wxs_suitang_09"), ("杜牧", "k_wxs_suitang_10"), ("温庭筠", "k_wxs_suitang_13"),
    ("李煜", "k_wxs_suitang_13"), ("陈子昂", "k_wxs_suitang_02"), ("王勃", "k_wxs_suitang_01"),
    ("曹操", "k_wxs_weijin_02"), ("曹植", "k_wxs_weijin_02"), ("曹丕", "k_wxs_weijin_02"),
    ("阮籍", "k_wxs_weijin_03"), ("嵇康", "k_wxs_weijin_03"), ("左思", "k_wxs_weijin_04"),
    ("陆机", "k_wxs_weijin_04"), ("潘岳", "k_wxs_weijin_04"), ("陶渊明", "k_wxs_weijin_05"),
    ("谢灵运", "k_wxs_weijin_06"), ("鲍照", "k_wxs_weijin_07"), ("谢朓", "k_wxs_weijin_08"),
    ("庾信", "k_wxs_weijin_08"), ("干宝", "k_wxs_weijin_10"), ("刘义庆", "k_wxs_weijin_10"),
    ("柳永", "k_wxs_songdai_04"), ("苏轼", "k_wxs_songdai_05"), ("周邦彦", "k_wxs_songdai_06"),
    ("李清照", "k_wxs_songdai_07"), ("辛弃疾", "k_wxs_songdai_08"), ("姜夔", "k_wxs_songdai_09"),
    ("欧阳修", "k_wxs_songdai_10"), ("黄庭坚", "k_wxs_songdai_02"), ("陆游", "k_wxs_songdai_03"),
    ("杨万里", "k_wxs_songdai_03"), ("范成大", "k_wxs_songdai_03"), ("秦观", "k_wxs_songdai_04"),
    ("张炎", "k_wxs_songdai_09"), ("关汉卿", "k_wxs_yuandai_01"), ("王实甫", "k_wxs_yuandai_02"),
    ("马致远", "k_wxs_yuandai_03"), ("白朴", "k_wxs_yuandai_02"), ("高明", "k_wxs_yuandai_04"),
    ("虞集", "k_wxs_yuandai_05"), ("元好问", "k_wxs_yuandai_05"), ("汤显祖", "k_wxs_mingdai_07"),
    ("徐渭", "k_wxs_mingdai_08"), ("李贽", "k_wxs_mingdai_06"), ("刘基", "k_wxs_mingdai_06"),
    ("归有光", "k_wxs_mingdai_06"), ("梁辰鱼", "k_wxs_mingdai_08"), ("李开先", "k_wxs_mingdai_08"),
    ("蒲松龄", "k_wxs_qingdai_01"), ("吴敬梓", "k_wxs_qingdai_02"), ("曹雪芹", "k_wxs_qingdai_03"),
    ("洪昇", "k_wxs_qingdai_04"), ("孔尚任", "k_wxs_qingdai_04"), ("张惠言", "k_wxs_qingdai_05"),
    ("周济", "k_wxs_qingdai_05"), ("汪中", "k_wxs_qingdai_05"), ("袁枚", "k_wxs_qingdai_05"),
    ("王士祯", "k_wxs_qingdai_05"), ("曾国藩", "k_wxs_qingdai_05"), ("李渔", "k_wxs_qingdai_01"),
    ("龚自珍", "k_wxs_jindai_01"), ("黄遵宪", "k_wxs_jindai_02"), ("梁启超", "k_wxs_jindai_02"),
    ("林纾", "k_wxs_jindai_04"), ("司马迁", "k_wxs_qinhan_03"), ("贾谊", "k_wxs_qinhan_08"),
    ("扬雄", "k_wxs_qinhan_02"), ("班固", "k_wxs_qinhan_02"), ("王褒", "k_wxs_qinhan_02"),
    ("司马相如", "k_wxs_qinhan_02"), ("刘勰", "k_wxs_weijin_11"), ("钟嵘", "k_wxs_weijin_11"),
    ("郦道元", "k_wxs_weijin_10"), ("郦道元", "k_wxs_weijin_11"), ("许询", "k_wxs_weijin_03"),
    ("孙绰", "k_wxs_weijin_03"), ("萧统", "k_wxs_weijin_11"), ("严羽", "k_wxs_songdai_02"),
    ("庄子", "k_wxs_xianqin_09"), ("孟子", "k_wxs_xianqin_08"), ("荀子", "k_wxs_xianqin_07"),
    ("韩非", "k_wxs_xianqin_07"), ("宋玉", "k_wxs_xianqin_11"), ("屈原", "k_wxs_xianqin_10"),
    ("孔三传", "k_wxs_yuandai_01"), ("周密", "k_wxs_songdai_03"), ("冯梦龙", "k_wxs_mingdai_05"),
    ("《论语》", "k_wxs_xianqin_07"), ("《战国策》", "k_wxs_xianqin_06"), ("《师说》", "k_wxs_suitang_11"),
    ("《桃花扇》", "k_wxs_qingdai_04"), ("《儒林外史》", "k_wxs_qingdai_02"), ("《阿房宫赋》", "k_wxs_qinhan_08"),
    ("《红楼梦》", "k_wxs_qingdai_03"), ("《春江花月夜》", "k_wxs_suitang_01"), ("《武林旧事》", "k_wxs_songdai_03"),
    ("《项脊轩志》", "k_wxs_mingdai_06"), ("《金瓶梅》", "k_wxs_mingdai_04"), ("《挂枝儿》", "k_wxs_mingdai_05"),
    ("七发", "k_wxs_qinhan_01"), ("玄言", "k_wxs_weijin_03"), ("边塞", "k_wxs_suitang_04"),
    ("《梼杌闲评》", "k_wxs_mingdai_04"), ("元好问", "k_wxs_yuandai_05"), ("黄庭坚", "k_wxs_songdai_02"),
    ("《报任安书》", "k_wxs_qinhan_03"), ("《报任少卿书》", "k_wxs_qinhan_03"), ("《师说》", "k_wxs_suitang_11"),
    ("《长恨歌》", "k_wxs_suitang_08"), ("元稹", "k_wxs_suitang_08"), ("张若虚", "k_wxs_suitang_01"),
    ("沈约", "k_wxs_weijin_07"), ("永明", "k_wxs_weijin_07"), ("《沧浪诗话》", "k_wxs_songdai_02"),
    ("《六一词》", "k_wxs_songdai_10"), ("《淮海词》", "k_wxs_songdai_04"), ("《稼轩长短句》", "k_wxs_songdai_08"),
    ("欧阳修", "k_wxs_songdai_10"), ("岳飞", "k_wxs_songdai_03"), ("赵五娘", "k_wxs_yuandai_04"),
    ("《西厢记》", "k_wxs_yuandai_02"), ("《窦娥冤》", "k_wxs_yuandai_01"), ("关汉卿", "k_wxs_yuandai_01"),
    ("《三国志演义》", "k_wxs_mingdai_01"), ("《水浒传》", "k_wxs_mingdai_02"), ("《西游记》", "k_wxs_mingdai_03"),
    ("《牡丹亭》", "k_wxs_mingdai_07"), ("《聊斋志异》", "k_wxs_qingdai_01"), ("《长生殿》", "k_wxs_qingdai_04"),
    ("《琵琶记》", "k_wxs_yuandai_04"), ("《搜神记》", "k_wxs_weijin_10"), ("《世说新语》", "k_wxs_weijin_10"),
    ("《孔雀东南飞》", "k_wxs_qinhan_06"), ("《古诗十九首》", "k_wxs_qinhan_07"), ("《离骚》", "k_wxs_xianqin_10"),
    ("《史记》", "k_wxs_qinhan_03"), ("《汉书》", "k_wxs_qinhan_08"), ("《左传》", "k_wxs_xianqin_05"),
    ("《诗经》", "k_wxs_xianqin_01"), ("《孟子》", "k_wxs_xianqin_08"), ("《庄子》", "k_wxs_xianqin_09"),
    ("《论语》", "k_wxs_xianqin_07"), ("《天演论》", "k_wxs_jindai_04"),
]

# ========== 全局诗句/stem 关键词 → 知识点（跨章，匹配题干） ==========
STEM_MAP = [
    ("欲度黄河冰塞川", "k_wxs_suitang_05"), ("将登太行雪满山", "k_wxs_suitang_05"),
    ("却看妻子愁何在", "k_wxs_suitang_06"), ("漫卷诗书喜欲狂", "k_wxs_suitang_06"),
    ("天若有情天亦老", "k_wxs_suitang_09"), ("衰兰送客咸阳道", "k_wxs_suitang_09"),
    ("醉里挑灯看剑", "k_wxs_songdai_08"), ("梦回吹角连营", "k_wxs_songdai_08"),
    ("桃李春风一杯酒", "k_wxs_songdai_02"), ("江湖夜雨十年灯", "k_wxs_songdai_02"),
    ("两情若是长久时", "k_wxs_songdai_04"), ("又岂在朝朝暮暮", "k_wxs_songdai_04"),
    ("人有悲欢离合", "k_wxs_songdai_05"), ("此事古难全", "k_wxs_songdai_05"),
    ("会挽雕弓如满月", "k_wxs_songdai_05"), ("西北望", "k_wxs_songdai_05"), ("纵使相逢应不识", "k_wxs_songdai_05"), ("尘满面", "k_wxs_songdai_05"),
    ("峰峦如聚", "k_wxs_yuandai_03"), ("山河表里潼关路", "k_wxs_yuandai_03"),
    ("空翠湿人衣", "k_wxs_suitang_03"), ("山路元无雨", "k_wxs_suitang_03"),
    ("江清月近人", "k_wxs_suitang_03"), ("野旷天低树", "k_wxs_suitang_03"),
    ("乱入池中看不见", "k_wxs_suitang_04"), ("闻歌始觉有人来", "k_wxs_suitang_04"),
    ("江流曲似九回肠", "k_wxs_suitang_07"), ("岭树重遮千里目", "k_wxs_suitang_07"),
    ("不师秦七", "k_wxs_songdai_09"), ("倚新声玉田差近", "k_wxs_songdai_09"),
    ("烈士暮年", "k_wxs_weijin_02"), ("壮心不已", "k_wxs_weijin_02"),
    ("箫鼓追随春社近", "k_wxs_songdai_03"), ("衣冠简朴古风存", "k_wxs_songdai_03"),
    ("以文字为诗", "k_wxs_songdai_02"), ("以才学为诗", "k_wxs_songdai_02"), ("以议论为诗", "k_wxs_songdai_02"),
    ("入话", "k_wxs_songdai_11"), ("正话", "k_wxs_songdai_11"),
    ("项脊轩", "k_wxs_mingdai_06"), ("昆山派", "k_wxs_mingdai_08"), ("挂枝儿", "k_wxs_mingdai_05"),
    ("武林旧事", "k_wxs_songdai_03"), ("诸子散文", "k_wxs_xianqin_07"), ("王风", "k_wxs_xianqin_01"),
    ("邹忌", "k_wxs_xianqin_06"), ("梼杌闲评", "k_wxs_mingdai_04"), ("似曾相识燕归来", "k_wxs_songdai_04"),
    ("无可奈何花落去", "k_wxs_songdai_04"), ("也无风雨也无晴", "k_wxs_songdai_05"), ("回首向来萧瑟处", "k_wxs_songdai_05"),
    ("雅就是", "k_wxs_xianqin_01"), ("周王朝直辖地区", "k_wxs_xianqin_01"), ("十五国风", "k_wxs_xianqin_01"), ("四家", "k_wxs_songdai_11"), ("讲史", "k_wxs_songdai_11"),
    ("乐府民歌", "k_wxs_qinhan_06"), ("南齐", "k_wxs_weijin_07"), ("四声", "k_wxs_weijin_07"),
]

def map_kp(ch, stem, answer=""):
    """章内关键词 → 全局stem → 答案反推 → None"""
    if ch in KP_MAP:
        for kw, kid in KP_MAP[ch]:
            if kw in stem:
                return kid
    for kw, kid in STEM_MAP:
        if kw in stem:
            return kid
    for kw, kid in ANS_MAP:
        if kw in answer:
            return kid
    return None

def main():
    cands = json.load(open(SRC_CAND, encoding="utf-8"))
    cur = json.load(open(SRC_CUR, encoding="utf-8"))
    k = json.load(open(KP, encoding="utf-8"))
    kp_ids = {kp["id"] for kp in k["knowledge"]}
    kp_by_ch = defaultdict(list)
    for kp in k["knowledge"]:
        kp_by_ch[kp["chapter"]].append(kp["id"])

    # 1) 归章
    for c in cands:
        if c["chapter"] == "未分类":
            ch = classify_ch(c["stem"])
            c["chapter"] = ch or "未分类"

    # 2) 知识点映射 + 生成题
    existing_stems = {norm(q["stem"]) for q in cur}
    new_questions = []
    mapped_cnt = Counter()
    unmapped = []
    for c in cands:
        ch = c["chapter"]
        kid = map_kp(ch, c["stem"], c["answer"])
        if not kid:
            unmapped.append(c); continue
        if ch == "未分类":
            # 由知识点反查章节
            ch = next((kp["chapter"] for kp in k["knowledge"] if kp["id"] == kid), None)
            if not ch:
                unmapped.append(c); continue
        stem = re.sub(r"\[[^\]]*?研\]", "", c["stem"]).strip()
        # 题干转标准填空（保留原空格 ____ ）
        if norm(stem) in existing_stems:
            continue  # 与现有题重复
        qid = f"{BANK}:ex_{len(new_questions):05d}"
        new_questions.append({
            "id": qid, "type": "blank", "stem": stem,
            "options": [], "answer": c["answer"], "explanation": c["analysis"] or c["answer"],
            "answerFormat": "作答格式：填空题，在横线处填入正确答案。",
            "chapter": ch, "tags": ["袁行霈题库"], "difficulty": "easy",
            "purpose": "basic", "knowledgeId": kid,
        })
        mapped_cnt[kid] += 1

    print(f"候选 {len(cands)} → 生成 {len(new_questions)} 题 | 未映射 {len(unmapped)}")
    print("各知识点新增:", dict(mapped_cnt))
    print("\n未映射/未归章（需人工）:")
    for c in unmapped:
        print(f"  [{c['chapter']}] {c['stem'][:45]} | 答:{c['answer'][:12]}")

    # 3) 现有 basic 题补 knowledgeId（关键词→答案反推→兜底章内首知识点）
    fixed = 0
    fallback = 0
    for q in cur:
        if q.get("knowledgeId"):
            continue
        if q["chapter"] not in kp_by_ch:
            continue
        kid = map_kp(q["chapter"], q["stem"], q.get("answer") or "")
        if not kid and q.get("purpose") == "basic":
            # 兜底：归章内第一个知识点（保证 basic 题 knowledgeId 有效）
            kid = kp_by_ch[q["chapter"]][0]
            fallback += 1
        if kid:
            q["knowledgeId"] = kid
            fixed += 1
    print(f"现有题补 knowledgeId: {fixed}（含兜底 {fallback}）")

    # 4) 合并输出
    merged = cur + new_questions
    json.dump(merged, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    from collections import Counter as C2
    print(f"\n合并后总 {len(merged)}（基础{sum(1 for q in merged if q.get('purpose')=='basic')}/测试{sum(1 for q in merged if q.get('purpose')=='test')}）")
    print("章节:", dict(C2(q["chapter"] for q in merged)))
    print("未映射 knowledgeId 的 basic 题:", sum(1 for q in merged if q.get("purpose")=="basic" and not q.get("knowledgeId")))
    print(f"输出 → {OUT}")

if __name__ == "__main__":
    main()
