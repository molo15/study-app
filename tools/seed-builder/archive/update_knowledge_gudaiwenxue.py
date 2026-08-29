# -*- coding: utf-8 -*-
"""补齐中国古代文学史 knowledge.json 缺失章节：元代/清代/近代知识点节点。"""
import json

KP = r"D:\study_app\tools\seed-builder\out\knowledge\中国古代文学史.knowledge.json"

NEW = [
    {"id": "k_wxs_yuandai_01", "name": "元杂剧的体制与关汉卿", "parent": "k_wenxueshi_yuandai",
     "chapter": "元代文学", "hot": True,
     "summary": "元杂剧结构一般为四折一楔子，角色分旦、末、净等，一人主唱。关汉卿是元杂剧奠基人，代表作《窦娥冤》写窦娥冤案与“三桩誓愿”，深刻揭露社会黑暗，另有《救风尘》《单刀会》等。",
     "examRef": "陕师高频考点",
     "basicQuestions": [
        {"stem": "元杂剧的结构体制一般为____一楔子。", "type": "blank", "answer": "四折", "explanation": "元杂剧一般由四折组成，必要时加楔子。", "options": None},
        {"stem": "关汉卿的代表作《____》写窦娥蒙冤及三桩誓愿。", "type": "blank", "answer": "窦娥冤", "explanation": "《窦娥冤》是关汉卿最著名的悲剧，借窦娥冤案控诉社会黑暗。", "options": None},
     ]},
    {"id": "k_wxs_yuandai_02", "name": "王实甫与《西厢记》", "parent": "k_wenxueshi_yuandai",
     "chapter": "元代文学", "hot": True,
     "summary": "王实甫《西厢记》写张生与崔莺莺的爱情故事，提出“愿天下有情人都成了眷属”，塑造了红娘等光彩形象，体制上突破四折一楔子为五本二十一折，语言华美。",
     "examRef": "陕师高频考点",
     "basicQuestions": [
        {"stem": "《西厢记》中“愿天下有情人____”这一口号由王实甫借人物之口喊出。", "type": "blank", "answer": "都成了眷属", "explanation": "《西厢记》以“愿天下有情人都成了眷属”为爱情理想口号。", "options": None},
        {"stem": "《西厢记》中性格最为光彩的婢女形象是____。", "type": "blank", "answer": "红娘", "explanation": "红娘是《西厢记》中撮合张生与莺莺的机敏婢女形象。", "options": None},
     ]},
    {"id": "k_wxs_yuandai_03", "name": "元代散曲", "parent": "k_wenxueshi_yuandai",
     "chapter": "元代文学", "hot": False,
     "summary": "散曲包括小令与套数两种形式，小令短小，套数由同一宫调若干曲牌联缀。代表作家有马致远（《天净沙·秋思》）、张养浩（《山坡羊·潼关怀古》）等。",
     "examRef": "",
     "basicQuestions": [
        {"stem": "“散曲”包括小令与____。", "type": "blank", "answer": "套数", "explanation": "散曲分小令和套数两种主要形式。", "options": None},
     ]},
    {"id": "k_wxs_yuandai_04", "name": "南戏与《琵琶记》", "parent": "k_wenxueshi_yuandai",
     "chapter": "元代文学", "hot": False,
     "summary": "南戏是宋元时期流行于南方的戏曲形式，被称作“南戏之祖”的是高明《琵琶记》，写蔡伯喈与赵五娘的悲欢离合，宣扬全忠全孝。",
     "examRef": "",
     "basicQuestions": [
        {"stem": "被称为“南戏之祖”的元代作品是高明的《____》。", "type": "blank", "answer": "琵琶记", "explanation": "高明《琵琶记》被后人誉为“南戏之祖”。", "options": None},
        {"stem": "《琵琶记》中的女主人公是____。", "type": "blank", "answer": "赵五娘", "explanation": "赵五娘是《琵琶记》中历尽艰辛的贤妻形象。", "options": None},
     ]},
    {"id": "k_wxs_yuandai_05", "name": "元诗四大家与元代诗文", "parent": "k_wenxueshi_yuandai",
     "chapter": "元代文学", "hot": False,
     "summary": "“元诗四大家”指虞集、杨载、范梈、揭傒斯。元好问是金末元初诗坛大家，其“寒波澹澹起，白鸟悠悠下”等句广为传诵。",
     "examRef": "",
     "basicQuestions": [
        {"stem": "“元诗四大家”是指____、杨载、范梈、揭傒斯四人。", "type": "blank", "answer": "虞集", "explanation": "元诗四大家以虞集为首。", "options": None},
     ]},
    {"id": "k_wxs_qingdai_01", "name": "《聊斋志异》与文言短篇小说", "parent": "k_wenxueshi_qingdai",
     "chapter": "清代文学", "hot": True,
     "summary": "蒲松龄《聊斋志异》是文言短篇小说的集大成之作，借花妖狐魅批判现实、寄托孤愤，“用传奇法，而以志怪”，如《促织》《婴宁》等。",
     "examRef": "陕师高频考点",
     "basicQuestions": [
        {"stem": "清代文言短篇小说集大成之作是蒲松龄的《____》。", "type": "blank", "answer": "聊斋志异", "explanation": "《聊斋志异》用传奇法而以志怪，为文言短篇小说巅峰。", "options": None},
     ]},
    {"id": "k_wxs_qingdai_02", "name": "《儒林外史》", "parent": "k_wenxueshi_qingdai",
     "chapter": "清代文学", "hot": True,
     "summary": "吴敬梓《儒林外史》是我国讽刺文学的典范，鲁迅概括其结构特点为“虽云长篇，颇同短制”，塑造范进、严监生等科举制度下的士人形象。",
     "examRef": "陕师高频考点",
     "basicQuestions": [
        {"stem": "鲁迅概括《____》的结构特点为“虽云长篇，颇同短制”。", "type": "blank", "answer": "儒林外史", "explanation": "《儒林外史》由相对独立的短篇故事缀连成篇。", "options": None},
     ]},
    {"id": "k_wxs_qingdai_03", "name": "《红楼梦》", "parent": "k_wenxueshi_qingdai",
     "chapter": "清代文学", "hot": True,
     "summary": "曹雪芹《红楼梦》以宝黛爱情悲剧为主线，展现贾府由盛转衰的封建家族史，有脂评本与程高本两个版本系统，人物塑造（王熙凤、焦大等）与结构艺术达到古典小说高峰。",
     "examRef": "陕师高频考点",
     "basicQuestions": [
        {"stem": "《红楼梦》有____与程高本两个版本系统。", "type": "blank", "answer": "脂评本", "explanation": "《红楼梦》版本分脂评抄本系统与程伟元高鹗活字本系统。", "options": None},
     ]},
    {"id": "k_wxs_qingdai_04", "name": "清代戏曲（《长生殿》《桃花扇》）", "parent": "k_wenxueshi_qingdai",
     "chapter": "清代文学", "hot": True,
     "summary": "洪昇《长生殿》写唐明皇与杨贵妃爱情，孔尚任《桃花扇》“借离合之情，写兴亡之感”，借侯方域李香君爱情写南明兴亡，两剧并称“南洪北孔”。",
     "examRef": "陕师高频考点",
     "basicQuestions": [
        {"stem": "“借离合之情，写兴亡之感”是《____》的独特结构方式。", "type": "blank", "answer": "桃花扇", "explanation": "孔尚任《桃花扇》借侯李爱情写南明兴亡。", "options": None},
        {"stem": "李香君是《____》中的人物。", "type": "blank", "answer": "桃花扇", "explanation": "李香君是《桃花扇》中的秦淮名妓、气节形象。", "options": None},
     ]},
    {"id": "k_wxs_qingdai_05", "name": "清代诗文词派", "parent": "k_wenxueshi_qingdai",
     "chapter": "清代文学", "hot": False,
     "summary": "清代诗文：桐城派（方苞、姚鼐）主张“义理、考据、辞章”；骈文有汪中《哀盐船文》等名篇；词有常州词派（张惠言开山、周济发扬光大）与浙西词派。",
     "examRef": "",
     "basicQuestions": [
        {"stem": "常州词派由张惠言开山，至____发扬光大，蔚为宗派。", "type": "blank", "answer": "周济", "explanation": "常州词派经周济发扬而蔚为大观。", "options": None},
     ]},
    {"id": "k_wxs_jindai_01", "name": "龚自珍与近代初期诗文", "parent": "k_wenxueshi_jindai",
     "chapter": "近代文学", "hot": True,
     "summary": "龚自珍是近代文学的开风气者，其诗如《己亥杂诗》“落红不是无情物，化作春泥更护花”，散文《病梅馆记》批判病态社会，“春夜伤心坐画屏”等句见其忧愤。",
     "examRef": "陕师高频考点",
     "basicQuestions": [
        {"stem": "“春夜伤心坐画屏，不如放眼入青冥”出自近代诗人____的《夜坐》。", "type": "blank", "answer": "龚自珍", "explanation": "龚自珍《夜坐》表现其忧愤与理想。", "options": None},
     ]},
    {"id": "k_wxs_jindai_02", "name": "诗界革命与黄遵宪、梁启超", "parent": "k_wenxueshi_jindai",
     "chapter": "近代文学", "hot": True,
     "summary": "诗界革命以黄遵宪“我手写我口”为先声，梁启超后期明确树起“诗界革命”旗帜；散文方面梁启超开创“新文体”（报章体）。",
     "examRef": "陕师高频考点",
     "basicQuestions": [
        {"stem": "近代后期鲜明提出“诗界革命”口号的是____。", "type": "blank", "answer": "梁启超", "explanation": "梁启超后期正式打出“诗界革命”旗帜。", "options": None},
     ]},
    {"id": "k_wxs_jindai_03", "name": "小说界革命与四大谴责小说", "parent": "k_wenxueshi_jindai",
     "chapter": "近代文学", "hot": True,
     "summary": "梁启超倡导“小说界革命”，将小说提高到新国新民的高度。清末四大谴责小说指李伯元《官场现形记》、吴趼人《二十年目睹之怪现状》、刘鹗《老残游记》、曾朴《孽海花》。",
     "examRef": "",
     "basicQuestions": [
        {"stem": "1902年梁启超发表《____》，将小说提高到新国新民的高度。", "type": "blank", "answer": "论小说与群治之关系", "explanation": "梁启超《论小说与群治之关系》是小说界革命的纲领。", "options": None},
     ]},
    {"id": "k_wxs_jindai_04", "name": "近代翻译文学与戏剧改良", "parent": "k_wenxueshi_jindai",
     "chapter": "近代文学", "hot": False,
     "summary": "近代翻译文学以严复《天演论》、林纾翻译西方小说为代表；戏剧改良运动推动话剧（文明戏）传入，1907年成立的春柳社是中国早期话剧团体。",
     "examRef": "",
     "basicQuestions": [
        {"stem": "近代翻译西方小说最多、影响最大的翻译家是____。", "type": "blank", "answer": "林纾", "explanation": "林纾（林琴南）译介大量西方小说，影响巨大。", "options": None},
     ]},
]

def main():
    k = json.load(open(KP, encoding="utf-8"))
    existing = {kp["id"] for kp in k["knowledge"]}
    added = 0
    for node in NEW:
        if node["id"] in existing:
            print("跳过已存在:", node["id"])
            continue
        k["knowledge"].append(node)
        added += 1
    order = ["先秦文学", "秦汉文学", "魏晋南北朝文学", "隋唐五代文学", "宋代文学", "元代文学", "明代文学", "清代文学", "近代文学"]
    k["chapters"] = [c for c in order if c in {kp["chapter"] for kp in k["knowledge"]}]
    k["knowledgeCount"] = len(k["knowledge"])
    json.dump(k, open(KP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"新增节点 {added}，总知识点 {k['knowledgeCount']}")
    print("chapters:", k["chapters"])

if __name__ == "__main__":
    main()
