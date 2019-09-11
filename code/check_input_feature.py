#! -*- coding: utf-8 -*-
import json
import codecs
import jieba
import editdistance
import re
import os
import sys
import numpy as np 
import cn2an
from  question_prepro import *
from config import * 
from utils import *

# 正则表达式
re_brack = "\\(.*?\\)|\\{.*?}|\\[.*?]|（.*?）|%" # 去掉括号里面的内容
num_to_upper_dict = ['零', '一', '两', '三', '四', '五', '六', '七', '八', '九', '十']
upper_to_num_dict = {}
for key, val in enumerate(num_to_upper_dict):
    upper_to_num_dict[val] = key 

re_expre_type_num = r"([零|一|两|三|四|五|六|七|八|九|十])([名|个|位|只|种|两|米|首|回|对|座])"
re_date_list = [r"(\d{2,4})年(\d{1,2})月(\d{1,2})[号|日|][到|至|与](\d{1,2})[号|日]", # 
                r"(\d{2,4})年(\d{1,2})月(\d{1,2})[号|日]",
                r"(\d{2,4})-(\d{1,2})-(\d{1,2})"]



def most_similar(source, target_list):
    """
       
    　这个只能针对于文本进行匹配的
      从词表中找最相近的词（当无法全匹配的时候）
    这里做了修正，如果没有能够匹配的值的话，返回 -1 
    """
    if len(target_list) == 0:
        return None 
    s_set = set([item for item in source])
    contain_score = []
    un_contain_score = []# target当中相比于source多出来的部分
    for target in target_list:
        t_set = set([t for t in target])
        contain_score.append(len(s_set & t_set))
        # un_contain_score.append(len(t_set.difference(s_set))) #
        un_contain_score.append(0) # 先不扣分了...
    char_match_score = [contain_score[idx]  for idx in range(len(target_list))]

    # 如果最高匹配分数为0,说明一个匹配的都没有，，那么返回None 
    if max(char_match_score) == 0: return None 

    # 下面计算编辑距离分数
    e_d_score = [ len(source) - editdistance.eval(source, t) for t in target_list] 

    final_score = [char_match_score[idx] + e_d_score[idx] for idx in range(len(target_list))]

    return target_list[final_score.index(max(final_score))]




def most_similar_out(source, target_list):
    """
    从词表中找最相近的词（当无法全匹配的时候）
    这里做了修正，如果没有能够匹配的值的话，返回 -1 
    """

    if len(target_list) == 0:
        return None 
    s_set = set([item for item in source])
    contain_score = []
    un_contain_score = []# target当中相比于source多出来的部分
    for target in target_list:
        t_set = set([t for t in target])
        contain_score.append(len(s_set & t_set))
        # un_contain_score.append(len(t_set.difference(s_set))) #
        un_contain_score.append(0) # 先不扣分了...
    char_match_score = [contain_score[idx] * 4 for idx in range(len(target_list))]

    # 如果最高匹配分数为0,说明一个匹配的都没有，，那么返回None 
    if max(char_match_score) == 0: return None 
    # 如果匹配分数为0，直接给个最小分吧
    for idx in range(len(target_list)):
        if char_match_score[idx] == 0:
            char_match_score[idx] = -65530

    # 下面计算编辑距离分数
    e_d_score = [ len(source) - editdistance.eval(source, t) for t in target_list] 

    final_score = [char_match_score[idx] + e_d_score[idx] for idx in range(len(target_list))]

    return target_list[final_score.index(max(final_score))]


def most_similar_new(source, target_list):
    if re.findall('[^\d\-\.\%]', source):
        return most_similar_out(source, target_list)
    else: 
        # if source + '.0'  in target_list: return source + '.0' # 针对于val.db数据中有的将数量存在text,而且还加了个.0, 莫名其妙  特殊新增的，其他都没有，，，只是为了测试
        new_target_list = [target for target in target_list if check_num_exactly_match(source, target)[0] >= 1]
        print('new target list is'.format(new_target_list))
        if len(new_target_list) == 0: return None  
        return new_target_list[0] if len(new_target_list) == 1 else most_similar_out(source, new_target_list)


# before of i,j, k is(2,2,100)

# real
# after of i,j, k is(1,2,2100)



ret = most_similar_new('100', ['', '24.0'])
print(ret)

