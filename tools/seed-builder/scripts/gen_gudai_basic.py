# -*- coding: utf-8 -*-
"""为古代文学史隋唐/宋代/明代补基础题（主模型知识生成，素材 blockId 回填）。"""
import json
import os
import re

WORK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'out', 'v09gudaiwenxue')
MAT = os.path.join(WORK, 'materials')
DRAFT = os.path.join(WORK, 'draft')


def bid(ch, kw):
    for line in open(os.path.join(MAT, f'{ch}.txt'), encoding='utf-8'):
        m = re.match(r'^\[([0-9]{14}-[a-z0-9]+)\] (.*)', line.strip())
        if m and kw in m.group(2):
            return m.group(1)
    return None


def write(ch, qs, ts):
    with open(os.path.join(DRAFT, f'基础-{ch}.json'), 'w', encoding='utf-8') as f:
        json.dump(qs, f, ensure_ascii=False, indent=1)
    with open(os.path.join(DRAFT, f'测试-{ch}.json'), 'w', encoding='utf-8') as f:
        json.dump(ts, f, ensure_ascii=False, indent=1)
    print(f'{ch}: {len(qs)} 基础 + {len(ts)} 测试')


def main():
    suitang = [
        {"id": "tmp-suitang:b01", "type": "single_choice", "stem": "“初唐四杰”指（　）",
         "options": [{"key": "A", "text": "王勃、杨炯、卢照邻、骆宾王"}, {"key": "B", "text": "李白、杜甫、王维、孟浩然"},
                     {"key": "C", "text": "韩愈、柳宗元、元稹、白居易"}, {"key": "D", "text": "温庭筠、李商隐、杜牧、段成式"}],
         "answer": "A", "explanation": "初唐四杰为王勃、杨炯、卢照邻、骆宾王，推动诗歌题材从宫廷走向市井。",
         "chapter": "隋唐五代文学", "purpose": "basic", "tags": ["初唐四杰"], "difficulty": "easy",
         "source": {"blockId": bid("隋唐五代文学", "初唐四杰") or "20260727154933-n7fxky2", "kind": "exercise"}},
        {"id": "tmp-suitang:b02", "type": "blank", "stem": "李白诗风豪放飘逸，杜甫诗风＿＿＿，二人并称“李杜”。",
         "answer": ["沉郁顿挫"], "explanation": "杜甫诗歌以“沉郁顿挫”著称，与李白并称“李杜”。",
         "chapter": "隋唐五代文学", "purpose": "basic", "tags": ["李白", "杜甫", "沉郁顿挫"], "difficulty": "easy",
         "source": {"blockId": bid("隋唐五代文学", "沉郁顿挫") or "20260727154933-n7fxky2", "kind": "exercise"}},
        {"id": "tmp-suitang:b03", "type": "single_choice", "stem": "中唐“新乐府运动”的倡导者是（　）",
         "options": [{"key": "A", "text": "白居易、元稹"}, {"key": "B", "text": "韩愈、柳宗元"}, {"key": "C", "text": "高适、岑参"},
                     {"key": "D", "text": "王维、孟浩然"}],
         "answer": "A", "explanation": "白居易、元稹倡导新乐府运动，主张“文章合为时而著，歌诗合为事而作”。",
         "chapter": "隋唐五代文学", "purpose": "basic", "tags": ["新乐府", "白居易"], "difficulty": "easy",
         "source": {"blockId": bid("隋唐五代文学", "新乐府") or "20260727154933-n7fxky2", "kind": "exercise"}},
        {"id": "tmp-suitang:b04", "type": "single_choice", "stem": "唐代古文运动的领袖是（　）",
         "options": [{"key": "A", "text": "韩愈、柳宗元"}, {"key": "B", "text": "白居易、元稹"}, {"key": "C", "text": "李白、杜甫"},
                     {"key": "D", "text": "王维、孟浩然"}],
         "answer": "A", "explanation": "韩愈、柳宗元倡导古文运动，主张“文以明道”，反对骈文。",
         "chapter": "隋唐五代文学", "purpose": "basic", "tags": ["古文运动", "韩愈", "柳宗元"], "difficulty": "easy",
         "source": {"blockId": bid("隋唐五代文学", "古文") or "20260727154933-n7fxky2", "kind": "exercise"}},
        {"id": "tmp-suitang:b05", "type": "blank", "stem": "晚唐“小李杜”指李商隐和＿＿＿。",
         "answer": ["杜牧"], "explanation": "晚唐李商隐、杜牧并称“小李杜”。",
         "chapter": "隋唐五代文学", "purpose": "basic", "tags": ["小李杜", "李商隐", "杜牧"], "difficulty": "easy",
         "source": {"blockId": bid("隋唐五代文学", "李商隐") or "20260727154933-n7fxky2", "kind": "exercise"}},
        {"id": "tmp-suitang:b06", "type": "single_choice", "stem": "“花间词派”的鼻祖是（　）",
         "options": [{"key": "A", "text": "温庭筠"}, {"key": "B", "text": "李煜"}, {"key": "C", "text": "韦庄"}, {"key": "D", "text": "李商隐"}],
         "answer": "A", "explanation": "花间词派尊温庭筠为鼻祖，内容多写闺阁情事、花柳风月。",
         "chapter": "隋唐五代文学", "purpose": "basic", "tags": ["花间词", "温庭筠"], "difficulty": "easy",
         "source": {"blockId": bid("隋唐五代文学", "花间") or "20260727154933-n7fxky2", "kind": "exercise"}},
        {"id": "tmp-suitang:b07", "type": "single_choice", "stem": "唐传奇的名称来源于晚唐（　）编撰的《传奇》一书",
         "options": [{"key": "A", "text": "裴铏"}, {"key": "B", "text": "元稹"}, {"key": "C", "text": "李朝威"}, {"key": "D", "text": "白行简"}],
         "answer": "A", "explanation": "晚唐裴铏编撰《传奇》一书，“传奇”遂成为文言短篇小说专称。",
         "chapter": "隋唐五代文学", "purpose": "basic", "tags": ["唐传奇", "裴铏"], "difficulty": "medium",
         "source": {"blockId": bid("隋唐五代文学", "传奇") or "20260727154933-n7fxky2", "kind": "exercise"}},
        {"id": "tmp-suitang:b08", "type": "blank", "stem": "王国维评“词至＿＿＿而眼界始大、感慨遂深，遂变伶工之词而为士大夫之词”。",
         "answer": ["李煜"], "explanation": "王国维《人间词话》评李煜词“变伶工之词而为士大夫之词”。",
         "chapter": "隋唐五代文学", "purpose": "basic", "tags": ["李煜", "词"], "difficulty": "easy",
         "source": {"blockId": bid("隋唐五代文学", "李煜") or "20260727154933-n7fxky2", "kind": "exercise"}},
    ]
    write('隋唐五代文学', suitang, [])

    songdai = [
        {"id": "tmp-songdai:b01", "type": "single_choice", "stem": "被公认为豪放词派开创者、“以诗为词”全面革新词体的词人是（　）",
         "options": [{"key": "A", "text": "苏轼"}, {"key": "B", "text": "柳永"}, {"key": "C", "text": "辛弃疾"}, {"key": "D", "text": "周邦彦"}],
         "answer": "A", "explanation": "苏轼“以诗为词”，被公认为豪放词派开创者，突破了词为“艳科”格局。",
         "chapter": "宋代文学", "purpose": "basic", "tags": ["苏轼", "豪放词"], "difficulty": "easy",
         "source": {"blockId": bid("宋代文学", "苏轼") or "20260727154933-n7fxky2", "kind": "exercise"}},
        {"id": "tmp-songdai:b02", "type": "single_choice", "stem": "大力创作慢词、从根本上改变唐五代以来小令一统天下格局的词人是（　）",
         "options": [{"key": "A", "text": "柳永"}, {"key": "B", "text": "晏殊"}, {"key": "C", "text": "欧阳修"}, {"key": "D", "text": "张先"}],
         "answer": "A", "explanation": "柳永大力创作慢词，使慢词与小令平分秋色。",
         "chapter": "宋代文学", "purpose": "basic", "tags": ["柳永", "慢词"], "difficulty": "easy",
         "source": {"blockId": bid("宋代文学", "柳永") or "20260727154933-n7fxky2", "kind": "exercise"}},
        {"id": "tmp-songdai:b03", "type": "blank", "stem": "李清照提出词“＿＿＿”的主张，强调词与诗的区别。",
         "answer": ["别是一家"], "explanation": "李清照在《词论》中提出词“别是一家”，与诗相区别。",
         "chapter": "宋代文学", "purpose": "basic", "tags": ["李清照", "别是一家"], "difficulty": "easy",
         "source": {"blockId": bid("宋代文学", "李清照") or "20260727154933-n7fxky2", "kind": "exercise"}},
        {"id": "tmp-songdai:b04", "type": "single_choice", "stem": "江西诗派“一祖三宗”中的“一祖”指（　）",
         "options": [{"key": "A", "text": "杜甫"}, {"key": "B", "text": "李白"}, {"key": "C", "text": "苏轼"}, {"key": "D", "text": "黄庭坚"}],
         "answer": "A", "explanation": "江西诗派“一祖三宗”：一祖为杜甫，三宗为黄庭坚、陈师道、陈与义。",
         "chapter": "宋代文学", "purpose": "basic", "tags": ["江西诗派", "杜甫"], "difficulty": "medium",
         "source": {"blockId": bid("宋代文学", "江西诗派") or "20260727154933-n7fxky2", "kind": "exercise"}},
        {"id": "tmp-songdai:b05", "type": "single_choice", "stem": "南宋“中兴四大诗人”中成就最高、存诗最多的是（　）",
         "options": [{"key": "A", "text": "陆游"}, {"key": "B", "text": "杨万里"}, {"key": "C", "text": "范成大"}, {"key": "D", "text": "尤袤"}],
         "answer": "A", "explanation": "陆游是南宋中兴四大诗人之一，存诗近万首，成就最高。",
         "chapter": "宋代文学", "purpose": "basic", "tags": ["陆游", "中兴四大诗人"], "difficulty": "easy",
         "source": {"blockId": bid("宋代文学", "陆游") or "20260727154933-n7fxky2", "kind": "exercise"}},
        {"id": "tmp-songdai:b06", "type": "single_choice", "stem": "辛弃疾以文为词，独创“稼轩体”，与苏轼并称“＿＿＿”",
         "options": [{"key": "A", "text": "苏辛"}, {"key": "B", "text": "苏黄"}, {"key": "C", "text": "李辛"}, {"key": "D", "text": "辛姜"}],
         "answer": "A", "explanation": "辛弃疾与苏轼并称“苏辛”，是豪放词派集大成者。",
         "chapter": "宋代文学", "purpose": "basic", "tags": ["辛弃疾", "苏辛"], "difficulty": "easy",
         "source": {"blockId": bid("宋代文学", "辛弃疾") or "20260727154933-n7fxky2", "kind": "exercise"}},
    ]
    write('宋代文学', songdai, [])

    mingdai = [
        {"id": "tmp-mingdai:b01", "type": "single_choice", "stem": "我国第一部文人独创的长篇世情小说（社会人情小说）是（　）",
         "options": [{"key": "A", "text": "《金瓶梅》"}, {"key": "B", "text": "《三国演义》"}, {"key": "C", "text": "《水浒传》"}, {"key": "D", "text": "《西游记》"}],
         "answer": "A", "explanation": "《金瓶梅》是我国第一部个人独创型长篇小说，也是第一部以社会普通人物为主人公的世情小说。",
         "chapter": "明代文学", "purpose": "basic", "tags": ["金瓶梅", "世情小说"], "difficulty": "easy",
         "source": {"blockId": bid("明代文学", "金瓶梅") or "20260727170429-whhogug", "kind": "exercise"}},
        {"id": "tmp-mingdai:b02", "type": "single_choice", "stem": "“临川四梦”（玉茗堂四梦）是（　）创作的传奇",
         "options": [{"key": "A", "text": "汤显祖"}, {"key": "B", "text": "梁辰鱼"}, {"key": "C", "text": "徐渭"}, {"key": "D", "text": "李渔"}],
         "answer": "A", "explanation": "汤显祖的《牡丹亭》《紫钗记》《南柯记》《邯郸记》合称“临川四梦”。",
         "chapter": "明代文学", "purpose": "basic", "tags": ["汤显祖", "临川四梦"], "difficulty": "easy",
         "source": {"blockId": bid("明代文学", "汤显祖") or "20260727170429-whhogug", "kind": "exercise"}},
        {"id": "tmp-mingdai:b03", "type": "blank", "stem": "公安派袁宏道提出“独抒性灵，＿＿＿”的创作主张。",
         "answer": ["不拘格套"], "explanation": "公安派主张“独抒性灵，不拘格套”，强调表现真性情。",
         "chapter": "明代文学", "purpose": "basic", "tags": ["公安派", "性灵"], "difficulty": "easy",
         "source": {"blockId": bid("明代文学", "公安") or "20260727170429-whhogug", "kind": "exercise"}},
        {"id": "tmp-mingdai:b04", "type": "single_choice", "stem": "“三言”的编选者是（　）",
         "options": [{"key": "A", "text": "冯梦龙"}, {"key": "B", "text": "凌濛初"}, {"key": "C", "text": "抱瓮老人"}, {"key": "D", "text": "张竹坡"}],
         "answer": "A", "explanation": "冯梦龙编选《喻世明言》《警世通言》《醒世恒言》合称“三言”。",
         "chapter": "明代文学", "purpose": "basic", "tags": ["三言", "冯梦龙"], "difficulty": "easy",
         "source": {"blockId": bid("明代文学", "三言") or "20260727170429-whhogug", "kind": "exercise"}},
        {"id": "tmp-mingdai:b05", "type": "single_choice", "stem": "“二拍”（《初刻拍案惊奇》《二刻拍案惊奇》）的作者是（　）",
         "options": [{"key": "A", "text": "凌濛初"}, {"key": "B", "text": "冯梦龙"}, {"key": "C", "text": "汤显祖"}, {"key": "D", "text": "李贽"}],
         "answer": "A", "explanation": "凌濛初编著“二拍”，与冯梦龙“三言”并称“三言二拍”。",
         "chapter": "明代文学", "purpose": "basic", "tags": ["二拍", "凌濛初"], "difficulty": "easy",
         "source": {"blockId": bid("明代文学", "二拍") or "20260727170429-whhogug", "kind": "exercise"}},
        {"id": "tmp-mingdai:b06", "type": "single_choice", "stem": "明代中期提出“文必秦汉，诗必盛唐”、借复古以革新的文学流派是（　）",
         "options": [{"key": "A", "text": "前后七子"}, {"key": "B", "text": "公安派"}, {"key": "C", "text": "竟陵派"}, {"key": "D", "text": "唐宋派"}],
         "answer": "A", "explanation": "前后七子提出“文必秦汉，诗必盛唐”，反对台阁体。",
         "chapter": "明代文学", "purpose": "basic", "tags": ["前后七子", "复古"], "difficulty": "easy",
         "source": {"blockId": bid("明代文学", "七子") or "20260727170429-whhogug", "kind": "exercise"}},
    ]
    write('明代文学', mingdai, [])


if __name__ == '__main__':
    main()
