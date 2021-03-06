get_val_by_pos_hand_set = set([
    '哪些楼盘平均售价低于2万或者容积率小于2',
    '容积率小于2或者楼盘平均下来卖价低于2万块每平的是哪些楼盘',
    '想咨询一下5月份上海有哪些楼盘的均价在20000/㎡以上同时月环比涨幅也是大于5的？',
    '我想查询一下本周成交面积超过1.5的城市或者是上周成交面积超过1的城市也行',
    '19年第1周有哪些电影周票房超过10000000并且票房占比高于10%的？',
    '你好，平均票价低于10美元，而且可支配收入低于4万美元，那么平均票价与可支配收入的比值你知道吗',
    '有哪些证券B的商誉B大于0.1亿元而且净资产大于0.1的？',
    '哪些电影单周票房超过了1亿或者累计票房小于1亿',
    '有几个国家电影平均票价低于10美元的，并且啊可支配收入小于3万的呀',
    '你好啊，你帮我看看现在有多少个国家电影平均票价小于10美元，可支配收入还小于3万的呀',
    '数数看电影平均票价低于10美元的，并且可支配收入小于3万的有几个国家啊',
    '住房3个月移动日均成交量高于30000平方米，那可以销售的面积和两个周期内的变化比情况怎样',
    '我就想知道环比和销售面积啊，它3个月移动日均成交量高于30000平方米的',
    '在12年这一个星期成交的面积超过5而且环比也在5以上的城市都有哪些？',
    '近年年房地产销售面积预测，一线城市小于4000万平或者二线城市小于400000000平的是哪几年',
    '哪几年的房地产销售面积预测在一线城市小于4000万平或者二线城市小于400000000平',
    '你知道哪些驾校排名前3的吗',
    '合格率排名前3的驾校叫啥名啊',
    '那个12月29号省级卫视晚间综艺节目收视率排名前3的都是哪些综艺，在哪个台播的',
    '17年度中国网络作家富豪榜排名前3的是哪些作家啊，他们版税多少啊',
    '你好啊，我想问问啊就是17年版税收入排名前3的都是哪些作家啊，他们的版税分别有多少啊',
    '呃你知道哪些作家在17年的中国网络作家富豪榜中名列前3的呀，那他们具体版税又有多少呢',
    '新房成交环比上周大于20%而且累计同比也大于20%的上周平均成交量为多少',
    '哪些城市的成交面积在本周是低于2的',
    '本周的一个住房成交情况怎么样啊，低于2的多不多，分布在哪些城市',
    '股价大于4块五而且总市值大于450的公司是哪个',
    '每套面积都大于100平，还有平均售价小于2万的是北京哪些楼盘啊，都是北京哪的呀',
    '诶，那个平均成交价低于2万，平均每套面积还大于100平的是哪些楼盘啊，在北京哪的啊',
    '你帮我看看北京哪里有楼盘成交均价低于2万，平均每套面积大于100平的呀，这些楼盘都叫啥名啊',
    '19年1月14号到20号票房排名前3的都是哪些影片啊，上映有多少天啊',
    '那个哪些影片在19年1月14号到20号期间票房排名前3的呀，都上映多久了呀',
    '请跟我说一下这个星期收盘的价格高于10块钱，这周的涨跌幅也在0.05以上的证券名，谢谢。',
    '请问近4周周均成交环比大于3并且同比大于30的重点城市有哪些呀？',
    '能不能查询哪一年商品房开发投资总额超过600亿而且施工面积的投资额大于5万块1平方米',
    '淡水河谷公司铁矿石产量高于3亿吨和必和必拓公司的高于1.7亿吨的每年总的产量是多少',
    '电视剧收视率排名前3的都是什么剧啊，是在哪个台播的呀',
    '诶，你知道哪个台播的电视剧收视率排名前3的吗，都是啥剧啊',
    '我问你啊那个收视率排在前3名的都是哪个台播的什么剧啊',
    '哪些城市的去化时间在本周超过了1年或者在上周超过了1年',
    '那个京沪高铁有哪几年是平均每日客流量都达到20万人以上的，或者净利润高于50亿的呀',
    '我想问一下啊就是京沪高铁日均客流量超过20万人次的，或者是净利润高达50亿的都是哪些年啊',
    '2018年12月最后一周国产动漫播放次量排名前3的都是什么国漫啊，在哪些平台播放啊',
    '诶，你知道18年12月24到30的时候国漫播放量排名前3的国漫都是在哪播放的吗，都是什么动漫啊',
    '呃那个哪些国漫在18年第52周国漫播放量排名前3的呀，在哪播的呀',
    '上周末库存去化周期超过1年或者库存去化周期环比超过08的城市有多少',
    '哪些城市能达到库存去化周期环比超过0.8或者上周末库存去化周期超过1年的',
    '11年每股盈余高于1毛，预计12年的每股盈余也高于1毛的地产公司有哪些？',
    '你知道什么公司一一年每股收益超过0.1元，估计12年的每股收益也会超过0.1元的吗？',
    '麻烦帮我查一下那些2011年每股税后利润达到1角以上，2012年的每股税后利润估值也达到1角以上的公司名吧',
    '流通A股占总股本比例低于60%或者周成交小于1亿股的股票周换手率是多少',
    '你知道像流通A股占总股本比例低于60%或者周成交小于1亿股这样的股票周换手率为多少吗',
    '你知道股票的周换手率是多少吗，它的流通A股占总股本比例低于60%或者周成交不到1亿股',
    '哪些城市的土地成交面积2011同期低于5000万平或2012年至今不足5000万平',
    '请问有没有库存在5万以上的城市而且这周销量又超过了1000的城市',
    '19年1月14号到18号涨幅排名前3的都是哪些公司啊，股价多少啊',
    '那个19年1月14号到18号哪些公司排在涨幅前3的呀，这些公司股价多少来着',
    '今年第1周电视综艺播放量排名前3的都是哪些电视综艺啊，播放量多少来着呀',
    '你知道那个今年第1周综艺播放量排前3的播放量分别是多少啊，都是什么综艺节目的呀',
    '哪些城市的上周成交面积超过了11或者本周成交面积超过5的',
    '已经知道城市库存去化周期同比地域4并且库存去化周期环比也不足与1，那么它较上年去化周期怎么样',
    '有没有最新股价超过5块一股而且持股数量超过5000000股的模拟组合啊',
    '2010年H1不足1年的城市去年同期的去化时间最高值为多少或者2010年H2一线城市去化时间不足1年的最大值',
    '想要知道这周成交超过30000平方米的城市中有哪个在上周也超过30000平方米',
    '想要问一下2012年6月19日有没有哪个城市上周住宅用地楼面价超过400块一平而且成交面积超过400000平',
    '本周成交面积低于9或者环比超过-63.05的城市，在上周成交了多少面积',
    '啊，那个上周的成交面积多少啊，你帮我着重查一下环比数超过-63.05或者本周成交面积低于9的城市哈',
    '3月楼盘套数超过100而且均价超过2万的楼盘有哪些？',
    '请你跟我说说3月楼盘套数达到100套以上且均价超过2万的楼盘有哪些？',
    '我想知道你们月楼盘套数高于100套以上而且均价达到2万以上的楼盘有哪些呢？',
    '你知道容积率高于1，平均每套还大于100平以及成交均价高于8千的天津新盘有多少个吗',
    '力拓的全球铁矿石产量低于3亿吨或者FMG高于1亿吨的年份是哪几年',
    '在哪几个年份里，FMG的铁矿石产量高于了1亿吨或者力拓是低于3亿吨的',
    '2012E每股收益大于5毛或者2013E每股收益大于5毛的股票2012E本益比是多少',
    '19年第7周电视综艺播放量排名前2总共有多大播放量',
    '诶，那个综艺类型的节目的播放数量在19年第7周的时候排名在前2的加起来播放数有多大啊',
    '你帮我算算那个19年2月18到2月24的电视的综艺节目排在前2名的播放数量一共是多少啊',
    '哪个城市物业面积超过50万方租赁收入超过50000000',
    '租赁收入在5千万以上物业面积超过50万方的城市是哪个',
    '平均价格高于10美元的，或者是可支配收入大于3万美元都是哪些国家啊，总票房多少啊',
    '你好啊，麻烦你帮我查一下那个有哪些国家电影平均票价大于10美元，或者可支配收入高于3万美元的呀，这些国家票房多少啊',
    '最新市值低于10000000并且市值比重不足10个百分点的股，最新股价为多少',
    '您好，我问一下，最新的股价出来了吗，能不能告诉我新市值低于10000000而且市值比重不足10个百分点的股票股价啊，谢谢',
    '你好啊，中国IOS游戏畅销排行榜中排名前3的都是什么游戏啊，是哪家公司研发的呀',
    '你知道那个中国IOS游戏畅销排行榜前3的都是哪些公司研发的吗，还有都是哪些游戏啊',
    '网络剧全网热度排名前3的都是哪些剧，当天最高热度为多少啊',
    '你帮我看一下啊网络剧全网热度排名前3的当天热度最高为多少啊，都是什么剧啊',
    '我想知道那个网络剧全网热度排名前3的都是什么剧，那这些网剧当天热度最高为多少啊',
    '开盘大于200套或者已签约套数超过200套的是什么项目',
    '哪个项目开盘大于200套或者已签约套数超过200套的',
    '有没有开盘大于200套或者已签约套数超过200套的项目，项目叫什么',
    '有几支港股的总市值是低于20亿港元或者周成交量小于1亿港元的',
    '总市值低于20亿港元或者周成交量小于1亿港元的港股有几支',
    '你知道总市值低于20亿港元或者周成交量小于1亿港元的证券简称有多少吗',
    '19年第四个星期有几部电影的票房达到5000000以上，其票房的占比也在5%以上的呀？',
    '1月12号省级卫视晚间综艺节目收视率排名前3的市场份额一共有多少啊',
    '诶，你帮我算一算那个1月12号省级卫视晚间综艺节目收视率排名前3的那个市场份额加起来有多少啊',
    '全球半导体销售额2017年大于300亿美元而且2018年也大于300亿美元的地区有哪几个',
    '想要了解一下PE-TTM10高1同时PB也在1以上的汽车电子板块股票都有哪些？',
    '单周票房低于1亿而且累计票房低于9000亿的电影最多上映了多少天',
    '这电影最多上映几天啊，它的单周的电影票房低于1亿而且累计票房小于9000亿，这么低',
    '小姐姐，请问单周票房低于1亿而且累计票房小于9000亿的电影，最多可以上映几天啊',
    '18E每股收益大于5角而且19E每股收益也大于5角的股票股价最小为多少',
    '我很好奇在18E和19E每股收益都超过5毛的所有股票中，他们的股价中最低值是多少',
    '我想找出有哪些正极企业总投资是大于10亿元的货扩产的产能大于1万吨的。',
    '总投资的金额是超过10亿的正极企业有哪些或者扩充产能超过1万吨的企业',
    'A股房地产股的最新市值是多少，它的最新股价是大于10块而且本周涨幅前10大于10%的',
    '我可以通过A股房地产股最新股价大于10块而且本周涨幅前10大于10%查询它的最新市值吗',
    '最新市值大于66亿而且最新股价大于6块6的地产板块的证券代码是什么',
    '请问一下有没有地产板块的公司最新的市值超过66亿还有最新的股票价格超过6块6，有的话对应的证券代码是什么',
    '那个19年第2周电视剧和网剧总播放量排名前3的都是哪些剧，播放量如何',
    '你帮我看一下啊那个哪些剧在19年第2周电视剧和网剧总播放量排名前3的呀，多少播放量啊',
    '你知道那些19年第2周电视剧和网剧总播放量排名前3的分别是多少播放量吗，还有啊前3的都是什么剧啊',
    '18年最后一周畅销书排行榜排行前3的有哪些畅销书啊',
    '我想知道就是18年第52周排在前3的都是哪些虚构和非虚构的书啊',
    '诶，哪些书在2018年12月24日到12月30的时候排在畅销书排行榜前3的呀',
    '这期大于200000平的城市里面有没有上期也大于200000平的城市',
    '哪些书的总字数超过了200000字，而且撰写字数也是超过200000字的',
    '诶你知道什么单位的岗位是要招2人或者2人以上的吗，这些单位你知道它们对学历有没有什么要求吗',
    '合格率排名前3的驾校叫啥名啊',
    '你知道哪些驾校排名前3的吗',
    '诶你帮我看看哪些词频率大于0.1，出现次数还高于8万的呀',
    '我想知道排名在世界前3的是什么学校'
])