def treate_num_related_in_q(re_expre,  question, cond_val):
    """
    处理question中的数字映射问题
    """
    try:
        mat_re = re.compile(re_expre)
    
        q_mat = mat_re.findall(question)
        alab_num = upper_to_num_dict.get(q_mat[0][0])
        question =  question.replace(q_mat[0][0] + q_mat[0][1], str(alab_num) + q_mat[0][1])
        return question
    except:
        return None 





class Subsets:
    # @param S, a list of integer
    # @return a list of lists of integer
    def __init__(self, max_len=5):
        self.max_len = max_len

    def dfs(self, start, S, result, father_subsets):
        
        if len(father_subsets) > self.max_len: return
        result.append(father_subsets)
        for i in range(start, len(S)):
            self.dfs(i+1, S, result, father_subsets+[S[i]])
    def subsets(self, S):
        # none case
        if S is None:
            return []
        # deep first search
        result = []
        self.dfs(0, sorted(S), result, [])
        return result

        
def most_similar_2(w, s, mode='input'):
    """从句子s中找与w最相近的片段，
    借助分词工具和ngram的方式尽量精确地确定边界。
     w : cond value 
     s: question 


     输入和输出的相似度函数不应该相同
     对于输入来说: 进行自动标注的时候，是按照相邻原则来标记的,所以输入采用的相似度方法是n-gram 
     对于输出来说： xxx
    """
    # 不再做任何预处理,因为
    sw = jieba.lcut(s)
    # print(sw)
    stop_words_set = set([])
    # get_stop_words_set()
    sl = [x for x in list(sw) if x not in stop_words_set]

    if mode == 'output': # 这里只需要组合最大长度为５吧　太长了不好
        s_subset = Subsets().subsets(sw)
        sl = [''.join(item) for item in s_subset if len(item) > 0] 
    elif mode == 'input': # 继续采用之前的匹配方式
    #    l = [c for c in s]
        sl.extend([char for char in s])
        sl.extend([''.join(i) for i in zip(sw, sw[1:])]) # 2-gram 
        sl.extend([''.join(i) for i in zip(sw, sw[1:], sw[2:])]) # 3-gram 
        sl.extend([''.join(i) for i in zip(sw, sw[1:], sw[2:], sw[3:])]) # 4-grarm 
        sl.extend([''.join(i) for i in zip(sw, sw[1:], sw[2:], sw[3:], sw[4:])]) # 5-gram
        sl.extend([''.join(i) for i in zip(sw, sw[1:], sw[2:], sw[3:], sw[4:], sw[5:])]) # 6-gram
        sl.extend([''.join(i) for i in zip(sw, sw[1:], sw[2:], sw[3:], sw[4:], sw[5:], sw[6:])]) # 7-gram      
    else:
        raise ValueError('Unsupported mode! ')
    # print(sl)
    return most_similar(w, sl) # delte in 08-19
    #return most_similar_out(w, sl) # modify in 08-19




q  = '帮我查一下那个珠三角机场群17年的旅客吞吐量达到多少'
val = '珠三角机场群（香港、澳门、广州、深圳、珠海）'

ret = most_similar_2('2018.9', '哪些书是2018年9月份出版的或者是在2018年12月份印刷的')



def alap_an_cn_mark(question, col_name, val):

    """
    val 为数字可以通过quesiton的col_name来判断
    通过列名称,找到匹配的位置,,然后顺次找到最近的数字

    这里返回 start_pos: 数字开始位置
            end_pos: 数字结束位置
            val_in_q : 数字

    todo: 
        负数是否可以准确位置标记出来
        小数当前是否可以准备全部标记出来
    """
    # col_name中的括号去掉
    col_name = re.sub(re_brack, "", col_name)


    question = trans_question_acc(question)

    col_in_question = most_similar_2(col_name, question)

    start_idx = 0 
    # 如果这个标题在question里面,好说

    if  col_in_question is not None and  col_in_question in question:
        start_idx = question.index(col_in_question) + len(col_in_question)
    elif col_in_question is not None:# 标题不在question里面,分散在里面
        pass 
        # raise ValueError('value uncorrect')
        # # 裁剪
        # # col_in_question分割词语,找出最右侧的
        # col_in_question = list(jieba.cut(col_in_question))[-1]
        # print("col find in q after cut is  {}".format(col_in_question))
    else:
        return None, None, None
    # pattern = re.compile(r'-\d+|\d+\.\d+|\d+') 
    pattern = re.compile(r'-\d+\.\d+|-\d+|\d+\.\d+|\d+') 
    num_find = pattern.findall(question, start_idx) # 匹配到标题后的第一个数字
    if num_find is None:
        return  
    try:
        start_idx = question.find(num_find[0], start_idx) # 第一个数字是我们想要标注的位置,找到他的起始位置
        end_idx = start_idx + len(num_find[0])
        # print(start_idx,  '\t', end_idx,  '\t', question[start_idx:end_idx])
        return start_idx, end_idx, question[start_idx:end_idx]
    except:
        print('except found')
        return None,None,None



