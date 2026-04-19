import xml.etree.ElementTree as ET
import sys
import re
from datetime import datetime

# RSS XML content from chinanews
rss_content = """<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet type="text/css" href="rsstyle.css"?>
<rss version="2.0">
<channel>
<title>中新网即时新闻</title>
<image>
  <title>中新网即时新闻</title>
  <link>https://www.chinanews.com.cn/scroll-news/news1.html</link>
  <url>https://www.chinanews.com/images/images1/logo2.gif</url>
</image>
<description></description>
<link>https://www.chinanews.com.cn/scroll-news/news1.html</link>
<language>zh-cn</language>
<item><title>英媒称霍尔木兹海峡航运再次停滞</title><link>https://www.chinanews.com.cn/gj/2026/04-19/10606399.shtml</link><description>
　　新华社伦敦4月18日电(记者高文成)据英国航运媒体《劳埃德船舶日报》报道，霍尔木兹海峡航运18日傍晚再次陷入停滞。此前，无线电通信警告称，伊朗武装部队已恢复对该海峡的“严格管理和控制”。相关海域内多艘船只听到警告，并已得到证实。</description>
<pubDate>Sun, 19 Apr 2026 06:22:34 +0800</pubDate>
</item>
<item><title>墨西哥中部一酒吧遭武装袭击致8人死亡</title><link>https://www.chinanews.com.cn/gj/2026/04-19/10606398.shtml</link><description>
　　新华社墨西哥城4月18日电(记者吴昊 翟淑睿)墨西哥中部莫雷洛斯州检方18日发布公告说，该州阿亚拉市一家酒吧当天凌晨发生武装袭击事件，造成至少8人死亡。</description>
<pubDate>Sun, 19 Apr 2026 06:19:57 +0800</pubDate>
</item>
<item><title>CBA常规赛：辽宁主场收官战不敌浙江</title><link>https://www.chinanews.com.cn/ty/2026/04-19/10606397.shtml</link><description>
　　中新社沈阳4月18日电 (记者 韩宏)2025-2026赛季中国男子篮球职业联赛(CBA)常规赛第40轮继续进行，辽宁队18日晚主场迎战浙江队，最终以71比76不敌浙江队。</description>
<pubDate>Sun, 19 Apr 2026 00:05:26 +0800</pubDate>
</item>
<item><title>乌克兰基辅枪击事件已致5人死亡 枪手身份公布</title><link>https://www.chinanews.com.cn/gj/2026/04-19/10606396.shtml</link><description>
　　乌克兰总统泽连斯基18日表示，基辅枪击事件已造成5人死亡，袭击者已被打死。截至目前共有10名伤者被送医接受治疗，4名人质被成功解救。泽连斯基表示，将对事件展开迅速调查，目前乌克兰国家警察和乌克兰安全局调查人员已介入。</description>
<pubDate>Sun, 19 Apr 2026 00:02:38 +0800</pubDate>
</item>
<item><title>CBA季后赛席位争夺升温 广州大胜吉林保留晋级希望</title><link>https://www.chinanews.com.cn/ty/2026/04-18/10606394.shtml</link><description>
　　中新社长春4月18日电 (记者 郭佳)18日晚，CBA常规赛第40轮打响，广州朗肽海本队(下称“广州队”)客场挑战吉林长白山恩都里队(下称“吉林队”)。最终广州队以93:75大胜对手，战绩更新为17胜23负，延续冲击季后赛的希望。</description>
<pubDate>Sat, 18 Apr 2026 23:46:22 +0800</pubDate>
</item>
<item><title>CBA常规赛第40轮：福建客场战胜广东</title><link>https://www.chinanews.com.cn/ty/2026/04-18/10606390.shtml</link><description>
　　中新社东莞4月18日电 (记者 张璐)2025-2026赛季中国男子篮球职业联赛(CBA)常规赛第40轮18日晚在东莞继续进行。福建晋江文旅队(简称“福建队”)客场以95:83战胜广东东阳光队(简称“广东队”)。</description>
<pubDate>Sat, 18 Apr 2026 23:45:46 +0800</pubDate>
</item>
<item><title>英海上贸易行动办公室：霍尔木兹海峡附近发生多起船只遇袭事件</title><link>https://www.chinanews.com.cn/gj/2026/04-18/10606393.shtml</link><description>
　　英国海上贸易行动办公室18日发布多份通报称，接到多起霍尔木兹海峡附近船只遇袭事件的报告。</description>
<pubDate>Sat, 18 Apr 2026 23:31:24 +0800</pubDate>
</item>
<item><title>乌克兰基辅发生枪击事件 致数人死亡</title><link>https://www.chinanews.com.cn/gj/2026/04-18/10606392.shtml</link><description>
　　当地时间18日，乌克兰基辅市长称基辅市内一家超市发生枪击事件，已造成多人受伤及数人死亡。枪手藏身于超市内，抓捕行动正在进行。</description>
<pubDate>Sat, 18 Apr 2026 23:29:31 +0800</pubDate>
</item>
<item><title>缅甸仰光至毛淡棉公路上发生严重交通事故 致9人死亡</title><link>https://www.chinanews.com.cn/gj/2026/04-18/10606391.shtml</link><description>
　　据缅甸消防部门消息，4月18日下午，仰光至毛淡棉公路上发生一起严重交通事故，一辆客车与载人货车相撞，导致货车上9人死亡多人受伤。目前伤者已由当地救援组织送往医院救治，事故原因相关部门正在调查。(总台记者 林曦)</description>
<pubDate>Sat, 18 Apr 2026 23:26:01 +0800</pubDate>
</item>
<item><title>中超第六轮：山东泰山战平上海海港 天津津门虎迎赛季首胜</title><link>https://www.chinanews.com.cn/ty/2026/04-18/10606389.shtml</link><description>
　　中新社北京4月18日电 (刘梦青)2026赛季中超联赛第六轮比赛18日全部战罢。焦点战中，山东泰山主场作战，虽各项数据占优，但终以1:1战平上海海港；天津津门虎3:0大胜云南玉昆，迎来赛季首胜。</description>
<pubDate>Sat, 18 Apr 2026 23:01:42 +0800</pubDate>
</item>
<item><title>俄外贝加尔边疆区交通事故致2名中国公民遇难</title><link>https://www.chinanews.com.cn/gj/2026/04-18/10606388.shtml</link><description>
　　中新社莫斯科4月18日电  俄罗斯远东外贝加尔边疆区18日发生大巴翻车事故，造成2名中国公民遇难，至少10名中国公民受伤。</description>
<pubDate>Sat, 18 Apr 2026 23:01:10 +0800</pubDate>
</item>
<item><title>五一假期首尾高峰时段，平均每天增开直通夜间高铁700列</title><link>https://www.chinanews.com.cn/gn/2026/04-18/10606385.shtml</link><description>
　　中新网北京4月18日电(记者 李京统)记者从中国铁路12306技术中心了解到，五一假期火车票开售以来，购票需求旺盛。为最大限度满足旅客购票需求，铁路部门在假期首尾出行高峰时段和旅客出行相对集中的方向，计划调整高铁夜间“天窗”维修时间，在确保安全前提下，于4月29日夜间至5月2日凌晨、5月4日夜间至6日凌晨，在京沪、京广、京哈等高铁干线，安排开行直通夜间高铁，平均每天增开可达700列左右。</description>
<pubDate>Sat, 18 Apr 2026 22:35:16 +0800</pubDate>
</item>
<item><title>伊朗正在审议美方新提议 尚未回应</title><link>https://www.chinanews.com.cn/gj/2026/04-18/10606386.shtml</link><description>
　　当地时间18日，伊朗最高国家安全委员会秘书处就美伊谈判最新进展发表声明。</description>
<pubDate>Sat, 18 Apr 2026 22:31:50 +0800</pubDate>
</item>
<item><title>伊朗：将控制霍尔木兹海峡通行直至战争彻底结束</title><link>https://www.chinanews.com.cn/gj/2026/04-18/10606384.shtml</link><description>
　　当地时间18日，伊朗最高国家安全委员会秘书处就美伊谈判最新进展发表声明。</description>
<pubDate>Sat, 18 Apr 2026 22:28:13 +0800</pubDate>
</item>
<item><title>俄罗斯远东交通事故中受伤的中国人已有14人回国治疗</title><link>https://www.chinanews.com.cn/gj/2026/04-18/10606383.shtml</link><description>
　　记者18日从内蒙古自治区满洲里市人民医院了解到，俄罗斯远东交通事故中受伤的中国人已有14人回国治疗。</description>
<pubDate>Sat, 18 Apr 2026 22:25:29 +0800</pubDate>
</item>
<item><title>土耳其指责以色列以安全为名攫取土地</title><link>https://www.chinanews.com.cn/gj/2026/04-18/10606382.shtml</link><description>
　　新华社北京4月18日电 土耳其外交部长费丹18日表示，以色列以安全为借口攫取更多土地，然而，要实现真正的和平应停止对他国动武。</description>
<pubDate>Sat, 18 Apr 2026 22:21:31 +0800</pubDate>
</item>
<item><title>哥伦比亚总统：美国若一意孤行将激起拉美国家“反抗”</title><link>https://www.chinanews.com.cn/gj/2026/04-18/10606381.shtml</link><description>
　　新华社北京4月18日电 哥伦比亚总统佩特罗接受媒体采访时表示，如果美国政府执意推行当前政策、打压持不同政治立场的拉丁美洲国家领导人，等待它的将是拉美国家再次“反抗”。</description>
<pubDate>Sat, 18 Apr 2026 22:19:53 +0800</pubDate>
</item>
<item><title>中国市场红利持续释放 东南亚企业消博会上寻新机</title><link>https://www.chinanews.com.cn/aseaninfo/2026/04-18/10606379.shtml</link><description>
　　中新网海口4月18日电(左雨晴 张静)从泰国的农牧食品企业到新加坡的跨境直播电商，诸多东南亚企业亮相近日举行的第六届消博会。</description>
<pubDate>Sat, 18 Apr 2026 22:05:28 +0800</pubDate>
</item>
<item><title>泰国类鼻疽疫情今年已确诊732例死亡23例</title><link>https://www.chinanews.com.cn/gj/2026/04-18/10606380.shtml</link><description>
　　中新社曼谷4月18日电 (李映民  刘宇博)泰国总理府副发言人拉丽达·佩里斯维瓦塔纳18日透露，今年以来泰国出现的类鼻疽疫情呈现令人担忧的趋势，1月1日至4月16日全国累计确诊病例732例，死亡23例。</description>
<pubDate>Sat, 18 Apr 2026 22:04:06 +0800</pubDate>
</item>
<item><title>2026津台文化交流季启动 两岸书画家笔墨传情话团圆</title><link>https://www.chinanews.com.cn/txy/2026/04-18/10606373.shtml</link><description>
　　中新社天津4月18日电 (记者 孙玲玲)2026津台文化交流季启动仪式暨“同源瀚海”津台书画作品展18日在天津津派文化国际艺术中心(曹锟故居)开幕。两岸约60位书画家齐聚津门，以笔墨为媒，共话团圆。</description>
<pubDate>Sat, 18 Apr 2026 22:00:40 +0800</pubDate>
</item>
<item><title>福建泉州直航台湾本岛集装箱航线新增周末船班</title><link>https://www.chinanews.com.cn/sh/2026/04-18/10606374.shtml</link><description>
　　中新社泉州4月18日电 (记者 孙虹)运载台湾日用品的集装箱轮“丰泽园”，18日靠泊福建泉州港石湖作业区，卸货后随即装载泉州货物前往台湾，标志着泉州直航台湾本岛集装箱航线新增周末船班，两岸海上快捷通道进一步畅通。</description>
<pubDate>Sat, 18 Apr 2026 22:00:01 +0800</pubDate>
</item>
<item><title>《再回闽南》在漳州上演 海外侨胞“沉浸式”共忆家国往事</title><link>https://www.chinanews.com.cn/cul/2026/04-18/10606375.shtml</link><description>
　　中新社漳州4月18日电 (记者 张金川)中国首部多维度楼体沉浸式演艺《再回闽南》连日来在侨乡福建漳州的侨芗剧场上演。沙特华侨华人联合会会长林大旺18日接受中新社记者采访时说，每一封侨批都承载着一段出海奋斗史，也映照着漳州华侨爱国爱乡的深沉情怀。</description>
<pubDate>Sat, 18 Apr 2026 21:58:35 +0800</pubDate>
</item>
<item><title>欧亚学者聚首广东 开展文明互鉴与人文交流合作</title><link>https://www.chinanews.com.cn/edu/2026/04-18/10606376.shtml</link><description>
　　中新社广东湛江4月18日电 (梁盛  赵宇清)来自中国、白俄罗斯、俄罗斯、波兰四国的53位专家学者，18日齐聚广东岭南师范学院，展开跨地域、跨文化、跨学科研讨，为欧亚人文交流与学术合作凝聚共识。</description>
<pubDate>Sat, 18 Apr 2026 21:57:57 +0800</pubDate>
</item>
<item><title>2026“中国华服周·吉韵东方”系列活动在长春启幕</title><link>https://www.chinanews.com.cn/cul/2026/04-18/10606377.shtml</link><description>
　　中新社长春4月18日电 (高龙安  李彦国)2026年“中国华服周·吉韵东方”系列活动18日在长春新民大街历史文化街区正式启幕。</description>
<pubDate>Sat, 18 Apr 2026 21:57:09 +0800</pubDate>
</item>
<item><title>中国—东盟翻译传播联盟成立</title><link>https://www.chinanews.com.cn/aseaninfo/2026/04-18/10606378.shtml</link><description>
　　【东盟专线】中国—东盟翻译传播联盟成立</description>
<pubDate>Sat, 18 Apr 2026 21:50:57 +0800</pubDate>
</item>
<item><title>台胞追忆抗战峥嵘岁月：唤醒两岸共御外侮记忆，让荣耀不再沉默</title><link>https://www.chinanews.com.cn/gn/2026/04-18/10606371.shtml</link><description>
　　中新网4月18日电(记者 陈文韬 姜雨薇 朱延静)“我的祖父雾峰林家第七代林幼春，在日据殖民黑夜中以笔为剑，以诗存史；时至今日，我的任务是还原及传播抗日历史真相。我们祖孙虽然相隔于百年，不同的年代，内心蕴藏的却是同一份深沉而坚韧的家国情怀。这份情怀，是血脉的传承，更是民族精神的守护。”</description>
<pubDate>Sat, 18 Apr 2026 21:36:58 +0800</pubDate>
</item>
<item><title>关了又开，开了又关，霍尔木兹海峡还有完没完？</title><link>https://www.chinanews.com.cn/gj/2026/04-18/10606372.shtml</link><description>
　　就在伊朗有条件开放霍尔木兹海峡、开放部分空域，中东局势似正趋缓之时，伊朗军方当地时间18日晚些时候突然宣布，由于美国“违背承诺”，伊朗恢复对霍尔木兹海峡的严格管控。</description>
<pubDate>Sat, 18 Apr 2026 21:35:46 +0800</pubDate>
</item>
<item><title>湖南省第14届“爱地球 看我的”主题宣传活动长沙举行</title><link>https://www.chinanews.com.cn/sh/2026/04-18/10606368.shtml</link><description>
　　中新网长沙4月18日电(向一鹏)18日，在第57个世界地球日来临之际，湖南省第14届“爱地球 看我的”主题宣传活动暨地下水科学知识博物馆巡讲活动在湖南省地质博物馆举办。</description>
<pubDate>Sat, 18 Apr 2026 21:28:08 +0800</pubDate>
</item>
<item><title>全国近千名击剑健儿齐聚广州从化 展开巅峰对决</title><link>https://www.chinanews.com.cn/ty/2026/04-18/10606367.shtml</link><description>
　　中新网广州4月18日电 (张璐 黄颖瑶)4月18日至19日，中国体育彩票—“中国温泉之都”2026年广州从化击剑公开赛(简称“赛事”)在广州南洋理工职业学院体育馆火热开赛。本次赛事吸引全国近千名击剑健儿齐聚从化，展开速度与技巧、智慧与勇气的巅峰对决。</description>
<pubDate>Sat, 18 Apr 2026 21:24:07 +0800</pubDate>
</item>
<item><title>中外专家在渝聚焦柑桔产业发展 两大联合实验室揭牌</title><link>https://www.chinanews.com.cn/sh/2026/04-18/10606369.shtml</link><description>
　　中新网重庆4月18日电 (记者 钟旖)柑桔重大病虫害防控暨产业高质量发展国际论坛18日在重庆市北碚区举行。</description>
<pubDate>Sat, 18 Apr 2026 21:22:11 +0800</pubDate>
</item>

</channel>
</rss>"""

