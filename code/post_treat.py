import json 
import numpy as np 
import sys 
import os 
import re 


regex_tail = r'([十|百|千|万|亿]+)' 
regex_unit_second_level =  r'([平|元|吨|件|支|股])' 
regex_num = r'([0|1|2|3|4|5|6|7|8|9]+)'
format_oper_dict = {'十': 10, '千': 1000, '万': 10000, '万亿': 1000000000000, '亿': 100000000, 
                  '百万': 1000000, '百': 100, '十万': 100000, '千万': 10000000}

title_unit_set = set([
     '亿元', '亿美元', '万平方米', '万平', '千桶','万人','万平米','亿股', '万吨','万亿件','元/平米',
    '亿吨','亿件', '万支', '亿人民币', '亿', '万人次', '百万美元', '百万元'])

unit_regexp = "亿元|亿美元|万平方米|万平|千桶|万人|万平米|亿股|万吨|万亿件|元/平米|亿吨|亿件|万支|亿人民币|亿|万人次|百万美元|百万元|万亿"

unit_dict = {'元': set(['亿元', '百万元', '亿', '元/平米', '百万美元', '万亿', '万']),
             '件': set(['亿件', '万亿件', '百万件', '千万件']),
             '支': set(['亿支']),
             '人': set(['万人次']),
             '美元': set(['百万美元']),
             '平': set(['万平方米','万平米', '万平']),
             '吨':set(['亿吨', '万吨', '千吨', '十吨', '百吨']),
             '桶':set(['亿桶']),
             '股': set(['亿股'])
           }

           
def smooth_numeric(start_idx, end_idx, question):
    """
    平滑处理数字缺失
    有的数字只标注了一部分,比如 问题中有数字100,但是标记成了 40 
    通过该函数,可以补充start_idx和end_idx的位置,进而准确标注
    """
    # question = ' ' + question
    match_val = question[start_idx: end_idx]
    if re.findall('[^\d\.]', match_val): # 找到非数字
        return start_idx, end_idx, match_val
    
    # while start_idx >= 0 and  question[start_idx].isnumeric():
    while start_idx >= 0 and not re.findall('[^\d\.]', question[start_idx]):
        start_idx -= 1 

    while end_idx  <= len(question) - 1 and not  re.findall('[^\d\.]', question[end_idx]):
        end_idx += 1 
    return start_idx + 1,  end_idx,  question[start_idx+1: end_idx]

# ret = smooth_numeric(4, 7, '今年收入500万')
# # ret = smooth_numeric(10, 11, '而且啊成交量大于10000万手的有哪些股啊')
# # ret = smooth_numeric(2, 4, '长沙2011年平均每天成交量是3.17，那么近一周的成交量是多少')
# print(ret)
# # sys.exit(0)

def get_append_unit(start_idx, end_idx, question):
    """
    获取数字后的单位,
    标注出来的时候15, 问题当中可能是15万, 所以需要把这个单位搞出来,,搞出来的意义是为了后续的单位统一
    """
    if re.findall('[^\d\.]', question[start_idx: end_idx]): # 找到非数字 
        return '', '' 
    start_idx, end_idx, val = smooth_numeric(start_idx, end_idx, question)
    unit_first = ''
    unit_second = ''
    # 获取 百十千万
    while end_idx  <= len(question) - 1 and  re.findall(regex_tail, question[end_idx]):
        unit_first += question[end_idx]
        end_idx += 1 

    # 获取二级单位 平/元
    while end_idx  <= len(question) - 1 and  re.findall(regex_unit_second_level, question[end_idx]):
        unit_second += question[end_idx]
        end_idx += 1 

    return unit_first, unit_second


def get_unit_from_title(title):
    """
     '010年至今土地市场成交情况（万亿、万平）'
    """

    # unit_regex = "(亿元).*?亿美元', '万平方米', '万平', '千桶','万人','万平米','亿股', '万吨','万亿件','元/平米',
    # '亿吨','亿件', '万支', '亿人民币', '亿', '万人次', '百万美元', '百万元'"
    unit_list = re.findall(r'（(.*?)）', title)

    if not unit_list: 
        unit_list = re.findall(r'\((.*?)\)', title)
        if not unit_list:  return unit_list
    
    title_unit = set([])
    print(unit_list)
    for unit in unit_list:
        print('unit is ' + unit)
        unit_in_title =  re.findall(unit_regexp, unit)

        if not unit_in_title: continue 
        else: title_unit = set(unit_in_title)
    return title_unit
    

print(get_unit_from_title('50 表2012年第23周（2012.5.28-2012.6.3） 二手成交数据（万平米）'))

# sys.exit(0)

def get_unit_set_from_title():
    """
    从标题中找到所有可选单位
    """
    unit_list = re.findall(r'（(.*?)）', title)
    if not unit_list: return None 
    unit_ret = []
    for unit in unit_list:
        if re.findall(regex_tail, unit):
            unit_ret.append(unit)
    return ' '.join(unit_ret)




ret = get_unit_from_title('08 表8:16个重点城市住宅土地供应对比表(单位:万平米) ')
print(ret)
# sys.exit(0)


def number_trans(num, col_header, title, format_of_number=None, format_desc=None):
    """
      将数字转换为和表头单位一致
      input: num 
             col_format: 列的格式(百万，千万等，先适配简单数字)
             titile: 图表标题
             format_of_number: 当前数字后面的计量词(百十千万等)
             format_descL 描述数字的，比如"件","元"等

       同时还需要数字补齐等功能
    """
    ori_num = num 
    col_header = col_header.replace('km', '千米')
    col_header = col_header.replace('KM', '千米')
    col_header = col_header.replace('kg', '千克')
    # 解析出header中的单位, 另外如果header里面没有单位，需要到title里面去找
    col_format = None 
    if re.findall(regex_tail, col_header) and '百分比' not in col_header: 
        col_format =  re.findall(regex_tail, col_header)
        col_format = col_format[0] # col_format为header中col的量词格式
    else: # 从标题里面找单位
        # 单位不出现在列名称里面，就可能出现在标题里面
        # title里面单位的格式还是很单一的，比如万， 万平 等，
        unit_from_title =  get_unit_from_title(title) # set 


    # 判断传入的是否是纯数字，如果是不是纯数字，而是后面带着单位的，那么需要修改下
    if format_of_number is not None: 
        num = num * format_oper_dict.get(format_of_number)

    # 数字转 对应的单位的值
    # 首先考虑列名称中的单位
    if  col_format:  # 如果header中包含单位
        if num < format_oper_dict.get(col_format, 1): return num 
        num_ret = int(int(num) / format_oper_dict.get(col_format, 1))
        
        return num_ret
    else: # 如果header中没有单位,那么考虑标题中的单位 
        unit_in_title_set =  get_unit_from_title(title)
        if unit_in_title_set is None or len(unit_in_title_set) == 0: return num  ### new add 
        
        if  format_desc is None: # 如果数字后面没有 支|个|吨|平  这些东西
            #　只能拿出和钱相关的，　有其他单位，比如“支”等不行
            unit_in_title_set = set([unit for unit in unit_in_title_set if not re.findall(r'([支|个|吨|平]+)', unit) ])
            unit = unit_in_title_set
            if len(unit)  == 0: return num 
        else: 
            if unit_dict.get(format_desc, None) is None: 
                unit = unit_in_title_set
            else:
                unit = unit_in_title_set & unit_dict.get(format_desc, None)

        # 从unit中获取到量词
        # 先只取一个吧
        #
        print(unit)
        unit  = unit.pop()

        # 匹配出计量词
        unit_in_strs =  re.findall(regex_tail, unit)
        if not unit_in_strs: return ori_num 
        title_unit_format = unit_in_strs[0]


        ret = int(int(num) / format_oper_dict.get(title_unit_format, 1))
        if  ret == 0: return ori_num 
        else: return ret 
    return num 


