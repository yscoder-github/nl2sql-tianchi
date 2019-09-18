

from config import * 
import os 
import json 
import numpy as np 


def read_data(data_file, table_file):
    data, tables = [], {}
    with open(data_file) as f:
        for l in f:
            data.append(json.loads(l))
    with open(table_file) as f:
        for l in f:
            l = json.loads(l)
            d = {}
            d['headers'] = l['header']
            d['header2id'] = {j: i for i, j in enumerate(d['headers'])}
            d['content'] = {}
            d['keywords'] = {}
            d['all_values'] = set()
            d['types'] = l['types']
            d['title'] = l['title']
            rows = np.array(l['rows'])
            for i, h in enumerate(d['headers']):
                d['content'][h] = set(rows[:, i])
                if d['types'][i] == 'text':
                    d['keywords'][i] = ''
                    # get_key_words(d['content'][h])
                else:
                    d['keywords'][i] = ''

                d['all_values'].update(d['content'][h])
            d['all_values'] = set([i for i in d['all_values'] if hasattr(i, '__len__')])
            tables[l['id']] = d
    return data, tables

train_data, train_tables = read_data(
                        os.path.join(train_data_path, 'train.json'),
                        os.path.join(train_data_path, 'train.tables.json')
                        ) # 41522  5013


def check_num_exactly_match(num, question):
    """
　　　判断数字是否可以全匹配

     ret : 
         find_cnt=0 表示没有找到
         find_cnt=1 表示精确匹配到1个
         find_cnt=2 表示精确匹配到2个

    　　一般程序后续做处理的时候，要根据find_cnt的不同进行分类处理: 
             find_cnt =1 情况下，是精准匹配，可以将一些包含两个不同数字的区分开
             find_cnt = 2 xxxxxx 
    """
    num = str(num)
    find_start_idx = 0 
    find_cnt = 0 
    num_start_idx, num_end_idx = 0, 0 
    while question.find(num, find_start_idx) != -1: 
        find_start_idx = question.index(num, find_start_idx)
        val_start_idx = find_start_idx - 1
        val_end_idx = find_start_idx + len(num)
        while val_start_idx >= 0 and question[val_start_idx] >= '0' and  question[val_start_idx] <= '9':
            val_start_idx = val_start_idx - 1 

        while val_end_idx  < len(question) and question[val_end_idx] >= '0' and  question[val_end_idx] <= '9':
            val_end_idx = val_end_idx + 1  
        
        if val_start_idx < find_start_idx - 1: # 确定不匹配
            find_start_idx = val_end_idx
        elif val_end_idx > find_start_idx  + len(num) \
                  and  int(question[find_start_idx + len(num): val_end_idx]) != 0: 
            find_start_idx = val_end_idx
        else: 
            find_cnt += 1 
            num_start_idx = val_start_idx + 1 
            num_end_idx = val_end_idx - 1 

            find_start_idx = val_end_idx 
    #print(find_cnt, num_start_idx, num_end_idx, val_start_idx, val_end_idx)
    return find_cnt, num_start_idx, num_end_idx
    

        
def check_num_exactly_match_test():
    assert check_num_exactly_match(1, '2011年北京排名第1的品牌') == (1, 10,10)  
    assert check_num_exactly_match(1, '1年北京排名第11的品牌') == (1, 0, 0)
    assert check_num_exactly_match(1, '11年北京排名第11的品牌')[0] == 0 
    assert check_num_exactly_match(20, '销量大于20吨且盈利大于20万的商品')[0] == 2 
    assert check_num_exactly_match(11, '11年北京排名第11的品牌')[0] == 2 
    assert check_num_exactly_match(2, '2020年销量大于20且盈利为2的品牌是啥')[0] == 2   ## 这种反例一定要考虑哦
    assert check_num_exactly_match(20, '2020年销量大于20且盈利为2的品牌是啥')== (1, 9,10)


def check_num_exactly_match_zero_case(num, question):
    """
　　　判断数字是否可以全匹配

     ret : 
         find_cnt=0 表示没有找到
         find_cnt=1 表示精确匹配到1个
         find_cnt=2 表示精确匹配到2个

         只有find_cnt=1可用
    """
    num = str(num)
    find_start_idx = 0 
    find_cnt = 0 
    num_start_idx, num_end_idx = 0, 0 
    while question.find(num, find_start_idx) != -1: 
        find_start_idx = question.index(num, find_start_idx)
        val_start_idx = find_start_idx - 1
        val_end_idx = find_start_idx + len(num)
        while val_start_idx >= 0 and question[val_start_idx] >= '0' and  question[val_start_idx] <= '9':
            val_start_idx = val_start_idx - 1 

        while val_end_idx  < len(question) and question[val_end_idx] >= '0' and  question[val_end_idx] <= '9':
            val_end_idx = val_end_idx + 1  
        
        if val_start_idx < find_start_idx - 1: # 　如果从该值的左侧出现数字的话，确定不匹配,
            find_start_idx = val_end_idx
        elif val_end_idx > find_start_idx  + len(num):
              #  and  int(question[find_start_idx + len(num): val_end_idx]) != 0: 
            find_start_idx = val_end_idx
        else: 
            find_cnt += 1 
            num_start_idx = val_start_idx + 1 
            num_end_idx = val_end_idx - 1 

            find_start_idx = val_end_idx 
    #print(find_cnt, num_start_idx, num_end_idx, val_start_idx, val_end_idx)
    return find_cnt, num_start_idx, num_end_idx


def check_num_exactly_match_zero_case_test():
    assert check_num_exactly_match_zero_case(20, '2000年销量大于20且盈利为2的品牌是啥') == (1, 9, 10)
    assert check_num_exactly_match_zero_case(20, '20年来北京卖出2000套且盈利为2的品牌是啥') == (1, 0, 1)
    assert check_num_exactly_match_zero_case(20, '20年来北京卖出2000套且盈利为20%的品牌是啥') == (2, 17, 18)
    # print(check_num_exactly_match_zero_case(10, '最新市值低于10000000并且市值比重不足10个百分点的股，最新股价为多少'))
    assert check_num_exactly_match_zero_case(1000, '19年第1周有哪些电影周票房超过10000000并且票房占比高于10%的？') == (0, 0, 0)


if __name__ == "__main__":
    check_num_exactly_match_test()
    check_num_exactly_match_zero_case_test() 