# Parse XML
root = ET.fromstring(rss_content)

# Categories and keywords
categories = {
    "金融": ["金融", "股市", "银行", "货币", "汇率", "投资", "资本", "经济", "消费", "市场", "红利", "企业"],
    "资本市场": ["股市", "股票", "资本市场", "证券", "交易所", "IPO", "融资", "并购", "债券", "基金"],
    "科技": ["科技", "创新", "互联网", "数字化", "人工智能", "AI", "5G", "芯片", "半导体", "科研", "实验室", "电商", "直播", "跨境"],
    "政治": ["政治", "政府", "领导人", "外交", "谈判", "协议", "制裁", "选举", "抗议", "冲突", "领土", "安全", "国防", "军控"],
    "军事": ["军事", "军队", "武器", "战争", "冲突", "袭击", "恐怖", "武装", "国防", "海军", "空军", "导弹", "演习", "海峡", "控制"]
}

# Store news by category
news_by_category = {cat: [] for cat in categories}

# Iterate through items
for item in root.findall('.//item'):
    title = item.find('title').text if item.find('title') is not None else ''
    link = item.find('link').text if item.find('link') is not None else ''
    description = item.find('description').text if item.find('description') is not None else ''
    pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ''
    
    # Determine category
    matched = False
    text = title + ' ' + description
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in text:
                news_by_category[cat].append({
                    'title': title,
                    'link': link,
                    'description': description[:100] + '...' if len(description) > 100 else description,
                    'pubDate': pubDate
                })
                matched = True
                break
        if matched:
            break
    # If no match, put in "其他" (but we skip for now)

# Output formatted news
output = []
output.append("📰 新闻摘要 (来源: 中新网)")
output.append("生成时间: 2026-04-19 07:00")
output.append("")

for cat, items in news_by_category.items():
    if items:
        output.append(f"## {cat}")
        for i, news in enumerate(items[:5], 1):  # Limit to top 5 per category
            output.append(f"{i}. {news['title']}")
            output.append(f"   {news['description']}")
            output.append(f"   链接: {news['link']}")
            output.append("")
        output.append("")

# Print result
result = "\n".join(output)
print(result)