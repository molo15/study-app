# -*- coding: utf-8 -*-
"""为古代文学史元/清/近代补基础题（无素材，按教材标准，source 用 textbook-standard 占位）。"""
import json
import os

WORK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'out', 'v09gudaiwenxue')
DRAFT = os.path.join(WORK, 'draft')

SRC = {"blockId": "textbook-standard", "docPath": "教材标准考点", "kind": "exercise"}


def write(ch, qs, ts):
    with open(os.path.join(DRAFT, f'基础-{ch}.json'), 'w', encoding='utf-8') as f:
        json.dump(qs, f, ensure_ascii=False, indent=1)
    with open(os.path.join(DRAFT, f'测试-{ch}.json'), 'w', encoding='utf-8') as f:
        json.dump(ts, f, ensure_ascii=False, indent=1)
    print(f'{ch}: {len(qs)} 基础 + {len(ts)} 测试')


def main():
    yuandai = [
        {"id": "tmp-yuandai:b01", "type": "single_choice", "stem": "“元曲四大家”指关汉卿、（　）、白朴、马致远",
         "options": [{"key": "A", "text": "王实甫"}, {"key": "B", "text": "郑光祖"}, {"key": "C", "text": "纪君祥"}, {"key": "D", "text": "高文秀"}],
         "answer": "B", "explanation": "元曲四大家：关汉卿、郑光祖、白朴、马致远。", "chapter": "元代文学", "purpose": "basic",
         "tags": ["元曲四大家"], "difficulty": "easy", "source": dict(SRC)},
        {"id": "tmp-yuandai:b02", "type": "single_choice", "stem": "被称为“天下夺魁”、以崔莺莺与张生爱情为题材的元杂剧是（　）",
         "options": [{"key": "A", "text": "《西厢记》"}, {"key": "B", "text": "《窦娥冤》"}, {"key": "C", "text": "《汉宫秋》"}, {"key": "D", "text": "《梧桐雨》"}],
         "answer": "A", "explanation": "王实甫《西厢记》写崔莺莺与张生爱情，被贾仲明称为“天下夺魁”。", "chapter": "元代文学", "purpose": "basic",
         "tags": ["西厢记", "王实甫"], "difficulty": "easy", "source": dict(SRC)},
        {"id": "tmp-yuandai:b03", "type": "blank", "stem": "关汉卿《窦娥冤》中，窦娥临刑前发下血溅白练、六月飞雪、＿＿＿三桩誓愿。",
         "answer": ["亢旱三年"], "explanation": "窦娥三桩誓愿：血溅白练、六月飞雪、亢旱三年，表现冤屈之深。", "chapter": "元代文学", "purpose": "basic",
         "tags": ["窦娥冤", "关汉卿"], "difficulty": "medium", "source": dict(SRC)},
        {"id": "tmp-yuandai:b04", "type": "single_choice", "stem": "元散曲包括小令和（　）两种形式",
         "options": [{"key": "A", "text": "套数"}, {"key": "B", "text": "诸宫调"}, {"key": "C", "text": "杂剧"}, {"key": "D", "text": "鼓子词"}],
         "answer": "A", "explanation": "散曲分小令与套数（套曲）两种。", "chapter": "元代文学", "purpose": "basic",
         "tags": ["散曲", "套数"], "difficulty": "easy", "source": dict(SRC)},
        {"id": "tmp-yuandai:b05", "type": "single_choice", "stem": "被称“南戏之祖”、写蔡伯喈与赵五娘故事的南戏是（　）",
         "options": [{"key": "A", "text": "《琵琶记》"}, {"key": "B", "text": "《荆钗记》"}, {"key": "C", "text": "《白兔记》"}, {"key": "D", "text": "《拜月亭》"}],
         "answer": "A", "explanation": "高明《琵琶记》被称为“南戏之祖”，写蔡伯喈与赵五娘故事。", "chapter": "元代文学", "purpose": "basic",
         "tags": ["琵琶记", "南戏"], "difficulty": "easy", "source": dict(SRC)},
        {"id": "tmp-yuandai:b06", "type": "blank", "stem": "马致远散曲名作《天净沙·秋思》被称为“秋思之祖”，其名句是“＿＿＿，断肠人在天涯”。",
         "answer": ["夕阳西下"], "explanation": "《天净沙·秋思》结句“夕阳西下，断肠人在天涯”。", "chapter": "元代文学", "purpose": "basic",
         "tags": ["马致远", "天净沙秋思"], "difficulty": "easy", "source": dict(SRC)},
    ]
    write('元代文学', yuandai, [])

    qingdai = [
        {"id": "tmp-qingdai:b01", "type": "single_choice", "stem": "《红楼梦》的作者是（　）",
         "options": [{"key": "A", "text": "曹雪芹"}, {"key": "B", "text": "高鹗"}, {"key": "C", "text": "吴敬梓"}, {"key": "D", "text": "蒲松龄"}],
         "answer": "A", "explanation": "《红楼梦》前八十回为曹雪芹所著，后四十回一般认为高鹗续补。", "chapter": "清代文学", "purpose": "basic",
         "tags": ["红楼梦", "曹雪芹"], "difficulty": "easy", "source": dict(SRC)},
        {"id": "tmp-qingdai:b02", "type": "single_choice", "stem": "鲁迅评“用传奇法，而以志怪”、借花妖狐魅写世情的文言小说是（　）",
         "options": [{"key": "A", "text": "《聊斋志异》"}, {"key": "B", "text": "《阅微草堂笔记》"}, {"key": "C", "text": "《儒林外史》"}, {"key": "D", "text": "《镜花缘》"}],
         "answer": "A", "explanation": "蒲松龄《聊斋志异》“用传奇法而以志怪”，是我国文言短篇小说的巅峰。", "chapter": "清代文学", "purpose": "basic",
         "tags": ["聊斋志异", "蒲松龄"], "difficulty": "easy", "source": dict(SRC)},
        {"id": "tmp-qingdai:b03", "type": "single_choice", "stem": "我国第一部讽刺小说、鲁迅评为“公心讽世之书”的是（　）",
         "options": [{"key": "A", "text": "《儒林外史》"}, {"key": "B", "text": "《聊斋志异》"}, {"key": "C", "text": "《红楼梦》"}, {"key": "D", "text": "《官场现形记》"}],
         "answer": "A", "explanation": "吴敬梓《儒林外史》是我国第一部讽刺小说，鲁迅称其“公心讽世之书”。", "chapter": "清代文学", "purpose": "basic",
         "tags": ["儒林外史", "吴敬梓", "讽刺小说"], "difficulty": "easy", "source": dict(SRC)},
        {"id": "tmp-qingdai:b04", "type": "blank", "stem": "孔尚任《桃花扇》“借离合之情，写＿＿＿”，以侯方域与李香君爱情贯穿明末兴亡。",
         "answer": ["兴亡之感"], "explanation": "《桃花扇》“借离合之情，写兴亡之感”。", "chapter": "清代文学", "purpose": "basic",
         "tags": ["桃花扇", "孔尚任"], "difficulty": "medium", "source": dict(SRC)},
        {"id": "tmp-qingdai:b05", "type": "single_choice", "stem": "与孔尚任并称“南洪北孔”的《长生殿》作者是（　）",
         "options": [{"key": "A", "text": "洪昇"}, {"key": "B", "text": "李渔"}, {"key": "C", "text": "蒋士铨"}, {"key": "D", "text": "方成培"}],
         "answer": "A", "explanation": "洪昇《长生殿》写唐明皇与杨贵妃故事，与孔尚任并称“南洪北孔”。", "chapter": "清代文学", "purpose": "basic",
         "tags": ["长生殿", "洪昇"], "difficulty": "easy", "source": dict(SRC)},
        {"id": "tmp-qingdai:b06", "type": "single_choice", "stem": "清代散文流派中，以方苞、姚鼐为代表、主张“义理考据辞章”合一的是（　）",
         "options": [{"key": "A", "text": "桐城派"}, {"key": "B", "text": "阳湖派"}, {"key": "C", "text": "公安派"}, {"key": "D", "text": "竟陵派"}],
         "answer": "A", "explanation": "桐城派以方苞、刘大櫆、姚鼐为代表，主张“义理、考据、辞章”合一。", "chapter": "清代文学", "purpose": "basic",
         "tags": ["桐城派"], "difficulty": "medium", "source": dict(SRC)},
    ]
    write('清代文学', qingdai, [])

    jindai = [
        {"id": "tmp-jindai:b01", "type": "single_choice", "stem": "近代“诗界革命”的旗帜性人物、提出“我手写我口”的是（　）",
         "options": [{"key": "A", "text": "黄遵宪"}, {"key": "B", "text": "梁启超"}, {"key": "C", "text": "龚自珍"}, {"key": "D", "text": "谭嗣同"}],
         "answer": "A", "explanation": "黄遵宪是“诗界革命”的旗帜，主张“我手写我口”。", "chapter": "近代文学", "purpose": "basic",
         "tags": ["诗界革命", "黄遵宪"], "difficulty": "easy", "source": dict(SRC)},
        {"id": "tmp-jindai:b02", "type": "single_choice", "stem": "近代“小说界革命”的倡导者、著《论小说与群治之关系》的是（　）",
         "options": [{"key": "A", "text": "梁启超"}, {"key": "B", "text": "黄遵宪"}, {"key": "C", "text": "严复"}, {"key": "D", "text": "林纾"}],
         "answer": "A", "explanation": "梁启超倡导“小说界革命”，将小说提高到“新国新民”的高度。", "chapter": "近代文学", "purpose": "basic",
         "tags": ["小说界革命", "梁启超"], "difficulty": "easy", "source": dict(SRC)},
        {"id": "tmp-jindai:b03", "type": "blank", "stem": "清末四大谴责小说为《官场现形记》《二十年目睹之怪现状》《老残游记》和《＿＿＿》。",
         "answer": ["孽海花"], "explanation": "清末四大谴责小说：官场现形记、二十年目睹之怪现状、老残游记、孽海花。", "chapter": "近代文学", "purpose": "basic",
         "tags": ["谴责小说"], "difficulty": "easy", "source": dict(SRC)},
        {"id": "tmp-jindai:b04", "type": "blank", "stem": "龚自珍《己亥杂诗》名句“我劝天公重抖擞，＿＿＿”。",
         "answer": ["不拘一格降人才"], "explanation": "龚自珍《己亥杂诗》“我劝天公重抖擞，不拘一格降人才”。", "chapter": "近代文学", "purpose": "basic",
         "tags": ["龚自珍", "己亥杂诗"], "difficulty": "easy", "source": dict(SRC)},
    ]
    write('近代文学', jindai, [])


if __name__ == '__main__':
    main()