if __name__ == "__main__":
    
    assert  number_trans(2000000000, '综合票房', '2018综合票房情况（亿）' ,format_of_number=None, format_desc='元') == 20 


    question = '哪几年的商品房新开工面积超过了90000万平或者竣工面积高于50000万平的'
    assert number_trans(90000,'商品房新开工面积','63 图表 ：2006年至2012年房地产投资模型（万平方米）',format_of_number='万', format_desc='平') == 90000
            
    question = '商品房竣工面积或者新开工面积分别超过5亿平和9亿平的是哪几年发生的事'
    assert number_trans(5,'商品房新开工面积','63 图表 ：2006年至2012年房地产投资模型（万平方米）',format_of_number='亿', format_desc='平') == 50000


    assert number_trans(70,'上周成交量','图17、重点类型城市二手房成交数据（万平米）',format_of_number='万', format_desc='平') == 70

    assert number_trans(40,'总市值（亿港元）','表 3：传媒互联网行业港股情况 传媒互联网行业港股情况',format_of_number='亿', format_desc=None) == 40 

    assert number_trans(200000,'本周','101表1:一线城市一手房两周成交（单位：万平方米） ',format_of_number=None, format_desc='平') == 20 

    assert number_trans(1500,'2010年成交面积','52 表1：2010年至今土地市场成交情况（万亿、万平） ',format_of_number=None, format_desc=None) == 1500 

    assert number_trans(100,'最新市值（亿港币）','18 表3：内房股上周股价涨幅前十表现 ',format_of_number='亿', format_desc=None) == 100 
    # print(get_unit_from_title('18 表3：内房股上周股价涨幅前十表现 '))

    # 下面这种情况， 就是title中无单位，，header中也没有单位，，但是值后面有单位。。这个时候转换有问题
    # assert number_trans(5,'库存（套）','140表 1：最近一周一线城市新盘成交动态 ',format_of_number='万', format_desc=None) == 50000

    # assert number_trans(55,'PE2012E','62 盈利预测和估值2',format_of_number=None, format_desc=None) == 55
    

    # assert number_trans(10,'归母净利润(亿元)','58表2：高速企业经营性现金流良好 ',format_of_number='亿', format_desc=None) == 10 

    # assert number_trans(180000,'规划建筑面积(万㎡)','表3：300城市土地出让情况预测 ',format_of_number='万', format_desc='平') == 180000

    # assert number_trans(5,'最新收盘价','图表81：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) == 5

    # assert number_trans(1,'原值（元）','',format_of_number='万', format_desc=None) == 10000 

    # assert number_trans(300,'公里数（km）','表67. 预计2018年新开通高铁线路15条线共计3559公里  ',format_of_number='千', format_desc=None) == 300 

    
    # assert number_trans(4,'5月均价(元/㎡)','49 表 ：2012年5月上海市部分环比涨价楼盘 ',format_of_number='万', format_desc=None) == 40000

    # assert number_trans(7,'月环比涨幅','49 表 ：2012年5月上海市部分环比涨价楼盘 ',format_of_number=None, format_desc=None) == 7 

    assert number_trans(20,'最新市价（百万元）','63 表4：2012年6月10日银河地产模拟组合 ',format_of_number=None, format_desc=None) == 20



    assert number_trans(90000,'商品房新开工面积','63 图表 ：2006年至2012年房地产投资模型（万平方米）',format_of_number='万', format_desc='平') ==90000
    assert number_trans(50000,'商品房竣工面积增速','63 图表 ：2006年至2012年房地产投资模型（万平方米）',format_of_number='万', format_desc='平') ==50000
    assert number_trans(5,'商品房新开工面积','63 图表 ：2006年至2012年房地产投资模型（万平方米）',format_of_number='亿', format_desc='平') ==50000
    assert number_trans(5,'商品房竣工面积增速','63 图表 ：2006年至2012年房地产投资模型（万平方米）',format_of_number='亿', format_desc='平') ==50000
    assert number_trans(5,'商品房竣工面积','63 图表 ：2006年至2012年房地产投资模型（万平方米）',format_of_number='亿', format_desc='平') ==50000
    assert number_trans(9,'商品房新开工面积','63 图表 ：2006年至2012年房地产投资模型（万平方米）',format_of_number='亿', format_desc='平') ==90000
    assert number_trans(70,'上周成交量','图17、重点类型城市二手房成交数据（万平米）',format_of_number='万', format_desc='平') ==70
    assert number_trans(100,'当月累计成交量','图17、重点类型城市二手房成交数据（万平米）',format_of_number='万', format_desc='平') ==100
    assert number_trans(70,'上周成交量','图17、重点类型城市二手房成交数据（万平米）',format_of_number='万', format_desc='平') ==70
    assert number_trans(100,'当月累计成交量','图17、重点类型城市二手房成交数据（万平米）',format_of_number='万', format_desc='平') ==100
    assert number_trans(70,'上周成交量','图17、重点类型城市二手房成交数据（万平米）',format_of_number='万', format_desc='平') ==70
    assert number_trans(100,'当月累计成交量','图17、重点类型城市二手房成交数据（万平米）',format_of_number='万', format_desc='平') ==100
    assert number_trans(40,'总市值（亿港元）','表 3：传媒互联网行业港股情况 传媒互联网行业港股情况',format_of_number='亿', format_desc=None) ==40
    assert number_trans(40,'总市值（亿港元）','表 3：传媒互联网行业港股情况 传媒互联网行业港股情况',format_of_number='亿', format_desc=None) ==40
    assert number_trans(40,'总市值（亿港元）','表 3：传媒互联网行业港股情况 传媒互联网行业港股情况',format_of_number='亿', format_desc=None) ==40
    assert number_trans(200000,'本周','101表1:一线城市一手房两周成交（单位：万平方米） ',format_of_number=None, format_desc='平') ==20
    assert number_trans(200000,'本周','101表1:一线城市一手房两周成交（单位：万平方米） ',format_of_number=None, format_desc='平') ==20
    assert number_trans(150000,'上周','101表1:一线城市一手房两周成交（单位：万平方米） ',format_of_number=None, format_desc='平') ==15
    assert number_trans(150000,'上周','101表1:一线城市一手房两周成交（单位：万平方米） ',format_of_number=None, format_desc='平') ==15
    assert number_trans(200000,'上周','101表1:一线城市一手房两周成交（单位：万平方米） ',format_of_number=None, format_desc='平') ==20
    assert number_trans(1500,'2010年成交面积','52 表1：2010年至今土地市场成交情况（万亿、万平） ',format_of_number=None, format_desc=None) ==1500
    assert number_trans(1500,'2010年成交面积','52 表1：2010年至今土地市场成交情况（万亿、万平） ',format_of_number=None, format_desc=None) ==1500
    assert number_trans(1500,'2010年成交面积','52 表1：2010年至今土地市场成交情况（万亿、万平） ',format_of_number=None, format_desc=None) ==1500
    assert number_trans(100,'最新市值（亿港币）','18 表3：内房股上周股价涨幅前十表现 ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'最新市值（亿港币）','18 表3：内房股上周股价涨幅前十表现 ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'最新市值（亿港币）','18 表3：内房股上周股价涨幅前十表现 ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(500,'投资总额（亿元）','表67. 预计2018年新开通高铁线路15条线共计3559公里  ',format_of_number='亿', format_desc='元') ==500
    assert number_trans(500,'投资总额（亿元）','表67. 预计2018年新开通高铁线路15条线共计3559公里  ',format_of_number='亿', format_desc='元') ==500
    assert number_trans(500,'投资总额（亿元）','表67. 预计2018年新开通高铁线路15条线共计3559公里  ',format_of_number='亿', format_desc='元') ==500
    assert number_trans(1000,'库存（万平米）','140表 1：最近一周一线城市新盘成交动态 ',format_of_number='万', format_desc='平') ==1000
    assert number_trans(1000,'库存（万平米）','140表 1：最近一周一线城市新盘成交动态 ',format_of_number='万', format_desc='平') ==1000
    assert number_trans(5,'净利润','95表2：国内6家廉航公司财务、飞机、基地等情况（亿元） ',format_of_number='亿', format_desc=None) ==5
    assert number_trans(5,'净利润','95表2：国内6家廉航公司财务、飞机、基地等情况（亿元） ',format_of_number='亿', format_desc=None) ==5
    assert number_trans(5,'净利润','95表2：国内6家廉航公司财务、飞机、基地等情况（亿元） ',format_of_number='亿', format_desc=None) ==5
    assert number_trans(54,'业务量(亿件)','135表5：2018年1-11月快递上市公司累计业务数据 ',format_of_number='亿', format_desc=None) ==54
    assert number_trans(54,'业务量(亿件)','135表5：2018年1-11月快递上市公司累计业务数据 ',format_of_number='亿', format_desc=None) ==54
    assert number_trans(54,'业务量(亿件)','135表5：2018年1-11月快递上市公司累计业务数据 ',format_of_number='亿', format_desc=None) ==54
    assert number_trans(100,'总市值','附表14：2012年06月11日地产+X公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(20,'总股本','附表14：2012年06月11日地产+X公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc='股') ==20
    assert number_trans(20,'总股本','附表14：2012年06月11日地产+X公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc='股') ==20
    assert number_trans(100,'总市值','附表14：2012年06月11日地产+X公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'总市值','附表14：2012年06月11日地产+X公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(20,'总股本','附表14：2012年06月11日地产+X公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc='股') ==20
    assert number_trans(1000,'本周票房（万元）','图表9: 周电影票房排行（12月10日~12月16日）',format_of_number='万', format_desc='元') ==1000
    assert number_trans(20000,'累计票房（万元）','图表9: 周电影票房排行（12月10日~12月16日）',format_of_number='万', format_desc='元') ==20000
    assert number_trans(10000000,'本周票房（万元）','图表9: 周电影票房排行（12月10日~12月16日）',format_of_number=None, format_desc=None) ==1000
    assert number_trans(20000,'累计票房（万元）','图表9: 周电影票房排行（12月10日~12月16日）',format_of_number='万', format_desc='元') ==20000
    assert number_trans(1000,'本周票房（万元）','图表9: 周电影票房排行（12月10日~12月16日）',format_of_number='万', format_desc='元') ==1000
    assert number_trans(20000,'累计票房（万元）','图表9: 周电影票房排行（12月10日~12月16日）',format_of_number='万', format_desc='元') ==20000
    assert number_trans(500,'周票房（万）','表7：2019年第2周（2019.1.14 - 2019.1.20）影投票房排名TOP10',format_of_number='万', format_desc=None) ==500
    assert number_trans(20,'观影人次（万）','表7：2019年第2周（2019.1.14 - 2019.1.20）影投票房排名TOP10',format_of_number='万', format_desc=None) ==20
    assert number_trans(20,'观影人次（万）','表7：2019年第2周（2019.1.14 - 2019.1.20）影投票房排名TOP10',format_of_number='万', format_desc=None) ==20
    assert number_trans(500,'周票房（万）','表7：2019年第2周（2019.1.14 - 2019.1.20）影投票房排名TOP10',format_of_number='万', format_desc=None) ==500
    assert number_trans(500,'周票房（万）','表7：2019年第2周（2019.1.14 - 2019.1.20）影投票房排名TOP10',format_of_number='万', format_desc=None) ==500
    assert number_trans(20,'观影人次（万）','表7：2019年第2周（2019.1.14 - 2019.1.20）影投票房排名TOP10',format_of_number='万', format_desc=None) ==20
    assert number_trans(50,'最新市值（亿元）','03 表 1：地产板块一周跌幅前列公司情况',format_of_number='亿', format_desc=None) ==50
    assert number_trans(50,'最新市值（亿元）','03 表 1：地产板块一周跌幅前列公司情况',format_of_number='亿', format_desc=None) ==50
    assert number_trans(50,'最新市值（亿元）','03 表 1：地产板块一周跌幅前列公司情况',format_of_number='亿', format_desc=None) ==50
    assert number_trans(0,'2018Q3营收同比增速（%）','表 11  A股高速公路行业重点跟踪公司业绩增速与估值（市值单位：亿人民币元；截止 2019.1.11） ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'2017Y营收同比增速（%）','表 11  A股高速公路行业重点跟踪公司业绩增速与估值（市值单位：亿人民币元；截止 2019.1.11） ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'2017Y营收同比增速（%）','表 11  A股高速公路行业重点跟踪公司业绩增速与估值（市值单位：亿人民币元；截止 2019.1.11） ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'2018Q3营收同比增速（%）','表 11  A股高速公路行业重点跟踪公司业绩增速与估值（市值单位：亿人民币元；截止 2019.1.11） ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'2018Q3营收同比增速（%）','表 11  A股高速公路行业重点跟踪公司业绩增速与估值（市值单位：亿人民币元；截止 2019.1.11） ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'2017Y营收同比增速（%）','表 11  A股高速公路行业重点跟踪公司业绩增速与估值（市值单位：亿人民币元；截止 2019.1.11） ',format_of_number=None, format_desc=None) ==0
    assert number_trans(10,'本周','表10:四城市一手房成交对比（单位：万平方米）',format_of_number='万', format_desc='平') ==10
    assert number_trans(10,'本周','表10:四城市一手房成交对比（单位：万平方米）',format_of_number='万', format_desc='平') ==10
    assert number_trans(100,'总市值','132附表15：2012年06月11日商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(30,'总股本','132附表15：2012年06月11日商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc='股') ==30
    assert number_trans(100,'总市值','132附表15：2012年06月11日商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(30,'总股本','132附表15：2012年06月11日商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc='股') ==30
    assert number_trans(100,'总市值','132附表15：2012年06月11日商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(30,'总股本','132附表15：2012年06月11日商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc='股') ==30
    assert number_trans(10,'11EPE','42 附表1：地产行业一线重点公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'10APE','42 附表1：地产行业一线重点公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'10APE','42 附表1：地产行业一线重点公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(3333,'2010成交面积','58表7:2012年三线城市土地成交面积(2011 年初至今)（万平）',format_of_number='万', format_desc='平') ==3333
    assert number_trans(3333,'2010成交面积','58表7:2012年三线城市土地成交面积(2011 年初至今)（万平）',format_of_number='万', format_desc='平') ==3333
    assert number_trans(3333,'2010成交面积','58表7:2012年三线城市土地成交面积(2011 年初至今)（万平）',format_of_number='万', format_desc='平') ==3333
    assert number_trans(20,'总股本(亿股)','04 表4重点覆盖公司估值表 ',format_of_number='亿', format_desc='股') ==20
    assert number_trans(20,'总股本(亿股)','04 表4重点覆盖公司估值表 ',format_of_number='亿', format_desc='股') ==20
    assert number_trans(20,'总股本(亿股)','04 表4重点覆盖公司估值表 ',format_of_number='亿', format_desc='股') ==20
    assert number_trans(20,'总股本(亿股)','04 表4重点覆盖公司估值表 ',format_of_number='亿', format_desc='股') ==20
    assert number_trans(5,'总投资(亿元）','表：主要正极厂商高镍产能单位投资情况 ',format_of_number='亿', format_desc=None) ==5
    assert number_trans(5,'总投资(亿元）','表：主要正极厂商高镍产能单位投资情况 ',format_of_number='亿', format_desc=None) ==5
    assert number_trans(5,'总投资(亿元）','表：主要正极厂商高镍产能单位投资情况 ',format_of_number='亿', format_desc=None) ==5
    assert number_trans(100000,'本周均成交面积','表 4：各城市周均成交面积与同比（万平） ',format_of_number=None, format_desc='平') ==10
    assert number_trans(100000,'本周均成交面积','表 4：各城市周均成交面积与同比（万平） ',format_of_number=None, format_desc='平') ==10
    assert number_trans(100000,'本周均成交面积','表 4：各城市周均成交面积与同比（万平） ',format_of_number=None, format_desc='平') ==10
    assert number_trans(100,'总市值（亿元）','06 表 5：住宅开发重点跟踪公司一览 ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'总市值（亿元）','06 表 5：住宅开发重点跟踪公司一览 ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'总市值（亿元）','06 表 5：住宅开发重点跟踪公司一览 ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(5,'本周均成交面积','139表 5：各城市周均成交面积与同比续（万平） ',format_of_number='万', format_desc='平') ==5
    assert number_trans(5,'上周均成交面积','139表 5：各城市周均成交面积与同比续（万平） ',format_of_number='万', format_desc='平') ==5
    assert number_trans(5,'本周均成交面积','139表 5：各城市周均成交面积与同比续（万平） ',format_of_number='万', format_desc='平') ==5
    assert number_trans(5,'上周均成交面积','139表 5：各城市周均成交面积与同比续（万平） ',format_of_number='万', format_desc='平') ==5
    assert number_trans(5,'本周均成交面积','139表 5：各城市周均成交面积与同比续（万平） ',format_of_number='万', format_desc='平') ==5
    assert number_trans(5,'上周均成交面积','139表 5：各城市周均成交面积与同比续（万平） ',format_of_number='万', format_desc='平') ==5
    assert number_trans(10,'快递业务营收(亿元)','表4：2018年10月快递上市公司业务数据 ',format_of_number='亿', format_desc=None) ==10
    assert number_trans(10,'快递业务营收(亿元)','表4：2018年10月快递上市公司业务数据 ',format_of_number='亿', format_desc=None) ==10
    assert number_trans(10,'快递业务营收(亿元)','表4：2018年10月快递上市公司业务数据 ',format_of_number='亿', format_desc=None) ==10
    assert number_trans(100,'总资产（亿元）','表 27：2018Q3出版发行公司货币资金分析',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'净资产（亿元）','表 27：2018Q3出版发行公司货币资金分析',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'总资产（亿元）','表 27：2018Q3出版发行公司货币资金分析',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'净资产（亿元）','表 27：2018Q3出版发行公司货币资金分析',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'总资产（亿元）','表 27：2018Q3出版发行公司货币资金分析',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'净资产（亿元）','表 27：2018Q3出版发行公司货币资金分析',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'总市值','40 表 2：房地产行业覆盖公司基本面和股票表现情况（元,亿元,万平） ',format_of_number=None, format_desc=None) ==100
    assert number_trans(10,'每股净资产','40 表 2：房地产行业覆盖公司基本面和股票表现情况（元,亿元,万平） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(100,'总市值','40 表 2：房地产行业覆盖公司基本面和股票表现情况（元,亿元,万平） ',format_of_number=None, format_desc=None) ==100
    assert number_trans(10,'每股净资产','40 表 2：房地产行业覆盖公司基本面和股票表现情况（元,亿元,万平） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(100,'总市值','40 表 2：房地产行业覆盖公司基本面和股票表现情况（元,亿元,万平） ',format_of_number=None, format_desc=None) ==100
    assert number_trans(10,'每股净资产','40 表 2：房地产行业覆盖公司基本面和股票表现情况（元,亿元,万平） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(6,'单位投资（亿元/万吨）','表：主要正极厂商高镍产能单位投资情况 ',format_of_number='亿', format_desc=None) ==6
    assert number_trans(6,'单位投资（亿元/万吨）','表：主要正极厂商高镍产能单位投资情况 ',format_of_number='亿', format_desc=None) ==6
    assert number_trans(6,'单位投资（亿元/万吨）','表：主要正极厂商高镍产能单位投资情况 ',format_of_number='亿', format_desc=None) ==6
    assert number_trans(20,'Jun','92 表18：福州住宅期房2007-2012年1月各月成交面积（万平）           ',format_of_number='万', format_desc='平') ==20
    assert number_trans(20,'Jan','92 表18：福州住宅期房2007-2012年1月各月成交面积（万平）           ',format_of_number='万', format_desc='平') ==20
    assert number_trans(20,'Jun','92 表18：福州住宅期房2007-2012年1月各月成交面积（万平）           ',format_of_number='万', format_desc='平') ==20
    assert number_trans(5,'扣非净利润（亿元）','表 9 快递公司的净利润及其增速（2018Q3） ',format_of_number='亿', format_desc=None) ==5
    assert number_trans(5,'净利润（亿元）','表 9 快递公司的净利润及其增速（2018Q3） ',format_of_number='亿', format_desc=None) ==5
    assert number_trans(5,'扣非净利润（亿元）','表 9 快递公司的净利润及其增速（2018Q3） ',format_of_number='亿', format_desc=None) ==5
    assert number_trans(5,'扣非净利润（亿元）','表 9 快递公司的净利润及其增速（2018Q3） ',format_of_number='亿', format_desc=None) ==5
    assert number_trans(2000,'2010成交面积','表5:2012年二线城市土地成交面积(2011 年初至今)（万平）',format_of_number='万', format_desc='平') ==2000
    assert number_trans(2000,'2011年成交面积','表5:2012年二线城市土地成交面积(2011 年初至今)（万平）',format_of_number='万', format_desc='平') ==2000
    assert number_trans(20000000,'2010成交面积','表5:2012年二线城市土地成交面积(2011 年初至今)（万平）',format_of_number=None, format_desc='平') ==2000
    assert number_trans(20000000,'2011年成交面积','表5:2012年二线城市土地成交面积(2011 年初至今)（万平）',format_of_number=None, format_desc='平') ==2000
    assert number_trans(2000,'2010成交面积','表5:2012年二线城市土地成交面积(2011 年初至今)（万平）',format_of_number='万', format_desc='平') ==2000
    assert number_trans(2000,'2011年成交面积','表5:2012年二线城市土地成交面积(2011 年初至今)（万平）',format_of_number='万', format_desc='平') ==2000
    assert number_trans(1000,'2010成交','表2:2012年统计城市土地成金额(2011 年初至今)（亿元）',format_of_number='亿', format_desc=None) ==1000
    assert number_trans(1000,'2011年成交','表2:2012年统计城市土地成金额(2011 年初至今)（亿元）',format_of_number='亿', format_desc=None) ==1000
    assert number_trans(1000,'2010成交','表2:2012年统计城市土地成金额(2011 年初至今)（亿元）',format_of_number='亿', format_desc=None) ==1000
    assert number_trans(1000,'2011年成交','表2:2012年统计城市土地成金额(2011 年初至今)（亿元）',format_of_number='亿', format_desc=None) ==1000
    assert number_trans(1000,'2010成交','表2:2012年统计城市土地成金额(2011 年初至今)（亿元）',format_of_number='亿', format_desc=None) ==1000
    assert number_trans(1000,'2011年成交','表2:2012年统计城市土地成金额(2011 年初至今)（亿元）',format_of_number='亿', format_desc=None) ==1000
    assert number_trans(50,'Jan','81 表6：天津住宅期房2007-2012年1月各月成交面积（万平）              ',format_of_number='万', format_desc='平') ==50
    assert number_trans(50,'Feb','81 表6：天津住宅期房2007-2012年1月各月成交面积（万平）              ',format_of_number='万', format_desc='平') ==50
    assert number_trans(50,'Jun','81 表6：天津住宅期房2007-2012年1月各月成交面积（万平）              ',format_of_number='万', format_desc='平') ==50
    assert number_trans(50,'Feb','81 表6：天津住宅期房2007-2012年1月各月成交面积（万平）              ',format_of_number='万', format_desc='平') ==50
    assert number_trans(50,'Jun','81 表6：天津住宅期房2007-2012年1月各月成交面积（万平）              ',format_of_number='万', format_desc='平') ==50
    assert number_trans(50,'Feb','81 表6：天津住宅期房2007-2012年1月各月成交面积（万平）              ',format_of_number='万', format_desc='平') ==50
    assert number_trans(10,'业务量(亿件)','135表5：2018年1-11月快递上市公司累计业务数据 ',format_of_number='亿', format_desc='件') ==10
    assert number_trans(100,'快递业务营收(亿元)','135表5：2018年1-11月快递上市公司累计业务数据 ',format_of_number='亿', format_desc='元') ==100
    assert number_trans(10,'业务量(亿件)','135表5：2018年1-11月快递上市公司累计业务数据 ',format_of_number='亿', format_desc='件') ==10
    assert number_trans(100,'快递业务营收(亿元)','135表5：2018年1-11月快递上市公司累计业务数据 ',format_of_number=None, format_desc='元') == 100
    assert number_trans(10,'业务量(亿件)','135表5：2018年1-11月快递上市公司累计业务数据 ',format_of_number='亿', format_desc='件') ==10
    assert number_trans(100,'快递业务营收(亿元)','135表5：2018年1-11月快递上市公司累计业务数据 ',format_of_number='亿', format_desc='元') ==100
    assert number_trans(5,'本周成交面积','137表 3：2012年6月19日各城市成交面积与环比续（万平） ',format_of_number='万', format_desc='平') ==5
    assert number_trans(10,'上本周成交面积','137表 3：2012年6月19日各城市成交面积与环比续（万平） ',format_of_number='万', format_desc='平') ==10
    assert number_trans(5,'本周成交面积','137表 3：2012年6月19日各城市成交面积与环比续（万平） ',format_of_number='万', format_desc='平') ==5
    assert number_trans(10,'上本周成交面积','137表 3：2012年6月19日各城市成交面积与环比续（万平） ',format_of_number='万', format_desc='平') ==10
    assert number_trans(5,'本周成交面积','137表 3：2012年6月19日各城市成交面积与环比续（万平） ',format_of_number='万', format_desc='平') ==5
    assert number_trans(10,'上本周成交面积','137表 3：2012年6月19日各城市成交面积与环比续（万平） ',format_of_number='万', format_desc='平') ==10
    assert number_trans(30,'商誉A（亿元）','表 3：2018年三季报传媒个股商誉情况一览（净资产或净利润为负的不统计）',format_of_number='亿', format_desc=None) ==30
    assert number_trans(1000,'商誉B（亿元）','表 3：2018年三季报传媒个股商誉情况一览（净资产或净利润为负的不统计）',format_of_number=None, format_desc=None) == 1000 
    assert number_trans(30,'商誉A（亿元）','表 3：2018年三季报传媒个股商誉情况一览（净资产或净利润为负的不统计）',format_of_number='亿', format_desc=None) ==30
    assert number_trans(30,'商誉A（亿元）','表 3：2018年三季报传媒个股商誉情况一览（净资产或净利润为负的不统计）',format_of_number='亿', format_desc=None) ==30
    assert number_trans(2,'净利润上限（亿元）','续  图表27.本周上市公司业绩预告（2019.01.28-2019.02.01）',format_of_number='亿', format_desc='元') ==2
    assert number_trans(2,'净利润上限（亿元）','续  图表27.本周上市公司业绩预告（2019.01.28-2019.02.01）',format_of_number='亿', format_desc='元') ==2
    assert number_trans(2,'净利润上限（亿元）','续  图表27.本周上市公司业绩预告（2019.01.28-2019.02.01）',format_of_number='亿', format_desc='元') ==2
    assert number_trans(20,'2014（亿元）','42图表 40   内资 PCB龙头企业（按2016 年产值排名） ',format_of_number='亿', format_desc=None) ==20
    assert number_trans(20,'2015（亿元）','42图表 40   内资 PCB龙头企业（按2016 年产值排名） ',format_of_number='亿', format_desc=None) ==20
    assert number_trans(20,'2016（亿元）','42图表 40   内资 PCB龙头企业（按2016 年产值排名） ',format_of_number='亿', format_desc=None) ==20
    assert number_trans(20,'2014（亿元）','42图表 40   内资 PCB龙头企业（按2016 年产值排名） ',format_of_number='亿', format_desc=None) ==20
    assert number_trans(20,'2015（亿元）','42图表 40   内资 PCB龙头企业（按2016 年产值排名） ',format_of_number='亿', format_desc=None) ==20
    assert number_trans(20,'2016（亿元）','42图表 40   内资 PCB龙头企业（按2016 年产值排名） ',format_of_number='亿', format_desc=None) ==20
    assert number_trans(20,'2014（亿元）','42图表 40   内资 PCB龙头企业（按2016 年产值排名） ',format_of_number='亿', format_desc=None) ==20
    assert number_trans(20,'2015（亿元）','42图表 40   内资 PCB龙头企业（按2016 年产值排名） ',format_of_number='亿', format_desc=None) ==20
    assert number_trans(20,'2016（亿元）','42图表 40   内资 PCB龙头企业（按2016 年产值排名） ',format_of_number='亿', format_desc=None) ==20
    assert number_trans(30,'2018','表6：2018年1-6月快递公司CR8剔除顺丰、韵达、圆通、申通 单量和份额数据（亿件）',format_of_number='亿', format_desc='件') ==30
    assert number_trans(20,'2017','表6：2018年1-6月快递公司CR8剔除顺丰、韵达、圆通、申通 单量和份额数据（亿件）',format_of_number='亿', format_desc='件') ==20
    assert number_trans(20,'2018','表6：2018年1-6月快递公司CR8剔除顺丰、韵达、圆通、申通 单量和份额数据（亿件）',format_of_number='亿', format_desc='件') ==20
    assert number_trans(20,'2017','表6：2018年1-6月快递公司CR8剔除顺丰、韵达、圆通、申通 单量和份额数据（亿件）',format_of_number='亿', format_desc='件') ==20
    assert number_trans(30,'2018','表6：2018年1-6月快递公司CR8剔除顺丰、韵达、圆通、申通 单量和份额数据（亿件）',format_of_number='亿', format_desc='件') ==30
    assert number_trans(20,'2018','表6：2018年1-6月快递公司CR8剔除顺丰、韵达、圆通、申通 单量和份额数据（亿件）',format_of_number='亿', format_desc='件') ==20
    assert number_trans(20,'2017','表6：2018年1-6月快递公司CR8剔除顺丰、韵达、圆通、申通 单量和份额数据（亿件）',format_of_number='亿', format_desc='件') ==20
    assert number_trans(30,'2018','表6：2018年1-6月快递公司CR8剔除顺丰、韵达、圆通、申通 单量和份额数据（亿件）',format_of_number='亿', format_desc='件') ==30
    assert number_trans(2500,'周票房（万）','表4：2018年第52周（2018.12.24 - 2018.12.30）全国电影票房TOP10',format_of_number='万', format_desc=None) ==2500
    assert number_trans(2500,'周票房（万）','表4：2018年第52周（2018.12.24 - 2018.12.30）全国电影票房TOP10',format_of_number='万', format_desc=None) ==2500
    assert number_trans(2500,'周票房（万）','表4：2018年第52周（2018.12.24 - 2018.12.30）全国电影票房TOP10',format_of_number='万', format_desc=None) ==2500
    assert number_trans(900,'总收入（万元）','131表 5航运业上市公司收入情况  ',format_of_number='亿', format_desc=None) ==9000000
    assert number_trans(20,'净利润（万元）','131表 5航运业上市公司收入情况  ',format_of_number='亿', format_desc=None) ==200000
    assert number_trans(900,'总收入（万元）','131表 5航运业上市公司收入情况  ',format_of_number='亿', format_desc=None) ==9000000
    assert number_trans(20,'净利润（万元）','131表 5航运业上市公司收入情况  ',format_of_number='亿', format_desc=None) ==200000
    assert number_trans(900,'总收入（万元）','131表 5航运业上市公司收入情况  ',format_of_number='亿', format_desc=None) ==9000000
    assert number_trans(20,'净利润（万元）','131表 5航运业上市公司收入情况  ',format_of_number='亿', format_desc=None) ==200000
    assert number_trans(500,'投资金额（亿元）','表91：预计2020年通车高铁线路 ',format_of_number='亿', format_desc=None) ==500
    assert number_trans(500,'投资金额（亿元）','表91：预计2020年通车高铁线路 ',format_of_number='亿', format_desc=None) ==500
    assert number_trans(500,'投资金额（亿元）','表91：预计2020年通车高铁线路 ',format_of_number='亿', format_desc=None) ==500
    assert number_trans(17,'11AEPS','附表14：2012年06月11日地产+X公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==17
    assert number_trans(17,'12EPE','附表14：2012年06月11日地产+X公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==17
    assert number_trans(17,'12EEPS','附表14：2012年06月11日地产+X公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==17
    assert number_trans(17,'11AEPS','附表14：2012年06月11日地产+X公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==17
    assert number_trans(17,'11AEPS','附表14：2012年06月11日地产+X公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==17
    assert number_trans(17,'10APE','附表14：2012年06月11日地产+X公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==17
    assert number_trans(300,'投资总额（亿元）','表67. 预计2018年新开通高铁线路15条线共计3559公里  ',format_of_number='亿', format_desc=None) ==300
    assert number_trans(300,'投资总额（亿元）','表67. 预计2018年新开通高铁线路15条线共计3559公里  ',format_of_number='亿', format_desc=None) ==300
    assert number_trans(300,'投资总额（亿元）','表67. 预计2018年新开通高铁线路15条线共计3559公里  ',format_of_number='亿', format_desc=None) ==300
    assert number_trans(1000,'绝对量','21 表 6：2012年1-5月全国房地产开发投资及销售情况（商品房销售额（亿元））',format_of_number=None, format_desc=None) ==1000
    assert number_trans(1000,'绝对量','21 表 6：2012年1-5月全国房地产开发投资及销售情况（商品房销售额（亿元））',format_of_number=None, format_desc=None) ==1000
    assert number_trans(1000,'绝对量','21 表 6：2012年1-5月全国房地产开发投资及销售情况（商品房销售额（亿元））',format_of_number=None, format_desc=None) ==1000
    assert number_trans(0,'本周跌幅后十','28 表3：2012年06月03日年A股房地产股上周股价跌幅前十表现 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(100,'最新市值（亿元）','28 表3：2012年06月03日年A股房地产股上周股价跌幅前十表现 ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'最新市值（亿元）','28 表3：2012年06月03日年A股房地产股上周股价跌幅前十表现 ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(10,'本周跌幅后十','28 表3：2012年06月03日年A股房地产股上周股价跌幅前十表现 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(0,'本周跌幅后十','28 表3：2012年06月03日年A股房地产股上周股价跌幅前十表现 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'本周跌幅后十','28 表3：2012年06月03日年A股房地产股上周股价跌幅前十表现 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(100,'最新市值（亿元）','28 表3：2012年06月03日年A股房地产股上周股价跌幅前十表现 ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(80,'销售面积','13 香港重点上市地产公司销售表现（亿元/万平方米） ',format_of_number=None, format_desc=None) ==80
    assert number_trans(80,'销售面积','13 香港重点上市地产公司销售表现（亿元/万平方米） ',format_of_number=None, format_desc=None) ==80
    assert number_trans(80,'销售面积','13 香港重点上市地产公司销售表现（亿元/万平方米） ',format_of_number=None, format_desc=None) ==80
    assert number_trans(500,'市值(亿元）','表3：重点物流、快递公司估值对比表           ',format_of_number='亿', format_desc=None) ==500
    assert number_trans(500,'市值(亿元）','表3：重点物流、快递公司估值对比表           ',format_of_number='亿', format_desc=None) ==500
    assert number_trans(500,'市值(亿元）','表3：重点物流、快递公司估值对比表           ',format_of_number='亿', format_desc=None) ==500
    assert number_trans(20,'2018','表9：2018年全年快递公司CR8剔除顺丰、韵达、圆通、申通 单量和份额数据（亿件）',format_of_number='亿', format_desc='件') ==20
    assert number_trans(20,'2017','表9：2018年全年快递公司CR8剔除顺丰、韵达、圆通、申通 单量和份额数据（亿件）',format_of_number='亿', format_desc='件') ==20
    assert number_trans(20,'2018','表9：2018年全年快递公司CR8剔除顺丰、韵达、圆通、申通 单量和份额数据（亿件）',format_of_number='亿', format_desc='件') ==20
    assert number_trans(20,'2017','表9：2018年全年快递公司CR8剔除顺丰、韵达、圆通、申通 单量和份额数据（亿件）',format_of_number='亿', format_desc='件') ==20
    assert number_trans(20,'2018','表9：2018年全年快递公司CR8剔除顺丰、韵达、圆通、申通 单量和份额数据（亿件）',format_of_number='亿', format_desc='件') ==20
    assert number_trans(20,'2017','表9：2018年全年快递公司CR8剔除顺丰、韵达、圆通、申通 单量和份额数据（亿件）',format_of_number='亿', format_desc='件') ==20
    assert number_trans(10000,'销售面积绝对数','24 表 2  2012年 1-5各区域房地产销售继续下跌，（万平方米/亿元）',format_of_number=None, format_desc=None) ==10000
    assert number_trans(10000,'销售额绝对数','24 表 2  2012年 1-5各区域房地产销售继续下跌，（万平方米/亿元）',format_of_number=None, format_desc=None) ==10000
    assert number_trans(10000,'销售面积绝对数','24 表 2  2012年 1-5各区域房地产销售继续下跌，（万平方米/亿元）',format_of_number=None, format_desc=None) ==10000
    assert number_trans(10000,'销售额绝对数','24 表 2  2012年 1-5各区域房地产销售继续下跌，（万平方米/亿元）',format_of_number=None, format_desc=None) ==10000
    assert number_trans(10000,'销售面积绝对数','24 表 2  2012年 1-5各区域房地产销售继续下跌，（万平方米/亿元）',format_of_number=None, format_desc=None) ==10000
    assert number_trans(10000,'销售额绝对数','24 表 2  2012年 1-5各区域房地产销售继续下跌，（万平方米/亿元）',format_of_number=None, format_desc=None) ==10000
    assert number_trans(20000,'商品房新开工面积','62 图表 ：1998年至2005年房地产投资模型（万平方米）',format_of_number='万', format_desc='平') ==20000
    assert number_trans(20000,'商品房竣工面积增速','62 图表 ：1998年至2005年房地产投资模型（万平方米）',format_of_number='万', format_desc='平') ==20000
    assert number_trans(20000,'商品房新开工面积','62 图表 ：1998年至2005年房地产投资模型（万平方米）',format_of_number='万', format_desc='平') ==20000
    assert number_trans(20000,'商品房竣工面积增速','62 图表 ：1998年至2005年房地产投资模型（万平方米）',format_of_number='万', format_desc='平') ==20000
    assert number_trans(20000,'商品房新开工面积','62 图表 ：1998年至2005年房地产投资模型（万平方米）',format_of_number='万', format_desc='平') ==20000
    assert number_trans(20000,'商品房竣工面积增速','62 图表 ：1998年至2005年房地产投资模型（万平方米）',format_of_number='万', format_desc='平') ==20000
    assert number_trans(8000,'当前设计旅客吞吐量','表 5 三大机场扩建后设计旅客吞吐量均接近1亿人次（万人次） ',format_of_number='万', format_desc=None) ==8000
    assert number_trans(8000,'扩建后旅客吞吐量','表 5 三大机场扩建后设计旅客吞吐量均接近1亿人次（万人次） ',format_of_number='万', format_desc=None) ==8000
    assert number_trans(8000,'当前设计旅客吞吐量','表 5 三大机场扩建后设计旅客吞吐量均接近1亿人次（万人次） ',format_of_number='万', format_desc=None) ==8000
    assert number_trans(8000,'扩建后旅客吞吐量','表 5 三大机场扩建后设计旅客吞吐量均接近1亿人次（万人次） ',format_of_number='万', format_desc=None) ==8000
    assert number_trans(8000,'当前设计旅客吞吐量','表 5 三大机场扩建后设计旅客吞吐量均接近1亿人次（万人次） ',format_of_number='万', format_desc=None) ==8000
    assert number_trans(8000,'扩建后旅客吞吐量','表 5 三大机场扩建后设计旅客吞吐量均接近1亿人次（万人次） ',format_of_number='万', format_desc=None) ==8000
    assert number_trans(100,'投资金额（亿元）','表91：预计2020年通车高铁线路 ',format_of_number='亿', format_desc='元') ==100
    assert number_trans(100,'投资金额（亿元）','表91：预计2020年通车高铁线路 ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'投资金额（亿元）','表91：预计2020年通车高铁线路 ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'2011同期','59 表8:2012年三线城市土地成交金额(2011 年初至今)（亿）',format_of_number='亿', format_desc=None) ==100
    assert number_trans(50,'2012至今','59 表8:2012年三线城市土地成交金额(2011 年初至今)（亿）',format_of_number='亿', format_desc=None) ==50
    assert number_trans(100,'2011同期','59 表8:2012年三线城市土地成交金额(2011 年初至今)（亿）',format_of_number='亿', format_desc=None) ==100
    assert number_trans(50,'2012至今','59 表8:2012年三线城市土地成交金额(2011 年初至今)（亿）',format_of_number='亿', format_desc=None) ==50
    assert number_trans(100,'2011同期','59 表8:2012年三线城市土地成交金额(2011 年初至今)（亿）',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'2012至今','59 表8:2012年三线城市土地成交金额(2011 年初至今)（亿）',format_of_number='亿', format_desc=None) ==100
    assert number_trans(50,'2011同期','59 表8:2012年三线城市土地成交金额(2011 年初至今)（亿）',format_of_number='亿', format_desc=None) ==50
    assert number_trans(50,'2012至今','59 表8:2012年三线城市土地成交金额(2011 年初至今)（亿）',format_of_number='亿', format_desc=None) ==50
    assert number_trans(10,'2011年成交面积','表1:2012年统计城市土地成交面积(2011 年初至今)（万平）',format_of_number='万', format_desc='平') ==10
    assert number_trans(10,'2011同期','表1:2012年统计城市土地成交面积(2011 年初至今)（万平）',format_of_number='万', format_desc='平') ==10
    assert number_trans(10,'2011年成交面积','表1:2012年统计城市土地成交面积(2011 年初至今)（万平）',format_of_number='万', format_desc='平') ==10
    assert number_trans(10,'2011同期','表1:2012年统计城市土地成交面积(2011 年初至今)（万平）',format_of_number='万', format_desc='平') ==10
    assert number_trans(10,'2011年成交面积','表1:2012年统计城市土地成交面积(2011 年初至今)（万平）',format_of_number='万', format_desc='平') ==10
    assert number_trans(10,'2011同期','表1:2012年统计城市土地成交面积(2011 年初至今)（万平）',format_of_number='万', format_desc='平') ==10
    assert number_trans(30,'市值（亿元）','图8： 本周个股涨跌幅排名(跌幅前十)  ',format_of_number='亿', format_desc='元') ==30
    assert number_trans(30,'市值（亿元）','图8： 本周个股涨跌幅排名(跌幅前十)  ',format_of_number='亿', format_desc='元') ==30
    assert number_trans(30,'市值（亿元）','图8： 本周个股涨跌幅排名(跌幅前十)  ',format_of_number='亿', format_desc='元') ==30
    assert number_trans(1000,'播放量（万）','318表13：2019年第1周（2019.01.07 - 2019.01.13）国漫播放量TOP10',format_of_number='万', format_desc=None) ==1000
    assert number_trans(4,'总股本(亿股)','04 表3重点覆盖公司估值表 ',format_of_number='亿', format_desc=None) ==4
    assert number_trans(4,'总股本(亿股)','04 表3重点覆盖公司估值表 ',format_of_number='亿', format_desc='股') ==4
    assert number_trans(4,'总市值(亿元)','04 表3重点覆盖公司估值表 ',format_of_number='亿', format_desc=None) ==4
    assert number_trans(4,'总市值(亿元)','04 表3重点覆盖公司估值表 ',format_of_number='亿', format_desc='股') ==4
    assert number_trans(4,'总市值(亿元)','04 表3重点覆盖公司估值表 ',format_of_number='亿', format_desc=None) ==4
    assert number_trans(4,'总股本(亿股)','04 表3重点覆盖公司估值表 ',format_of_number='亿', format_desc='股') ==4
    assert number_trans(10,'市值(亿元)','表80. 机械行业主要上市公司估值表',format_of_number='亿', format_desc=None) ==10
    assert number_trans(10,'市值(亿元)','表80. 机械行业主要上市公司估值表',format_of_number='亿', format_desc='元') ==10
    assert number_trans(6,'10AEPS','124附表3：商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'11AEPS','124附表3：商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'10AEPS','124附表3：商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'11AEPS','124附表3：商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==6
    assert number_trans(30,'成交住宅建筑面积（万平米）','21 图13： 福州市月度住宅用地成交情况  ',format_of_number='万', format_desc='平') ==30
    assert number_trans(30,'成交住宅建筑面积（万平米）','21 图13： 福州市月度住宅用地成交情况  ',format_of_number='万', format_desc='平') ==30
    assert number_trans(30,'成交住宅建筑面积（万平米）','21 图13： 福州市月度住宅用地成交情况  ',format_of_number='万', format_desc='平') ==30
    assert number_trans(100000,'10年H2','表2:一线城市一手房H1、H2成交对比（单位：万平方米） ',format_of_number=None, format_desc='平') ==10
    assert number_trans(100000,'10年H2','表2:一线城市一手房H1、H2成交对比（单位：万平方米） ',format_of_number=None, format_desc='平') ==10
    assert number_trans(100000,'10年H1','表2:一线城市一手房H1、H2成交对比（单位：万平方米） ',format_of_number=None, format_desc='平') ==10
    assert number_trans(20,'最新市价（百万元）','63 表4：2012年6月10日银河地产模拟组合 ',format_of_number=None, format_desc=None) == 20 
    assert number_trans(150,'持股数量（万股）','63 表4：2012年6月10日银河地产模拟组合 ',format_of_number='万', format_desc=None) ==150
    assert number_trans(20,'最新市价（百万元）','63 表4：2012年6月10日银河地产模拟组合 ',format_of_number=None, format_desc=None) ==20 
    assert number_trans(150,'持股数量（万股）','63 表4：2012年6月10日银河地产模拟组合 ',format_of_number='万', format_desc=None) ==150
    assert number_trans(20,'最新市价（百万元）','63 表4：2012年6月10日银河地产模拟组合 ',format_of_number=None, format_desc=None) == 20 
    assert number_trans(150,'持股数量（万股）','63 表4：2012年6月10日银河地产模拟组合 ',format_of_number='万', format_desc=None) ==150
    assert number_trans(5,'净利润上限（亿元）','图表5.本周上市公司业绩预告（2019.01.28-2019.02.01）',format_of_number='亿', format_desc='元') ==5
    assert number_trans(5,'净利润下限（亿元）','图表5.本周上市公司业绩预告（2019.01.28-2019.02.01）',format_of_number='亿', format_desc='元') ==5
    assert number_trans(5,'净利润上限（亿元）','图表5.本周上市公司业绩预告（2019.01.28-2019.02.01）',format_of_number='亿', format_desc='元') ==5
    assert number_trans(5,'净利润下限（亿元）','图表5.本周上市公司业绩预告（2019.01.28-2019.02.01）',format_of_number='亿', format_desc='元') ==5
    assert number_trans(5,'净利润上限（亿元）','图表5.本周上市公司业绩预告（2019.01.28-2019.02.01）',format_of_number='亿', format_desc='元') ==5
    assert number_trans(5,'净利润下限（亿元）','图表5.本周上市公司业绩预告（2019.01.28-2019.02.01）',format_of_number='亿', format_desc='元') ==5
    assert number_trans(10,'上周成交量','图17、重点类型城市二手房成交数据（万平米）',format_of_number='万', format_desc='平') ==10
    assert number_trans(10,'上周成交量','图17、重点类型城市二手房成交数据（万平米）',format_of_number='万', format_desc='平') ==10
    assert number_trans(10,'上周成交量','图17、重点类型城市二手房成交数据（万平米）',format_of_number='万', format_desc='平') ==10
    assert number_trans(10,'产能（万吨）','表11：2017年中国混凝土外加剂前十企业市场占有率 ',format_of_number='万', format_desc='吨') ==10
    assert number_trans(10,'产能（万吨）','表11：2017年中国混凝土外加剂前十企业市场占有率 ',format_of_number='万', format_desc='吨') ==10
    assert number_trans(10,'产能（万吨）','表11：2017年中国混凝土外加剂前十企业市场占有率 ',format_of_number='万', format_desc='吨') ==10
    assert number_trans(70,'市值（亿元）','表65：重点公司估值及评级 ',format_of_number='亿', format_desc='元') ==70
    assert number_trans(70,'市值（亿元）','表65：重点公司估值及评级 ',format_of_number='亿', format_desc=None) ==70
    assert number_trans(70,'市值（亿元）','表65：重点公司估值及评级 ',format_of_number='亿', format_desc=None) ==70
    assert number_trans(80,'物业面积（万方）','34 表2 张江高科月租金偏低，收入增长主要来自于规模增长 ',format_of_number='万', format_desc=None) ==80
    assert number_trans(800000,'物业面积（万方）','34 表2 张江高科月租金偏低，收入增长主要来自于规模增长 ',format_of_number=None, format_desc=None) ==80
    assert number_trans(80,'物业面积（万方）','34 表2 张江高科月租金偏低，收入增长主要来自于规模增长 ',format_of_number='万', format_desc=None) ==80
    assert number_trans(3,'播放量（亿）','表6：2019年第7周（2019.02.18 - 2019.02.24）电视剧和网剧总播放量TOP10',format_of_number='亿', format_desc=None) ==3
    assert number_trans(3,'播放量（亿）','表6：2019年第7周（2019.02.18 - 2019.02.24）电视剧和网剧总播放量TOP10',format_of_number='亿', format_desc=None) ==3
    assert number_trans(3,'播放量（亿）','表6：2019年第7周（2019.02.18 - 2019.02.24）电视剧和网剧总播放量TOP10',format_of_number='亿', format_desc=None) ==3
    assert number_trans(10,'总股本','124附表3：商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc='股') ==10
    assert number_trans(10,'总股本','124附表3：商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc='股') ==10
    assert number_trans(10,'0608股价','124附表3：商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc='股') ==10
    assert number_trans(100,'货币资金（亿元）','表 27：2018Q3出版发行公司货币资金分析',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'总资产（亿元）','表 27：2018Q3出版发行公司货币资金分析',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'总资产（亿元）','表 27：2018Q3出版发行公司货币资金分析',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'货币资金（亿元）','表 27：2018Q3出版发行公司货币资金分析',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'总资产（亿元）','表 27：2018Q3出版发行公司货币资金分析',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'货币资金（亿元）','表 27：2018Q3出版发行公司货币资金分析',format_of_number='亿', format_desc=None) ==100
    assert number_trans(10,'绝对量','16表 1：2012年1-5月全国房地产开发投资及销售情况（房地产开发投资（亿元）） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'同比增长（%）','16表 1：2012年1-5月全国房地产开发投资及销售情况（房地产开发投资（亿元）） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'绝对量','16表 1：2012年1-5月全国房地产开发投资及销售情况（房地产开发投资（亿元）） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'同比增长（%）','16表 1：2012年1-5月全国房地产开发投资及销售情况（房地产开发投资（亿元）） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'绝对量','16表 1：2012年1-5月全国房地产开发投资及销售情况（房地产开发投资（亿元）） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'同比增长（%）','16表 1：2012年1-5月全国房地产开发投资及销售情况（房地产开发投资（亿元）） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(50,'2018年票房（亿元）','图表 21   现有院线的经营情况',format_of_number='亿', format_desc=None) ==50
    assert number_trans(100,'单银幕票房（万元）','图表 21   现有院线的经营情况',format_of_number='万', format_desc=None) ==100
    assert number_trans(50,'2018年票房（亿元）','图表 21   现有院线的经营情况',format_of_number='亿', format_desc=None) ==50
    assert number_trans(100,'单银幕票房（万元）','图表 21   现有院线的经营情况',format_of_number='万', format_desc=None) ==100
    assert number_trans(50,'2018年票房（亿元）','图表 21   现有院线的经营情况',format_of_number='亿', format_desc=None) ==50
    assert number_trans(100,'单银幕票房（万元）','图表 21   现有院线的经营情况',format_of_number='万', format_desc=None) ==100
    assert number_trans(10,'周成交额(亿元)','表 3：传媒互联网行业',format_of_number='亿', format_desc=None) ==10
    assert number_trans(10,'周成交额(亿元)','表 3：传媒互联网行业',format_of_number='亿', format_desc=None) ==10
    assert number_trans(10,'周成交额(亿元)','表 3：传媒互联网行业',format_of_number='亿', format_desc=None) ==10
    assert number_trans(10,'0608股价','132附表15：2012年06月11日商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(200,'总市值','132附表15：2012年06月11日商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc=None) ==200
    assert number_trans(200,'总市值','132附表15：2012年06月11日商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc=None) ==200
    assert number_trans(10,'0608股价','132附表15：2012年06月11日商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'0608股价','132附表15：2012年06月11日商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(200,'总市值','132附表15：2012年06月11日商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc=None) ==200
    assert number_trans(60,'最新市值（亿元）','02 表 1：地产板块一周涨幅前列公司情况 ',format_of_number='亿', format_desc='元') ==60
    assert number_trans(60,'最新市值（亿元）','02 表 1：地产板块一周涨幅前列公司情况 ',format_of_number='亿', format_desc=None) ==60
    assert number_trans(60,'最新市值（亿元）','02 表 1：地产板块一周涨幅前列公司情况 ',format_of_number='亿', format_desc='元') ==60
    assert number_trans(500,'总市值','14 附表4：地产+X行业重点公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc=None) ==500
    assert number_trans(50,'总股本','14 附表4：地产+X行业重点公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc=None) ==50
    assert number_trans(500,'总市值','14 附表4：地产+X行业重点公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc=None) ==500
    assert number_trans(50,'总股本','14 附表4：地产+X行业重点公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc=None) ==50
    assert number_trans(50,'总股本','14 附表4：地产+X行业重点公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc=None) ==50
    assert number_trans(500,'总市值','14 附表4：地产+X行业重点公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc=None) ==500
    assert number_trans(10,'市盈率','表 11  A股高速公路行业重点跟踪公司业绩增速与估值（市值单位：亿人民币元；截止 2019.1.11） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(1,'市净率','表 11  A股高速公路行业重点跟踪公司业绩增速与估值（市值单位：亿人民币元；截止 2019.1.11） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(10,'市盈率','表 11  A股高速公路行业重点跟踪公司业绩增速与估值（市值单位：亿人民币元；截止 2019.1.11） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(1,'市净率','表 11  A股高速公路行业重点跟踪公司业绩增速与估值（市值单位：亿人民币元；截止 2019.1.11） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'市净率','表 11  A股高速公路行业重点跟踪公司业绩增速与估值（市值单位：亿人民币元；截止 2019.1.11） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(10,'市盈率','表 11  A股高速公路行业重点跟踪公司业绩增速与估值（市值单位：亿人民币元；截止 2019.1.11） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(9,'Jun','94 表25：东莞住宅期房2007-2012年1月各月成交面积（万平）             ',format_of_number='万', format_desc='平') ==9
    assert number_trans(9,'Feb','94 表25：东莞住宅期房2007-2012年1月各月成交面积（万平）             ',format_of_number='万', format_desc='平') ==9
    assert number_trans(9,'Jan','94 表25：东莞住宅期房2007-2012年1月各月成交面积（万平）             ',format_of_number='万', format_desc='平') ==9
    assert number_trans(204,'最新市值（亿元）','17 表2：A股房地产股上周股价跌幅前十表现 ',format_of_number='亿', format_desc=None) ==204
    assert number_trans(204,'最新市值（亿元）','17 表2：A股房地产股上周股价跌幅前十表现 ',format_of_number='亿', format_desc=None) ==204
    assert number_trans(240,'最新市值（亿元）','17 表2：A股房地产股上周股价跌幅前十表现 ',format_of_number='亿', format_desc=None) ==240
    assert number_trans(50,'最新市值（亿元）','02 表 1：地产板块一周涨幅前列公司情况 ',format_of_number='亿', format_desc='元') ==50
    assert number_trans(50,'最新市值（亿元）','02 表 1：地产板块一周涨幅前列公司情况 ',format_of_number='亿', format_desc=None) ==50
    assert number_trans(50,'最新市值（亿元）','02 表 1：地产板块一周涨幅前列公司情况 ',format_of_number='亿', format_desc=None) ==50
    assert number_trans(40000,'一线城市','64 表5：近年年房地产销售面积预测（万平米） ',format_of_number='万', format_desc='平') ==40000
    assert number_trans(40000000,'一线城市','64 表5：近年年房地产销售面积预测（万平米） ',format_of_number=None, format_desc='平') ==4000
    assert number_trans(40000000,'一线城市','64 表5：近年年房地产销售面积预测（万平米） ',format_of_number=None, format_desc='平') ==4000
    assert number_trans(0,'本周跌幅后十','30 表5：2012年06月内房股上周股价跌幅前十表现    ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'本周跌幅后十','30 表5：2012年06月内房股上周股价跌幅前十表现    ',format_of_number=None, format_desc=None) ==0
    assert number_trans(5,'0612股价','44 附表3：地产行业三线重点公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc='元') ==5
    assert number_trans(50,'总市值','44 附表3：地产行业三线重点公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc=None) ==50
    assert number_trans(5,'0612股价','44 附表3：地产行业三线重点公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc='元') ==5
    assert number_trans(50,'总市值','44 附表3：地产行业三线重点公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc=None) ==50
    assert number_trans(5,'0612股价','44 附表3：地产行业三线重点公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc='元') ==5
    assert number_trans(50,'总市值','44 附表3：地产行业三线重点公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc=None) ==50
    assert number_trans(1000,'销售收入（百万美元）','表84：2017年全球物流自动化系统集成十五强 ',format_of_number='百万', format_desc=None) ==1000
    assert number_trans(1000,'销售收入（百万美元）','表84：2017年全球物流自动化系统集成十五强 ',format_of_number='百万', format_desc=None) ==1000
    assert number_trans(1000,'销售收入（百万美元）','表84：2017年全球物流自动化系统集成十五强 ',format_of_number='百万', format_desc=None) ==1000
    assert number_trans(100,'股东权益价值（亿元）','67表2：大秦铁路拟入股蒙华、唐港铁路，整体收购太原通信段 ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'股东权益价值（亿元）','67表2：大秦铁路拟入股蒙华、唐港铁路，整体收购太原通信段 ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'股东权益价值（亿元）','67表2：大秦铁路拟入股蒙华、唐港铁路，整体收购太原通信段 ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(20,'2018年票房（亿元）','图表 23   现有院线的经营情况',format_of_number='亿', format_desc=None) ==20
    assert number_trans(20,'2018年票房（亿元）','图表 23   现有院线的经营情况',format_of_number='亿', format_desc=None) ==20
    assert number_trans(50,'Jan','85表15：南京住宅期房2007-2012年1月各月成交面积（万平） ',format_of_number='万', format_desc='平') ==50
    assert number_trans(50,'Feb','85表15：南京住宅期房2007-2012年1月各月成交面积（万平） ',format_of_number='万', format_desc='平') ==50
    assert number_trans(50,'Jan','85表15：南京住宅期房2007-2012年1月各月成交面积（万平） ',format_of_number='万', format_desc='平') ==50
    assert number_trans(50,'Feb','85表15：南京住宅期房2007-2012年1月各月成交面积（万平） ',format_of_number='万', format_desc='平') ==50
    assert number_trans(50,'Jan','85表15：南京住宅期房2007-2012年1月各月成交面积（万平） ',format_of_number='万', format_desc='平') ==50
    assert number_trans(50,'Feb','85表15：南京住宅期房2007-2012年1月各月成交面积（万平） ',format_of_number='万', format_desc='平') ==50
    assert number_trans(20,'2018','表5：2018年1-6月快递公司顺丰+韵达+圆通+申通单量和份额数据（亿件）     ',format_of_number='亿', format_desc='件') ==20
    assert number_trans(15,'2017','表5：2018年1-6月快递公司顺丰+韵达+圆通+申通单量和份额数据（亿件）     ',format_of_number='亿', format_desc='件') ==15
    assert number_trans(20,'2018','表5：2018年1-6月快递公司顺丰+韵达+圆通+申通单量和份额数据（亿件）     ',format_of_number='亿', format_desc='件') ==20
    assert number_trans(15,'2017','表5：2018年1-6月快递公司顺丰+韵达+圆通+申通单量和份额数据（亿件）     ',format_of_number='亿', format_desc='件') ==15
    assert number_trans(20,'2018','表5：2018年1-6月快递公司顺丰+韵达+圆通+申通单量和份额数据（亿件）     ',format_of_number='亿', format_desc='件') ==20
    assert number_trans(15,'2017','表5：2018年1-6月快递公司顺丰+韵达+圆通+申通单量和份额数据（亿件）     ',format_of_number='亿', format_desc='件') ==15
    assert number_trans(2000,'周票房（万）','表4：2019年第1周（2019.01.07 - 2019.01.13）全国电影票房TOP10',format_of_number='万', format_desc=None) ==2000
    assert number_trans(20000000,'周票房（万）','表4：2019年第1周（2019.01.07 - 2019.01.13）全国电影票房TOP10',format_of_number=None, format_desc=None) ==2000
    assert number_trans(2000,'周票房（万）','表4：2019年第1周（2019.01.07 - 2019.01.13）全国电影票房TOP10',format_of_number='万', format_desc=None) ==2000
    assert number_trans(1000,'市值（亿元）','表1：欧美廉航龙头市值超过千亿元 ',format_of_number='亿', format_desc='元') ==1000
    assert number_trans(1000,'市值（亿元）','表1：欧美廉航龙头市值超过千亿元 ',format_of_number='亿', format_desc=None) ==1000
    assert number_trans(1000,'市值（亿元）','表1：欧美廉航龙头市值超过千亿元 ',format_of_number='亿', format_desc=None) ==1000
    assert number_trans(40,'4月成交面积','22 表02：2012年北上广深杭销售量情况汇总（万平方米） ',format_of_number='万', format_desc='平') ==40
    assert number_trans(40,'4月成交面积','22 表02：2012年北上广深杭销售量情况汇总（万平方米） ',format_of_number='万', format_desc='平') ==40
    assert number_trans(40,'4月成交面积','22 表02：2012年北上广深杭销售量情况汇总（万平方米） ',format_of_number='万', format_desc='平') ==40
    assert number_trans(100,'市值（亿元）','表65：重点公司估值及评级 ',format_of_number='亿', format_desc='元') ==100
    assert number_trans(100,'市值（亿元）','表65：重点公司估值及评级 ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'市值（亿元）','表65：重点公司估值及评级 ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(500,'周票房（万）','表7：2019年第2周（2019.1.14 - 2019.1.20）影投票房排名TOP10',format_of_number='万', format_desc=None) ==500
    assert number_trans(5000000,'周票房（万）','表7：2019年第2周（2019.1.14 - 2019.1.20）影投票房排名TOP10',format_of_number=None, format_desc=None) ==500
    assert number_trans(500,'周票房（万）','表7：2019年第2周（2019.1.14 - 2019.1.20）影投票房排名TOP10',format_of_number='万', format_desc=None) ==500
    assert number_trans(10,'2010成交面积','59 表8:2012年三线城市土地成交金额(2011 年初至今)（亿）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2011年成交面积','59 表8:2012年三线城市土地成交金额(2011 年初至今)（亿）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2010成交面积','59 表8:2012年三线城市土地成交金额(2011 年初至今)（亿）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2011年成交面积','59 表8:2012年三线城市土地成交金额(2011 年初至今)（亿）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'累计同比','59 表8:2012年三线城市土地成交金额(2011 年初至今)（亿）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2010成交面积','59 表8:2012年三线城市土地成交金额(2011 年初至今)（亿）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2011年成交面积','59 表8:2012年三线城市土地成交金额(2011 年初至今)（亿）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'累计同比','59 表8:2012年三线城市土地成交金额(2011 年初至今)（亿）',format_of_number=None, format_desc=None) ==10
    assert number_trans(15,'2018年票房（亿元）','图表 23   现有院线的经营情况',format_of_number='亿', format_desc=None) ==15
    assert number_trans(15,'2018年票房（亿元）','图表 23   现有院线的经营情况',format_of_number='亿', format_desc=None) ==15
    assert number_trans(15,'2018年票房（亿元）','图表 23   现有院线的经营情况',format_of_number='亿', format_desc=None) ==15
    assert number_trans(5,'2018年票房（亿）','表5：各院线公司2018年票房情况',format_of_number='亿', format_desc=None) ==5
    assert number_trans(5,'2018年票房（亿）','表5：各院线公司2018年票房情况',format_of_number='亿', format_desc=None) ==5
    assert number_trans(5,'2018年票房（亿）','表5：各院线公司2018年票房情况',format_of_number='亿', format_desc=None) ==5
    assert number_trans(10,'2011年成交面积','57表6:2012年二线城市土地成交金额(2011 年初至今)（亿）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2011同期','57表6:2012年二线城市土地成交金额(2011 年初至今)（亿）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2011年成交面积','57表6:2012年二线城市土地成交金额(2011 年初至今)（亿）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2011同期','57表6:2012年二线城市土地成交金额(2011 年初至今)（亿）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2011年成交面积','57表6:2012年二线城市土地成交金额(2011 年初至今)（亿）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2011同期','57表6:2012年二线城市土地成交金额(2011 年初至今)（亿）',format_of_number=None, format_desc=None) ==10
    assert number_trans(200,'2010成交面积','59 表8:2012年三线城市土地成交金额(2011 年初至今)（亿）',format_of_number=None, format_desc=None) ==200
    assert number_trans(200,'2010成交面积','59 表8:2012年三线城市土地成交金额(2011 年初至今)（亿）',format_of_number=None, format_desc=None) ==200
    assert number_trans(200,'2010成交面积','59 表8:2012年三线城市土地成交金额(2011 年初至今)（亿）',format_of_number=None, format_desc=None) ==200
    assert number_trans(200,'2010成交面积','59 表8:2012年三线城市土地成交金额(2011 年初至今)（亿）',format_of_number=None, format_desc=None) ==200
    assert number_trans(1000,'市值（亿元）','表1：欧美廉航龙头市值超过千亿元 ',format_of_number='亿', format_desc=None) ==1000
    assert number_trans(1000,'市值（亿元）','表1：欧美廉航龙头市值超过千亿元 ',format_of_number='亿', format_desc=None) ==1000
    assert number_trans(1000,'市值（亿元）','表1：欧美廉航龙头市值超过千亿元 ',format_of_number='亿', format_desc=None) ==1000
    assert number_trans(133701,'商品房销售额:累计','表6：2019年房地产销售金额预测（亿元） ',format_of_number=None, format_desc=None) ==133701
    assert number_trans(133701,'商品房销售额:累计','表6：2019年房地产销售金额预测（亿元） ',format_of_number=None, format_desc=None) ==133701
    assert number_trans(133701,'商品房销售额:累计','表6：2019年房地产销售金额预测（亿元） ',format_of_number=None, format_desc=None) ==133701
    assert number_trans(100,'单银幕票房（万元）','图表 21   现有院线的经营情况',format_of_number='亿', format_desc=None) ==1000000
    assert number_trans(50,'2018年票房（亿元）','图表 21   现有院线的经营情况',format_of_number='亿', format_desc=None) ==50
    assert number_trans(100,'单银幕票房（万元）','图表 21   现有院线的经营情况',format_of_number='亿', format_desc=None) ==1000000
    assert number_trans(50,'2018年票房（亿元）','图表 21   现有院线的经营情况',format_of_number='亿', format_desc=None) ==50
    assert number_trans(100,'单银幕票房（万元）','图表 21   现有院线的经营情况',format_of_number='亿', format_desc=None) ==1000000
    assert number_trans(50,'2018年票房（亿元）','图表 21   现有院线的经营情况',format_of_number='亿', format_desc=None) ==50
    assert number_trans(100,'2011同期','表3:2012年一线城市土地成交面积(2011 年初至今)（万平）',format_of_number='万', format_desc='平') ==100
    assert number_trans(100,'2012至今','表3:2012年一线城市土地成交面积(2011 年初至今)（万平）',format_of_number='万', format_desc='平') ==100
    assert number_trans(100,'2011同期','表3:2012年一线城市土地成交面积(2011 年初至今)（万平）',format_of_number='万', format_desc='平') ==100
    assert number_trans(100,'2012至今','表3:2012年一线城市土地成交面积(2011 年初至今)（万平）',format_of_number='万', format_desc='平') ==100
    assert number_trans(100,'2011同期','表3:2012年一线城市土地成交面积(2011 年初至今)（万平）',format_of_number='万', format_desc='平') ==100
    assert number_trans(100,'2012至今','表3:2012年一线城市土地成交面积(2011 年初至今)（万平）',format_of_number='万', format_desc='平') ==100
    assert number_trans(500,'总市值','附表11：2012年06月11日一线公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc='元') ==500
    assert number_trans(500,'总市值','附表11：2012年06月11日一线公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc='元') ==500
    assert number_trans(500,'总市值','附表11：2012年06月11日一线公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number='亿', format_desc='元') ==500
    assert number_trans(30,'观影人次（万）','表6：2019年第2周（2019.1.14 - 2019.1.20）全国院线票房TOP10',format_of_number='万', format_desc=None) ==30
    assert number_trans(30,'观影人次（万）','表6：2019年第2周（2019.1.14 - 2019.1.20）全国院线票房TOP10',format_of_number='万', format_desc=None) ==30
    assert number_trans(30,'观影人次（万）','表6：2019年第2周（2019.1.14 - 2019.1.20）全国院线票房TOP10',format_of_number='万', format_desc=None) ==30
    assert number_trans(30,'总市值（亿元）','表4：A股传媒行业教育公司估值一览（加阴影为华金证券研究所预测，其余为wind一致预期）',format_of_number='亿', format_desc=None) ==30
    assert number_trans(20,'流通市值（亿元）','表4：A股传媒行业教育公司估值一览（加阴影为华金证券研究所预测，其余为wind一致预期）',format_of_number='亿', format_desc=None) ==20
    assert number_trans(30,'总市值（亿元）','表4：A股传媒行业教育公司估值一览（加阴影为华金证券研究所预测，其余为wind一致预期）',format_of_number='亿', format_desc=None) ==30
    assert number_trans(20,'流通市值（亿元）','表4：A股传媒行业教育公司估值一览（加阴影为华金证券研究所预测，其余为wind一致预期）',format_of_number='亿', format_desc=None) ==20
    assert number_trans(30,'总市值（亿元）','表4：A股传媒行业教育公司估值一览（加阴影为华金证券研究所预测，其余为wind一致预期）',format_of_number='亿', format_desc=None) ==30
    assert number_trans(20,'流通市值（亿元）','表4：A股传媒行业教育公司估值一览（加阴影为华金证券研究所预测，其余为wind一致预期）',format_of_number='亿', format_desc=None) ==20
    assert number_trans(10,'归母净利润(亿元)','58表2：高速企业经营性现金流良好 ',format_of_number='亿', format_desc=None) ==10
    assert number_trans(10,'归母净利润(亿元)','58表2：高速企业经营性现金流良好 ',format_of_number='亿', format_desc=None) ==10
    assert number_trans(10,'归母净利润(亿元)','58表2：高速企业经营性现金流良好 ',format_of_number='亿', format_desc=None) ==10
    assert number_trans(100,'上周成交量（万平米）','图16、重点城市新房成交数据 ',format_of_number='万', format_desc='平') ==100
    assert number_trans(100,'上周成交量（万平米）','图16、重点城市新房成交数据 ',format_of_number='万', format_desc='平') ==100
    assert number_trans(100,'上周成交量（万平米）','图16、重点城市新房成交数据 ',format_of_number='万', format_desc='平') ==100
    assert number_trans(180000,'规划建筑面积(万㎡)','表3：300城市土地出让情况预测 ',format_of_number='万', format_desc='平') ==180000
    assert number_trans(180000,'规划建筑面积(万㎡)','表3：300城市土地出让情况预测 ',format_of_number='万', format_desc='平') ==180000
    assert number_trans(180000,'规划建筑面积(万㎡)','表3：300城市土地出让情况预测 ',format_of_number='万', format_desc='平') ==180000
    assert number_trans(150000,'累计值','表5：近年年房地产销售面积预测（万平米） ',format_of_number='万', format_desc='平') ==150000
    assert number_trans(150000,'累计值','表5：近年年房地产销售面积预测（万平米） ',format_of_number='万', format_desc='平') ==150000
    assert number_trans(150000,'累计值','表5：近年年房地产销售面积预测（万平米） ',format_of_number='万', format_desc='平') ==150000
    assert number_trans(10,'10APE','44 附表3：地产行业三线重点公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'10APE','44 附表3：地产行业三线重点公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'12EPE','44 附表3：地产行业三线重点公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(8000,'扩建后旅客吞吐量','表 5 三大机场扩建后设计旅客吞吐量均接近1亿人次（万人次） ',format_of_number='万', format_desc=None) ==8000
    assert number_trans(8000,'扩建后旅客吞吐量','表 5 三大机场扩建后设计旅客吞吐量均接近1亿人次（万人次） ',format_of_number='万', format_desc=None) ==8000
    assert number_trans(8000,'扩建后旅客吞吐量','表 5 三大机场扩建后设计旅客吞吐量均接近1亿人次（万人次） ',format_of_number='万', format_desc=None) ==8000
    assert number_trans(20,'17年营收/亿美元','表2： 全球被动元器件核心上市公司梳理 ',format_of_number='亿', format_desc=None) ==20
    assert number_trans(7,'2018年票房（亿元）','图表 22   符合成立电影院线公司条件的影投公司',format_of_number='亿', format_desc=None) ==7
    assert number_trans(7,'2018年票房（亿元）','图表 22   符合成立电影院线公司条件的影投公司',format_of_number='亿', format_desc=None) ==7
    assert number_trans(7,'2018年票房（亿元）','图表 22   符合成立电影院线公司条件的影投公司',format_of_number='亿', format_desc=None) ==7
    assert number_trans(20,'Jan','92 表18：福州住宅期房2007-2012年1月各月成交面积（万平）           ',format_of_number='万', format_desc='平') ==20
    assert number_trans(20,'Mar','92 表18：福州住宅期房2007-2012年1月各月成交面积（万平）           ',format_of_number='万', format_desc='平') ==20
    assert number_trans(20,'Jun','92 表18：福州住宅期房2007-2012年1月各月成交面积（万平）           ',format_of_number='万', format_desc='平') ==20
    assert number_trans(20,'Feb','92 表18：福州住宅期房2007-2012年1月各月成交面积（万平）           ',format_of_number='万', format_desc='平') ==20
    assert number_trans(20,'Jan','92 表18：福州住宅期房2007-2012年1月各月成交面积（万平）           ',format_of_number='万', format_desc='平') ==20
    assert number_trans(20,'Feb','92 表18：福州住宅期房2007-2012年1月各月成交面积（万平）           ',format_of_number='万', format_desc='平') ==20
    assert number_trans(20,'RNAV','132附表15：2012年06月11日商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'RNAV','132附表15：2012年06月11日商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'RNAV','132附表15：2012年06月11日商业地产公司和关注公司业绩预测及财务估值 （单位：元，亿股，亿元） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(100,'工程投资（亿）','1图表 7 我国特高压建设及投运时间 ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'工程投资（亿）','1图表 7 我国特高压建设及投运时间 ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(8000,'2017年旅客吞吐量（万人次）','表 4 全球主要枢纽机场主基地航空公司份额（2017） ',format_of_number='万', format_desc=None) ==8000
    assert number_trans(8000,'2017年旅客吞吐量（万人次）','表 4 全球主要枢纽机场主基地航空公司份额（2017） ',format_of_number='万', format_desc=None) ==8000
    assert number_trans(8000,'2017年旅客吞吐量（万人次）','表 4 全球主要枢纽机场主基地航空公司份额（2017） ',format_of_number='万', format_desc=None) ==8000
    assert number_trans(20000,'18冬春航班数量','95表2：国内6家廉航公司财务、飞机、基地等情况（亿元） ',format_of_number=None, format_desc=None) ==20000
    assert number_trans(20000,'18冬春航班数量','95表2：国内6家廉航公司财务、飞机、基地等情况（亿元） ',format_of_number=None, format_desc=None) ==20000
    assert number_trans(20000,'18冬春航班数量','95表2：国内6家廉航公司财务、飞机、基地等情况（亿元） ',format_of_number=None, format_desc=None) ==20000
    assert number_trans(3000,'销售收入（百万美元）','表84：2017年全球物流自动化系统集成十五强 ',format_of_number='百万', format_desc=None) ==3000
    assert number_trans(3000,'销售收入（百万美元）','表84：2017年全球物流自动化系统集成十五强 ',format_of_number='百万', format_desc=None) ==3000
    assert number_trans(3000,'销售收入（百万美元）','表84：2017年全球物流自动化系统集成十五强 ',format_of_number='百万', format_desc=None) ==3000
    assert number_trans(1200000,'观影人次（万）','表5：2019年第1周（2019.01.07 - 2019.01.13）全国院线票房TOP10',format_of_number=None, format_desc=None) ==120
    assert number_trans(1200000,'观影人次（万）','表5：2019年第1周（2019.01.07 - 2019.01.13）全国院线票房TOP10',format_of_number=None, format_desc=None) ==120
    assert number_trans(1200000,'观影人次（万）','表5：2019年第1周（2019.01.07 - 2019.01.13）全国院线票房TOP10',format_of_number=None, format_desc=None) ==120
    assert number_trans(5000,'投资额（亿元）','26 表 4  2012年1-5月东中西部地区房地产开发投资情况 ',format_of_number='亿', format_desc=None) ==5000
    assert number_trans(5000,'投资额（亿元）','26 表 4  2012年1-5月东中西部地区房地产开发投资情况 ',format_of_number='亿', format_desc=None) ==5000
    assert number_trans(10,'本周均成交面积','表 4：各城市周均成交面积与同比（万平） ',format_of_number='万', format_desc='平') ==10
    assert number_trans(10,'本周均成交面积','表 4：各城市周均成交面积与同比（万平） ',format_of_number='万', format_desc='平') ==10
    assert number_trans(10,'本周均成交面积','表 4：各城市周均成交面积与同比（万平） ',format_of_number='万', format_desc='平') ==10
    assert number_trans(20,'总市值（亿元）','图表 15   行业涨幅后五',format_of_number='亿', format_desc=None) ==20
    assert number_trans(20,'总市值（亿元）','图表 15   行业涨幅后五',format_of_number='亿', format_desc=None) ==20
    assert number_trans(20,'总市值（亿元）','图表 15   行业涨幅后五',format_of_number='亿', format_desc=None) ==20
    assert number_trans(2,'拨款额（万元）','',format_of_number='万', format_desc=None) ==2
    assert number_trans(2,'拨款额（万元）','',format_of_number='万', format_desc=None) ==2
    assert number_trans(2,'拨款额（万元）','',format_of_number='万', format_desc=None) ==2
    assert number_trans(40,'薪酬(万/年薪)','',format_of_number='万', format_desc=None) ==40
    assert number_trans(40,'薪酬(万/年薪)','',format_of_number='万', format_desc=None) ==40
    assert number_trans(40,'薪酬(万/年薪)','',format_of_number='万', format_desc=None) ==40
    assert number_trans(10,'总投资（万元）','',format_of_number='亿', format_desc=None) ==100000
    assert number_trans(10,'总投资（万元）','',format_of_number='亿', format_desc=None) ==100000
    assert number_trans(10,'总投资（万元）','',format_of_number='亿', format_desc=None) ==100000
    assert number_trans(1,'拨款额（万元）','',format_of_number='万', format_desc='元') ==1
    assert number_trans(1,'拨款额（万元）','',format_of_number='万', format_desc='元') ==1
    assert number_trans(1,'拨款额（万元）','',format_of_number='万', format_desc='元') ==1
    assert number_trans(2,'总投资（万元）','',format_of_number='万', format_desc='元') ==2
    assert number_trans(2,'补助资金（万元）','',format_of_number='万', format_desc='元') ==2
    assert number_trans(2,'总投资（万元）','',format_of_number='万', format_desc='元') ==2
    assert number_trans(2,'补助资金（万元）','',format_of_number='万', format_desc='元') ==2
    assert number_trans(2,'总投资（万元）','',format_of_number='万', format_desc='元') ==2
    assert number_trans(2,'补助资金（万元）','',format_of_number='万', format_desc='元') ==2
    assert number_trans(1,'展位费补贴(万元）','',format_of_number='万', format_desc='元') ==1
    assert number_trans(1,'展位费补贴(万元）','',format_of_number='万', format_desc='元') ==1
    assert number_trans(1,'展位费补贴(万元）','',format_of_number='万', format_desc=None) ==1







    # error start 
    assert number_trans(2,'最新股价','18 表3：内房股上周股价涨幅前十表现 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'最新股价','18 表3：内房股上周股价涨幅前十表现 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'最新股价','18 表3：内房股上周股价涨幅前十表现 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(300,'公里数（km）','表67. 预计2018年新开通高铁线路15条线共计3559公里  ',format_of_number='千', format_desc=None) ==300
    assert number_trans(300,'公里数（km）','表67. 预计2018年新开通高铁线路15条线共计3559公里  ',format_of_number='千', format_desc=None) ==300
    assert number_trans(300,'公里数（km）','表67. 预计2018年新开通高铁线路15条线共计3559公里  ',format_of_number='千', format_desc=None) ==300
    assert number_trans(5,'库存（套）','140表 1：最近一周一线城市新盘成交动态 ',format_of_number='万', format_desc=None) == 50000
    assert number_trans(5,'库存（套）','140表 1：最近一周一线城市新盘成交动态 ',format_of_number='万', format_desc=None) ==50000
    assert number_trans(5,'库存（套）','140表 1：最近一周一线城市新盘成交动态 ',format_of_number='万', format_desc=None) ==50000
    assert number_trans(1000,'库存（套）','140表 1：最近一周一线城市新盘成交动态 ',format_of_number='万', format_desc='平') ==10000000
    assert number_trans(4,'2015股息率','图表3：港口股息率领先标的（%） ',format_of_number=None, format_desc=None) ==4
    assert number_trans(4,'2015股息率','图表3：港口股息率领先标的（%） ',format_of_number=None, format_desc=None) ==4
    assert number_trans(4,'2017股息率','图表3：港口股息率领先标的（%） ',format_of_number=None, format_desc=None) ==4
    assert number_trans(1,'日成交','02 表2：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'日成交环比','02 表2：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'日成交','02 表2：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'日成交环比','02 表2：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'日成交','02 表2：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'日成交环比','02 表2：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(10,'股价2018/12/28','表25：证券行业重点覆盖公司估值比较表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(1,'PE19E','表25：证券行业重点覆盖公司估值比较表 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'PE17A','表25：证券行业重点覆盖公司估值比较表 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(10,'股价2018/12/28','表25：证券行业重点覆盖公司估值比较表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'股价2018/12/28','表25：证券行业重点覆盖公司估值比较表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(1,'收益率','表25：证券行业重点覆盖公司估值比较表 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(6,'7日成交环比','37 表：主要城市成交信息一览表（粗体标注的城市已出台限购令，5月25日为T日） ',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'7日成交同比','37 表：主要城市成交信息一览表（粗体标注的城市已出台限购令，5月25日为T日） ',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'7日成交环比','37 表：主要城市成交信息一览表（粗体标注的城市已出台限购令，5月25日为T日） ',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'7日成交同比','37 表：主要城市成交信息一览表（粗体标注的城市已出台限购令，5月25日为T日） ',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'7日成交同比','37 表：主要城市成交信息一览表（粗体标注的城市已出台限购令，5月25日为T日） ',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'7日成交同比','37 表：主要城市成交信息一览表（粗体标注的城市已出台限购令，5月25日为T日） ',format_of_number=None, format_desc=None) ==6
    assert number_trans(1000,'绝对量','134 图1: 2012年1-4月房地产行业表现：',format_of_number=None, format_desc=None) ==1000
    assert number_trans(10,'同比增长（%）','134 图1: 2012年1-4月房地产行业表现：',format_of_number=None, format_desc=None) ==10
    assert number_trans(1000,'绝对量','134 图1: 2012年1-4月房地产行业表现：',format_of_number=None, format_desc=None) ==1000
    assert number_trans(10,'同比增长（%）','134 图1: 2012年1-4月房地产行业表现：',format_of_number=None, format_desc=None) ==10
    assert number_trans(1000,'绝对量','134 图1: 2012年1-4月房地产行业表现：',format_of_number=None, format_desc=None) ==1000
    assert number_trans(10,'同比增长（%）','134 图1: 2012年1-4月房地产行业表现：',format_of_number=None, format_desc=None) ==10
    assert number_trans(1,'收视率（%）','图表 23   1.26电视剧收视率 TOP10',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'收视率（%）','图表 23   1.26电视剧收视率 TOP10',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'收视率（%）','图表 23   1.26电视剧收视率 TOP10',format_of_number=None, format_desc=None) ==1
    assert number_trans(100,'股价','表5：海外传媒互联网公司盈利预测及估值一览',format_of_number=None, format_desc=None) ==100
    assert number_trans(3,'EPS17A','表5：海外传媒互联网公司盈利预测及估值一览',format_of_number=None, format_desc=None) ==3
    assert number_trans(100,'股价','表5：海外传媒互联网公司盈利预测及估值一览',format_of_number=None, format_desc=None) ==100
    assert number_trans(3,'EPS17A','表5：海外传媒互联网公司盈利预测及估值一览',format_of_number=None, format_desc='元') ==3
    assert number_trans(10,'达美航空','101表10：1989~2017年7个阶段西南航空股价表现几乎均强于三大航 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'联合大陆航空','101表10：1989~2017年7个阶段西南航空股价表现几乎均强于三大航 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'达美航空','101表10：1989~2017年7个阶段西南航空股价表现几乎均强于三大航 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(11,'PE19E','11表11：行业重点上市公司估值表 ',format_of_number=None, format_desc=None) ==11
    assert number_trans(11,'PE19E','11表11：行业重点上市公司估值表 ',format_of_number=None, format_desc=None) ==11
    assert number_trans(11,'PE19E','11表11：行业重点上市公司估值表 ',format_of_number=None, format_desc=None) ==11
    assert number_trans(30,'溢价','43 表1：上周住宅用地成交活跃度城市 ',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'溢价','43 表1：上周住宅用地成交活跃度城市 ',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'溢价','43 表1：上周住宅用地成交活跃度城市 ',format_of_number=None, format_desc=None) ==30
    assert number_trans(20,'票房占比（%）','表3：2019年第4周（2019.01.28 - 2019.02.03）全国电影票房TOP10',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'票房占比（%）','表3：2019年第4周（2019.01.28 - 2019.02.03）全国电影票房TOP10',format_of_number=None, format_desc=None) ==20
    assert number_trans(5,'最新收盘价','图表18：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'最新收盘价','图表18：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'最新收盘价','图表18：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'同比(5月全月)','42 表2：45个重点跟踪城市分类成交概况 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(1,'同比(2012年累计)','42 表2：45个重点跟踪城市分类成交概况 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(10,'同比(5月全月)','42 表2：45个重点跟踪城市分类成交概况 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(1,'同比(2012年累计)','42 表2：45个重点跟踪城市分类成交概况 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(10,'同比(5月全月)','42 表2：45个重点跟踪城市分类成交概况 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(1,'同比(2012年累计)','42 表2：45个重点跟踪城市分类成交概况 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(10,'占总收入比重','图表 28   达美辅助收入 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(100,'人均（总乘客数计）','图表 28   达美辅助收入 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'人均（总乘客数计）','图表 28   达美辅助收入 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(10,'占总收入比重','图表 28   达美辅助收入 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'占总收入比重','图表 28   达美辅助收入 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(100,'人均（总乘客数计）','图表 28   达美辅助收入 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(6,'最新收盘价','图表21：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'增发价格','图表21：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'最新收盘价','图表21：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'增发价格','图表21：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'最新收盘价','图表21：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'增发价格','图表21：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==6
    print(number_trans(200,'本年累计','08 表8:16个重点城市住宅土地供应对比表(单位:万平米) ',format_of_number='万', format_desc='平'))
    assert number_trans(200,'本年累计','08 表8:16个重点城市住宅土地供应对比表(单位:万平米) ',format_of_number='万', format_desc='平') ==200
    assert number_trans(200,'本年累计','08 表8:16个重点城市住宅土地供应对比表(单位:万平米) ',format_of_number='万', format_desc='平') ==200
    assert number_trans(200,'本年累计','08 表8:16个重点城市住宅土地供应对比表(单位:万平米) ',format_of_number='万', format_desc='平') ==200
    assert number_trans(2000,'本周销量（套）','140表 1：最近一周一线城市新盘成交动态 ',format_of_number=None, format_desc=None) ==2000
    assert number_trans(20,'本周销量（套）','140表 1：最近一周一线城市新盘成交动态 ',format_of_number='万', format_desc='平') ==200000
    assert number_trans(2000,'本周销量（套）','140表 1：最近一周一线城市新盘成交动态 ',format_of_number=None, format_desc=None) ==2000
    assert number_trans(20,'本周销量（套）','140表 1：最近一周一线城市新盘成交动态 ',format_of_number='万', format_desc='平') ==200000
    assert number_trans(2000,'本周销量（套）','140表 1：最近一周一线城市新盘成交动态 ',format_of_number=None, format_desc=None) ==2000
    assert number_trans(20,'本周销量（套）','140表 1：最近一周一线城市新盘成交动态 ',format_of_number='万', format_desc='平') ==200000
    assert number_trans(10,'同比增长（%）','18 表 3：2012年1-5月全国房地产开发投资及销售情况（房屋新开工面积（万平方米））',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'同比增长（%）','18 表 3：2012年1-5月全国房地产开发投资及销售情况（房屋新开工面积（万平方米））',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'同比增长（%）','18 表 3：2012年1-5月全国房地产开发投资及销售情况（房屋新开工面积（万平方米））',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'最新股价','03 表 1：地产板块一周跌幅前列公司情况',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'最新股价','03 表 1：地产板块一周跌幅前列公司情况',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'最新股价','03 表 1：地产板块一周跌幅前列公司情况',format_of_number=None, format_desc=None) ==5
    assert number_trans(1000,'月成交量','05 表 4:大城市一周成交情况',format_of_number=None, format_desc=None) ==1000
    assert number_trans(100,'同比增长','05 表 4:大城市一周成交情况',format_of_number=None, format_desc=None) ==100
    assert number_trans(1000,'月成交量','05 表 4:大城市一周成交情况',format_of_number=None, format_desc=None) ==1000
    assert number_trans(100,'同比增长','05 表 4:大城市一周成交情况',format_of_number=None, format_desc=None) ==100
    assert number_trans(1000,'月成交量','05 表 4:大城市一周成交情况',format_of_number=None, format_desc=None) ==1000
    assert number_trans(100,'同比增长','05 表 4:大城市一周成交情况',format_of_number=None, format_desc=None) ==100
    assert number_trans(10,'上周','表10:四城市一手房成交对比（单位：万平方米）',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'最新收盘价','图表11：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'最新收盘价','图表11：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==5
    assert number_trans(0,'引进窄体机','149图表10： 2019年飞机引进计划      ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'退出窄体机','149图表10： 2019年飞机引进计划      ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'引进窄体机','149图表10： 2019年飞机引进计划      ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'退出窄体机','149图表10： 2019年飞机引进计划      ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'引进窄体机','149图表10： 2019年飞机引进计划      ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'退出窄体机','149图表10： 2019年飞机引进计划      ',format_of_number=None, format_desc=None) ==0
    assert number_trans(1,'EPS18E','55图表92：公路行业重点推荐公司估值表 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS19E','55图表92：公路行业重点推荐公司估值表 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'PE19E','55图表92：公路行业重点推荐公司估值表 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS18E','55图表92：公路行业重点推荐公司估值表 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS20E','55图表92：公路行业重点推荐公司估值表 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS18E','55图表92：公路行业重点推荐公司估值表 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS20E','55图表92：公路行业重点推荐公司估值表 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS18E','55图表92：公路行业重点推荐公司估值表 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS19E','55图表92：公路行业重点推荐公司估值表 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS18E','55图表92：公路行业重点推荐公司估值表 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'最新股价','62  表4：2012年6月17日内房股上周股价跌幅前十表现    ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'最新股价','62  表4：2012年6月17日内房股上周股价跌幅前十表现    ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'最新股价','62  表4：2012年6月17日内房股上周股价跌幅前十表现    ',format_of_number=None, format_desc=None) ==1
    assert number_trans(5,'2012年日均成交','27 表：主要城市成交信息一览表（粗体标注的城市已出台限购令，5月23日为T日） ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'2012年日均成交','27 表：主要城市成交信息一览表（粗体标注的城市已出台限购令，5月23日为T日） ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'2012年日均成交','27 表：主要城市成交信息一览表（粗体标注的城市已出台限购令，5月23日为T日） ',format_of_number=None, format_desc=None) ==5
    assert number_trans(1,'较上年','177表5：山西喷吹煤产地价格持平 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'较上年','177表5：山西喷吹煤产地价格持平 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'上年','177表5：山西喷吹煤产地价格持平 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(10,'收盘价(元)','04 表4重点覆盖公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'收盘价(元)','04 表4重点覆盖公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'收盘价(元)','04 表4重点覆盖公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'收盘价(元)','04 表4重点覆盖公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(500,'近4周周均成交','73 表3：2012-05-30房地产重点城市成交数据二 ',format_of_number=None, format_desc=None) ==500
    assert number_trans(500,'近4周周均成交','73 表3：2012-05-30房地产重点城市成交数据二 ',format_of_number=None, format_desc=None) ==500
    assert number_trans(500,'近4周周均成交','73 表3：2012-05-30房地产重点城市成交数据二 ',format_of_number=None, format_desc=None) ==500
    assert number_trans(25,'本周环比','表6:二线城市一手房成交周同比、环比对比 ',format_of_number=None, format_desc=None) ==25
    assert number_trans(25,'本周环比','表6:二线城市一手房成交周同比、环比对比 ',format_of_number=None, format_desc=None) ==25
    assert number_trans(25,'本周环比','表6:二线城市一手房成交周同比、环比对比 ',format_of_number=None, format_desc=None) ==25
    assert number_trans(10,'收盘价','图表8：中概股美股行情',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'周涨跌幅','图表8：中概股美股行情',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'收盘价','图表8：中概股美股行情',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'周涨跌幅','图表8：中概股美股行情',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'收盘价','图表8：中概股美股行情',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'周涨跌幅','图表8：中概股美股行情',format_of_number=None, format_desc=None) ==10
    assert number_trans(0,'PE-TTM','图52：汽车电子板块估值 ',format_of_number=None, format_desc='股') ==0
    assert number_trans(0,'PE-TTM','图52：汽车电子板块估值 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(5,'2012年4月成交量环比','63 表2：重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'2012年4月成交量环比','63 表2：重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'2012年4月成交量环比','63 表2：重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==5
    assert number_trans(6,'PE2012E','34 表6：2012年6月住宅开发关注类公司估值表 ',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'PB估值','34 表6：2012年6月住宅开发关注类公司估值表 ',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'PE2012E','34 表6：2012年6月住宅开发关注类公司估值表 ',format_of_number=None, format_desc=None) ==6
    assert number_trans(7000,'扩产产能（吨）','表：主要正极厂商高镍产能单位投资情况 ',format_of_number=None, format_desc='吨') ==7000
    assert number_trans(7000,'扩产产能（吨）','表：主要正极厂商高镍产能单位投资情况 ',format_of_number=None, format_desc='吨') ==7000
    assert number_trans(7000,'扩产产能（吨）','表：主要正极厂商高镍产能单位投资情况 ',format_of_number=None, format_desc='吨') ==7000
    assert number_trans(10,'成交面积同比11年','74 表2：除一线外主要城市2012年1-5月累计住宅/商品房成交量 1',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'成交面积同比11年','74 表2：除一线外主要城市2012年1-5月累计住宅/商品房成交量 1',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'成交面积同比11年','74 表2：除一线外主要城市2012年1-5月累计住宅/商品房成交量 1',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'成交面积同比11年','74 表2：除一线外主要城市2012年1-5月累计住宅/商品房成交量 1',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'成交面积同比11年','74 表2：除一线外主要城市2012年1-5月累计住宅/商品房成交量 1',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'成交面积同比11年','74 表2：除一线外主要城市2012年1-5月累计住宅/商品房成交量 1',format_of_number=None, format_desc=None) ==10
    assert number_trans(3,'销售收入排名','表84：2017年全球物流自动化系统集成十五强 ',format_of_number=None, format_desc=None) ==3
    assert number_trans(15,'同比增长率','表84：2017年全球物流自动化系统集成十五强 ',format_of_number=None, format_desc=None) ==15
    assert number_trans(15,'同比增长率','表84：2017年全球物流自动化系统集成十五强 ',format_of_number=None, format_desc=None) ==15
    assert number_trans(15,'同比增长率','表84：2017年全球物流自动化系统集成十五强 ',format_of_number=None, format_desc=None) ==15
    assert number_trans(500,'近4周周均成交','73 表3：2012-05-30房地产重点城市成交数据二 ',format_of_number=None, format_desc=None) ==500
    assert number_trans(1,'近4周周均成交环比','73 表3：2012-05-30房地产重点城市成交数据二 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(500,'近4周周均成交','73 表3：2012-05-30房地产重点城市成交数据二 ',format_of_number=None, format_desc=None) ==500
    assert number_trans(1,'近4周周均成交环比','73 表3：2012-05-30房地产重点城市成交数据二 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(500,'近4周周均成交','73 表3：2012-05-30房地产重点城市成交数据二 ',format_of_number=None, format_desc=None) ==500
    assert number_trans(1,'近4周周均成交环比','73 表3：2012-05-30房地产重点城市成交数据二 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(10,'最新股价','34 表6：2012年6月住宅开发关注类公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'最新股价','34 表6：2012年6月住宅开发关注类公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'最新股价','34 表6：2012年6月住宅开发关注类公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'日成交环比','03表3：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(2,'日成交','03表3：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'日成交','03表3：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(10,'日成交环比','03表3：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(2,'日成交环比','03表3：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(10,'日成交环比','03表3：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10000,'楼盘均价','08表2：苏州2012年4月新盘去化及价格比较情况（单位：元/平） ',format_of_number=None, format_desc=None) ==10000
    assert number_trans(1,'楼盘容积率','08表2：苏州2012年4月新盘去化及价格比较情况（单位：元/平） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'楼盘容积率','08表2：苏州2012年4月新盘去化及价格比较情况（单位：元/平） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(10000,'楼盘均价','08表2：苏州2012年4月新盘去化及价格比较情况（单位：元/平） ',format_of_number=None, format_desc=None) ==10000
    assert number_trans(1,'楼盘容积率','08表2：苏州2012年4月新盘去化及价格比较情况（单位：元/平） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(10000,'楼盘均价','08表2：苏州2012年4月新盘去化及价格比较情况（单位：元/平） ',format_of_number=None, format_desc=None) ==10000
    assert number_trans(10,'PE-17','表2煤炭行业炼焦煤估值比较 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'PE-19E','表2煤炭行业炼焦煤估值比较 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'PE-17','表2煤炭行业炼焦煤估值比较 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'PE-18E','表2煤炭行业炼焦煤估值比较 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'PE-17','表2煤炭行业炼焦煤估值比较 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'PE-18E','表2煤炭行业炼焦煤估值比较 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(1000000,'2016','144表11：广深铁路盈利预测 ',format_of_number=None, format_desc=None) ==1000000
    assert number_trans(1000000,'2016','144表11：广深铁路盈利预测 ',format_of_number=None, format_desc='元') ==1000000
    assert number_trans(1,'2016','144表11：广深铁路盈利预测 ',format_of_number='百万', format_desc='元') ==1000000
    assert number_trans(10,'股权比例','35 表3 园区开发公司转型有望提升估值 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(20,'利润率','35 表3 园区开发公司转型有望提升估值 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(10,'股权比例','35 表3 园区开发公司转型有望提升估值 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(20,'利润率','35 表3 园区开发公司转型有望提升估值 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(10,'股权比例','35 表3 园区开发公司转型有望提升估值 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(20,'利润率','35 表3 园区开发公司转型有望提升估值 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(18,'本周换手率（%）','04图表28运输业A股个股市场表现-本周涨跌幅后10 ',format_of_number=None, format_desc=None) ==18
    assert number_trans(18,'本周换手率（%）','04图表28运输业A股个股市场表现-本周涨跌幅后10 ',format_of_number=None, format_desc=None) ==18
    assert number_trans(30,'2012年销售额','87 图表2：2012年07月08日重点跟踪公司上下半年销售情况预测',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'1H2011销售额','87 图表2：2012年07月08日重点跟踪公司上下半年销售情况预测',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'1H2011销售额','87 图表2：2012年07月08日重点跟踪公司上下半年销售情况预测',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'2012年销售额','87 图表2：2012年07月08日重点跟踪公司上下半年销售情况预测',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'2012年销售额','87 图表2：2012年07月08日重点跟踪公司上下半年销售情况预测',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'1H2011销售额','87 图表2：2012年07月08日重点跟踪公司上下半年销售情况预测',format_of_number=None, format_desc=None) ==30
    assert number_trans(5,'累计值同比增速','表5：近年年房地产销售面积预测（万平米） ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'一线同比增速','表5：近年年房地产销售面积预测（万平米） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'累计值','表5：近年年房地产销售面积预测（万平米） ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'一线同比增速','表5：近年年房地产销售面积预测（万平米） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'累计值同比增速','表5：近年年房地产销售面积预测（万平米） ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'一线城市','表5：近年年房地产销售面积预测（万平米） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'最新股价','33 表7：2012年06月03日非住宅类开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==10
    assert number_trans(1,'EPS2011','33 表7：2012年06月03日非住宅类开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS2011','33 表7：2012年06月03日非住宅类开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==1
    assert number_trans(10,'最新股价','33 表7：2012年06月03日非住宅类开发重点覆盖公司估值表  ',format_of_number=None, format_desc='元') ==10
    assert number_trans(1,'EPS2011','33 表7：2012年06月03日非住宅类开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==1
    assert number_trans(10,'最新股价','33 表7：2012年06月03日非住宅类开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==10
    assert number_trans(2,'本周均成交面积','表 4：各城市周均成交面积与同比（万平） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'上周均成交面积','表 4：各城市周均成交面积与同比（万平） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'本周均成交面积','表 4：各城市周均成交面积与同比（万平） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'上周均成交面积','表 4：各城市周均成交面积与同比（万平） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'本周均成交面积','表 4：各城市周均成交面积与同比（万平） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'上周均成交面积','表 4：各城市周均成交面积与同比（万平） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(100,'同比','表 4：各城市周均成交面积与同比（万平） ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'同比','表 4：各城市周均成交面积与同比（万平） ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'同比','表 4：各城市周均成交面积与同比（万平） ',format_of_number=None, format_desc=None) ==100
    assert number_trans(5,'收盘价（元）','图8： 本周个股涨跌幅排名(跌幅前十)  ',format_of_number=None, format_desc='元') ==5
    assert number_trans(1,'周涨跌（%）','图8： 本周个股涨跌幅排名(跌幅前十)  ',format_of_number=None, format_desc=None) ==1
    assert number_trans(5,'收盘价（元）','图8： 本周个股涨跌幅排名(跌幅前十)  ',format_of_number=None, format_desc='元') ==5
    assert number_trans(1,'周涨跌（%）','图8： 本周个股涨跌幅排名(跌幅前十)  ',format_of_number=None, format_desc=None) ==1
    assert number_trans(5,'收盘价（元）','图8： 本周个股涨跌幅排名(跌幅前十)  ',format_of_number=None, format_desc='元') ==5
    assert number_trans(1,'周涨跌（%）','图8： 本周个股涨跌幅排名(跌幅前十)  ',format_of_number=None, format_desc=None) ==1
    assert number_trans(200,'线路长度（公里）','表90：预计2018年部分通车高铁线路 ',format_of_number=None, format_desc=None) ==200
    assert number_trans(200,'线路长度（公里）','表90：预计2018年部分通车高铁线路 ',format_of_number=None, format_desc=None) ==200
    assert number_trans(200,'线路长度（公里）','表90：预计2018年部分通车高铁线路 ',format_of_number=None, format_desc=None) ==200
    assert number_trans(2,'PB','06 表 5：住宅开发重点跟踪公司一览 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'PB','06 表 5：住宅开发重点跟踪公司一览 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'PB','06 表 5：住宅开发重点跟踪公司一览 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(0,'本周涨跌幅','43图表2：交运子板块行情 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'本月涨跌幅','43图表2：交运子板块行情 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'今年以来','43图表2：交运子板块行情 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'本周涨跌幅','43图表2：交运子板块行情 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'本月涨跌幅','43图表2：交运子板块行情 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'今年以来','43图表2：交运子板块行情 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(100,'年初至今累计销售面积','50 表2012年第23周（2012.5.28-2012.6.3） 二手成交数据（万平米）',format_of_number='万', format_desc='平') ==100
    # assert number_trans(100,'年初至今累计销售面积','50 表2012年第23周（2012.5.28-2012.6.3） 二手成交数据（万平米）',format_of_number='万', format_desc='平') ==100
    # assert number_trans(100,'年初至今累计销售面积','50 表2012年第23周（2012.5.28-2012.6.3） 二手成交数据（万平米）',format_of_number='万', format_desc='平') ==100
    assert number_trans(1000,'上周成交量（套）','56 表4：跟踪的中部城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==1000
    assert number_trans(10,'成交量同比增长','56 表4：跟踪的中部城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(1000,'上周成交量（套）','56 表4：跟踪的中部城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==1000
    assert number_trans(10,'成交量同比增长','56 表4：跟踪的中部城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(1000,'上周成交量（套）','56 表4：跟踪的中部城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==1000
    assert number_trans(10,'成交量同比增长','56 表4：跟踪的中部城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(3,'最新收盘价','130表4市值前十航运业上市公司股价表现 ',format_of_number=None, format_desc=None) ==3
    assert number_trans(2,'最新涨跌幅','130表4市值前十航运业上市公司股价表现 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'最新涨跌幅','130表4市值前十航运业上市公司股价表现 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(3,'最新收盘价','130表4市值前十航运业上市公司股价表现 ',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'最新收盘价','130表4市值前十航运业上市公司股价表现 ',format_of_number=None, format_desc=None) ==3
    assert number_trans(2,'最新涨跌幅','130表4市值前十航运业上市公司股价表现 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(1,'周涨跌幅（%）','图51：汽车电子板块市场表现 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'月涨跌幅（%）','图51：汽车电子板块市场表现 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'周涨跌幅（%）','图51：汽车电子板块市场表现 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'月涨跌幅（%）','图51：汽车电子板块市场表现 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'周涨跌幅（%）','图51：汽车电子板块市场表现 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'月涨跌幅（%）','图51：汽车电子板块市场表现 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(0,'上年','177表5：山西喷吹煤产地价格持平 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'上年','177表5：山西喷吹煤产地价格持平 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'较上月','177表5：山西喷吹煤产地价格持平 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'上年','177表5：山西喷吹煤产地价格持平 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'上年','177表5：山西喷吹煤产地价格持平 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'较上月','177表5：山西喷吹煤产地价格持平 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(1000,'本周销售套数','49 表2012年第23周（2012.5.28-2012.6.3） 新房成交数据 2',format_of_number=None, format_desc=None) ==1000
    assert number_trans(1000,'本周销售套数','49 表2012年第23周（2012.5.28-2012.6.3） 新房成交数据 2',format_of_number=None, format_desc=None) ==1000
    assert number_trans(20,'净利率','图表 72   2015 年京沪高铁与上市公司ROE对比 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'资产负债率','图表 72   2015 年京沪高铁与上市公司ROE对比 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'资产负债率','图表 72   2015 年京沪高铁与上市公司ROE对比 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'净利率','图表 72   2015 年京沪高铁与上市公司ROE对比 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'净利率','图表 72   2015 年京沪高铁与上市公司ROE对比 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'资产负债率','图表 72   2015 年京沪高铁与上市公司ROE对比 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'货币资金/净资产','227表 25：2018Q3出版发行公司货币资金分析',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'货币资金/总资产','227表 25：2018Q3出版发行公司货币资金分析',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'货币资金/总资产','227表 25：2018Q3出版发行公司货币资金分析',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'货币资金/总资产','227表 25：2018Q3出版发行公司货币资金分析',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'货币资金/净资产','227表 25：2018Q3出版发行公司货币资金分析',format_of_number=None, format_desc=None) ==20
    assert number_trans(600,'日熔量（吨）','表41：2018年我国冷修玻璃产线情况 ',format_of_number=None, format_desc='吨') ==600
    assert number_trans(600,'日熔量（吨）','表41：2018年我国冷修玻璃产线情况 ',format_of_number=None, format_desc='吨') ==600
    assert number_trans(600,'日熔量（吨）','表41：2018年我国冷修玻璃产线情况 ',format_of_number=None, format_desc='吨') ==600
    assert number_trans(5,'定增价除权后至今价格','图表16：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'定增价除权后至今价格','图表16：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'定增价除权后至今价格','图表16：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==5
    assert number_trans(2011,'较11年均值增长','77 表 1：最近一周新盘成交动态 ',format_of_number=None, format_desc=None) ==2011
    assert number_trans(12,'本周价格-元/平米','77 表 1：最近一周新盘成交动态 ',format_of_number=None, format_desc=None) ==12
    assert number_trans(2011,'较11年均值增长','77 表 1：最近一周新盘成交动态 ',format_of_number=None, format_desc=None) ==2011
    assert number_trans(12,'本周价格环比','77 表 1：最近一周新盘成交动态 ',format_of_number=None, format_desc=None) ==12
    assert number_trans(2011,'本周价格-元/平米','77 表 1：最近一周新盘成交动态 ',format_of_number=None, format_desc=None) ==2011
    assert number_trans(12,'本周价格-元/平米','77 表 1：最近一周新盘成交动态 ',format_of_number=None, format_desc=None) ==12
    assert number_trans(600,'2018E绝对值','50表10：2016-2020年主要公司客机数进情况      ',format_of_number=None, format_desc=None) ==600
    assert number_trans(600,'2019E绝对值','50表10：2016-2020年主要公司客机数进情况      ',format_of_number=None, format_desc=None) ==600
    assert number_trans(600,'2018E绝对值','50表10：2016-2020年主要公司客机数进情况      ',format_of_number=None, format_desc=None) ==600
    assert number_trans(600,'2019E绝对值','50表10：2016-2020年主要公司客机数进情况      ',format_of_number=None, format_desc=None) ==600
    assert number_trans(600,'2018E绝对值','50表10：2016-2020年主要公司客机数进情况      ',format_of_number=None, format_desc=None) ==600
    assert number_trans(600,'2019E绝对值','50表10：2016-2020年主要公司客机数进情况      ',format_of_number=None, format_desc=None) ==600
    assert number_trans(8,'目前','81 表2:典型一线城市去化时间 ',format_of_number=None, format_desc=None) ==8
    assert number_trans(10,'11年底','81 表2:典型一线城市去化时间 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'11年底','81 表2:典型一线城市去化时间 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(8,'目前','81 表2:典型一线城市去化时间 ',format_of_number=None, format_desc=None) ==8
    assert number_trans(8,'目前','81 表2:典型一线城市去化时间 ',format_of_number=None, format_desc=None) ==8
    assert number_trans(10,'11年底','81 表2:典型一线城市去化时间 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(400,'线路长度(公里）','表68. 近2年拟开通的铁路新项目，总投资超过13400亿元',format_of_number=None, format_desc=None) ==400
    assert number_trans(400,'线路长度(公里）','表68. 近2年拟开通的铁路新项目，总投资超过13400亿元',format_of_number=None, format_desc=None) ==400
    assert number_trans(400,'线路长度(公里）','表68. 近2年拟开通的铁路新项目，总投资超过13400亿元',format_of_number=None, format_desc=None) ==400
    assert number_trans(20,'大型金融机构调整前','16 表2: 07年以来历次降准 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'大型金融机构调整后','16 表2: 07年以来历次降准 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'大型金融机构调整幅度','16 表2: 07年以来历次降准 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'大型金融机构调整前','16 表2: 07年以来历次降准 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'大型金融机构调整前','16 表2: 07年以来历次降准 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'大型金融机构调整幅度','16 表2: 07年以来历次降准 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(100,'服务器','图表 19   2019年第 4周（1.21-1.27）网页游戏开服排行榜TOP6-10（仅列上市公司游戏）',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'服务器','图表 19   2019年第 4周（1.21-1.27）网页游戏开服排行榜TOP6-10（仅列上市公司游戏）',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'服务器','图表 19   2019年第 4周（1.21-1.27）网页游戏开服排行榜TOP6-10（仅列上市公司游戏）',format_of_number=None, format_desc=None) ==100
    assert number_trans(5000,'扩产产能（吨）','表：主要正极厂商高镍产能单位投资情况 ',format_of_number=None, format_desc='吨') ==5000
    assert number_trans(5000,'扩产产能（吨）','表：主要正极厂商高镍产能单位投资情况 ',format_of_number=None, format_desc='吨') ==5000
    assert number_trans(5000,'扩产产能（吨）','表：主要正极厂商高镍产能单位投资情况 ',format_of_number=None, format_desc='吨') ==5000
    assert number_trans(10,'股价','21 表5：住宅开发公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'股价','21 表5：住宅开发公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'股价','21 表5：住宅开发公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(500,'2011周平均成交量','55 表3：跟踪的珠三角城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==500
    assert number_trans(0,'成交量同比增长','55 表3：跟踪的珠三角城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(500,'2011周平均成交量','55 表3：跟踪的珠三角城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==500
    assert number_trans(0,'成交量同比增长','55 表3：跟踪的珠三角城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(500,'2011周平均成交量','55 表3：跟踪的珠三角城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==500
    assert number_trans(100,'里程','65表12：路段收费情况（截止2018年12月17日） ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'权益','65表12：路段收费情况（截止2018年12月17日） ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'里程','65表12：路段收费情况（截止2018年12月17日） ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'权益','65表12：路段收费情况（截止2018年12月17日） ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'里程','65表12：路段收费情况（截止2018年12月17日） ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'权益','65表12：路段收费情况（截止2018年12月17日） ',format_of_number=None, format_desc=None) ==100
    assert number_trans(7,'豆瓣评分','表5：票房排名前20的网文IP改编国产电影',format_of_number=None, format_desc=None) ==7
    assert number_trans(7,'豆瓣评分','表5：票房排名前20的网文IP改编国产电影',format_of_number=None, format_desc=None) ==7
    assert number_trans(7,'豆瓣评分','表5：票房排名前20的网文IP改编国产电影',format_of_number=None, format_desc=None) ==7
    assert number_trans(3000,'本周指数','43图表2：交运子板块行情 ',format_of_number=None, format_desc=None) ==3000
    assert number_trans(3000,'本周指数','43图表2：交运子板块行情 ',format_of_number=None, format_desc=None) ==3000
    assert number_trans(3000,'本周指数','43图表2：交运子板块行情 ',format_of_number=None, format_desc=None) ==3000
    assert number_trans(5,'利润同比增速','表 9 快递公司的净利润及其增速（2018Q3） ',format_of_number='亿', format_desc=None) ==500000000
    assert number_trans(5,'利润同比增速','表 9 快递公司的净利润及其增速（2018Q3） ',format_of_number='亿', format_desc=None) ==500000000
    assert number_trans(20,'PE2012E','65表5: 2012年6月园区类地产公司盈利预测和估值',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2013E','65表5: 2012年6月园区类地产公司盈利预测和估值',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2011','65表5: 2012年6月园区类地产公司盈利预测和估值',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2012E','65表5: 2012年6月园区类地产公司盈利预测和估值',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2011','65表5: 2012年6月园区类地产公司盈利预测和估值',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2012E','65表5: 2012年6月园区类地产公司盈利预测和估值',format_of_number=None, format_desc=None) ==20
    assert number_trans(5,'2013','80表 1 首都机场2013-2015及2016前三季度毛利率情况 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'2014','80表 1 首都机场2013-2015及2016前三季度毛利率情况 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'2013','80表 1 首都机场2013-2015及2016前三季度毛利率情况 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'2014','80表 1 首都机场2013-2015及2016前三季度毛利率情况 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'2013','80表 1 首都机场2013-2015及2016前三季度毛利率情况 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'2014','80表 1 首都机场2013-2015及2016前三季度毛利率情况 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'2012/4成交面积','70 表1：一线城市2012年5月住宅/商品房成交量            ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'11年均值','70 表1：一线城市2012年5月住宅/商品房成交量            ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2012/4成交面积','70 表1：一线城市2012年5月住宅/商品房成交量            ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'11年均值','70 表1：一线城市2012年5月住宅/商品房成交量            ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'11年均值','70 表1：一线城市2012年5月住宅/商品房成交量            ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'11年均值','70 表1：一线城市2012年5月住宅/商品房成交量            ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2012/4成交面积','70 表1：一线城市2012年5月住宅/商品房成交量            ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'11年均值','70 表1：一线城市2012年5月住宅/商品房成交量            ',format_of_number=None, format_desc=None) ==10
    assert number_trans(400,'去年同期28日均成交','78 表 1：2012-05-31房地产  重点城市成交数据一 ',format_of_number=None, format_desc=None) ==400
    assert number_trans(400,'去年同期28日均成交','78 表 1：2012-05-31房地产  重点城市成交数据一 ',format_of_number=None, format_desc=None) ==400
    assert number_trans(400,'去年同期28日均成交','78 表 1：2012-05-31房地产  重点城市成交数据一 ',format_of_number=None, format_desc=None) ==400
    assert number_trans(3,'调整前','41 表1：6月8日利率调整表（单位%） ',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'调整后','41 表1：6月8日利率调整表（单位%） ',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'调整前','41 表1：6月8日利率调整表（单位%） ',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'调整后','41 表1：6月8日利率调整表（单位%） ',format_of_number=None, format_desc=None) ==3
    assert number_trans(10,'股价','23 非住宅公司估值表',format_of_number=None, format_desc='元') ==10
    assert number_trans(10,'股价','23 非住宅公司估值表',format_of_number=None, format_desc='元') ==10
    assert number_trans(10,'股价','23 非住宅公司估值表',format_of_number=None, format_desc=None) ==10
    assert number_trans(3,'RNAV','27 2012-05-22 -26个城市周交易报（5.14-5.20）    ',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'PB','27 2012-05-22 -26个城市周交易报（5.14-5.20）    ',format_of_number=None, format_desc=None) ==3
    assert number_trans(10,'PB','27 2012-05-22 -26个城市周交易报（5.14-5.20）    ',format_of_number=None, format_desc=None) ==10
    assert number_trans(1000,'商誉B/净利润','表 3：2018年三季报传媒个股商誉情况一览（净资产或净利润为负的不统计）',format_of_number=None, format_desc=None) ==1000
    assert number_trans(1000,'商誉B/净利润','表 3：2018年三季报传媒个股商誉情况一览（净资产或净利润为负的不统计）',format_of_number=None, format_desc=None) ==1000
    assert number_trans(100,'净利润增速上限（%）','续  图表27.本周上市公司业绩预告（2019.01.28-2019.02.01）',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'净利润增速上限（%）','续  图表27.本周上市公司业绩预告（2019.01.28-2019.02.01）',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'净利润增速上限（%）','续  图表27.本周上市公司业绩预告（2019.01.28-2019.02.01）',format_of_number=None, format_desc=None) ==100
    assert number_trans(10,'定增价除权后至今价格','图表48：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'定增价除权后至今价格','图表48：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'定增价除权后至今价格','图表48：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'A收盘价','图表74：传媒个股一周情况',format_of_number=None, format_desc=None) ==5
    assert number_trans(3,'A涨跌幅','图表74：传媒个股一周情况',format_of_number=None, format_desc=None) ==3
    assert number_trans(5,'A收盘价','图表74：传媒个股一周情况',format_of_number=None, format_desc=None) ==5
    assert number_trans(3,'A涨跌幅','图表74：传媒个股一周情况',format_of_number=None, format_desc=None) ==3
    assert number_trans(5,'A收盘价','图表74：传媒个股一周情况',format_of_number=None, format_desc=None) ==5
    assert number_trans(3,'A涨跌幅','图表74：传媒个股一周情况',format_of_number=None, format_desc=None) ==3
    assert number_trans(20,'收盘价','图表84：中概股美股行情',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'收盘价','图表84：中概股美股行情',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'收盘价','图表84：中概股美股行情',format_of_number=None, format_desc=None) ==20
    assert number_trans(0,'累计同比','113 表12:四线城市一手房成交周同比、环比对比 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'累计同比','113 表12:四线城市一手房成交周同比、环比对比 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'累计同比','113 表12:四线城市一手房成交周同比、环比对比 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(4,'7日成交环比','02 表2：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==4
    assert number_trans(4,'7日成交同比','02 表2：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==4
    assert number_trans(4,'7日成交同比','02 表2：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==4
    assert number_trans(4,'7日成交环比','02 表2：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==4
    assert number_trans(4,'7日成交环比','02 表2：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==4
    assert number_trans(4,'7日成交环比','02 表2：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==4
    assert number_trans(10,'2018Q1','表 7 快递公司的单票成本及其变动（2017Q1-Q3） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2018Q2','表 7 快递公司的单票成本及其变动（2017Q1-Q3） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2018Q1','表 7 快递公司的单票成本及其变动（2017Q1-Q3） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2018Q1','表 7 快递公司的单票成本及其变动（2017Q1-Q3） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2018Q1','表 7 快递公司的单票成本及其变动（2017Q1-Q3） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2018Q1','表 7 快递公司的单票成本及其变动（2017Q1-Q3） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(0,'本月涨跌幅','85 图表7：交运子板块行情 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'本周涨跌幅','85 图表7：交运子板块行情 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'本月涨跌幅','85 图表7：交运子板块行情 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'本周涨跌幅','85 图表7：交运子板块行情 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(10,'周涨跌幅（%）','图51：汽车电子板块市场表现 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'月涨跌幅（%）','图51：汽车电子板块市场表现 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'周涨跌幅（%）','图51：汽车电子板块市场表现 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'月涨跌幅（%）','图51：汽车电子板块市场表现 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'周涨跌幅（%）','图51：汽车电子板块市场表现 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'月涨跌幅（%）','图51：汽车电子板块市场表现 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'股价','39 2012年06月地产行业重点公司主要财务指标  ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'股价','39 2012年06月地产行业重点公司主要财务指标  ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'股价','39 2012年06月地产行业重点公司主要财务指标  ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'场均人次','表4：2018年第52周（2018.12.24 - 2018.12.30）全国电影票房TOP10',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'票房占比（%）','表4：2018年第52周（2018.12.24 - 2018.12.30）全国电影票房TOP10',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'场均人次','表4：2018年第52周（2018.12.24 - 2018.12.30）全国电影票房TOP10',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'票房占比（%）','表4：2018年第52周（2018.12.24 - 2018.12.30）全国电影票房TOP10',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'场均人次','表4：2018年第52周（2018.12.24 - 2018.12.30）全国电影票房TOP10',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'票房占比（%）','表4：2018年第52周（2018.12.24 - 2018.12.30）全国电影票房TOP10',format_of_number=None, format_desc=None) ==5
    assert number_trans(1900,'上周','表17：华鲁恒升（小颗粒）价格略有上涨 ',format_of_number=None, format_desc='元') ==1900
    assert number_trans(1900,'上周','表17：华鲁恒升（小颗粒）价格略有上涨 ',format_of_number=None, format_desc='元') ==1900
    assert number_trans(400,'对应时间','表 2：不同娱乐消费形式单位时间价格预估',format_of_number=None, format_desc=None) ==400
    assert number_trans(400,'对应时间','表 2：不同娱乐消费形式单位时间价格预估',format_of_number=None, format_desc=None) ==400
    assert number_trans(15,'PE17','图表24： A股航空可比公司估值表（2018年11月16日的收盘价） ',format_of_number=None, format_desc=None) ==15
    assert number_trans(2,'PB19E','图表24： A股航空可比公司估值表（2018年11月16日的收盘价） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(20,'PE17','图表24： A股航空可比公司估值表（2018年11月16日的收盘价） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(2,'ROE17','图表24： A股航空可比公司估值表（2018年11月16日的收盘价） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(20,'PE17','图表24： A股航空可比公司估值表（2018年11月16日的收盘价） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(2,'ROE17','图表24： A股航空可比公司估值表（2018年11月16日的收盘价） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'2011年日均成交','86 表：渤海湾主要城市成交信息一览表（粗体标注的城市已出台限购令，7月3日为T日） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'2012年日均成交','86 表：渤海湾主要城市成交信息一览表（粗体标注的城市已出台限购令，7月3日为T日） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'2011年日均成交','86 表：渤海湾主要城市成交信息一览表（粗体标注的城市已出台限购令，7月3日为T日） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'2012年日均成交','86 表：渤海湾主要城市成交信息一览表（粗体标注的城市已出台限购令，7月3日为T日） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'2011年日均成交','86 表：渤海湾主要城市成交信息一览表（粗体标注的城市已出台限购令，7月3日为T日） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'2012年日均成交','86 表：渤海湾主要城市成交信息一览表（粗体标注的城市已出台限购令，7月3日为T日） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(100,'线路长度（公里）','表91：预计2020年通车高铁线路 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'线路长度（公里）','表91：预计2020年通车高铁线路 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(20,'2017','122表 11 快递公司的资本开（2017-2018Q3） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'2017H1','122表 11 快递公司的资本开（2017-2018Q3） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'2017H1','122表 11 快递公司的资本开（2017-2018Q3） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'2017H1','122表 11 快递公司的资本开（2017-2018Q3） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'2017H1','122表 11 快递公司的资本开（2017-2018Q3） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'2017H1','122表 11 快递公司的资本开（2017-2018Q3） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(10000,'上月','177表5：山西喷吹煤产地价格持平 ',format_of_number=None, format_desc='元') ==10000
    assert number_trans(10000,'上年','177表5：山西喷吹煤产地价格持平 ',format_of_number=None, format_desc='元') ==10000
    assert number_trans(10000,'上月','177表5：山西喷吹煤产地价格持平 ',format_of_number=None, format_desc=None) ==10000
    assert number_trans(10000,'上年','177表5：山西喷吹煤产地价格持平 ',format_of_number=None, format_desc=None) ==10000
    assert number_trans(10000,'上月','177表5：山西喷吹煤产地价格持平 ',format_of_number=None, format_desc=None) ==10000
    assert number_trans(10000,'上年','177表5：山西喷吹煤产地价格持平 ',format_of_number=None, format_desc=None) ==10000
    assert number_trans(1,'EPS(元)2011A','14 需要关注的重点公司 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS(元)2012E','14 需要关注的重点公司 ',format_of_number=None, format_desc='股') ==1
    assert number_trans(1,'EPS(元)2011A','14 需要关注的重点公司 ',format_of_number=None, format_desc='股') ==1
    assert number_trans(1,'EPS(元)2012E','14 需要关注的重点公司 ',format_of_number=None, format_desc='股') ==1
    assert number_trans(1,'EPS(元)2013E','14 需要关注的重点公司 ',format_of_number=None, format_desc='股') ==1
    assert number_trans(1,'EPS(元)2012E','14 需要关注的重点公司 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS(元)2011A','14 需要关注的重点公司 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(200,'公里数（km）','表67. 预计2018年新开通高铁线路15条线共计3559公里  ',format_of_number=None, format_desc=None) ==200
    assert number_trans(200,'公里数（km）','表67. 预计2018年新开通高铁线路15条线共计3559公里  ',format_of_number=None, format_desc=None) ==200
    assert number_trans(200,'公里数（km）','表67. 预计2018年新开通高铁线路15条线共计3559公里  ',format_of_number=None, format_desc=None) ==200
    assert number_trans(40,'收盘价','图表84：中概股美股行情',format_of_number=None, format_desc=None) ==40
    assert number_trans(3,'周涨跌幅','图表84：中概股美股行情',format_of_number=None, format_desc=None) ==3
    assert number_trans(40,'收盘价','图表84：中概股美股行情',format_of_number=None, format_desc=None) ==40
    assert number_trans(3,'周涨跌幅','图表84：中概股美股行情',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'周涨跌幅','图表84：中概股美股行情',format_of_number=None, format_desc=None) ==3
    assert number_trans(40,'收盘价','图表84：中概股美股行情',format_of_number=None, format_desc=None) ==40
    assert number_trans(0,'同比增速','20图表 44   全球主要 LED显示屏制造商营收与增速 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(100,'PE17A','表65：重点公司估值及评级 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'PE17A','表65：重点公司估值及评级 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'PE17A','表65：重点公司估值及评级 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(20,'PE2019E','表27：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2020E','表27：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2019E','表27：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2020E','表27：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(3400,'拟周成交','42 表3：2012-06-13房地产二线城市成交数据二 ',format_of_number='万', format_desc='平') ==34000000
    assert number_trans(1000,'近4周周均成交','42 表3：2012-06-13房地产二线城市成交数据二 ',format_of_number='万', format_desc='平') ==10000000
    assert number_trans(3400,'拟周成交','42 表3：2012-06-13房地产二线城市成交数据二 ',format_of_number='万', format_desc='平') ==34000000
    assert number_trans(1000,'近4周周均成交','42 表3：2012-06-13房地产二线城市成交数据二 ',format_of_number='万', format_desc='平') ==10000000
    assert number_trans(3400,'拟周成交','42 表3：2012-06-13房地产二线城市成交数据二 ',format_of_number='万', format_desc='平') ==34000000
    assert number_trans(1000,'近4周周均成交','42 表3：2012-06-13房地产二线城市成交数据二 ',format_of_number='万', format_desc='平') ==10000000
    assert number_trans(2,'周均成交面积','95 表 3：各城市周均成交面积与同比 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'周均成交面积','95 表 3：各城市周均成交面积与同比 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'周均成交面积','95 表 3：各城市周均成交面积与同比 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(500,'土地储备','18 表 1：重点公司投资评级 ',format_of_number=None, format_desc=None) ==500
    assert number_trans(500,'土地储备','18 表 1：重点公司投资评级 ',format_of_number=None, format_desc=None) ==500
    assert number_trans(500,'土地储备','18 表 1：重点公司投资评级 ',format_of_number=None, format_desc=None) ==500
    assert number_trans(22,'PE17','158图表69： 航运：海外可比公司估值表 ',format_of_number=None, format_desc=None) ==22
    assert number_trans(22,'PE17','158图表69： 航运：海外可比公司估值表 ',format_of_number=None, format_desc=None) ==22
    assert number_trans(22,'PE17','158图表69： 航运：海外可比公司估值表 ',format_of_number=None, format_desc=None) ==22
    assert number_trans(10,'2011年12月成交量环比','64 表2：二线重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(1,'2011年11月成交量环比','64 表2：二线重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(10,'2011年12月成交量环比','64 表2：二线重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(1,'2011年12月成交量环比','64 表2：二线重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(10,'2011年12月成交量环比','64 表2：二线重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(1,'2011年12月成交量环比','64 表2：二线重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(10000,'5月均价(元/㎡)','85表 5：2012年5月北京城市部分环比涨价楼盘 ',format_of_number=None, format_desc=None) ==10000
    assert number_trans(5,'月环比涨幅','85表 5：2012年5月北京城市部分环比涨价楼盘 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(11000,'5月均价(元/㎡)','85表 5：2012年5月北京城市部分环比涨价楼盘 ',format_of_number=None, format_desc='平') ==11000
    assert number_trans(5,'月环比涨幅','85表 5：2012年5月北京城市部分环比涨价楼盘 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10000,'5月均价(元/㎡)','85表 5：2012年5月北京城市部分环比涨价楼盘 ',format_of_number=None, format_desc=None) ==10000
    assert number_trans(5,'月环比涨幅','85表 5：2012年5月北京城市部分环比涨价楼盘 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10000,'5月均价(元/㎡)','85表 5：2012年5月北京城市部分环比涨价楼盘 ',format_of_number=None, format_desc=None) ==10000
    assert number_trans(5,'月环比涨幅','85表 5：2012年5月北京城市部分环比涨价楼盘 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(4,'股息率','图表91：公路板块标的筛选 ',format_of_number=None, format_desc=None) ==4
    assert number_trans(40,'2017年分红比例','图表91：公路板块标的筛选 ',format_of_number=None, format_desc=None) ==40
    assert number_trans(4,'股息率','图表91：公路板块标的筛选 ',format_of_number=None, format_desc=None) ==4
    assert number_trans(40,'2017年分红比例','图表91：公路板块标的筛选 ',format_of_number=None, format_desc=None) ==40
    assert number_trans(4,'股息率','图表91：公路板块标的筛选 ',format_of_number=None, format_desc=None) ==4
    assert number_trans(40,'2017年分红比例','图表91：公路板块标的筛选 ',format_of_number=None, format_desc=None) ==40
    assert number_trans(15,'收盘价','表26：非金属建材类股票周涨幅前五  ',format_of_number=None, format_desc=None) ==15
    assert number_trans(20,'涨跌幅','表26：非金属建材类股票周涨幅前五  ',format_of_number=None, format_desc=None) ==20
    assert number_trans(15,'收盘价','表26：非金属建材类股票周涨幅前五  ',format_of_number=None, format_desc=None) ==15
    assert number_trans(20,'涨跌幅','表26：非金属建材类股票周涨幅前五  ',format_of_number=None, format_desc=None) ==20
    assert number_trans(15,'收盘价','表26：非金属建材类股票周涨幅前五  ',format_of_number=None, format_desc=None) ==15
    assert number_trans(20,'涨跌幅','表26：非金属建材类股票周涨幅前五  ',format_of_number=None, format_desc=None) ==20
    assert number_trans(10,'周收盘(美元)','表 23：传媒互联网行业美国中概股情况 传媒互联网行业美国中概股情况',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'周涨跌幅%','表 23：传媒互联网行业美国中概股情况 传媒互联网行业美国中概股情况',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'周收盘(美元)','表 23：传媒互联网行业美国中概股情况 传媒互联网行业美国中概股情况',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'周涨跌幅%','表 23：传媒互联网行业美国中概股情况 传媒互联网行业美国中概股情况',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'周收盘(美元)','表 23：传媒互联网行业美国中概股情况 传媒互联网行业美国中概股情况',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'周涨跌幅%','表 23：传媒互联网行业美国中概股情况 传媒互联网行业美国中概股情况',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'11年H2','116表4:三线城市去化时间对比表（单位：月） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'10年H2','116表4:三线城市去化时间对比表（单位：月） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'11年H2','116表4:三线城市去化时间对比表（单位：月） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'11年H1','116表4:三线城市去化时间对比表（单位：月） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'11年H1','116表4:三线城市去化时间对比表（单位：月） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'10年H2','116表4:三线城市去化时间对比表（单位：月） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(1,'EPS(元)2011A','14 需要关注的重点公司 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS(元)2011A','14 需要关注的重点公司 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS(元)2011A','14 需要关注的重点公司 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1000,'2016','表92：三桶油勘探开发投资情况',format_of_number=None, format_desc=None) ==1000
    assert number_trans(10,'10年H1','表3:二线城市去化时间对比表（单位：月） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(1,'11年H1','表3:二线城市去化时间对比表（单位：月） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'11年H1','表3:二线城市去化时间对比表（单位：月） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(19,'收盘价','表14: 行业重点上市公司盈利预测、估值与评级 ',format_of_number=None, format_desc=None) ==19
    assert number_trans(25,'目标价（元）','表14: 行业重点上市公司盈利预测、估值与评级 ',format_of_number=None, format_desc=None) ==25
    assert number_trans(19,'收盘价','表14: 行业重点上市公司盈利预测、估值与评级 ',format_of_number=None, format_desc=None) ==19
    assert number_trans(25,'目标价（元）','表14: 行业重点上市公司盈利预测、估值与评级 ',format_of_number=None, format_desc=None) ==25
    assert number_trans(25,'目标价（元）','表14: 行业重点上市公司盈利预测、估值与评级 ',format_of_number=None, format_desc=None) ==25
    assert number_trans(19,'收盘价','表14: 行业重点上市公司盈利预测、估值与评级 ',format_of_number=None, format_desc=None) ==19
    assert number_trans(10,'权重','56 表1：投资组合收益状况  ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'权重','56 表1：投资组合收益状况  ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'权重','56 表1：投资组合收益状况  ',format_of_number=None, format_desc=None) ==10
    assert number_trans(20,'PE2018E','表105：相关标的盈利预测表及估值表',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2019E','表105：相关标的盈利预测表及估值表',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2018E','表105：相关标的盈利预测表及估值表',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2019E','表105：相关标的盈利预测表及估值表',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2018E','表105：相关标的盈利预测表及估值表',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2019E','表105：相关标的盈利预测表及估值表',format_of_number=None, format_desc=None) ==20
    assert number_trans(3,'跌股收盘价','表20: 地产板块涨跌幅 ',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'跌幅','表20: 地产板块涨跌幅 ',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'跌股收盘价','表20: 地产板块涨跌幅 ',format_of_number=None, format_desc=None) ==3
    assert number_trans(10,'2017总收入同比增长率(%)','131表 5航运业上市公司收入情况  ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2017总收入同比增长率(%)','131表 5航运业上市公司收入情况  ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2017总收入同比增长率(%)','131表 5航运业上市公司收入情况  ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'收盘价','图表8：中概股美股行情',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'收盘价','图表8：中概股美股行情',format_of_number=None, format_desc=None) ==10
    assert number_trans(100,'线路长度（公里）','表91：预计2020年通车高铁线路 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'线路长度（公里）','表91：预计2020年通车高铁线路 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'线路长度（公里）','表91：预计2020年通车高铁线路 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(1,'本周涨跌幅','43图表2：交运子板块行情 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'本周涨跌幅','43图表2：交运子板块行情 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'本周涨跌幅','43图表2：交运子板块行情 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(0,'周均成交同比','38 表：主要城市成交信息一览表（粗体标注的城市已出台限购令） ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'本周成交环比','38 表：主要城市成交信息一览表（粗体标注的城市已出台限购令） ',format_of_number=None, format_desc=None) ==0
    assert number_trans(9000,'售价（元/平）','36 图 9：厦门市部分典型降价楼盘 ',format_of_number=None, format_desc='元') ==9000
    assert number_trans(4,'收盘价(元)','04 表3重点覆盖公司估值表 ',format_of_number=None, format_desc=None) ==4
    assert number_trans(4,'收盘价(元)','04 表3重点覆盖公司估值表 ',format_of_number=None, format_desc='元') ==4
    assert number_trans(4,'每股预收(元)','04 表3重点覆盖公司估值表 ',format_of_number='亿', format_desc=None) ==400000000
    assert number_trans(4,'收盘价(元)','04 表3重点覆盖公司估值表 ',format_of_number=None, format_desc='元') ==4
    assert number_trans(1,'EPS19E','表1：航空重点公司估值对比表 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(20,'盈利增长率20E','表1：航空重点公司估值对比表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(100,'盈利增长率20E','表1：航空重点公司估值对比表 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(1,'EPS20E','表1：航空重点公司估值对比表 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(20,'PE18E','表1：航空重点公司估值对比表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(100,'PE18E','表1：航空重点公司估值对比表 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'盈利增长率20E','表1：航空重点公司估值对比表 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(1,'盈利增长率20E','表1：航空重点公司估值对比表 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(20,'PE20E','表1：航空重点公司估值对比表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(10,'环比上上周','48 表3:2012年6月一线城市房地产行业区域统计情况',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'环比上上周','48 表3:2012年6月一线城市房地产行业区域统计情况',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'环比上上周','48 表3:2012年6月一线城市房地产行业区域统计情况',format_of_number=None, format_desc=None) ==10
    assert number_trans(14,'上周成交量','图17、重点类型城市二手房成交数据（万平米）',format_of_number=None, format_desc=None) ==14
    assert number_trans(0,'周涨跌幅（%）','图53：海外燃料电池板块市场表现 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'年涨跌幅%）','图53：海外燃料电池板块市场表现 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'周涨跌幅（%）','图53：海外燃料电池板块市场表现 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'年涨跌幅%）','图53：海外燃料电池板块市场表现 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'周涨跌幅（%）','图53：海外燃料电池板块市场表现 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'年涨跌幅%）','图53：海外燃料电池板块市场表现 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(10,'2016A每股收益(元/股)','表80. 机械行业主要上市公司估值表',format_of_number='亿', format_desc=None) ==1000000000
    assert number_trans(2,'市场份额%','图表15: 上周五综艺节目收视数据（12月14日）',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'市场份额%','图表15: 上周五综艺节目收视数据（12月14日）',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'市场份额%','图表15: 上周五综艺节目收视数据（12月14日）',format_of_number=None, format_desc=None) ==2
    assert number_trans(10,'股价（元）','15表3：快递、物流重点公司估值对比表 ',format_of_number=None, format_desc='元') ==10
    assert number_trans(10,'股价（元）','15表3：快递、物流重点公司估值对比表 ',format_of_number=None, format_desc='元') ==10
    assert number_trans(10,'股价（元）','15表3：快递、物流重点公司估值对比表 ',format_of_number=None, format_desc='元') ==10
    assert number_trans(6,'贷款利率调整前','15 表1: 近年来历次降息 ',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'贷款利率调整后','15 表1: 近年来历次降息 ',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'贷款利率调整前','15 表1: 近年来历次降息 ',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'贷款利率调整后','15 表1: 近年来历次降息 ',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'贷款利率调整前','15 表1: 近年来历次降息 ',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'贷款利率调整后','15 表1: 近年来历次降息 ',format_of_number=None, format_desc=None) ==6
    assert number_trans(200,'2011供应面积','62表3:2012年6月二线城市统计土地供应(2011 年初至今)',format_of_number='万', format_desc='平') ==2000000
    assert number_trans(200,'2012至今','62表3:2012年6月二线城市统计土地供应(2011 年初至今)',format_of_number='万', format_desc='平') ==2000000
    assert number_trans(200,'2011供应面积','62表3:2012年6月二线城市统计土地供应(2011 年初至今)',format_of_number='万', format_desc='平') ==2000000
    assert number_trans(200,'2011同期','62表3:2012年6月二线城市统计土地供应(2011 年初至今)',format_of_number='万', format_desc='平') ==2000000
    assert number_trans(200,'2011同期','62表3:2012年6月二线城市统计土地供应(2011 年初至今)',format_of_number='万', format_desc='平') ==2000000
    assert number_trans(200,'2012至今','62表3:2012年6月二线城市统计土地供应(2011 年初至今)',format_of_number='万', format_desc='平') ==2000000
    assert number_trans(10,'市盈率PE','图表91：公路板块标的筛选 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'股息率','图表91：公路板块标的筛选 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'市盈率PE','图表91：公路板块标的筛选 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'股息率','图表91：公路板块标的筛选 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'市盈率PE','图表91：公路板块标的筛选 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'股息率','图表91：公路板块标的筛选 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(1,'本月相对大盘收益','表22：A股26家银行涨跌幅及A-H股溢价率（单位：%） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'本周涨跌幅','表22：A股26家银行涨跌幅及A-H股溢价率（单位：%） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'本月相对大盘收益','表22：A股26家银行涨跌幅及A-H股溢价率（单位：%） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'本周涨跌幅','表22：A股26家银行涨跌幅及A-H股溢价率（单位：%） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'本月相对大盘收益','表22：A股26家银行涨跌幅及A-H股溢价率（单位：%） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'本周涨跌幅','表22：A股26家银行涨跌幅及A-H股溢价率（单位：%） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(20,'PE19E','图表7：重点推荐公司估值表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'评级','图表7：重点推荐公司估值表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'评级','图表7：重点推荐公司估值表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE20E','图表7：重点推荐公司估值表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'评级','图表7：重点推荐公司估值表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE20E','图表7：重点推荐公司估值表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(10,'2011年12月成交量环比','63 表2：重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2011年11月成交量环比','63 表2：重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2011年12月成交量环比','63 表2：重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2011年11月成交量环比','63 表2：重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2011年12月成交量环比','63 表2：重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2011年11月成交量环比','63 表2：重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(4,'5月均价(元/㎡)','49 表 ：2012年5月上海市部分环比涨价楼盘 ',format_of_number='万', format_desc=None) ==40000
    assert number_trans(7,'月环比涨幅','49 表 ：2012年5月上海市部分环比涨价楼盘 ',format_of_number=None, format_desc=None) ==7
    assert number_trans(4,'5月均价(元/㎡)','49 表 ：2012年5月上海市部分环比涨价楼盘 ',format_of_number='万', format_desc=None) ==40000
    assert number_trans(7,'月环比涨幅','49 表 ：2012年5月上海市部分环比涨价楼盘 ',format_of_number=None, format_desc=None) ==7
    assert number_trans(4,'5月均价(元/㎡)','49 表 ：2012年5月上海市部分环比涨价楼盘 ',format_of_number='万', format_desc=None) ==40000
    assert number_trans(7,'月环比涨幅','49 表 ：2012年5月上海市部分环比涨价楼盘 ',format_of_number=None, format_desc=None) ==7
    assert number_trans(6,'每股预收(元)','04 表3重点覆盖公司估值表 ',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'每股预收(元)','04 表3重点覆盖公司估值表 ',format_of_number=None, format_desc='元') ==6
    assert number_trans(6,'每股预收(元)','04 表3重点覆盖公司估值表 ',format_of_number=None, format_desc=None) ==6
    assert number_trans(0,'2016Q2','表2：电容行业-季度营收同比增速-算数平均 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'2016Q2','表2：电容行业-季度营收同比增速-算数平均 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'2016Q2','表2：电容行业-季度营收同比增速-算数平均 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'2016Q2','表2：电容行业-季度营收同比增速-算数平均 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(1,'本期','06 表6:16个重点城市全部土地成交楼面地价溢价率对比表(单位:元/平米) ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'上期','06 表6:16个重点城市全部土地成交楼面地价溢价率对比表(单位:元/平米) ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'本期','06 表6:16个重点城市全部土地成交楼面地价溢价率对比表(单位:元/平米) ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'上期','06 表6:16个重点城市全部土地成交楼面地价溢价率对比表(单位:元/平米) ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'本期','06 表6:16个重点城市全部土地成交楼面地价溢价率对比表(单位:元/平米) ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'上期','06 表6:16个重点城市全部土地成交楼面地价溢价率对比表(单位:元/平米) ',format_of_number=None, format_desc=None) ==1
    assert number_trans(10,'2011年11月成交量环比','63 表2：重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'2011年11月成交量环比','63 表2：重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'2011年11月成交量环比','63 表2：重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'2011年12月成交量环比','63 表2：重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'2011年12月成交量环比','63 表2：重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'2011年11月成交量环比','63 表2：重点城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==5
    assert number_trans(3,'PB估值','69 表4：2012年6月12日关注类非住宅开发公司估值表 ',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'PB估值','69 表4：2012年6月12日关注类非住宅开发公司估值表 ',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'PB估值','69 表4：2012年6月12日关注类非住宅开发公司估值表 ',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'成交住宅土地宗数','21 图13： 福州市月度住宅用地成交情况  ',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'成交住宅土地宗数','21 图13： 福州市月度住宅用地成交情况  ',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'成交住宅土地宗数','21 图13： 福州市月度住宅用地成交情况  ',format_of_number=None, format_desc=None) ==3
    assert number_trans(10,'2011年周均成交','37 表：主要城市成交信息一览表（粗体标注的城市已出台限购令） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2011年周均成交','37 表：主要城市成交信息一览表（粗体标注的城市已出台限购令） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2011年周均成交','37 表：主要城市成交信息一览表（粗体标注的城市已出台限购令） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'最新股价（元/股）','63 表4：2012年6月10日银河地产模拟组合 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'最新股价（元/股）','63 表4：2012年6月10日银河地产模拟组合 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'最新股价（元/股）','63 表4：2012年6月10日银河地产模拟组合 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(100,'上周成交量（套）','55 表3：跟踪的珠三角城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'成交量同比增长','55 表3：跟踪的珠三角城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'成交量同比增长','55 表3：跟踪的珠三角城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'上周成交量（套）','55 表3：跟踪的珠三角城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'上周成交量（套）','55 表3：跟踪的珠三角城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'成交量同比增长','55 表3：跟踪的珠三角城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'当月累计成交量','图17、重点类型城市二手房成交数据（万平米）',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'当月累计成交量','图17、重点类型城市二手房成交数据（万平米）',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'当月累计成交量','图17、重点类型城市二手房成交数据（万平米）',format_of_number=None, format_desc=None) ==100
    assert number_trans(30,'PE19E','表2：铁路海运重点公司估值对比表 ',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'PE20E','表2：铁路海运重点公司估值对比表 ',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'PE19E','表2：铁路海运重点公司估值对比表 ',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'PE19E','表2：铁路海运重点公司估值对比表 ',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'PE19E','表2：铁路海运重点公司估值对比表 ',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'PE19E','表2：铁路海运重点公司估值对比表 ',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'PE20E','表2：铁路海运重点公司估值对比表 ',format_of_number=None, format_desc=None) ==30
    assert number_trans(1,'每股净资产','表2煤炭行业炼焦煤估值比较 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(5,'P/B','表2煤炭行业炼焦煤估值比较 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(1,'每股净资产','表2煤炭行业炼焦煤估值比较 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(5,'P/B','表2煤炭行业炼焦煤估值比较 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(1,'每股净资产','表2煤炭行业炼焦煤估值比较 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(5,'P/B','表2煤炭行业炼焦煤估值比较 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(1,'市场占有率','表11：2017年中国混凝土外加剂前十企业市场占有率 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'市场占有率','表11：2017年中国混凝土外加剂前十企业市场占有率 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'市场占有率','表11：2017年中国混凝土外加剂前十企业市场占有率 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(10,'股价（元）','表65：重点公司估值及评级 ',format_of_number=None, format_desc='元') ==10
    assert number_trans(10,'股价（元）','表65：重点公司估值及评级 ',format_of_number=None, format_desc='元') ==10
    assert number_trans(10,'股价（元）','表65：重点公司估值及评级 ',format_of_number=None, format_desc='元') ==10
    assert number_trans(5,'贷款利率','10 表：降息以及利率打折后影响分析 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10000,'月度还款额','10 表：降息以及利率打折后影响分析 ',format_of_number=None, format_desc=None) ==10000
    assert number_trans(10000,'月度还款额','10 表：降息以及利率打折后影响分析 ',format_of_number=None, format_desc=None) ==10000
    assert number_trans(5,'贷款利率','10 表：降息以及利率打折后影响分析 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10000,'月度还款额','10 表：降息以及利率打折后影响分析 ',format_of_number=None, format_desc=None) ==10000
    assert number_trans(5,'贷款利率','10 表：降息以及利率打折后影响分析 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'3Q18/3817','图表 8. 全球半导体设备公司三季度账单 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'3Q18/2Q18','图表 8. 全球半导体设备公司三季度账单 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'3Q2018','图表 8. 全球半导体设备公司三季度账单 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'3Q18/2Q18','图表 8. 全球半导体设备公司三季度账单 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'3Q18/2Q18','图表 8. 全球半导体设备公司三季度账单 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'3Q18/2Q18','图表 8. 全球半导体设备公司三季度账单 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'P/R-V','61 盈利预测和估值1',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'RNAV','61 盈利预测和估值1',format_of_number=None, format_desc=None) ==10
    assert number_trans(1,'P/R-V','61 盈利预测和估值1',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'PB2011','61 盈利预测和估值1',format_of_number=None, format_desc=None) ==1
    assert number_trans(10,'RNAV','61 盈利预测和估值1',format_of_number=None, format_desc=None) ==10
    assert number_trans(0,'环比','137表 3：2012年6月19日各城市成交面积与环比续（万平） ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'环比','137表 3：2012年6月19日各城市成交面积与环比续（万平） ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'环比','137表 3：2012年6月19日各城市成交面积与环比续（万平） ',format_of_number=None, format_desc=None) ==0
    assert number_trans(500,'2010成交面积','表3:2012年一线城市土地成交面积(2011 年初至今)（万平）',format_of_number=None, format_desc=None) ==500
    assert number_trans(500,'2011年成交面积','表3:2012年一线城市土地成交面积(2011 年初至今)（万平）',format_of_number=None, format_desc=None) ==500
    assert number_trans(500,'2010成交面积','表3:2012年一线城市土地成交面积(2011 年初至今)（万平）',format_of_number=None, format_desc=None) ==500
    assert number_trans(500,'2011年成交面积','表3:2012年一线城市土地成交面积(2011 年初至今)（万平）',format_of_number=None, format_desc=None) ==500
    assert number_trans(500,'2010成交面积','表3:2012年一线城市土地成交面积(2011 年初至今)（万平）',format_of_number=None, format_desc=None) ==500
    assert number_trans(500,'2011年成交面积','表3:2012年一线城市土地成交面积(2011 年初至今)（万平）',format_of_number=None, format_desc=None) ==500
    assert number_trans(1,'可售去化时间','49 表4:2012年6月一线城市房地产行业区域可售统计情况',format_of_number=None, format_desc=None) ==1
    assert number_trans(36,'可售去化时间','49 表4:2012年6月一线城市房地产行业区域可售统计情况',format_of_number=None, format_desc=None) ==36
    assert number_trans(0,'可售环比','49 表4:2012年6月一线城市房地产行业区域可售统计情况',format_of_number=None, format_desc=None) ==0
    assert number_trans(1,'可售去化时间','49 表4:2012年6月一线城市房地产行业区域可售统计情况',format_of_number=None, format_desc=None) ==1
    assert number_trans(0,'可售环比','49 表4:2012年6月一线城市房地产行业区域可售统计情况',format_of_number=None, format_desc=None) ==0
    assert number_trans(300,'本周销售套数','49 表2012年第23周（2012.5.28-2012.6.3） 新房成交数据 4',format_of_number=None, format_desc=None) ==300
    assert number_trans(300,'本周销售套数','49 表2012年第23周（2012.5.28-2012.6.3） 新房成交数据 4',format_of_number=None, format_desc=None) ==300
    assert number_trans(300,'本周销售套数','49 表2012年第23周（2012.5.28-2012.6.3） 新房成交数据 4',format_of_number=None, format_desc=None) ==300
    assert number_trans(1,'环比','30 表 1：重点城市成交数据一 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'近8日日均环比','30 表 1：重点城市成交数据一 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'环比','30 表 1：重点城市成交数据一 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'近8日日均环比','30 表 1：重点城市成交数据一 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'近8日日均环比','30 表 1：重点城市成交数据一 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'环比','30 表 1：重点城市成交数据一 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(100,'上周','47 表2:2012年6月一、二、三线城市房地产行业区域统计情况',format_of_number=None, format_desc=None) ==100
    assert number_trans(1,'累计同比','47 表2:2012年6月一、二、三线城市房地产行业区域统计情况',format_of_number=None, format_desc=None) ==1
    assert number_trans(100,'上周','47 表2:2012年6月一、二、三线城市房地产行业区域统计情况',format_of_number=None, format_desc=None) ==100
    assert number_trans(10,'累计同比','47 表2:2012年6月一、二、三线城市房地产行业区域统计情况',format_of_number=None, format_desc=None) ==10
    assert number_trans(100,'上周','47 表2:2012年6月一、二、三线城市房地产行业区域统计情况',format_of_number=None, format_desc=None) ==100
    assert number_trans(10,'累计同比','47 表2:2012年6月一、二、三线城市房地产行业区域统计情况',format_of_number=None, format_desc=None) ==10
    assert number_trans(12,'周前收盘价(元)','表 3：传媒互联网行业',format_of_number=None, format_desc='元') ==12
    assert number_trans(0,'一线城市','64 表5：近年年房地产销售面积预测（万平米） ',format_of_number=None, format_desc=None) ==0
    assert number_trans(10,'2011年周均成交','38 表：主要城市成交信息一览表（粗体标注的城市已出台限购令） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2012年周均成交','38 表：主要城市成交信息一览表（粗体标注的城市已出台限购令） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2011年周均成交','38 表：主要城市成交信息一览表（粗体标注的城市已出台限购令） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2012年周均成交','38 表：主要城市成交信息一览表（粗体标注的城市已出台限购令） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2011年周均成交','38 表：主要城市成交信息一览表（粗体标注的城市已出台限购令） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2012年周均成交','38 表：主要城市成交信息一览表（粗体标注的城市已出台限购令） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(0,'年涨跌幅','85 图表7：交运子板块行情 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'年涨跌幅','85 图表7：交运子板块行情 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'今年以来','85 图表7：交运子板块行情 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'今年以来','85 图表7：交运子板块行情 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(150,'里程(公里)','139表3：京沪高铁2011年6月通车，运营里程1318公里 ',format_of_number=None, format_desc=None) ==150
    assert number_trans(150,'里程(公里)','139表3：京沪高铁2011年6月通车，运营里程1318公里 ',format_of_number=None, format_desc=None) ==150
    assert number_trans(150,'里程(公里)','139表3：京沪高铁2011年6月通车，运营里程1318公里 ',format_of_number=None, format_desc=None) ==150
    assert number_trans(10,'商誉/净资产2','表 5：2018 年三季报传媒个股商誉情况一览（净资产或净利润为负的不统计）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'商誉/净利润2','表 5：2018 年三季报传媒个股商誉情况一览（净资产或净利润为负的不统计）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'商誉/净资产2','表 5：2018 年三季报传媒个股商誉情况一览（净资产或净利润为负的不统计）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'商誉/净利润2','表 5：2018 年三季报传媒个股商誉情况一览（净资产或净利润为负的不统计）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'商誉/净资产2','表 5：2018 年三季报传媒个股商誉情况一览（净资产或净利润为负的不统计）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'商誉/净利润2','表 5：2018 年三季报传媒个股商誉情况一览（净资产或净利润为负的不统计）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10000,'单日单厅票房（元）','表9：2019-1-14至2019-1-20影院票房排行',format_of_number=None, format_desc='元') ==10000
    assert number_trans(5,'单日单厅场次','表9：2019-1-14至2019-1-20影院票房排行',format_of_number=None, format_desc=None) ==5
    assert number_trans(10000,'单日单厅票房（元）','表9：2019-1-14至2019-1-20影院票房排行',format_of_number=None, format_desc='元') ==10000
    assert number_trans(5,'单日单厅票房（元）','表9：2019-1-14至2019-1-20影院票房排行',format_of_number=None, format_desc=None) ==5
    assert number_trans(10000,'单日单厅票房（元）','表9：2019-1-14至2019-1-20影院票房排行',format_of_number=None, format_desc='元') ==10000
    assert number_trans(5,'单日单厅场次','表9：2019-1-14至2019-1-20影院票房排行',format_of_number=None, format_desc=None) ==5
    assert number_trans(50,'3月套数','51 表 ：北京2012年4月部分涨价楼盘一览 ',format_of_number=None, format_desc=None) ==50
    assert number_trans(100,'3月均价','51 表 ：北京2012年4月部分涨价楼盘一览 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(50,'3月套数','51 表 ：北京2012年4月部分涨价楼盘一览 ',format_of_number=None, format_desc=None) ==50
    assert number_trans(100,'3月均价','51 表 ：北京2012年4月部分涨价楼盘一览 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(50,'3月套数','51 表 ：北京2012年4月部分涨价楼盘一览 ',format_of_number=None, format_desc=None) ==50
    assert number_trans(100,'3月均价','51 表 ：北京2012年4月部分涨价楼盘一览 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(20,'上周成交面积','47 表 5：各城市周均成交面积与同比 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(5,'本周成交面积','47 表 5：各城市周均成交面积与同比 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(20,'上周成交面积','47 表 5：各城市周均成交面积与同比 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(5,'本周成交面积','47 表 5：各城市周均成交面积与同比 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(20,'上周成交面积','47 表 5：各城市周均成交面积与同比 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(5,'本周成交面积','47 表 5：各城市周均成交面积与同比 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(7,'批文数占比（%）','表47：需要做一致性评价的药企及其品种统计 ',format_of_number=None, format_desc=None) ==7
    assert number_trans(7,'药品数（个）','表47：需要做一致性评价的药企及其品种统计 ',format_of_number=None, format_desc=None) ==7
    assert number_trans(7,'批文数占比（%）','表47：需要做一致性评价的药企及其品种统计 ',format_of_number=None, format_desc=None) ==7
    assert number_trans(3,'周涨跌（%）','图7： 本周个股涨跌幅排名(涨幅前十)   ',format_of_number=None, format_desc=None) ==3
    assert number_trans(15,'收盘价（元）','图7： 本周个股涨跌幅排名(涨幅前十)   ',format_of_number=None, format_desc='元') ==15
    assert number_trans(3,'周涨跌（%）','图7： 本周个股涨跌幅排名(涨幅前十)   ',format_of_number=None, format_desc=None) ==3
    assert number_trans(15,'收盘价（元）','图7： 本周个股涨跌幅排名(涨幅前十)   ',format_of_number=None, format_desc=None) ==15
    assert number_trans(3,'周涨跌（%）','图7： 本周个股涨跌幅排名(涨幅前十)   ',format_of_number=None, format_desc=None) ==3
    assert number_trans(15,'收盘价（元）','图7： 本周个股涨跌幅排名(涨幅前十)   ',format_of_number=None, format_desc=None) ==15
    assert number_trans(1000,'前一周成交','73 表3：2012-05-30房地产重点城市成交数据二 ',format_of_number=None, format_desc=None) ==1000
    assert number_trans(1000,'近4周周均成交','73 表3：2012-05-30房地产重点城市成交数据二 ',format_of_number=None, format_desc=None) ==1000
    assert number_trans(1000,'近4周周均成交环比','73 表3：2012-05-30房地产重点城市成交数据二 ',format_of_number=None, format_desc=None) ==1000
    assert number_trans(1000,'前一周成交','73 表3：2012-05-30房地产重点城市成交数据二 ',format_of_number=None, format_desc=None) ==1000
    assert number_trans(1000,'上一年度同期成交','73 表3：2012-05-30房地产重点城市成交数据二 ',format_of_number=None, format_desc=None) ==1000
    assert number_trans(1000,'前一周成交','73 表3：2012-05-30房地产重点城市成交数据二 ',format_of_number=None, format_desc=None) ==1000
    assert number_trans(1000,'近4周周均成交','73 表3：2012-05-30房地产重点城市成交数据二 ',format_of_number=None, format_desc=None) ==1000
    assert number_trans(6,'最新收盘价','图表13：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==6
    assert number_trans(50,'倒挂率','图表13：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==50
    assert number_trans(6,'最新收盘价','图表13：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==6
    assert number_trans(50,'倒挂率','图表13：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==50
    assert number_trans(6,'最新收盘价','图表13：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==6
    assert number_trans(50,'倒挂率','图表13：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==50
    assert number_trans(10,'PE2012E','61 盈利预测和估值1',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE2013E','61 盈利预测和估值1',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE2012E','61 盈利预测和估值1',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE2013E','61 盈利预测和估值1',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE2012E','61 盈利预测和估值1',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE2013E','61 盈利预测和估值1',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'定增价除权后至今价格','图表17：教育行业近三年定增倒挂个股',format_of_number=None, format_desc='元') ==10
    assert number_trans(20,'增发价格','图表17：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==20
    assert number_trans(10,'定增价除权后至今价格','图表17：教育行业近三年定增倒挂个股',format_of_number=None, format_desc='元') ==10
    assert number_trans(20,'增发价格','图表17：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==20
    assert number_trans(10,'定增价除权后至今价格','图表17：教育行业近三年定增倒挂个股',format_of_number=None, format_desc='元') ==10
    assert number_trans(20,'增发价格','图表17：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==20
    assert number_trans(3,'PB估值','24 表6：关注类住宅开发公司估值表 ',format_of_number=None, format_desc=None) ==3
    assert number_trans(10,'最新股价','24 表6：关注类住宅开发公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'最新股价','24 表6：关注类住宅开发公司估值表 ',format_of_number=None, format_desc='元') ==10
    assert number_trans(3,'PB估值','24 表6：关注类住宅开发公司估值表 ',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'PB估值','24 表6：关注类住宅开发公司估值表 ',format_of_number=None, format_desc=None) ==3
    assert number_trans(10,'最新股价','24 表6：关注类住宅开发公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'本周换手率（%）','195图表28A股个股市场表现-本周涨跌幅后10 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'本周换手率（%）','195图表28A股个股市场表现-本周涨跌幅后10 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'2018年动态PE','195图表28A股个股市场表现-本周涨跌幅后10 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'本周换手率（%）','195图表28A股个股市场表现-本周涨跌幅后10 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'周均成交同比','24 表：2012年主要城市成交信息一览 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'周均成交同比','24 表：2012年主要城市成交信息一览 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'周均成交同比','24 表：2012年主要城市成交信息一览 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(40000,'楼面价','30表2：南京仙林临近地块土地出让比较 ',format_of_number=None, format_desc=None) ==40000
    assert number_trans(40000,'楼面价','30表2：南京仙林临近地块土地出让比较 ',format_of_number=None, format_desc=None) ==40000
    assert number_trans(10,'最新股价','02 表 1：地产板块一周涨幅前列公司情况 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'最新股价','02 表 1：地产板块一周涨幅前列公司情况 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'最新股价','02 表 1：地产板块一周涨幅前列公司情况 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(100,'收入','119表 8 快递公司的净利润及其增速（2018Q1-Q3）（亿元） ',format_of_number='亿', format_desc='元') ==100
    assert number_trans(20,'净利润','119表 8 快递公司的净利润及其增速（2018Q1-Q3）（亿元） ',format_of_number='亿', format_desc='元') ==20
    assert number_trans(100,'收入','119表 8 快递公司的净利润及其增速（2018Q1-Q3）（亿元） ',format_of_number='亿', format_desc='元') ==100
    assert number_trans(20,'净利润','119表 8 快递公司的净利润及其增速（2018Q1-Q3）（亿元） ',format_of_number='亿', format_desc='元') ==20
    assert number_trans(100,'收入','119表 8 快递公司的净利润及其增速（2018Q1-Q3）（亿元） ',format_of_number='亿', format_desc='元') ==100
    assert number_trans(20,'净利润','119表 8 快递公司的净利润及其增速（2018Q1-Q3）（亿元） ',format_of_number='亿', format_desc='元') ==20
    assert number_trans(10000,'降息前月还款额10年','14 表2 本次降息对购房人财务影响 ',format_of_number=None, format_desc='元') ==10000
    assert number_trans(10000,'降息前月还款额10年','14 表2 本次降息对购房人财务影响 ',format_of_number=None, format_desc=None) ==10000
    assert number_trans(10000,'降息前月还款额10年','14 表2 本次降息对购房人财务影响 ',format_of_number=None, format_desc='元') ==10000
    assert number_trans(100,'目前影院数量','图表 24   现有院线的经营情况',format_of_number=None, format_desc=None) ==100
    assert number_trans(600,'2018年底银幕数量','图表 24   现有院线的经营情况',format_of_number=None, format_desc=None) ==600
    assert number_trans(100,'目前影院数量','图表 24   现有院线的经营情况',format_of_number=None, format_desc=None) ==100
    assert number_trans(600,'2018年底银幕数量','图表 24   现有院线的经营情况',format_of_number=None, format_desc=None) ==600
    assert number_trans(600,'2018年底银幕数量','图表 24   现有院线的经营情况',format_of_number=None, format_desc=None) ==600
    assert number_trans(100,'目前影院数量','图表 24   现有院线的经营情况',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'2018年底银幕数量','图表 24   现有院线的经营情况',format_of_number=None, format_desc=None) ==100
    assert number_trans(20,'平均费率（元/公里）','95表 7 宁沪高速各类车型单车平均费率和收入占比估计 ',format_of_number=None, format_desc='元') ==20
    assert number_trans(2,'日均全程交通量（辆/日）','95表 7 宁沪高速各类车型单车平均费率和收入占比估计 ',format_of_number='千万', format_desc=None) ==20000000
    assert number_trans(20,'平均费率（元/公里）','95表 7 宁沪高速各类车型单车平均费率和收入占比估计 ',format_of_number=None, format_desc='元') ==20
    assert number_trans(2,'日均全程交通量（辆/日）','95表 7 宁沪高速各类车型单车平均费率和收入占比估计 ',format_of_number='千万', format_desc=None) ==20000000
    assert number_trans(2,'日均全程交通量（辆/日）','95表 7 宁沪高速各类车型单车平均费率和收入占比估计 ',format_of_number='千万', format_desc=None) ==20000000
    assert number_trans(20,'平均费率（元/公里）','95表 7 宁沪高速各类车型单车平均费率和收入占比估计 ',format_of_number=None, format_desc='元') ==20
    assert number_trans(2,'收盘价','图表82：中概股美股行情',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'收盘价','图表82：中概股美股行情',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'收盘价','图表82：中概股美股行情',format_of_number=None, format_desc=None) ==2
    assert number_trans(20,'周涨跌幅%','表 3：传媒互联网行业港股情况 传媒互联网行业港股情况',format_of_number=None, format_desc=None) ==20
    assert number_trans(2,'周换手率%','表 3：传媒互联网行业港股情况 传媒互联网行业港股情况',format_of_number=None, format_desc=None) ==2
    assert number_trans(20,'周涨跌幅%','表 3：传媒互联网行业港股情况 传媒互联网行业港股情况',format_of_number=None, format_desc=None) ==20
    assert number_trans(2,'周换手率%','表 3：传媒互联网行业港股情况 传媒互联网行业港股情况',format_of_number=None, format_desc=None) ==2
    assert number_trans(20,'周涨跌幅%','表 3：传媒互联网行业港股情况 传媒互联网行业港股情况',format_of_number=None, format_desc=None) ==20
    assert number_trans(2,'周换手率%','表 3：传媒互联网行业港股情况 传媒互联网行业港股情况',format_of_number=None, format_desc=None) ==2
    assert number_trans(0,'累计同比','表3:一线城市一手房成交周同比、环比对比',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'累计同比','表3:一线城市一手房成交周同比、环比对比',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'累计同比','表3:一线城市一手房成交周同比、环比对比',format_of_number=None, format_desc=None) ==0
    assert number_trans(9,'Jun','94 表25：东莞住宅期房2007-2012年1月各月成交面积（万平）             ',format_of_number=None, format_desc=None) ==9
    assert number_trans(6,'本周成交面积','47 表 5：各城市周均成交面积与同比 ',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'本周成交面积','47 表 5：各城市周均成交面积与同比 ',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'本周成交面积','47 表 5：各城市周均成交面积与同比 ',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'本周成交面积','47 表 5：各城市周均成交面积与同比 ',format_of_number=None, format_desc=None) ==6
    assert number_trans(10,'最新股价','02 表 1：地产板块一周涨幅前列公司情况 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'最新股价','02 表 1：地产板块一周涨幅前列公司情况 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'最新股价','02 表 1：地产板块一周涨幅前列公司情况 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(1200,'上周成交量（套）','54 表2：跟踪的环渤海湾城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==1200
    assert number_trans(1200,'上周成交量（套）','54 表2：跟踪的环渤海湾城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==1200
    assert number_trans(1200,'上周成交量（套）','54 表2：跟踪的环渤海湾城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==1200
    assert number_trans(1,'PE-TTM','表89：H股整车行业汇总 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'PB','表89：H股整车行业汇总 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'PS','表89：H股整车行业汇总 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'PE-TTM','表89：H股整车行业汇总 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(20,'PE','93表2：本周跌幅前五个股（2019.1.14-2019.1.18） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE','93表2：本周跌幅前五个股（2019.1.14-2019.1.18） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE','93表2：本周跌幅前五个股（2019.1.14-2019.1.18） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(40,'2018年TOP5','图表 6   2018-2019 年春节档TOP5 影片前六日均价',format_of_number=None, format_desc='元') ==40
    assert number_trans(40,'平均票价（元）','图表 6   2018-2019 年春节档TOP5 影片前六日均价',format_of_number=None, format_desc='元') ==40
    assert number_trans(40,'平均票价（元）','图表 6   2018-2019 年春节档TOP5 影片前六日均价',format_of_number=None, format_desc=None) ==40
    assert number_trans(100,'5月均价(元/㎡)','85表 5：2012年5月北京城市部分环比涨价楼盘 ',format_of_number=None, format_desc='元') ==100
    assert number_trans(100,'5月均价(元/㎡)','85表 5：2012年5月北京城市部分环比涨价楼盘 ',format_of_number=None, format_desc='元') ==100
    assert number_trans(100,'5月均价(元/㎡)','85表 5：2012年5月北京城市部分环比涨价楼盘 ',format_of_number=None, format_desc='元') ==100
    assert number_trans(10,'最新收盘价','图表15：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'最新收盘价','图表15：教育行业近三年定增倒挂个股',format_of_number=None, format_desc='元') ==10
    assert number_trans(10,'最新收盘价','图表15：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==10
    assert number_trans(20,'本周销售面积','49 表2012年第23周（2012.5.28-2012.6.3） 新房成交数据 2',format_of_number=None, format_desc=None) ==20
    assert number_trans(1000,'本周销售套数','49 表2012年第23周（2012.5.28-2012.6.3） 新房成交数据 2',format_of_number=None, format_desc=None) ==1000
    assert number_trans(20,'本周销售面积','49 表2012年第23周（2012.5.28-2012.6.3） 新房成交数据 2',format_of_number=None, format_desc=None) ==20
    assert number_trans(1000,'本周销售套数','49 表2012年第23周（2012.5.28-2012.6.3） 新房成交数据 2',format_of_number=None, format_desc=None) ==1000
    assert number_trans(20,'本周销售面积','49 表2012年第23周（2012.5.28-2012.6.3） 新房成交数据 2',format_of_number=None, format_desc=None) ==20
    assert number_trans(1000,'本周销售套数','49 表2012年第23周（2012.5.28-2012.6.3） 新房成交数据 2',format_of_number=None, format_desc=None) ==1000
    assert number_trans(10,'同比增长率','表84：2017年全球物流自动化系统集成十五强 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'同比增长率','表84：2017年全球物流自动化系统集成十五强 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'同比增长率','表84：2017年全球物流自动化系统集成十五强 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(1,'PE14E','60 附表：国信证券重点覆盖的上市公司盈利预测   ',format_of_number=None, format_desc=None) ==1
    assert number_trans(8,'PB','60 附表：国信证券重点覆盖的上市公司盈利预测   ',format_of_number=None, format_desc=None) ==8
    assert number_trans(1,'PB','60 附表：国信证券重点覆盖的上市公司盈利预测   ',format_of_number=None, format_desc=None) ==1
    assert number_trans(8,'PB','60 附表：国信证券重点覆盖的上市公司盈利预测   ',format_of_number=None, format_desc=None) ==8
    assert number_trans(1,'PB','60 附表：国信证券重点覆盖的上市公司盈利预测   ',format_of_number=None, format_desc=None) ==1
    assert number_trans(8,'PB','60 附表：国信证券重点覆盖的上市公司盈利预测   ',format_of_number=None, format_desc=None) ==8
    assert number_trans(50,'2017Q1','表8：电感行业-季度营收同比增速-算数平均 ',format_of_number=None, format_desc=None) ==50
    assert number_trans(10,'2017Q1','表8：电感行业-季度营收同比增速-算数平均 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(50,'2016Q3','表8：电感行业-季度营收同比增速-算数平均 ',format_of_number=None, format_desc=None) ==50
    assert number_trans(10,'2017Q3','表8：电感行业-季度营收同比增速-算数平均 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(50,'2017Q1','表8：电感行业-季度营收同比增速-算数平均 ',format_of_number=None, format_desc=None) ==50
    assert number_trans(10,'2017Q1','表8：电感行业-季度营收同比增速-算数平均 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'股权占比','67表2：大秦铁路拟入股蒙华、唐港铁路，整体收购太原通信段 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'股权占比','67表2：大秦铁路拟入股蒙华、唐港铁路，整体收购太原通信段 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'股权占比','67表2：大秦铁路拟入股蒙华、唐港铁路，整体收购太原通信段 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'环比','40 表 2：二线城市2012-06-13房地产成交数据一 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'环比','40 表 2：二线城市2012-06-13房地产成交数据一 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'环比','40 表 2：二线城市2012-06-13房地产成交数据一 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(200,'开盘套数','01表8：北京2012年5月样本新盘去化及价格比较情况（单位：元/平） ',format_of_number=None, format_desc=None) ==200
    assert number_trans(40,'已签约套数','01表8：北京2012年5月样本新盘去化及价格比较情况（单位：元/平） ',format_of_number=None, format_desc=None) ==40
    assert number_trans(200,'开盘套数','01表8：北京2012年5月样本新盘去化及价格比较情况（单位：元/平） ',format_of_number=None, format_desc=None) ==200
    assert number_trans(40,'已签约套数','01表8：北京2012年5月样本新盘去化及价格比较情况（单位：元/平） ',format_of_number=None, format_desc=None) ==40
    assert number_trans(40,'已签约套数','01表8：北京2012年5月样本新盘去化及价格比较情况（单位：元/平） ',format_of_number=None, format_desc=None) ==40
    assert number_trans(200,'开盘套数','01表8：北京2012年5月样本新盘去化及价格比较情况（单位：元/平） ',format_of_number=None, format_desc=None) ==200
    assert number_trans(40,'市值','表 9 美股交通运输行业（陆运）重点跟踪公司业绩增速与估值（市值单位：亿美元；截止 2019.1.11）  ',format_of_number='亿', format_desc=None) ==40
    assert number_trans(40,'市值','表 9 美股交通运输行业（陆运）重点跟踪公司业绩增速与估值（市值单位：亿美元；截止 2019.1.11）  ',format_of_number='亿', format_desc=None) ==40
    assert number_trans(40,'收益','表 9 美股交通运输行业（陆运）重点跟踪公司业绩增速与估值（市值单位：亿美元；截止 2019.1.11）  ',format_of_number='亿', format_desc=None) ==40
    assert number_trans(100,'去年同期28日成交','40 表 2：二线城市2012-06-13房地产成交数据一 ',format_of_number='万', format_desc='平') ==1000000
    assert number_trans(100,'近7日日均成交环比','40 表 2：二线城市2012-06-13房地产成交数据一 ',format_of_number='万', format_desc='平') ==1000000
    assert number_trans(100,'近7日日均交','40 表 2：二线城市2012-06-13房地产成交数据一 ',format_of_number='万', format_desc='平') ==1000000
    assert number_trans(100,'近7日日均成交环比','40 表 2：二线城市2012-06-13房地产成交数据一 ',format_of_number='万', format_desc='平') ==1000000
    assert number_trans(100,'去年同期28日成交','40 表 2：二线城市2012-06-13房地产成交数据一 ',format_of_number='万', format_desc='平') ==1000000
    assert number_trans(100,'近7日日均成交环比','40 表 2：二线城市2012-06-13房地产成交数据一 ',format_of_number='万', format_desc='平') ==1000000


    print(number_trans(100,'在产产能','表10：2018年11月行业前五家企业产能情况（单位：万吨/年） ',format_of_number='万', format_desc='吨'))
    assert number_trans(100,'在产产能','表10：2018年11月行业前五家企业产能情况（单位：万吨/年） ',format_of_number='万', format_desc='吨') ==100
    assert number_trans(100,'总产能','表10：2018年11月行业前五家企业产能情况（单位：万吨/年） ',format_of_number='万', format_desc='吨') ==100
    assert number_trans(100,'总产能','表10：2018年11月行业前五家企业产能情况（单位：万吨/年） ',format_of_number='万', format_desc='吨') ==100
    assert number_trans(100,'在产产能','表10：2018年11月行业前五家企业产能情况（单位：万吨/年） ',format_of_number='万', format_desc='吨') ==100
    assert number_trans(100,'在产产能','表10：2018年11月行业前五家企业产能情况（单位：万吨/年） ',format_of_number='万', format_desc='吨') ==100
    assert number_trans(100,'总产能','表10：2018年11月行业前五家企业产能情况（单位：万吨/年） ',format_of_number='万', format_desc='吨') ==100
    assert number_trans(10,'18/09单季营收增速','表1： 全球被动元器件核心上市公司梳理 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE','表1： 全球被动元器件核心上市公司梳理 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE','表1： 全球被动元器件核心上市公司梳理 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE','表1： 全球被动元器件核心上市公司梳理 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(1000,'楼面价','43 表1：上周住宅用地成交活跃度城市 ',format_of_number=None, format_desc=None) ==1000
    assert number_trans(0,'溢价','43 表1：上周住宅用地成交活跃度城市 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(1000,'楼面价','43 表1：上周住宅用地成交活跃度城市 ',format_of_number=None, format_desc=None) ==1000
    assert number_trans(0,'溢价','43 表1：上周住宅用地成交活跃度城市 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(1000,'楼面价','43 表1：上周住宅用地成交活跃度城市 ',format_of_number=None, format_desc=None) ==1000
    assert number_trans(0,'溢价','43 表1：上周住宅用地成交活跃度城市 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(23,'May','85表15：南京住宅期房2007-2012年1月各月成交面积（万平） ',format_of_number=None, format_desc=None) ==23
    assert number_trans(23,'May','85表15：南京住宅期房2007-2012年1月各月成交面积（万平） ',format_of_number=None, format_desc=None) ==23
    assert number_trans(48,'May','85表15：南京住宅期房2007-2012年1月各月成交面积（万平） ',format_of_number=None, format_desc=None) ==48
    assert number_trans(48,'May','85表15：南京住宅期房2007-2012年1月各月成交面积（万平） ',format_of_number=None, format_desc=None) ==48
    assert number_trans(2327,'前一周成交','12 表一：拟周成交情况（套数） ',format_of_number=None, format_desc=None) ==2327
    assert number_trans(40,'环比','12 表一：拟周成交情况（套数） ',format_of_number=None, format_desc=None) ==40
    assert number_trans(2327,'前一周成交','12 表一：拟周成交情况（套数） ',format_of_number=None, format_desc=None) ==2327
    assert number_trans(2327,'前一周成交','12 表一：拟周成交情况（套数） ',format_of_number=None, format_desc=None) ==2327
    assert number_trans(40,'环比','12 表一：拟周成交情况（套数） ',format_of_number=None, format_desc=None) ==40
    assert number_trans(30,'本周收盘价','图表 13   行业涨幅后五',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'本周收盘价','图表 13   行业涨幅后五',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'本周收盘价','图表 13   行业涨幅后五',format_of_number=None, format_desc=None) ==30
    assert number_trans(10,'股价','69 表4：2012年6月12日关注类非住宅开发公司估值表 ',format_of_number=None, format_desc='元') ==10
    assert number_trans(10,'股价','69 表4：2012年6月12日关注类非住宅开发公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'股价','69 表4：2012年6月12日关注类非住宅开发公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(8,'股价','23 非住宅公司估值表',format_of_number=None, format_desc=None) ==8
    assert number_trans(8,'股价','23 非住宅公司估值表',format_of_number=None, format_desc=None) ==8
    assert number_trans(8,'股价','23 非住宅公司估值表',format_of_number=None, format_desc='元') ==8
    assert number_trans(1,'2011年日均成交','01 表：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'2012年日均成交','01 表：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'2011年日均成交','01 表：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'2012年日均成交','01 表：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'2011年日均成交','01 表：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'2012年日均成交','01 表：主要城市成交信息一览表（粗体标注的城市已出台限购令，6月7日为T日） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(20,'PE17A','表25：证券行业重点覆盖公司估值比较表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE19E','表25：证券行业重点覆盖公司估值比较表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE18E','表25：证券行业重点覆盖公司估值比较表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE19E','表25：证券行业重点覆盖公司估值比较表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE17A','表25：证券行业重点覆盖公司估值比较表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE19E','表25：证券行业重点覆盖公司估值比较表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE19E','表25：证券行业重点覆盖公司估值比较表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE19E','表25：证券行业重点覆盖公司估值比较表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE18E','表25：证券行业重点覆盖公司估值比较表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE19E','表25：证券行业重点覆盖公司估值比较表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE18E','表25：证券行业重点覆盖公司估值比较表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE19E','表25：证券行业重点覆盖公司估值比较表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(11,'市盈率PE','171图表37：公路板块标的筛选 ',format_of_number=None, format_desc=None) ==11
    assert number_trans(5,'GDP增速','171图表37：公路板块标的筛选 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(11,'市盈率PE','171图表37：公路板块标的筛选 ',format_of_number=None, format_desc=None) ==11
    assert number_trans(5,'GDP增速','171图表37：公路板块标的筛选 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'GDP增速','171图表37：公路板块标的筛选 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(11,'市盈率PE','171图表37：公路板块标的筛选 ',format_of_number=None, format_desc=None) ==11
    assert number_trans(3,'跑道数量（条）','86表 9 主要机场设计小时容量水平 ',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'跑道数量（条）','86表 9 主要机场设计小时容量水平 ',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'跑道数量（条）','86表 9 主要机场设计小时容量水平 ',format_of_number=None, format_desc=None) ==3
    assert number_trans(5,'周涨跌幅（%）','图54：海外锂电池板块市场表现 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'月涨跌幅（%）','图54：海外锂电池板块市场表现 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'周涨跌幅（%）','图54：海外锂电池板块市场表现 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'月涨跌幅（%）','图54：海外锂电池板块市场表现 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'周涨跌幅（%）','图54：海外锂电池板块市场表现 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'月涨跌幅（%）','图54：海外锂电池板块市场表现 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(1000,'09年高点','79 表2:二线城市可售面积 ',format_of_number=None, format_desc=None) ==1000
    assert number_trans(1000,'09年高点','79 表2:二线城市可售面积 ',format_of_number=None, format_desc=None) ==1000
    assert number_trans(1000,'09年高点','79 表2:二线城市可售面积 ',format_of_number=None, format_desc=None) ==1000
    assert number_trans(100,'联合大陆航空','101表10：1989~2017年7个阶段西南航空股价表现几乎均强于三大航 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'美国航空','101表10：1989~2017年7个阶段西南航空股价表现几乎均强于三大航 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'联合大陆航空','101表10：1989~2017年7个阶段西南航空股价表现几乎均强于三大航 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'美国航空','101表10：1989~2017年7个阶段西南航空股价表现几乎均强于三大航 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'联合大陆航空','101表10：1989~2017年7个阶段西南航空股价表现几乎均强于三大航 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'美国航空','101表10：1989~2017年7个阶段西南航空股价表现几乎均强于三大航 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(10,'2018年动态PE','图表27A股个股市场表现-本周涨跌幅前10   ',format_of_number=None, format_desc=None) ==10
    assert number_trans(8,'座位增长','149图表10： 2019年飞机引进计划      ',format_of_number=None, format_desc=None) ==8
    assert number_trans(8,'座位增长','149图表10： 2019年飞机引进计划      ',format_of_number=None, format_desc=None) ==8
    assert number_trans(8,'座位增长','149图表10： 2019年飞机引进计划      ',format_of_number=None, format_desc=None) ==8
    assert number_trans(8,'座位增长','149图表10： 2019年飞机引进计划      ',format_of_number=None, format_desc=None) ==8
    assert number_trans(8,'座位增长','149图表10： 2019年飞机引进计划      ',format_of_number=None, format_desc=None) ==8
    assert number_trans(1000,'绝对量','134 图1: 2012年1-4月房地产行业表现：',format_of_number='亿', format_desc=None) ==100000000000
    assert number_trans(1000,'绝对量','134 图1: 2012年1-4月房地产行业表现：',format_of_number=None, format_desc=None) ==1000
    assert number_trans(1000,'绝对量','134 图1: 2012年1-4月房地产行业表现：',format_of_number='亿', format_desc=None) ==100000000000
    assert number_trans(10,'收盘价','表32：建材行业重点公司估值情况 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'收盘价','表32：建材行业重点公司估值情况 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'收盘价','表32：建材行业重点公司估值情况 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(24,'营业收入','50图表 56. LED（申万）行业公司前三季度财务数据 ',format_of_number=None, format_desc=None) ==24
    assert number_trans(24,'营业收入','50图表 56. LED（申万）行业公司前三季度财务数据 ',format_of_number=None, format_desc=None) ==24
    assert number_trans(24,'营业收入','50图表 56. LED（申万）行业公司前三季度财务数据 ',format_of_number=None, format_desc=None) ==24
    assert number_trans(20,'收盘价','75表24：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(1,'PE2019E','75表24：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'PE2019E','75表24：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(20,'收盘价','75表24：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc='元') ==20
    assert number_trans(20,'收盘价','75表24：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc='元') ==20
    assert number_trans(1,'PE2019E','75表24：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(0,'2017A','表1：财务报表和主要财务比率之现金流量表 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'2018E','表1：财务报表和主要财务比率之现金流量表 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'2018E','表1：财务报表和主要财务比率之现金流量表 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'2017A','表1：财务报表和主要财务比率之现金流量表 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(10000,'5月均价(元/㎡)','48 表 ：2012年5月广州市部分环比涨价楼盘 ',format_of_number=None, format_desc='元') ==10000
    assert number_trans(10000,'5月均价(元/㎡)','48 表 ：2012年5月广州市部分环比涨价楼盘 ',format_of_number=None, format_desc='元') ==10000
    assert number_trans(10000,'5月均价(元/㎡)','48 表 ：2012年5月广州市部分环比涨价楼盘 ',format_of_number=None, format_desc='元') ==10000
    assert number_trans(80,'月产能（K/月）','表74. 大陆规划新建12寸晶圆厂将在 3年内迎来建设高峰 ',format_of_number=None, format_desc=None) ==80
    assert number_trans(80,'月产能（K/月）','表74. 大陆规划新建12寸晶圆厂将在 3年内迎来建设高峰 ',format_of_number=None, format_desc=None) ==80
    assert number_trans(80,'月产能（K/月）','表74. 大陆规划新建12寸晶圆厂将在 3年内迎来建设高峰 ',format_of_number=None, format_desc=None) ==80
    assert number_trans(10,'PE2011','04 表5重点覆盖公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE2012E','04 表5重点覆盖公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE2011','04 表5重点覆盖公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE2012E','04 表5重点覆盖公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE2011','04 表5重点覆盖公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE2012E','04 表5重点覆盖公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(24,'PE2019E','75表24：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==24
    assert number_trans(24,'PE2019E','75表24：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==24
    assert number_trans(24,'PE2020E','75表24：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==24
    assert number_trans(24,'PE2018E','75表24：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==24
    assert number_trans(24,'PE2018E','75表24：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==24
    assert number_trans(24,'PE2019E','75表24：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==24
    assert number_trans(24,'PE2019E','75表24：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==24
    assert number_trans(24,'PE2018E','75表24：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==24
    assert number_trans(1000000,'一类车','表 5 深高速各条线路客货车流量情况（辆/日） ',format_of_number=None, format_desc=None) ==1000000
    assert number_trans(10000,'二类车','表 5 深高速各条线路客货车流量情况（辆/日） ',format_of_number=None, format_desc=None) ==10000
    assert number_trans(1000000,'一类车','表 5 深高速各条线路客货车流量情况（辆/日） ',format_of_number=None, format_desc=None) ==1000000
    assert number_trans(10000,'二类车','表 5 深高速各条线路客货车流量情况（辆/日） ',format_of_number=None, format_desc=None) ==10000
    assert number_trans(1000000,'一类车','表 5 深高速各条线路客货车流量情况（辆/日） ',format_of_number=None, format_desc=None) ==1000000
    assert number_trans(10000,'二类车','表 5 深高速各条线路客货车流量情况（辆/日） ',format_of_number=None, format_desc=None) ==10000
    assert number_trans(5,'2012年4月成交量环比','64 表2：一线城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'2011年12月成交量环比','64 表2：一线城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'2012年2月成交量环比','64 表2：一线城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'2011年12月成交量环比','64 表2：一线城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'2012年3月成交量环比','64 表2：一线城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'2011年12月成交量环比','64 表2：一线城市周成交数据2（万平米、元） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'票房占比（%）','表4：2019年第1周（2019.01.07 - 2019.01.13）全国电影票房TOP10',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'场均人次','表4：2019年第1周（2019.01.07 - 2019.01.13）全国电影票房TOP10',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'票房占比（%）','表4：2019年第1周（2019.01.07 - 2019.01.13）全国电影票房TOP10',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'场均人次','表4：2019年第1周（2019.01.07 - 2019.01.13）全国电影票房TOP10',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'票房占比（%）','表4：2019年第1周（2019.01.07 - 2019.01.13）全国电影票房TOP10',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'场均人次','表4：2019年第1周（2019.01.07 - 2019.01.13）全国电影票房TOP10',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'最新收盘价','图表31：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc='元') ==5
    assert number_trans(5,'最新收盘价','图表31：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'最新收盘价','图表31：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'场均人次','表3：2019年第4周（2019.01.28 - 2019.02.03）全国电影票房TOP10',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'场均人次','表3：2019年第4周（2019.01.28 - 2019.02.03）全国电影票房TOP10',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'场均人次','表3：2019年第4周（2019.01.28 - 2019.02.03）全国电影票房TOP10',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'PE2011A','48 表2：重点公司盈利预测及投资评级（2012/05/28） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE2011A','48 表2：重点公司盈利预测及投资评级（2012/05/28） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE2011A','48 表2：重点公司盈利预测及投资评级（2012/05/28） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(40,'本周同比(%)','69 表1  重点城市商品房周成交面积（万平米） ',format_of_number=None, format_desc=None) ==40
    assert number_trans(40,'本周同比(%)','69 表1  重点城市商品房周成交面积（万平米） ',format_of_number=None, format_desc=None) ==40
    assert number_trans(40,'本周同比(%)','69 表1  重点城市商品房周成交面积（万平米） ',format_of_number=None, format_desc=None) ==40
    assert number_trans(1,'日成交','87 表：长三角主要城市成交信息一览表（粗体标注的城市已出台限购令，7月3日为T日） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'日成交','87 表：长三角主要城市成交信息一览表（粗体标注的城市已出台限购令，7月3日为T日） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'日成交','87 表：长三角主要城市成交信息一览表（粗体标注的城市已出台限购令，7月3日为T日） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(20,'房地产开发投资完成额同比','21 表01：各因素对房地产开发投资的拉动作用 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'房地产开发投资完成额同比','21 表01：各因素对房地产开发投资的拉动作用 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'房地产开发投资完成额同比','21 表01：各因素对房地产开发投资的拉动作用 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(1,'EPS2017A','表33：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc='元') ==1
    assert number_trans(20,'PE2018E','表33：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(1,'EPS2017A','表33：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc='元') ==1
    assert number_trans(20,'PE2018E','表33：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(1,'EPS2017A','表33：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc='元') ==1
    assert number_trans(20,'PE2017A','表33：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'场均人次','表7：2019年第2周（2019.1.14 - 2019.1.20）影投票房排名TOP10',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'场均人次','表7：2019年第2周（2019.1.14 - 2019.1.20）影投票房排名TOP10',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'场均人次','表7：2019年第2周（2019.1.14 - 2019.1.20）影投票房排名TOP10',format_of_number=None, format_desc=None) ==20
    assert number_trans(2,'市场份额%','表10：1月19日省级卫视晚间综艺节目收视率TOP10',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'市场份额%','表10：1月19日省级卫视晚间综艺节目收视率TOP10',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'市场份额%','表10：1月19日省级卫视晚间综艺节目收视率TOP10',format_of_number=None, format_desc=None) ==2
    assert number_trans(7,'收盘价','表33：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==7
    assert number_trans(5,'最新股价','18 表3：内房股上周股价涨幅前十表现 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'最新股价','18 表3：内房股上周股价涨幅前十表现 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'最新股价','18 表3：内房股上周股价涨幅前十表现 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(1000,'目前影院数量','图表 21   现有院线的经营情况',format_of_number=None, format_desc=None) ==1000
    assert number_trans(5000,'2018年底银幕数量','图表 21   现有院线的经营情况',format_of_number=None, format_desc=None) ==5000
    assert number_trans(1000,'目前影院数量','图表 21   现有院线的经营情况',format_of_number=None, format_desc=None) ==1000
    assert number_trans(5000,'2018年底银幕数量','图表 21   现有院线的经营情况',format_of_number=None, format_desc=None) ==5000
    assert number_trans(1000,'目前影院数量','图表 21   现有院线的经营情况',format_of_number=None, format_desc=None) ==1000
    assert number_trans(5000,'2018年底银幕数量','图表 21   现有院线的经营情况',format_of_number=None, format_desc=None) ==5000
    assert number_trans(8000,'降息前月还款额10年','14 表2 本次降息对购房人财务影响 ',format_of_number=None, format_desc=None) ==8000
    assert number_trans(8000,'降息前月还款额20年','14 表2 本次降息对购房人财务影响 ',format_of_number=None, format_desc=None) ==8000
    assert number_trans(8000,'降息前月还款额10年','14 表2 本次降息对购房人财务影响 ',format_of_number=None, format_desc=None) ==8000
    assert number_trans(8000,'降息前月还款额20年','14 表2 本次降息对购房人财务影响 ',format_of_number=None, format_desc=None) ==8000
    assert number_trans(8000,'降息前月还款额20年','14 表2 本次降息对购房人财务影响 ',format_of_number=None, format_desc=None) ==8000
    assert number_trans(8000,'降息前月还款额30年','14 表2 本次降息对购房人财务影响 ',format_of_number=None, format_desc=None) ==8000
    assert number_trans(10,'引进宽体机','149图表10： 2019年飞机引进计划      ',format_of_number=None, format_desc=None) ==10
    assert number_trans(50,'引进窄体机','149图表10： 2019年飞机引进计划      ',format_of_number=None, format_desc=None) ==50
    assert number_trans(10,'引进宽体机','149图表10： 2019年飞机引进计划      ',format_of_number=None, format_desc=None) ==10
    assert number_trans(50,'引进窄体机','149图表10： 2019年飞机引进计划      ',format_of_number=None, format_desc=None) ==50
    assert number_trans(10,'引进宽体机','149图表10： 2019年飞机引进计划      ',format_of_number=None, format_desc=None) ==10
    assert number_trans(50,'引进窄体机','149图表10： 2019年飞机引进计划      ',format_of_number=None, format_desc=None) ==50
    assert number_trans(2,'存款利率调整前','15 表1: 近年来历次降息 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'存款利率调整后','15 表1: 近年来历次降息 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'存款利率调整前','15 表1: 近年来历次降息 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'存款利率调整后','15 表1: 近年来历次降息 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'存款利率调整前','15 表1: 近年来历次降息 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'存款利率调整后','15 表1: 近年来历次降息 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'票房占比（%）','表4：2019年第1周（2019.01.07 - 2019.01.13）全国电影票房TOP10',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'票房占比（%）','表4：2019年第1周（2019.01.07 - 2019.01.13）全国电影票房TOP10',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'票房占比（%）','表4：2019年第1周（2019.01.07 - 2019.01.13）全国电影票房TOP10',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'EPS2013','07 综合经营重点跟踪公司一览      ',format_of_number=None, format_desc=None) ==2
    assert number_trans(10,'PE2011','07 综合经营重点跟踪公司一览      ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE2010','07 综合经营重点跟踪公司一览      ',format_of_number=None, format_desc=None) ==10
    assert number_trans(2,'EPS2013','07 综合经营重点跟踪公司一览      ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'EPS2013','07 综合经营重点跟踪公司一览      ',format_of_number=None, format_desc=None) ==2
    assert number_trans(10,'PE2013','07 综合经营重点跟踪公司一览      ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'国内客运量占比','表1：欧美廉航龙头市值超过千亿元 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'国内客运量占比','表1：欧美廉航龙头市值超过千亿元 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'国内客运量占比','表1：欧美廉航龙头市值超过千亿元 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(3,'最新收盘价','图表11：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==3
    assert number_trans(20,'增发价格','图表11：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==20
    assert number_trans(3,'最新收盘价','图表11：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==3
    assert number_trans(20,'增发价格','图表11：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'增发价格','图表11：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==20
    assert number_trans(3,'最新收盘价','图表11：教育行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==3
    assert number_trans(100,'收入','119表 8 快递公司的净利润及其增速（2018Q1-Q3）（亿元） ',format_of_number='亿', format_desc='元') ==100
    assert number_trans(15,'净利润','119表 8 快递公司的净利润及其增速（2018Q1-Q3）（亿元） ',format_of_number='亿', format_desc='元') ==15
    assert number_trans(100,'收入','119表 8 快递公司的净利润及其增速（2018Q1-Q3）（亿元） ',format_of_number='亿', format_desc='元') ==100
    assert number_trans(15,'净利润','119表 8 快递公司的净利润及其增速（2018Q1-Q3）（亿元） ',format_of_number='亿', format_desc='元') ==15
    assert number_trans(100,'收入','119表 8 快递公司的净利润及其增速（2018Q1-Q3）（亿元） ',format_of_number='亿', format_desc='元') ==100
    assert number_trans(15,'净利润','119表 8 快递公司的净利润及其增速（2018Q1-Q3）（亿元） ',format_of_number='亿', format_desc='元') ==15
    assert number_trans(6,'最新股价','35 表7：2012年6月综合类关注型公司估值表 ',format_of_number=None, format_desc=None) ==6
    assert number_trans(2,'PB估值','35 表7：2012年6月综合类关注型公司估值表 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'PB估值','35 表7：2012年6月综合类关注型公司估值表 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(6,'最新股价','35 表7：2012年6月综合类关注型公司估值表 ',format_of_number=None, format_desc=None) ==6
    assert number_trans(6,'最新股价','35 表7：2012年6月综合类关注型公司估值表 ',format_of_number=None, format_desc='元') ==6
    assert number_trans(2,'PB估值','35 表7：2012年6月综合类关注型公司估值表 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(800,'目前影院数量','图表 21   现有院线的经营情况',format_of_number=None, format_desc=None) ==800
    assert number_trans(800,'目前影院数量','图表 21   现有院线的经营情况',format_of_number=None, format_desc=None) ==800
    assert number_trans(800,'目前影院数量','图表 21   现有院线的经营情况',format_of_number=None, format_desc=None) ==800
    assert number_trans(100,'去年同期28日日均环比','30 表 1：重点城市成交数据一 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(1,'去年同期28日日均环比','30 表 1：重点城市成交数据一 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(100,'去年同期28日日均环比','30 表 1：重点城市成交数据一 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(1,'去年同期28日日均环比','30 表 1：重点城市成交数据一 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(100,'去年同期28日日均环比','30 表 1：重点城市成交数据一 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(1,'近8日日均环比','30 表 1：重点城市成交数据一 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(40,'首付成数','90 表 6：贷款年限20年假设降20个基点对月供影响测算（元/%） ',format_of_number=None, format_desc=None) ==40
    assert number_trans(100,'每月减少还','90 表 6：贷款年限20年假设降20个基点对月供影响测算（元/%） ',format_of_number=None, format_desc=None) ==100
    assert number_trans(40,'首付成数','90 表 6：贷款年限20年假设降20个基点对月供影响测算（元/%） ',format_of_number=None, format_desc=None) ==40
    assert number_trans(100,'每月减少还','90 表 6：贷款年限20年假设降20个基点对月供影响测算（元/%） ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'每月减少还','90 表 6：贷款年限20年假设降20个基点对月供影响测算（元/%） ',format_of_number=None, format_desc=None) ==100
    assert number_trans(40,'首付成数','90 表 6：贷款年限20年假设降20个基点对月供影响测算（元/%） ',format_of_number=None, format_desc=None) ==40
    assert number_trans(2,'市场份额%','图表15: 上周五综艺节目收视数据（12月14日）',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'市场份额%','图表15: 上周五综艺节目收视数据（12月14日）',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'市场份额%','图表15: 上周五综艺节目收视数据（12月14日）',format_of_number=None, format_desc=None) ==2
    assert number_trans(23,'PE2010','07 综合经营重点跟踪公司一览      ',format_of_number=None, format_desc=None) ==23
    assert number_trans(23,'PE2013','07 综合经营重点跟踪公司一览      ',format_of_number=None, format_desc=None) ==23
    assert number_trans(2,'PE2010','07 综合经营重点跟踪公司一览      ',format_of_number=None, format_desc=None) ==2
    assert number_trans(23,'PB','07 综合经营重点跟踪公司一览      ',format_of_number=None, format_desc=None) ==23
    assert number_trans(23,'PE2010','07 综合经营重点跟踪公司一览      ',format_of_number=None, format_desc=None) ==23
    assert number_trans(23,'PE2011','07 综合经营重点跟踪公司一览      ',format_of_number=None, format_desc=None) ==23
    assert number_trans(700,'2018E绝对值','50表10：2016-2020年主要公司客机数进情况      ',format_of_number=None, format_desc=None) ==700
    assert number_trans(700,'2019E绝对值','50表10：2016-2020年主要公司客机数进情况      ',format_of_number=None, format_desc=None) ==700
    assert number_trans(700,'2018E绝对值','50表10：2016-2020年主要公司客机数进情况      ',format_of_number=None, format_desc=None) ==700
    assert number_trans(700,'2019E绝对值','50表10：2016-2020年主要公司客机数进情况      ',format_of_number=None, format_desc=None) ==700
    assert number_trans(700,'2018E绝对值','50表10：2016-2020年主要公司客机数进情况      ',format_of_number=None, format_desc=None) ==700
    assert number_trans(700,'2019E绝对值','50表10：2016-2020年主要公司客机数进情况      ',format_of_number=None, format_desc=None) ==700
    assert number_trans(1,'EPS2011','33 表7：2012年06月03日非住宅类开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS2012E','33 表7：2012年06月03日非住宅类开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS2013E','33 表7：2012年06月03日非住宅类开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS2011','33 表7：2012年06月03日非住宅类开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS2012E','33 表7：2012年06月03日非住宅类开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS2013E','33 表7：2012年06月03日非住宅类开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS2013E','33 表7：2012年06月03日非住宅类开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS2011','33 表7：2012年06月03日非住宅类开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS2012E','33 表7：2012年06月03日非住宅类开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS2013E','33 表7：2012年06月03日非住宅类开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==1
    assert number_trans(100,'上周成交量（套）','55 表3：跟踪的珠三角城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'上周成交量（套）','55 表3：跟踪的珠三角城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'上周成交量（套）','55 表3：跟踪的珠三角城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(0,'成交量环比增长','57 表5：跟踪的西部城市楼市一周成交详细表 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(30,'平均票价','表6：2019年第2周（2019.1.14 - 2019.1.20）全国院线票房TOP10',format_of_number=None, format_desc='元') ==30
    assert number_trans(30,'平均票价','表6：2019年第2周（2019.1.14 - 2019.1.20）全国院线票房TOP10',format_of_number=None, format_desc='元') ==30
    assert number_trans(30,'平均票价','表6：2019年第2周（2019.1.14 - 2019.1.20）全国院线票房TOP10',format_of_number=None, format_desc='元') ==30
    assert number_trans(4,'EPS18E','表2：铁路海运重点公司估值对比表 ',format_of_number=None, format_desc=None) ==4 
    assert number_trans(55,'PE2012E','62 盈利预测和估值2',format_of_number=None, format_desc=None) ==55
    assert number_trans(55,'PE2013E','62 盈利预测和估值2',format_of_number=None, format_desc=None) ==55
    assert number_trans(55,'PE2013E','62 盈利预测和估值2',format_of_number=None, format_desc=None) ==55
    assert number_trans(55,'PE2012E','62 盈利预测和估值2',format_of_number=None, format_desc=None) ==55
    assert number_trans(55,'PE2012E','62 盈利预测和估值2',format_of_number=None, format_desc=None) ==55
    assert number_trans(55,'PE2013E','62 盈利预测和估值2',format_of_number=None, format_desc=None) ==55
    assert number_trans(20,'环比上周（%）','图16、重点城市新房成交数据 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'环比上周（%）','图16、重点城市新房成交数据 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'环比上周（%）','图16、重点城市新房成交数据 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(5,'最新收盘价','图表81：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'定增价除权后至今价格','图表81：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'最新收盘价','图表81：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'定增价除权后至今价格','图表81：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'最新收盘价','图表81：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'定增价除权后至今价格','图表81：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'环比上周（%）','图17、重点类型城市二手房成交数据（万平米）',format_of_number=None, format_desc=None) ==5
    assert number_trans(1,'环比上月（%）','图17、重点类型城市二手房成交数据（万平米）',format_of_number=None, format_desc=None) ==1
    assert number_trans(5,'环比上周（%）','图17、重点类型城市二手房成交数据（万平米）',format_of_number=None, format_desc=None) ==5
    assert number_trans(1,'环比上月（%）','图17、重点类型城市二手房成交数据（万平米）',format_of_number=None, format_desc=None) ==1
    assert number_trans(5,'环比上周（%）','图17、重点类型城市二手房成交数据（万平米）',format_of_number=None, format_desc=None) ==5
    assert number_trans(1,'环比上月（%）','图17、重点类型城市二手房成交数据（万平米）',format_of_number=None, format_desc=None) ==1
    assert number_trans(500,'前一日成交','40 表 2：二线城市2012-06-13房地产成交数据一 ',format_of_number='万', format_desc='平') ==5000000 # mark 
    assert number_trans(500,'日成交','40 表 2：二线城市2012-06-13房地产成交数据一 ',format_of_number='万', format_desc='平') ==5000000 # mark 
    assert number_trans(500,'日成交','40 表 2：二线城市2012-06-13房地产成交数据一 ',format_of_number='万', format_desc='平') ==5000000 # mark 
    assert number_trans(500,'前一日成交','40 表 2：二线城市2012-06-13房地产成交数据一 ',format_of_number='万', format_desc='平') ==5000000
    assert number_trans(500,'日成交','40 表 2：二线城市2012-06-13房地产成交数据一 ',format_of_number='万', format_desc='平') ==5000000
    assert number_trans(500,'前一日成交','40 表 2：二线城市2012-06-13房地产成交数据一 ',format_of_number='万', format_desc='平') ==5000000
    assert number_trans(10,'累计值同比增速','表5：近年年房地产销售面积预测（万平米） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'累计值同比增速','表5：近年年房地产销售面积预测（万平米） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'累计值同比增速','表5：近年年房地产销售面积预测（万平米） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'股价','表4：A股传媒行业网络游戏公司估值一览（加阴影为华金证券研究所预测，其余为wind一致预期）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PETTM','表4：A股传媒行业网络游戏公司估值一览（加阴影为华金证券研究所预测，其余为wind一致预期）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'股价','表4：A股传媒行业网络游戏公司估值一览（加阴影为华金证券研究所预测，其余为wind一致预期）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE18E','表4：A股传媒行业网络游戏公司估值一览（加阴影为华金证券研究所预测，其余为wind一致预期）',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'股价','表4：A股传媒行业网络游戏公司估值一览（加阴影为华金证券研究所预测，其余为wind一致预期）',format_of_number=None, format_desc='元') ==10
    assert number_trans(10,'PETTM','表4：A股传媒行业网络游戏公司估值一览（加阴影为华金证券研究所预测，其余为wind一致预期）',format_of_number=None, format_desc=None) ==10
    assert number_trans(2,'PB估值','34 表6：2012年6月住宅开发关注类公司估值表 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'PB估值','34 表6：2012年6月住宅开发关注类公司估值表 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(30,'PE2017','图表52、重点公司估值表（2018.12.14） ',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'PE2017','图表52、重点公司估值表（2018.12.14） ',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'PE2017','图表52、重点公司估值表（2018.12.14） ',format_of_number=None, format_desc=None) ==30
    assert number_trans(5,'月环比涨幅','88表 4：2012年5月深圳城市部分环比涨价楼盘 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'月环比涨幅','88表 4：2012年5月深圳城市部分环比涨价楼盘 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'月环比涨幅','88表 4：2012年5月深圳城市部分环比涨价楼盘 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(400,'11年底','80 表3:三线城市可售面积 ',format_of_number=None, format_desc=None) ==400
    assert number_trans(400,'09年高点','80 表3:三线城市可售面积 ',format_of_number=None, format_desc=None) ==400
    assert number_trans(400,'11年底','80 表3:三线城市可售面积 ',format_of_number=None, format_desc=None) ==400
    assert number_trans(400,'11年底','80 表3:三线城市可售面积 ',format_of_number=None, format_desc=None) ==400
    assert number_trans(400,'11年底','80 表3:三线城市可售面积 ',format_of_number=None, format_desc=None) ==400
    assert number_trans(400,'09年高点','80 表3:三线城市可售面积 ',format_of_number=None, format_desc=None) ==400
    assert number_trans(20,'主要业务','表2： 全球被动元器件核心上市公司梳理 ',format_of_number='亿', format_desc=None) ==2000000000
    assert number_trans(20,'主要业务','表2： 全球被动元器件核心上市公司梳理 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(10,'周涨跌幅%','表 12：传媒互联网行业 传媒互联网行业 A 股情况 股情况',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'周涨跌幅%','表 12：传媒互联网行业 传媒互联网行业 A 股情况 股情况',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'周涨跌幅%','表 12：传媒互联网行业 传媒互联网行业 A 股情况 股情况',format_of_number=None, format_desc=None) ==10
    assert number_trans(100,'4月套数','51 表 ：北京2012年4月部分涨价楼盘一览 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(20000,'3月均价','51 表 ：北京2012年4月部分涨价楼盘一览 ',format_of_number=None, format_desc=None) ==20000
    assert number_trans(100,'4月套数','51 表 ：北京2012年4月部分涨价楼盘一览 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(20000,'4月套数','51 表 ：北京2012年4月部分涨价楼盘一览 ',format_of_number=None, format_desc=None) ==20000
    assert number_trans(100,'4月套数','51 表 ：北京2012年4月部分涨价楼盘一览 ',format_of_number=None, format_desc=None) ==100
    assert number_trans(20000,'3月均价','51 表 ：北京2012年4月部分涨价楼盘一览 ',format_of_number=None, format_desc=None) ==20000
    assert number_trans(50,'营业收入同比增长率','50图表 56. LED（申万）行业公司前三季度财务数据 ',format_of_number=None, format_desc=None) ==50
    assert number_trans(30,'归母净利润同比','50图表 56. LED（申万）行业公司前三季度财务数据 ',format_of_number=None, format_desc=None) ==30
    assert number_trans(50,'营业收入同比增长率','50图表 56. LED（申万）行业公司前三季度财务数据 ',format_of_number=None, format_desc=None) ==50
    assert number_trans(30,'归母净利润','50图表 56. LED（申万）行业公司前三季度财务数据 ',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'归母净利润','50图表 56. LED（申万）行业公司前三季度财务数据 ',format_of_number=None, format_desc=None) ==30
    assert number_trans(50,'营业收入同比增长率','50图表 56. LED（申万）行业公司前三季度财务数据 ',format_of_number=None, format_desc=None) ==50
    assert number_trans(1,'2016A每股收益(元/股)','表79. 机械行业主要上市公司估值表',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'2016A每股收益(元/股)','表79. 机械行业主要上市公司估值表',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'2016A每股收益(元/股)','表79. 机械行业主要上市公司估值表',format_of_number=None, format_desc=None) ==1
    assert number_trans(20,'定增价除权后至今价格','图表199：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'增发价格','图表199：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'定增价除权后至今价格','图表199：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'增发价格','图表199：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'定增价除权后至今价格','图表199：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'增发价格','图表199：传媒行业近三年定增倒挂个股',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2019E','75表24：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2020E','75表24：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2019E','75表24：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2020E','75表24：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2019E','75表24：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2020E','75表24：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==20
    assert number_trans(300,'市值','表 10 港股交通运输行业（公路与铁路）重点跟踪公司业绩增速与估值（市值单位：亿港元；截止 2019.1.11） ',format_of_number='亿', format_desc=None) ==300
    assert number_trans(300,'市值','表 10 港股交通运输行业（公路与铁路）重点跟踪公司业绩增速与估值（市值单位：亿港元；截止 2019.1.11） ',format_of_number='亿', format_desc=None) ==300
    assert number_trans(300,'市值','表 10 港股交通运输行业（公路与铁路）重点跟踪公司业绩增速与估值（市值单位：亿港元；截止 2019.1.11） ',format_of_number='亿', format_desc=None) ==300
    assert number_trans(10,'总地面积','26 表2012年5月至今部分上市房企拿地情况 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'建筑面积','26 表2012年5月至今部分上市房企拿地情况 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'总地面积','26 表2012年5月至今部分上市房企拿地情况 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'建筑面积','26 表2012年5月至今部分上市房企拿地情况 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'总地面积','26 表2012年5月至今部分上市房企拿地情况 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'建筑面积','26 表2012年5月至今部分上市房企拿地情况 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE2011','31 表5：2012年06月03日住宅开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE2012E','31 表5：2012年06月03日住宅开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE2011','31 表5：2012年06月03日住宅开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'NAV','31 表5：2012年06月03日住宅开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE2011','31 表5：2012年06月03日住宅开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE2012E','31 表5：2012年06月03日住宅开发重点覆盖公司估值表  ',format_of_number=None, format_desc=None) ==10
    assert number_trans(30,'本周同比','表3:一线城市一手房成交周同比、环比对比',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'本周环比','表3:一线城市一手房成交周同比、环比对比',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'本周同比','表3:一线城市一手房成交周同比、环比对比',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'本周环比','表3:一线城市一手房成交周同比、环比对比',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'本周环比','表3:一线城市一手房成交周同比、环比对比',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'本周同比','表3:一线城市一手房成交周同比、环比对比',format_of_number=None, format_desc=None) ==30
    assert number_trans(10,'本周','116表4:三线城市去化时间对比表（单位：月） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'上周','116表4:三线城市去化时间对比表（单位：月） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'本周','116表4:三线城市去化时间对比表（单位：月） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'上周','116表4:三线城市去化时间对比表（单位：月） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'本周','116表4:三线城市去化时间对比表（单位：月） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'上周','116表4:三线城市去化时间对比表（单位：月） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'去年同期','116表4:三线城市去化时间对比表（单位：月） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(20,'PE2018E','表105：相关标的盈利预测表及估值表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2019E','表105：相关标的盈利预测表及估值表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2018E','表105：相关标的盈利预测表及估值表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2019E','表105：相关标的盈利预测表及估值表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2018E','表105：相关标的盈利预测表及估值表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'PE2019E','表105：相关标的盈利预测表及估值表 ',format_of_number=None, format_desc=None) ==20
    assert number_trans(10,'民航客运（全年）','图表7：2011-2017年我国交通运输方式全年客运量与春运客运量增速对比 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'公路客运(春运）','图表7：2011-2017年我国交通运输方式全年客运量与春运客运量增速对比 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'民航客运（全年）','图表7：2011-2017年我国交通运输方式全年客运量与春运客运量增速对比 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'公路客运（全年）','图表7：2011-2017年我国交通运输方式全年客运量与春运客运量增速对比 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'铁路客运量（全年）','图表7：2011-2017年我国交通运输方式全年客运量与春运客运量增速对比 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'公路客运（全年）','图表7：2011-2017年我国交通运输方式全年客运量与春运客运量增速对比 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(0,'周涨跌幅（%）','图51：汽车电子板块市场表现 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'月涨跌幅（%）','图51：汽车电子板块市场表现 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'月涨跌幅（%）','图51：汽车电子板块市场表现 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'月涨跌幅（%）','图51：汽车电子板块市场表现 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'周涨跌幅（%）','图51：汽车电子板块市场表现 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'月涨跌幅（%）','图51：汽车电子板块市场表现 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(500,'上月','表2：山西动力煤部分产地价格略有上涨 ',format_of_number=None, format_desc=None) ==500
    assert number_trans(500,'上年','表2：山西动力煤部分产地价格略有上涨 ',format_of_number=None, format_desc=None) ==500
    assert number_trans(500,'上月','表2：山西动力煤部分产地价格略有上涨 ',format_of_number=None, format_desc=None) ==500
    assert number_trans(500,'上年','表2：山西动力煤部分产地价格略有上涨 ',format_of_number=None, format_desc=None) ==500
    assert number_trans(500,'上月','表2：山西动力煤部分产地价格略有上涨 ',format_of_number=None, format_desc=None) ==500
    assert number_trans(500,'较上年','表2：山西动力煤部分产地价格略有上涨 ',format_of_number=None, format_desc=None) ==500
    assert number_trans(10,'11年H1','08 表8:16个重点城市住宅土地供应对比表(单位:万平米) ',format_of_number='万', format_desc='平') ==10
    assert number_trans(10,'本期环比','08 表8:16个重点城市住宅土地供应对比表(单位:万平米) ',format_of_number='万', format_desc='平') ==10
    assert number_trans(10,'去年累计','08 表8:16个重点城市住宅土地供应对比表(单位:万平米) ',format_of_number='万', format_desc='平') ==10
    assert number_trans(10,'本期环比','08 表8:16个重点城市住宅土地供应对比表(单位:万平米) ',format_of_number='万', format_desc='平') ==10
    assert number_trans(10,'11年H1','08 表8:16个重点城市住宅土地供应对比表(单位:万平米) ',format_of_number='万', format_desc='平') ==10
    assert number_trans(10,'本期环比','08 表8:16个重点城市住宅土地供应对比表(单位:万平米) ',format_of_number='万', format_desc='平') ==10
    assert number_trans(30,'Q3业务量','表 4 递公司的业务量及其增速（2018Q1-Q3）（万亿件） ',format_of_number='亿', format_desc='件') ==30
    assert number_trans(10,'Q3份额','表 4 递公司的业务量及其增速（2018Q1-Q3）（万亿件） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'Q3份额','表 4 递公司的业务量及其增速（2018Q1-Q3）（万亿件） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(30,'Q3业务量','表 4 递公司的业务量及其增速（2018Q1-Q3）（万亿件） ',format_of_number='亿', format_desc='件') ==30
    assert number_trans(30,'Q3业务量','表 4 递公司的业务量及其增速（2018Q1-Q3）（万亿件） ',format_of_number='亿', format_desc='件') ==30
    assert number_trans(10,'Q3份额','表 4 递公司的业务量及其增速（2018Q1-Q3）（万亿件） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(120,'PB','表87：A股汽车服务估值变化 ',format_of_number=None, format_desc=None) ==120
    assert number_trans(120,'PB','表87：A股汽车服务估值变化 ',format_of_number=None, format_desc=None) ==120
    assert number_trans(120,'PB','表87：A股汽车服务估值变化 ',format_of_number=None, format_desc=None) ==120
    assert number_trans(10,'上周成交面积','36 表 2：2012年6月12日各城市成交面积与环比 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'上周成交面积','36 表 2：2012年6月12日各城市成交面积与环比 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'上周成交面积','36 表 2：2012年6月12日各城市成交面积与环比 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'2018E','28表  20：航空公司机队增速引进计划 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'2019E','28表  20：航空公司机队增速引进计划 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'2018E','28表  20：航空公司机队增速引进计划 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'2019E','28表  20：航空公司机队增速引进计划 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'2018E','28表  20：航空公司机队增速引进计划 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'2019E','28表  20：航空公司机队增速引进计划 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(500,'2018年底银幕数量','图表 22   符合成立电影院线公司条件的影投公司',format_of_number=None, format_desc=None) ==500
    assert number_trans(500,'2018年底银幕数量','图表 22   符合成立电影院线公司条件的影投公司',format_of_number=None, format_desc=None) ==500
    assert number_trans(500,'2018年底银幕数量','图表 22   符合成立电影院线公司条件的影投公司',format_of_number=None, format_desc=None) ==500
    assert number_trans(30,'已签约套数','03表7：上海2012年5月新盘去化及价格比较情况（单位：元/平） ',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'已签约套数','03表7：上海2012年5月新盘去化及价格比较情况（单位：元/平） ',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'已签约套数','03表7：上海2012年5月新盘去化及价格比较情况（单位：元/平） ',format_of_number=None, format_desc=None) ==30
    assert number_trans(0,'本周环比','113 表12:四线城市一手房成交周同比、环比对比 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'本周同比','113 表12:四线城市一手房成交周同比、环比对比 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'本周环比','113 表12:四线城市一手房成交周同比、环比对比 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'本周同比','113 表12:四线城市一手房成交周同比、环比对比 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'本周环比','113 表12:四线城市一手房成交周同比、环比对比 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(0,'本周同比','113 表12:四线城市一手房成交周同比、环比对比 ',format_of_number=None, format_desc=None) ==0
    assert number_trans(10,'收盘价','表27：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'收盘价','表27：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'收盘价','表27：同行业可比公司估值（收盘价为2018年12月19日） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE18E','图表7：重点推荐公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE19E','图表7：重点推荐公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE18E','图表7：重点推荐公司估值表 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(2,'变动百分比2012','58 表 4：国信房地产小组重点关注上市公司未来两年业绩受降息影响变化幅度   ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'降息对EPS的增厚2013','58 表 4：国信房地产小组重点关注上市公司未来两年业绩受降息影响变化幅度   ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'变动百分比2012','58 表 4：国信房地产小组重点关注上市公司未来两年业绩受降息影响变化幅度   ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'变动百分比2013','58 表 4：国信房地产小组重点关注上市公司未来两年业绩受降息影响变化幅度   ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'变动百分比2012','58 表 4：国信房地产小组重点关注上市公司未来两年业绩受降息影响变化幅度   ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'变动百分比2013','58 表 4：国信房地产小组重点关注上市公司未来两年业绩受降息影响变化幅度   ',format_of_number=None, format_desc=None) ==2
    assert number_trans(1,'股价','表4：A股传媒行业教育公司估值一览（加阴影为华金证券研究所预测，其余为wind一致预期）',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'股价','表4：A股传媒行业教育公司估值一览（加阴影为华金证券研究所预测，其余为wind一致预期）',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'股价','表4：A股传媒行业教育公司估值一览（加阴影为华金证券研究所预测，其余为wind一致预期）',format_of_number=None, format_desc=None) ==1
    assert number_trans(500,'2019E','149图表10： 2019年飞机引进计划      ',format_of_number=None, format_desc=None) ==500
    assert number_trans(500,'2019E','149图表10： 2019年飞机引进计划      ',format_of_number=None, format_desc=None) ==500
    assert number_trans(500,'2019E','149图表10： 2019年飞机引进计划      ',format_of_number=None, format_desc=None) ==500
    assert number_trans(5,'1月','73表7：主要机场最新业务量数据同比增速（%）更新 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'2月','73表7：主要机场最新业务量数据同比增速（%）更新 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'1月','73表7：主要机场最新业务量数据同比增速（%）更新 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'2月','73表7：主要机场最新业务量数据同比增速（%）更新 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'2月','73表7：主要机场最新业务量数据同比增速（%）更新 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'2月','73表7：主要机场最新业务量数据同比增速（%）更新 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'同比增长率','表84：2017年全球物流自动化系统集成十五强 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'同比增长率','表84：2017年全球物流自动化系统集成十五强 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'同比增长率','表84：2017年全球物流自动化系统集成十五强 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(100,'市值','表 9 美股交通运输行业（陆运）重点跟踪公司业绩增速与估值（市值单位：亿美元；截止 2019.1.11）  ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'收益','表 9 美股交通运输行业（陆运）重点跟踪公司业绩增速与估值（市值单位：亿美元；截止 2019.1.11）  ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(100,'市值','表 9 美股交通运输行业（陆运）重点跟踪公司业绩增速与估值（市值单位：亿美元；截止 2019.1.11）  ',format_of_number='亿', format_desc=None) ==100
    assert number_trans(50000,'2012:1-5月累计值','表2：2012年1-5月全国房地产市场开工建设数据（万平米） ',format_of_number=None, format_desc=None) ==50000
    assert number_trans(1,'2012:1-5月累计同比','表2：2012年1-5月全国房地产市场开工建设数据（万平米） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(50000,'2012:1-5月累计值','表2：2012年1-5月全国房地产市场开工建设数据（万平米） ',format_of_number=None, format_desc=None) ==50000
    assert number_trans(1,'2012:1-5月累计同比','表2：2012年1-5月全国房地产市场开工建设数据（万平米） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(50000,'2012:1-5月累计值','表2：2012年1-5月全国房地产市场开工建设数据（万平米） ',format_of_number=None, format_desc=None) ==50000
    assert number_trans(1,'2012:1-5月累计同比','表2：2012年1-5月全国房地产市场开工建设数据（万平米） ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS2012E','54 附件 6：2012年6月地产公司盈利预测和估值 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'EPS2012E','54 附件 6：2012年6月地产公司盈利预测和估值 ',format_of_number=None, format_desc=None) ==1
    assert number_trans(6,'可售数量','49 表4:2012年6月一线城市房地产行业区域可售统计情况',format_of_number='万', format_desc=None) ==60000
    assert number_trans(60000,'可售数量','49 表4:2012年6月一线城市房地产行业区域可售统计情况',format_of_number=None, format_desc=None) ==60000
    assert number_trans(60000,'可售数量','49 表4:2012年6月一线城市房地产行业区域可售统计情况',format_of_number=None, format_desc=None) ==60000
    assert number_trans(5000,'住宅投资额','26 表 4  2012年1-5月东中西部地区房地产开发投资情况 ',format_of_number='亿', format_desc=None) ==500000000000
    assert number_trans(5000,'住宅投资额','26 表 4  2012年1-5月东中西部地区房地产开发投资情况 ',format_of_number='亿', format_desc=None) ==500000000000
    assert number_trans(5000,'同比增长（%）','26 表 4  2012年1-5月东中西部地区房地产开发投资情况 ',format_of_number='亿', format_desc=None) ==500000000000
    assert number_trans(1,'变动百分比2012','56 表 6：国信房地产小组重点关注上市公司未来两年业绩受降息影响变化幅度   ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'降息对EPS的增厚2013','56 表 6：国信房地产小组重点关注上市公司未来两年业绩受降息影响变化幅度   ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'变动百分比2012','56 表 6：国信房地产小组重点关注上市公司未来两年业绩受降息影响变化幅度   ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'变动百分比2013','56 表 6：国信房地产小组重点关注上市公司未来两年业绩受降息影响变化幅度   ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'变动百分比2012','56 表 6：国信房地产小组重点关注上市公司未来两年业绩受降息影响变化幅度   ',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'变动百分比2013','56 表 6：国信房地产小组重点关注上市公司未来两年业绩受降息影响变化幅度   ',format_of_number=None, format_desc=None) ==1
    assert number_trans(2,'TPPE','表 7：主要 PCB填充材料 Dk及 Df参数 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'CE','表 7：主要 PCB填充材料 Dk及 Df参数 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'CE','表 7：主要 PCB填充材料 Dk及 Df参数 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'PTFE','表 7：主要 PCB填充材料 Dk及 Df参数 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'PTFE','表 7：主要 PCB填充材料 Dk及 Df参数 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'PI','表 7：主要 PCB填充材料 Dk及 Df参数 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'TPPE','表 7：主要 PCB填充材料 Dk及 Df参数 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'CE','表 7：主要 PCB填充材料 Dk及 Df参数 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'PI','表 7：主要 PCB填充材料 Dk及 Df参数 ',format_of_number=None, format_desc=None) ==2
    assert number_trans(3,'RNAV','52 附件1 盈利预测和估值',format_of_number=None, format_desc=None) ==3
    assert number_trans(10,'股价','52 附件1 盈利预测和估值',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'股价','52 附件1 盈利预测和估值',format_of_number=None, format_desc=None) ==10
    assert number_trans(3,'RNAV','52 附件1 盈利预测和估值',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'RNAV','52 附件1 盈利预测和估值',format_of_number=None, format_desc=None) ==3
    assert number_trans(10,'股价','52 附件1 盈利预测和估值',format_of_number=None, format_desc=None) ==10
    assert number_trans(30,'月涨幅%','89 2、涨幅前5位的房地产上市公司 ',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'月涨幅%','89 2、涨幅前5位的房地产上市公司 ',format_of_number=None, format_desc=None) ==30
    assert number_trans(5,'市净率','89 2、涨幅前5位的房地产上市公司 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(30,'月涨幅%','89 2、涨幅前5位的房地产上市公司 ',format_of_number=None, format_desc=None) ==30
    assert number_trans(5,'市净率','89 2、涨幅前5位的房地产上市公司 ',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'2016','表 20：2011-2017国有出版公司ROE变化',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2016','表 20：2011-2017国有出版公司ROE变化',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2017','表 20：2011-2017国有出版公司ROE变化',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2017','表 20：2011-2017国有出版公司ROE变化',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'2016','表 20：2011-2017国有出版公司ROE变化',format_of_number=None, format_desc=None) ==10
    assert number_trans(10000,'售价','20 图9：福州市部分典型降价楼盘 ',format_of_number=None, format_desc=None) ==10000
    assert number_trans(10000,'售价','20 图9：福州市部分典型降价楼盘 ',format_of_number=None, format_desc=None) ==10000
    assert number_trans(200000,'一类车','表 4 深高速各条线路客货车流量情况（辆/日） ',format_of_number=None, format_desc=None) ==200000
    assert number_trans(200000,'二类车','表 4 深高速各条线路客货车流量情况（辆/日） ',format_of_number=None, format_desc=None) ==200000
    assert number_trans(200000,'一类车','表 4 深高速各条线路客货车流量情况（辆/日） ',format_of_number=None, format_desc=None) ==200000
    assert number_trans(200000,'二类车','表 4 深高速各条线路客货车流量情况（辆/日） ',format_of_number=None, format_desc=None) ==200000
    assert number_trans(200000,'一类车','表 4 深高速各条线路客货车流量情况（辆/日） ',format_of_number=None, format_desc=None) ==200000
    assert number_trans(200000,'二类车','表 4 深高速各条线路客货车流量情况（辆/日） ',format_of_number=None, format_desc=None) ==200000
    assert number_trans(10,'PE18E','图表26： 美国航空可比公司估值表（2018年11月16日的收盘价） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(2,'PE18E','图表26： 美国航空可比公司估值表（2018年11月16日的收盘价） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'PE17','图表26： 美国航空可比公司估值表（2018年11月16日的收盘价） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(10,'PE19E','图表26： 美国航空可比公司估值表（2018年11月16日的收盘价） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'PE17','图表26： 美国航空可比公司估值表（2018年11月16日的收盘价） ',format_of_number=None, format_desc=None) ==10
    assert number_trans(2,'PE17','图表26： 美国航空可比公司估值表（2018年11月16日的收盘价） ',format_of_number=None, format_desc=None) ==2
    assert number_trans(6000,'发热量/规格','177表5：山西喷吹煤产地价格持平 ',format_of_number=None, format_desc=None) ==6000
    assert number_trans(6000,'发热量/规格','177表5：山西喷吹煤产地价格持平 ',format_of_number=None, format_desc=None) ==6000
    assert number_trans(6000,'发热量/规格','177表5：山西喷吹煤产地价格持平 ',format_of_number=None, format_desc=None) ==6000
    assert number_trans(10,'市盈率(TTM)','图表 15   行业涨幅后五',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'市盈率(TTM)','图表 15   行业涨幅后五',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'市盈率(TTM)','图表 15   行业涨幅后五',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'近4周周均成交','42 表3：2012-06-13房地产二线城市成交数据二 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'近4周周均成交','42 表3：2012-06-13房地产二线城市成交数据二 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'近4周周均成交','42 表3：2012-06-13房地产二线城市成交数据二 ',format_of_number=None, format_desc=None) ==10
    assert number_trans(20,'人数','',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'人数','',format_of_number=None, format_desc=None) ==20
    assert number_trans(50,'估定价标记','',format_of_number=None, format_desc='元') ==50
    assert number_trans(50,'估定价标记','',format_of_number=None, format_desc='元') ==50
    assert number_trans(50,'估定价标记','',format_of_number=None, format_desc='元') ==50
    assert number_trans(2,'学分','',format_of_number=None, format_desc=None) ==2
    assert number_trans(32,'理论学时','',format_of_number=None, format_desc=None) ==32
    assert number_trans(5,'计划学期','',format_of_number=None, format_desc=None) ==5
    assert number_trans(2,'学分','',format_of_number=None, format_desc=None) ==2
    assert number_trans(32,'理论学时','',format_of_number=None, format_desc=None) ==32
    assert number_trans(5,'计划学期','',format_of_number=None, format_desc=None) ==5
    assert number_trans(2,'学分','',format_of_number=None, format_desc=None) ==2
    assert number_trans(32,'理论学时','',format_of_number=None, format_desc=None) ==32
    assert number_trans(5,'计划学期','',format_of_number=None, format_desc=None) ==5
    assert number_trans(500,'批复经费','',format_of_number='万', format_desc=None) ==5000000
    assert number_trans(500,'批复经费','',format_of_number='万', format_desc=None) ==5000000
    assert number_trans(500,'批复经费','',format_of_number='万', format_desc=None) ==5000000
    assert number_trans(30,'备案价格（元）','',format_of_number=None, format_desc='元') ==30
    assert number_trans(30,'备案价格（元）','',format_of_number=None, format_desc='元') ==30
    assert number_trans(30,'备案价格（元）','',format_of_number=None, format_desc='元') ==30
    assert number_trans(2110081,'课程代码','',format_of_number=None, format_desc=None) ==2110081
    assert number_trans(2110081,'课程代码','',format_of_number=None, format_desc=None) ==2110081
    assert number_trans(2110081,'课程代码','',format_of_number=None, format_desc=None) ==2110081
    assert number_trans(5000,'宽度(m)','',format_of_number=None, format_desc=None) ==5000
    assert number_trans(5,'长度(m)','',format_of_number=None, format_desc=None) ==5
    assert number_trans(30,'用工数量','',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'用工数量','',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'用工数量','',format_of_number=None, format_desc=None) ==30
    assert number_trans(10,'平峰期发车间隔','',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'最低日运营趟次','',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'最低日运营趟次','',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'最低日运营趟次','',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'最低日运营趟次','',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'平峰期发车间隔','',format_of_number=None, format_desc=None) ==5
    assert number_trans(15000,'分配额度（枚）','',format_of_number=None, format_desc=None) ==15000
    assert number_trans(15000,'分配额度（枚）','',format_of_number=None, format_desc=None) ==15000
    assert number_trans(15000,'分配额度（枚）','',format_of_number=None, format_desc=None) ==15000
    assert number_trans(20,'项目补助市、县（区）财政分担比例','',format_of_number='万', format_desc='元') ==200000
    assert number_trans(20,'项目补助市、县（区）财政分担比例','',format_of_number='万', format_desc='元') ==200000
    assert number_trans(20,'项目补助市、县（区）财政分担比例','',format_of_number='万', format_desc='元') ==200000
    assert number_trans(20,'项目补助市、县（区）财政分担比例','',format_of_number='万', format_desc='元') ==200000
    assert number_trans(20,'项目补助市、县（区）财政分担比例','',format_of_number='万', format_desc='元') ==200000
    assert number_trans(20,'项目补助市、县（区）财政分担比例','',format_of_number='万', format_desc='元') ==200000
    assert number_trans(10,'招聘人数','',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'招聘人数','',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'招聘人数','',format_of_number=None, format_desc=None) ==10
    assert number_trans(2000,'指数中文简称IndexChineseName','',format_of_number=None, format_desc=None) ==2000
    assert number_trans(2000,'指数中文简称IndexChineseName','',format_of_number=None, format_desc=None) ==2000
    assert number_trans(2000,'指数中文简称IndexChineseName','',format_of_number=None, format_desc=None) ==2000
    assert number_trans(2000,'指数中文简称IndexChineseName','',format_of_number=None, format_desc=None) ==2000
    assert number_trans(2000,'指数中文简称IndexChineseName','',format_of_number=None, format_desc=None) ==2000
    assert number_trans(2000,'指数中文简称IndexChineseName','',format_of_number=None, format_desc=None) ==2000
    assert number_trans(8,'部数','',format_of_number=None, format_desc=None) ==8
    assert number_trans(6000,'分钟数','',format_of_number=None, format_desc=None) ==6000
    assert number_trans(8,'部数','',format_of_number=None, format_desc=None) ==8
    assert number_trans(6000,'分钟数','',format_of_number=None, format_desc=None) ==6000
    assert number_trans(9787551133272,'书号','',format_of_number=None, format_desc=None) ==9787551133272
    assert number_trans(9787551133272,'书号','',format_of_number=None, format_desc=None) ==9787551133272
    assert number_trans(9787551133272,'书号','',format_of_number=None, format_desc=None) ==9787551133272
    assert number_trans(20,'单价','',format_of_number=None, format_desc='元') ==20
    assert number_trans(20,'单价','',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'单价','',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'线路长度（公里）','',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'线路长度（公里）','',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'线路长度（公里）','',format_of_number=None, format_desc=None) ==20
    assert number_trans(1,'原值（元）','',format_of_number='万', format_desc=None) ==10000
    assert number_trans(1,'原值（元）','',format_of_number='万', format_desc='元') ==10000
    assert number_trans(1,'原值（元）','',format_of_number='万', format_desc=None) ==10000
    assert number_trans(20,'集数','',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'集数','',format_of_number=None, format_desc=None) ==20
    assert number_trans(20,'集数','',format_of_number=None, format_desc=None) ==20
    assert number_trans(1,'获奖人数','',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'获奖人数','',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'获奖人数','',format_of_number=None, format_desc=None) ==1
    assert number_trans(20000,'市场价格','',format_of_number=None, format_desc=None) ==20000
    assert number_trans(10000,'协议供货价格','',format_of_number=None, format_desc=None) ==10000
    assert number_trans(20000,'市场价格','',format_of_number=None, format_desc=None) ==20000
    assert number_trans(10000,'协议供货价格','',format_of_number=None, format_desc=None) ==10000
    assert number_trans(20000,'市场价格','',format_of_number=None, format_desc=None) ==20000
    assert number_trans(10000,'协议供货价格','',format_of_number=None, format_desc=None) ==10000
    assert number_trans(3000,'用地面积','',format_of_number='万', format_desc='平') ==30000000
    assert number_trans(3000,'用地面积','',format_of_number='万', format_desc='平') ==30000000
    assert number_trans(3000,'用地面积','',format_of_number='万', format_desc='平') ==30000000
    assert number_trans(50,'ISBN','',format_of_number=None, format_desc='元') ==50
    assert number_trans(50,'ISBN','',format_of_number=None, format_desc='元') ==50
    assert number_trans(50,'ISBN','',format_of_number=None, format_desc='元') ==50
    assert number_trans(1,'招聘名额','',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'招聘名额','',format_of_number=None, format_desc=None) ==1
    assert number_trans(1,'招聘名额','',format_of_number=None, format_desc=None) ==1
    assert number_trans(50,'估定价','',format_of_number=None, format_desc='元') ==50
    assert number_trans(50,'估定价','',format_of_number=None, format_desc=None) ==50
    assert number_trans(100000,'无锡镍价格','',format_of_number=None, format_desc=None) ==100000
    assert number_trans(15000,'伦敦镍价格','',format_of_number=None, format_desc=None) ==15000
    assert number_trans(100000,'无锡镍价格','',format_of_number=None, format_desc=None) ==100000
    assert number_trans(15000,'伦敦镍价格','',format_of_number=None, format_desc=None) ==15000
    assert number_trans(50,'定价','',format_of_number=None, format_desc='元') ==50
    assert number_trans(50,'定价','',format_of_number=None, format_desc='元') ==50
    assert number_trans(50,'出版日期','',format_of_number=None, format_desc='元') ==50
    assert number_trans(5,'事项数量','',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'人员','',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'事项数量','',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'人员','',format_of_number=None, format_desc=None) ==10
    assert number_trans(5,'事项数量','',format_of_number=None, format_desc=None) ==5
    assert number_trans(10,'人员','',format_of_number=None, format_desc=None) ==10
    assert number_trans(2,'招聘人数','',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'招聘人数','',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'招聘人数','',format_of_number=None, format_desc=None) ==2
    assert number_trans(1000,'专项经费','',format_of_number=None, format_desc=None) ==1000
    assert number_trans(1000,'专项经费','',format_of_number=None, format_desc=None) ==1000
    assert number_trans(1000,'专项经费','',format_of_number=None, format_desc=None) ==1000
    assert number_trans(1000,'专项经费','',format_of_number=None, format_desc=None) ==1000
    assert number_trans(1000,'专项经费','',format_of_number=None, format_desc=None) ==1000
    assert number_trans(1000,'专项经费','',format_of_number=None, format_desc=None) ==1000
    assert number_trans(60,'定价','',format_of_number=None, format_desc='元') ==60
    assert number_trans(60,'定价','',format_of_number=None, format_desc='元') ==60
    assert number_trans(3,'学分','',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'学分','',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'学分','',format_of_number=None, format_desc=None) ==3
    assert number_trans(1000,'状态数量（条）','',format_of_number=None, format_desc=None) ==1000
    assert number_trans(1000,'状态数量（条）','',format_of_number=None, format_desc=None) ==1000
    assert number_trans(1000,'状态数量（条）','',format_of_number=None, format_desc=None) ==1000
    assert number_trans(5000,'座位数（个）','',format_of_number=None, format_desc=None) ==5000
    assert number_trans(500,'座位数（个）','',format_of_number='万', format_desc=None) ==5000000
    assert number_trans(500,'座位数（个）','',format_of_number='万', format_desc=None) ==5000000
    assert number_trans(5000,'座位数（个）','',format_of_number=None, format_desc=None) ==5000
    assert number_trans(30,'定价','',format_of_number=None, format_desc='元') ==30
    assert number_trans(30,'定价','',format_of_number=None, format_desc=None) ==30
    assert number_trans(30,'定价','',format_of_number=None, format_desc='元') ==30
    assert number_trans(6000,'兑换数量（枚）','',format_of_number=None, format_desc=None) ==6000
    assert number_trans(6000,'兑换数量（枚）','',format_of_number=None, format_desc=None) ==6000
    assert number_trans(6000,'兑换数量（枚）','',format_of_number=None, format_desc=None) ==6000
    assert number_trans(50,'单价','',format_of_number=None, format_desc='元') ==50
    assert number_trans(50,'单价','',format_of_number=None, format_desc=None) ==50
    assert number_trans(50,'单价','',format_of_number=None, format_desc=None) ==50
    assert number_trans(100,'线上额度（枚）','',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'线上额度（枚）','',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'线上额度（枚）','',format_of_number=None, format_desc=None) ==100
    assert number_trans(35,'估定价','',format_of_number=None, format_desc=None) ==35
    assert number_trans(35,'估定价','',format_of_number=None, format_desc='元') ==35
    assert number_trans(35,'估定价','',format_of_number=None, format_desc=None) ==35
    assert number_trans(3,'缺岗数','',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'缺岗数','',format_of_number=None, format_desc=None) ==3
    assert number_trans(3,'缺岗数','',format_of_number=None, format_desc=None) ==3
    assert number_trans(10,'集数','',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'集数','',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'集数','',format_of_number=None, format_desc=None) ==10
    assert number_trans(100,'数量','',format_of_number=None, format_desc=None) ==100
    assert number_trans(100,'数量','',format_of_number=None, format_desc=None) ==100
    assert number_trans(40000,'座位数（个）','',format_of_number=None, format_desc=None) ==40000
    assert number_trans(40000,'座位数（个）','',format_of_number=None, format_desc=None) ==40000
    assert number_trans(40000,'座位数（个）','',format_of_number=None, format_desc=None) ==40000
    assert number_trans(2,'评分标准','',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'评分标准','',format_of_number=None, format_desc=None) ==2
    assert number_trans(2,'评分标准','',format_of_number=None, format_desc=None) ==2
    assert number_trans(5,'薪资待遇（年薪）','',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'薪资待遇（年薪）','',format_of_number=None, format_desc=None) ==5
    assert number_trans(5,'薪资待遇（年薪）','',format_of_number=None, format_desc=None) ==5
    assert number_trans(6,'薪资待遇（年薪）','',format_of_number='万', format_desc=None) ==60000
    assert number_trans(10,'数量','',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'数量','',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'数量','',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'录取数','',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'录取数','',format_of_number=None, format_desc=None) ==10
    assert number_trans(10,'录取数','',format_of_number=None, format_desc=None) ==10
    assert number_trans(30,'定价（元）','',format_of_number=None, format_desc='元') ==30
    assert number_trans(30,'书号（ISBN）','',format_of_number=None, format_desc='元') ==30
    assert number_trans(30,'定价（元）','',format_of_number=None, format_desc='元') ==30
    assert number_trans(50,'定价','',format_of_number=None, format_desc='元') ==50
    assert number_trans(50,'定价','',format_of_number=None, format_desc='元') ==50
    assert number_trans(50,'定价','',format_of_number=None, format_desc='元') ==50
    assert number_trans(1000,'资助金额(元)','',format_of_number=None, format_desc='元') ==1000
    assert number_trans(1000,'资助金额(元)','',format_of_number=None, format_desc='元') ==1000
    assert number_trans(1000,'资助金额(元)','',format_of_number=None, format_desc='元') ==1000
    assert number_trans(50,'ISBN','',format_of_number=None, format_desc=None) ==50
    assert number_trans(50,'ISBN','',format_of_number=None, format_desc=None) ==50
    assert number_trans(10,'展位面积（平方米）','',format_of_number=None, format_desc='平') ==10
    assert number_trans(10,'展位面积（平方米）','',format_of_number=None, format_desc='平') ==10
    assert number_trans(10,'展位面积（平方米）','',format_of_number=None, format_desc='平') ==10








    ret = number_trans(20,'平均费率（元/公里）','95表 7 宁沪高速各类车型单车平均费率和收入占比估计 ',format_of_number=None, format_desc='元')
    print(ret)

    # ret = number_trans(700000, '租赁收入（万元）', format_of_number='万')
    # ret = number_trans(5, '库存（套）', '', format_of_number='万')
    a = get_append_unit(25,28, '那个10年成交面积大于900万平的同时成交金额也在3000000亿以上的城市有哪些')
    ret = number_trans(300000000000000, '综合票房', 
            '53 表3：2010年至今土地市场成交情况（万亿、万平） ' ,format_of_number=None, format_desc=None)



    # ret = number_trans(1,'原值（元）','',format_of_number='万', format_desc=None)


    # 如果这个k后面有 一些其他单位的话，， 根据单位变换下
    # 另外如果当前col 为 real的话，那么即使op是2，也不要做most_similar

    # 上面的情形都先罗列出来