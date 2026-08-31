# -*- coding: utf-8 -*-
"""补长 29 条过短选择题解析：在原有正确解析后追加一句知识性延伸。"""
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

FILES = {
    '现代汉语': r'D:\study_app\tools\seed-builder\out\knowledge\现代汉语.knowledge.json',
    '古代汉语': r'D:\study_app\tools\seed-builder\out\knowledge\古代汉语.knowledge.json',
    '中国现代文学史': r'D:\study_app\tools\seed-builder\out\knowledge\中国现代文学史.knowledge.json',
    '中国古代文学史': r'D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json',
    '中国当代文学史': r'D:\study_app\tools\seed-builder\out\knowledge\中国当代文学史.knowledge.json',
}

# key = (knowledge id, bq_idx) -> 追加句
ADD = {
    ('k_xdyy_xiuci_05', 5): '借代以部分特征代指整体，重在相关性；与之相对的是重在相似性的比喻。',
    ('k_xdyy_xiuci_10', 4): '反复分连续反复与间隔反复两种，句中两个“沉默呵”紧接出现，属连续反复。',
    ('k_xdyy_xiuci_12', 2): '双关利用语音或语义条件使语句同时兼有两层意思，此处谐音双关既写天气又写爱情。',
    ('k_xdyy_wenzi_07', 4): '“的”的部首是“白”，现代汉语字典按部首笔画检索时可据“白”部查得。',
    ('k_xdyy_xulun_02', 4): '普通话语法规范以典范的现代白话文著作为准，即以书面语通行用法为依据。',
    # 古代汉语
    ('k_gdyy_xiuci_03', 7): '以声音的相似性作比，把琵琶声比作珠落玉盘之声，属明喻。',
    ('k_gdyy_wenti_05', 0): '柳宗元的山水游记以《永州八记》最著，被誉为杂记文典范。',
    ('k_gdyy_wenti_05', 5): '杂记内容广泛，可记楼台亭阁、山水风物，《岳阳楼记》即借楼抒怀。',
    ('k_gdyy_wenti_06', 5): '“表”为臣下上奏君主的奏议文体，《出师表》为诸葛亮北伐前所上。',
    ('k_gdyy_gongjushu_04', 2): '王引之《经传释词》专释古书虚词，与《经义述闻》同为训诂名著。',
    ('k_gdyy_wenzi_shang_01', 4): '“武”由“止”“戈”会意，“止戈为武”，属会意字而非形声字。',
    ('k_gdyy_yufa_shang_03', 10): '“之”指代曹刿，作“乘”的宾语，是第三人称代词。',
    ('k_gdyy_yufa_xia_05', 9): '“异之”即“以之为异”，形容词“异”带宾语活用为意动用法。',
    ('k_gdyy_yufa_xia_08', 11): '疑问句中疑问代词宾语前置，“何操”即“操何”，属宾语前置句式。',
    ('k_gdyy_yinyun_06', 7): '反切上字取声母、下字取韵母和声调，“郎”与“练”声母相同。',
    ('k_zhen_gdhy_训诂', 2): '《说文解字》为东汉许慎所著，是我国第一部系统分析字形、考究字源的字典。',
    # 现代文学
    ('k_xdwx_x1_02', 1): '冰心《斯人独憔悴》与《两个家庭》等开创了“问题小说”风气。',
    ('k_xdwx_lx2_02', 3): '《热风》收录鲁迅早期杂文，集中批判封建旧礼教与旧传统。',
    # 古代文学
    ('k_wxs_qinhan_02', 0): '汉赋四大家为司马相如、扬雄、班固、张衡，代表汉大赋最高成就。',
    ('k_wxs_suitang_12', 0): '晚唐裴铏小说集名《传奇》，后世遂以“传奇”泛称唐人小说。',
    # 当代文学
    ('k_ddwx_2000s_02', 2): '《玉米》写玉秀、玉秧等三个农村年轻女性，获鲁迅文学奖。',
    ('k_ddwx_2000s_03', 3): '《应物兄》获第十届茅盾文学奖，是近年知识分子题材长篇代表作。',
    ('k_ddwx_xiaoshuo60_12', 4): '《青春之歌》是杨沫代表作，林道静是其女主人公。',
    ('k_ddwx_xiaoshuo80_11', 1): '《人生》《平凡的世界》中城乡冲突常以爱情纠葛形式呈现。',
    ('k_ddwx_xiaoshuo90_09', 4): '王朔以调侃笔法解构崇高，代表90年代小说的一种“顽主”风格。',
    ('k_ddwx_xinshi80_07', 5): '海子《面朝大海，春暖花开》写于其自杀前两个月，是其代表作。',
    ('k_ddwx_taigang_01', 6): '白先勇《台北人》写台北都市人生，《游园惊梦》为其名篇。',
    # 现代汉语 剩余两条
    ('k_xdyy_xiuci_05', 5): None,  # 已覆盖
}

n = 0
for cn, f in FILES.items():
    k = json.load(open(f, encoding='utf-8'))
    for x in k['knowledge']:
        for i, bq in enumerate(x.get('basicQuestions', [])):
            key = (x['id'], i)
            if key in ADD and ADD[key]:
                bq['explanation'] = (bq.get('explanation') or '') + ADD[key]
                n += 1
                print(f"  {x['id']}/{i} 补长 -> {len(re.sub(chr(92)+'s+','',bq['explanation']))}字")
    json.dump(k, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('补长条数:', n)
