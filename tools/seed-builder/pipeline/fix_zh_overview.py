# -*- coding: utf-8 -*-
"""为现代文学'综合专题'章补充 overview + knowledge"""
import io, sys, zipfile, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
zp = r'D:\study_app\app\assets\banks\bank-zhongguo-xiandai-wenxue-v0.14.0.zip'
tmp = zp + '.tmp'

overview = {
    "chapter": "综合专题",
    "knowledgeCount": 3,
    "questionCount": 15,
    "summary": "本章共 3 个知识点、15 道综合测试题。覆盖跨作家比较与文学史专题：国民性思考（鲁迅与老舍、高晓声）、知识分子形象谱系（鲁迅、郁达夫、茅盾、巴金、钱钟书）、现代新诗发展脉络与台湾现代文学轮廓、东北作家群等。"
}
knowledge = [
    {
        "id": "k_xdwx_zh_01",
        "name": "国民性思考：鲁迅与老舍、高晓声等的比较",
        "chapter": "综合专题",
        "parent": "k_xdwx_zonghe",
        "summary": "改造国民性是中国现代文学的母题之一。鲁迅以\"立人\"为旨归，在《呐喊》《彷徨》中批判国民劣根性（看客、麻木、精神胜利法）；老舍在《二马》《四世同堂》等中通过国民性格的反思与现代文明批判相勾连；高晓声则在新时期以陈奂生形象延续对农民精神状态的审视。比较题常考三者在批判对象、批判方式与时代语境上的异同。",
        "hot": True,
        "examRef": "陕师综合比较高频",
        "questionCount": 4
    },
    {
        "id": "k_xdwx_zh_02",
        "name": "知识分子形象谱系与文学史专题",
        "chapter": "综合专题",
        "parent": "k_xdwx_zonghe",
        "summary": "现代文学中的知识分子形象谱系：从鲁迅笔下的狂人、魏连殳（孤独觉醒者），到郁达夫的自叙传\"零余者\"，到茅盾《蚀》《子夜》中的时代女性与职业知识分子，再到巴金《寒夜》汪文宣（被生活压垮的小人物）、钱钟书《围城》方鸿渐（围城困境的讽刺性写照）。梳理其演变反映作家对启蒙、革命与个人命运的不同理解。",
        "hot": True,
        "examRef": "陕师论述常考",
        "questionCount": 6
    },
    {
        "id": "k_xdwx_zh_03",
        "name": "东北作家群与地方文学书写",
        "chapter": "综合专题",
        "parent": "k_xdwx_zonghe",
        "summary": "\"东北作家群\"指 20 世纪 30 年代流亡关内的东北籍青年作家群，代表作家有萧红、萧军、端木蕻良、骆宾基、舒群等，代表作品如萧红《生死场》《呼兰河传》、萧军《八月的乡村》、端木蕻良《科尔沁旗草原》。他们以\"九一八\"后沦陷区的乡愁与抗争为底色，将民族苦难与东北地域风情相结合，形成粗犷苍凉的美学风格。",
        "hot": False,
        "examRef": "名词解释常考",
        "questionCount": 2
    }
]

with zipfile.ZipFile(zp) as zin:
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for n in zin.namelist():
            data = zin.read(n)
            if n == 'manifest.json':
                m = json.loads(data)
                m['overviews'] = [o for o in m['overviews'] if o.get('chapter') != '综合专题']
                m['overviews'].append(overview)
                m['knowledge'] = [k for k in m['knowledge'] if k.get('chapter') != '综合专题']
                m['knowledge'].extend(knowledge)
                data = json.dumps(m, ensure_ascii=False, indent=2).encode('utf-8')
            zout.writestr(n, data)
os.replace(tmp, zp)
print('现代文学 manifest 已更新：overviews +综合专题, knowledge +3')