question = '收入为-10.5的单位有哪些'
col_name = '收入'
word = '-10.5'
assert alap_an_cn_mark(question, col_name, word) == (3, 8, '-10.5')



question = '收入为-100的单位有哪些'
col_name = '收入'
word = '-100'
assert alap_an_cn_mark(question, col_name, word) == (3, 7, '-100')



question = '你好啊，我想知道出现次数大于8万，频率还高于0.1的都是什么词来着'
col_name = '频率'
val = '0.15666'
assert alap_an_cn_mark(question, col_name, val) == (22, 25, '0.1')


question = '你好啊，我想知道出现次数大于8万，频率还高于4325的都是什么词来着'
col_name = '频率'
val = '133'
assert alap_an_cn_mark(question, col_name, val) == (22, 26, '4325')


question = '你好啊，我想知道出现次数大于8万，频率还高于4万的都是什么词来着'
col_name = '频率'
val = '133'
assert alap_an_cn_mark(question, col_name, val) == (22, 23, '4')

question = '2020年通车高铁线路中长超过100公里，投资高于100亿的线路叫啥名呀'
col_name = '线路长度（公里）'

#"线路名称", "沿线地区", "线路长度（公里）", "投资金额（亿元）"
val = '100'
assert alap_an_cn_mark(question, col_name, val) == (15, 18, '100')

question = '哪些股票是周涨跌幅小于0或年涨跌幅大于0的？'
col_name = '投资金额（亿元）'

#"线路名称", "沿线地区", "线路长度（公里）", "投资金额（亿元）"
val = '100'
assert alap_an_cn_mark(question, col_name, val) == (None, None, None)

question = '请问在什么时候贷款利率调整前大于6%并且贷款利率调整后大于6%？'
col_name = '贷款利率调整前'
#"贷款利率调整前", "贷款利率调整后"
val = '6'
assert  alap_an_cn_mark(question, col_name, val) == (16, 17, '6')



question = '请问在什么时候贷款利率调整前大于6%并且贷款利率调整后大于6%？'
col_name = '贷款利率调整后'
#"贷款利率调整前", "贷款利率调整后"
val = '6'
assert alap_an_cn_mark(question, col_name, val) == (29, 30, '6')


question = '我想知道上周5综艺收视率超过3%的，在湖南台播的都有几个啊'
col_name = '收视率'# 百分号也干掉
word = '0.3'
assert alap_an_cn_mark(question, col_name, word) == (14, 15, '3')



question = '哪些城市的成交面积在本周是低于2的'
col_name = '本周成交面积'
word = '1.67'
assert alap_an_cn_mark(question, col_name, word) == (15, 16, '2')



question = '有没有最新股价超过5块一股而且持股数量超过五百万股的模拟组合啊' 
col_name =  '持股数量'
word = '500'
assert alap_an_cn_mark(question, col_name, word) == (21, 28, '5000000')


question = '这周票房达到八千万以上的影片共有几部呀' 
col_name =  '本周票房'
word = '8000'
assert alap_an_cn_mark(question, col_name, word) == (6, 14, '80000000')


# question = '哪些岗位只招一个人？' 
# col_name =  '招聘人数'
# word = '1'
# ret = alap_an_cn_mark(question, col_name, word)


# case2 :col_name 分散在question里面

question = '电视剧收视率排名前3的都是什么剧啊，是在哪个台播的呀'
col_name = '排名'
word = '4'
assert  alap_an_cn_mark(question, col_name, word) == (9, 10, '3')


question = '新房成交环比上周大于20%而且累计同比也大于20%的上周平均成交量为多少'
col_name =  '累计同比'
word = '10'
assert alap_an_cn_mark(question, col_name, word) == (22, 24, '20')


question = '场均人次小于10而且上映了10天以上的电影最大累计票房为多少万'
col_name = '上映天数'
word = '10'
ret = alap_an_cn_mark(question, col_name, word)
print(ret)






# 最高超过2000而且最低也超过2000的开盘价多少
# [[7, 0, '2000'], [8, 0, '2000']]
# 最高High 最高
# 6 8 00
# 最低Low 最低
# 15 19 2000


