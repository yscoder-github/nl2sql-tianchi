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
    
    while start_idx >= 0 and not re.findall('[^\d\.]', question[start_idx]):
        start_idx -= 1 

    while end_idx  <= len(question) - 1 and not  re.findall('[^\d\.]', question[end_idx]):
        end_idx += 1 
    return start_idx + 1,  end_idx,  question[start_idx+1: end_idx]


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
    　从title中提取出　单位
    eg: 
       title: '010年至今土地市场成交情况（万亿、万平）'
       ret: 万亿　万平　
    """
    # unit_regex = "(亿元).*?亿美元', '万平方米', '万平', '千桶','万人','万平米','亿股', '万吨','万亿件','元/平米',
    # '亿吨','亿件', '万支', '亿人民币', '亿', '万人次', '百万美元', '百万元'"
    unit_list = re.findall(r'（(.*?)）', title)

    if not unit_list: 
        unit_list = re.findall(r'\((.*?)\)', title)
        if not unit_list:  return unit_list
    title_unit = set([])
    for unit in unit_list:
        unit_in_title =  re.findall(unit_regexp, unit)

        if not unit_in_title: continue 
        else: title_unit = set(unit_in_title)
    return title_unit
    

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
        unit  = unit.pop()
        # 匹配出计量词
        unit_in_strs =  re.findall(regex_tail, unit)
        if not unit_in_strs: return ori_num 
        title_unit_format = unit_in_strs[0]
        ret = int(int(num) / format_oper_dict.get(title_unit_format, 1))
        if  ret == 0: return ori_num 
        else: return ret 
    return num 


def number_trans_test():
    """ number_trans函数测试""" 

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


if __name__ == "__main__":
    number_trans_test() 
    