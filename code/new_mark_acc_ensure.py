from hand_set import * 
from question_prepro import *  # 需要里面的文件返回函数

from config import * 
from check_input_feature import *
from utils import * 



 #  文件路径配置
# base_dir = '/home/yinshuai/code/code/nlp/nlp_competition_private/tianchi/bert_in_keras/data'
base_dir = '/home/yinshuai/nlp/nlp_competition_private/tianchi/bert_in_keras/data'
base_dir = '../data/prepare_data'




# 新的
q_correct_path = os.path.join(base_dir, 'new_q_correct') # 不区分类型的 正确匹配
q_no_num_similar_path = os.path.join(base_dir, 'new_q_no_num_similar') # 非数字的，通过相似函数可以匹配正确的
q_num_double_more_path = os.path.join(base_dir, 'q_num_double_more.log')
q_need_col_similar_path = os.path.join(base_dir, 'new_q_need_col_sim.log')
q_one_vs_more_col_path = os.path.join(base_dir, 'new_q_one_vs_more_col.log')
q_need_exactly_match_path = os.path.join(base_dir, 'new_q_exactly_match.log')
q_need_exactly_match_more_strict_path =  os.path.join(base_dir, 'new_q_exactly_more_strict_match.log')
q_text_contain_similar_path =  os.path.join(base_dir, 'new_q_text_contain_similar.log')





q_real_text_mix_path =  os.path.join(base_dir, 'new_q_exactly_more_strict_match.log')







# _ = os.path.join(base_dir, 'q_num_double_match')
# col_in_q_digit_path = os.path.join(base_dir, 'col_in_digit') # 不区分类型的 正确匹配
# col_in_q_text_path = os.path.join(base_dir, 'col_in_text') # 不区分类型的 正确匹配



# correct_q_f_h = open(correct_q_path, 'r')
# # col_in_q_text_path_fh = open(col_in_q_text_path, 'r')

# # 去重set 配置
# digit_double_match_q_set = set([])

# correct_exact_match_q = set([])

# correct_exact_match_data =  correct_q_f_h.readlines()

# col_in_q_digit_path_data = col_in_q_digit_path_fh.readlines()
# col_in_q_text_path_data = col_in_q_text_path_fh.readlines()


# already_set = set([])
# correct_exact_match_q = set([q[:-1] for q in  correct_exact_match_data])
# col_in_q_digit_path_set = set([q[:-1] for q in col_in_q_digit_path_data ])
# col_in_q_text_path_set = set([q[:-1] for q in col_in_q_text_path_data ])
# already_set = already_set | correct_exact_match_q
# already_set = already_set | col_in_q_digit_path_set
# already_set = already_set | col_in_q_text_path_set



train_data, train_tables = read_data(
                        os.path.join(train_data_path, 'train.json'),
                        os.path.join(train_data_path, 'train.tables.json')
                        ) # 41522  5013


table_types  = {}
table_headers = {}
    
for d in train_tables:
    types = train_tables[d]['types']
    table_types[d] = types

    table_headers[d] = train_tables[d]['headers']
    


'''

## 人工修正训练集中的异常标注
for idx, d in enumerate(train_data):
    question = trans_question_acc(d['question'])
    if question == '新房上周成交量大于100万平而且当月累计成交量也大于100万平的城市有哪些':
        train_data[idx]['sql']['conds'] = [[1, 0, '0.9'], [2, 0, '0.9']]

    print(idx)
    print(question)
    print(train_data[idx][''])


sys.exit(0)

'''

wrong_mark_official = set([ 
'你知道新房上周成交量和当月累计成交量都大于100万平的是哪些城市吗',
'成交面积在本周或者上周都大于14万平的城市有哪些',
'你知道那些成交面积在本周或者上周都超过14万平的城市吗',
'请问吉林省它的保障房数量在2011年超过了，那么2012年是多少呢？',
'涨幅和溢价率都大于20%的股票重估净资产是多少',
'股票重估净资产多少的时候它的涨幅以及溢价率都会超过20%',
'你好，是这样，我想问一下像涨幅和溢价率都大于20%这样的股票重估净资产达到了多少',
'设计时速等于500公里每小时，或者投资总额205亿元的线路是哪条？',
'你知道全球排名前3的学校是哪几间吗',
'你帮我查一下排在全球前5的是哪个国家的大学来着',
'你好，你知道目前排在前5名的是什么国家的大学吗',
'排名前5的大学分别是哪些国家的',
'你好，你帮我查一下目前全球排名前3的学校',
'你知道全球排名前3的学校是哪几间吗',
'请问有没有18年12月的时候超过4块钱收盘的证券啊，这些证券代码给我一下',
'哪几款机器人在2016销售量可以超过4800而且占市场总销量可达90',
'你好，为了调查2017年机器人本体市场国产厂商比重情况，我想了解一下2016年的机器人款型，名称，特别是销量超4800.占比超90%的机器人厂商',
'西北省市保障房计划的十二五规划情况怎么样，特别是2012年的',
'请问哪一个城市在2010的时候成交面积超过了200',
'可以查查有没有哪个城市2010成交面积高于200的',
'请问一下2012年6月17日A股房地产股最新股票价格大于50块而且最新市值超过450亿的证券代码是哪个',
'111111111111'






])

other_need_trans = set([
    '你帮我查一下股价在12块五毛以上的公司叫啥名',
    '我想了解一下什么公司的股票交易价格是高于12块五毛的呀',
    '我想知道三大航的总市场份额超过0.7的机场有多少？',
    '你好啊请问一下上海哪些楼盘的价格在2012年的5月份超过了一万五一平',
    '请问哪个香港市场重点房地产公司的股票现价低于2块四的',
    '想要了解香港市场重点房地产公司有哪个的股票现价是小于2块四的吗',
    'A股价格大于9块四的公司简称是什么',
    '哪些股最后一笔交易的成交价多于1块五八的啊，那代码是多少',
    '那些收市价超过1块五八的股票叫什么并且所对应的股票代码又是什么呢',
    '2011年每股盈余在两毛以上的公司共有多少家',
    '上周的住房成交面积大概多少啊'

])



bad_question = set([
    '听说产线被关停了，为什么啊，具体原因呢',
    '产线关停，大新闻啊，什么时候，为什么，以后还能不能恢复',
    '呃呃那个上周被禁二手房成交量达到多少啊，还有这个月的成交量呢',
    '你能帮我算一下这几只股票的平均股价吗？',
    '我想知道上周收盘价最高达到了多少？',
    '你知道人文学院招聘哪些岗位吗，代码是什么，招多少人呀',
    '人文学院开始招聘了，麻烦告诉我有哪些岗位在招人，招多少人，岗位代码是什么',
    '你好，我想了解一下人文学院提供了什么岗位吗，它们的岗位代码是什么呀，人数有多少啊',
    '你好啊我想要知道的是什么出版社出版的《阿尔喀比亚德》和《阿尔喀比亚德》这两本书',
    '你看过做智慧班主任这本书吗，我想问一下它的出版单位是谁',
    '地产板块中的换手股的收盘价和周换手率都是知道的，就是不知道股名，哎呀，能不能告诉我一下',
    '这些线路的起始站和终点站是哪，什么时候开通',
    '为了更好地计算同比数，请务必告知近两期的土地成交情况',
    '听说产线被关停了，为什么啊，具体原因呢',
    '产线关停，大新闻啊，什么时候，为什么，以后还能不能恢复',
    '我想知道上周收盘价最高达到了多少？',
    '你能帮我算一下这几只股票的平均股价吗？',
    '我想调查一下日成交环比，但是目前我只知道最近7天的一个成交量'

    


])

# 需要后处理  小数是否可以完整标记??
# 17年的每股盈余超过5毛的公司它们的市盈率平均下来会是多少呀
# 请问有没有什么证券的2011的基本每股收益高于8毛，有的话是哪个证券代码
# 你好啊，你帮我看一下啊倒挂率超过0.3的是什么证券啊 
# 股价低于9块九的公司是哪个



# 哪些城市去年同期去化时间在1年以上




# case 1 
'''
你们可以找出有哪些地产类股票收盘价是3元并且跌幅超过10%的不？
3 3
-10 10%
----------
跌幅超过10%并且收盘的价格大于3元钱的地产类股票有那几个？
3 3
-10 10%
----------
能不能查出尾盘价格为大于3元的并且超过10%跌幅的股票有哪些？
3 3
-10 10%
'''


def get_correct_q(file_path, mode='write', unwanted=set([])):
    """
     - 所有的条件之必须在q中出现过，而且出现的次数必须等于1, 
     - 在conds中不能出现条件值相同(排除那些一词对应多列的情况)
    """
    d_s = set([])

    if mode == 'write':
        f_h = open(file_path, 'w')
        for d in train_data:
            question = d['question']

            if question in unwanted: continue
            conds = d['sql']['conds']
            types = table_types[d['table_id']]
            header = table_headers[d['table_id']]
            exact_match = True 
            question = trans_question_acc(question)
            print(question)
            print(conds) 
            all_correct = True 
            con_val_list = [cond[2] for cond in conds]
            print(con_val_list)

            q_op_mark = [0] * len(question)

            for cond in conds:
                print(con_val_list.count(cond[2]))
                if cond[2] in question and con_val_list.count(cond[2]) == 1:

                    if (types[cond[0]] == 'real' and check_num_exactly_match(cond[2], question)[0] !=1) or\
                      (types[cond[0]] == 'text' and  question.count(cond[2]) != 1 ):
                        all_correct = False 
                        break 


                    if max(q_op_mark[question.index(cond[2]): question.index(cond[2]) + len(cond[2])]) == 1: 
                        all_correct = False  
                        break 
                    q_op_mark[question.index(cond[2]): question.index(cond[2]) + len(cond[2])] = [1] * len(cond[2]) 
                else:
                    all_correct = False 
                    break 
            print(all_correct)
            if all_correct == True:
                d_s.add(question + '\n')
            
        f_h.writelines(list(d_s))
    elif mode == 'read':
        f_h = open(file_path, 'r')
        for line in f_h.readlines():
            d_s.add(line[:-1])
        return d_s 
    else: 
        raise ValueError('unsupported mode ')



correct_q_set =  get_correct_q(q_correct_path, mode='read', unwanted=wrong_mark_official) 
print(len(correct_q_set)) # 28052 



def get_no_num_similar(file_path, mode='write', unwanted=set([])):
    """
    获取非数字，而且通过similar可以匹配正确的
    mode: 'write' or 'read' f
    unwanted:  排除掉的question集合
    """
    d_s = set([])
    
    if mode == 'write':
        f_h = open(file_path, 'w')
        for d in train_data:
            question = d['question']
            conds = d['sql']['conds']
            types = table_types[d['table_id']]
            header = table_headers[d['table_id']]
            question = trans_question_acc(question) # 转化是必须的
            if question in unwanted: continue

            # all cond val is not 'real'
            type_set = set([types[cond[0]] for cond in conds ])
            if 'real' in type_set: continue # 获取非数字
            print('-' * 10)
            print(question)
            good = True 

            q_op_mark = [0] * len(question)

            for cond in conds:
                
                print(cond[2])
                if cond[2] in question:
                    sim = cond[2]
                else:
                    sim = most_similar_2(cond[2], question)
                if sim is None: 
                    good = False 
                    break 
                print(most_similar_2(cond[2], question))

                if max(q_op_mark[question.index(sim): question.index(sim) + len(sim)]) == 1: 
                    good = False  
                    break 

                q_op_mark[question.index(sim): question.index(sim) + len(sim)] = [1] * len(sim)

            

            if good == True:
                d_s.add(question + '\n')



            # continue 
        f_h.writelines(list(d_s)) 

    elif mode == 'read':
        f_h = open(file_path, 'r')
        for line in f_h.readlines():
            d_s.add(line[:-1])
        return d_s
    else: 
        raise ValueError('unsupported mode ')



no_num_similar_set = get_no_num_similar(q_no_num_similar_path, mode='read', unwanted=wrong_mark_official|correct_q_set)
# 7020
print(len(no_num_similar_set))
######



def q_one_vs_more_col(file_path, mode='write', unwanted=set([])):
    """
    获取cond的个数大于1  并且cond中val的值都相同
    另外question中的val只出现一次

    需要条件值全是数字
    """
    unwanted = unwanted | set(['超过30万字，而且页数还超300的是什么书',
               '你知道哪些书字数超30万，页数也超300的吗',
               '我想问问你啊就是哪些书超过300页，超过30万字的吗',
               '单周票房多少的电影，他的人均的场次低于10，但是上映时间在十天以上的'])
    cnts = 0 
    if mode == 'write':
        f_h = open(file_path, 'w')
        for d in train_data:
            question = d['question']

            conds = d['sql']['conds']
            types = table_types[d['table_id']]
            header = table_headers[d['table_id']]
            question = trans_question_acc(question) # 转化是必须的
            if question in unwanted: continue

            vals = set([cond[2] for cond in conds])
            if len(vals) == len(conds) : continue 
            is_good = True
            for val in vals:
                try: 
                    
                    int(float(val))
                except: 
                    print('except')
                    is_good = False 
                    continue 
                if check_num_exactly_match(val, question)[0] != 1 \
                    and check_num_exactly_match_zero_case(val, question)[0] != 1:
                    is_good = False 
                    break 
            cnts += 1 
            #f_h.write(question + '\n')
            if question == '帮我查查市价盈利比率在10年和11都在1以上的公司共有几个':

                print(question)
                print(is_good)
                # sys.exit(0)
            if is_good == True:
                f_h.write(question + '\n')
            # print(conds)
    elif mode == 'read':
        with open(q_one_vs_more_col_path, 'r') as f:
            return set([line[:-1] for line in f.readlines()])


# q_one_vs_more_col()
q_one_vs_more_col_set =  q_one_vs_more_col(q_one_vs_more_col_path, 
                mode='read',unwanted=wrong_mark_official|correct_q_set|no_num_similar_set)

print(len(q_one_vs_more_col_set))
# 1349




def q_need_exactly_match(file_path, mode='write', unwanted=set([])):
    """
    获取cond的个数可以是多个，但是需要保证，每个值都可以通过exactly方法进行匹配
    即 20和2011虽然q.find()是可以定位的，但是显然，这个定位是错误的。
    那么需要find一步，一步的来
    需要条件值全是数字哦
    """

    cnts = 0 
        
    if mode == 'write':
        f_h = open(file_path, 'w')
        for d in train_data:

            question = d['question']
            conds = d['sql']['conds']
            types = table_types[d['table_id']]
            header = table_headers[d['table_id']]
            question = trans_question_acc(question) # 转化是必须的
            if question in unwanted: continue
            is_good = True 


            for cond in conds:
                try: 
                    int(cond[2])
                except: 
                    is_good = False 
                    break 
                if question.count(cond[2]) > 1:
                    cnt = check_num_exactly_match(cond[2], question)[0]
                    if cnt != 1:
                        is_good = False 
                        break 
                elif question.count(cond[2]) == 0:
                    is_good = False 


            if is_good:
                #f_h.write(question + '\n' + str(conds) + '\n')
                f_h.write(question + '\n')
    elif mode == 'read':
        with open(file_path, 'r') as f:
            return set([line[:-1] for line in f.readlines()])


q_need_exactly_match_set =  q_need_exactly_match(q_need_exactly_match_path, 
                mode='read',unwanted=wrong_mark_official|correct_q_set|no_num_similar_set| q_one_vs_more_col_set)

print(len(q_need_exactly_match_set))# 359 


def q_need_exactly_match_more_strict(file_path, mode='write', unwanted=set([])):
    """
    更加严格的匹配 20就是和20匹配上，并不能匹配上2000
    """

    cnts = 0 
    if mode == 'write':
        f_h = open(file_path, 'w')
        for d in train_data:
            question = d['question']
            conds = d['sql']['conds']
            types = table_types[d['table_id']]
            header = table_headers[d['table_id']]
            question = trans_question_acc(question) # 转化是必须的
            if question in unwanted: continue
            is_good = True 
            mark_q = [0] * len(question)
            for cond in conds:
                try: 
                    int(cond[2])
                except: 
                    is_good = False 
                    break 
                print(question)
                print(conds)
                print(cond)
                if question.count(cond[2]) >= 1:
                    cnt_info = check_num_exactly_match_zero_case(cond[2], question)
                    print(cnt_info)
                    if cnt_info[0] != 1:
                        is_good = False 
                        break 
                    if max(mark_q[cnt_info[1]: cnt_info[2] + 1]) > 0 : 
                        is_good = False 
                        break 
                    mark_q[cnt_info[1]: cnt_info[2] + 1] = [1] * (cnt_info[1] + 1 - cnt_info[0]) 
                elif question.count(cond[2]) == 0:
                    is_good = False 

            if is_good:
                print(question)

            if is_good:
                # f_h.write(question + '\n' + str(conds) + '\n' + str(header) + '\n')
                f_h.write(question + '\n')
    elif mode == 'read':
        with open(file_path, 'r') as f:
            return set([line[:-1] for line in f.readlines()])


q_need_exactly_match_more_strinct_set =  q_need_exactly_match_more_strict(q_need_exactly_match_more_strict_path, 
                mode='read',unwanted=wrong_mark_official|correct_q_set|no_num_similar_set| q_one_vs_more_col_set|q_need_exactly_match_set)

print(len(q_need_exactly_match_more_strinct_set))# 342 

b_c = 0 
uw = correct_q_set|no_num_similar_set| q_one_vs_more_col_set|q_need_exactly_match_set|q_need_exactly_match_more_strinct_set
f_h = open(q_num_double_more_path, 'r')



'''
for line in f_h.readlines():
    if line[:-1] not in uw:
        b_c +=1 
        print(line[:-1])
print(b_c)
'''

## 一些纯文本的，完全可以通过most_similar啊!!!!! 文本加数字组合的也可以通过我那个精准函数




def q_text_contain_similar(file_path, mode='write', unwanted=set([])):
    """
    为啥有的文本能够匹配上，还不在,
    """
    d_s = set([])
    unwanted = unwanted | set([
            '强烈推荐评级为A并且股价超过30的重点公司总共有多少家？',
            '一共有多少家重点公司强烈推荐评级为A并且他的股票价格高于30块钱一股的？',
            '这些重点公司强烈推荐评级为A并且股票的价格超过30块的总共有多少家？',
            '那个宁波市上个星期不是成交了有100000平米以下的吗，那宁波这个星期呢，成交的面积有多大呀',
            '那些售价高于1万每平的或者降价幅度在10%以上的楼盘有得什么销售名次吗',
            '单周票房超过1亿或者上映天数大于10天或者口碑指数大于6的电影有多少部',
            '有几部电影的单周票房超过了1亿或者上映天数大于10天或者口碑指数大于6的',
            '你知道单周票房超过1亿或者上映天数大于10天或者口碑指数大于6的电影名称有几个吗',
            '市值大于32万或者股份大于100手的公司有哪些',
            '你知道那些市值高于32万或者股份高于100手的公司名称吗',
            '新湖中宝和建发的涨幅分别是多少啊',
            '诶，你帮我查一下那个新湖中宝和建发他们的涨的一个幅度吧',
            '所有招5人以上的职位中，哪些对专业不作要求？',
            '什么岗位的最低学历要求为大专，招聘人数还少于3人？',
            '所有96年十二月通过的项目中，哪些级别是南安市市级的项目？',
            '在广西桂林师范大学出版社在2011年出版的题名有哪些呀？其作者是谁呢？',
            '麻烦看看，2011年在广西桂林师范大学出版社出版的有哪些题名，这当中作者是谁？',
            '麻烦问一下，都有哪些题名在2011年广西桂林师范大学出版社出版的？这作者都有谁啊？',
            '你好，我想知道目前有哪些专业是4年制的，还有每年学费四千的',
            '诶你知道学费四千一年，而且还是4年制的是哪些专业吗',
            '学费超过6000元的而且学制是4年的有哪些专业课程呢？',
            '请问都有哪些专业课程是4年制的并且学费是超过6000的？',
            '哪些企业的频炉产能超过了40万吨或者有2个中工频炉且每个炉有20吨',
            '有2个20吨的中工频炉或者产能在40万吨以上的企业有哪些',
            '那把那些有2个20吨中工频炉或者产能超过40万吨的公司名称告诉我一下',
            '所有统计报关单数比4000多的企业中，哪些是A类？',
            '你能帮我查查10年有几座城市的土地成交面积破了千万平吗？',
            '你知道什么地方在这个星期成交新房面积大于100000平米，套数超过100的吗',
            '去年同期有没有去化时间超过1年的1线城市啊，都是什么城市',
            '11年和12年累计土地成交超过1000万平的城市有哪些',
            '我想在2011-2012年土地成交量超过1000万平的城市选房，能不能帮我看看哪些城市符合条件',
            '上周末库存去化周期超过1年或者库存去化周期环比超过08的城市有多少',
            '2016年销量大于4800并且销售量为市场总量的90%以上，这是哪几款机器人啊',
            '2011年每股盈余在两毛以上的公司共有多少家'

            ]) 
    cnt = 0 
    if mode == 'write':
        f_h = open(file_path, 'w')
        for d in train_data:
            question = d['question']
            if question in unwanted: continue
            conds = d['sql']['conds']
            types = table_types[d['table_id']]
            header = table_headers[d['table_id']]
            question = trans_question_acc(question) # 转化是必须的

            # all cond val is not 'real'
            type_set = set([types[cond[0]] for cond in conds ])
            if question in unwanted: continue
            # if 'text' not in type_set: continue 
            # headers = [header[cond[0]] for cond in conds]
            # print(conds)
            # print(headers)
            good = True 
            ## 条件值有多个，并且是相同值的　进行标记
            # 哪些需要留下来? 条件值出现在条件中多次

            # 不能出现标注重叠
            mark_list = [0] * len(question)
            for cond in conds:
                if types[cond[0]] == 'real': # 如果是数字的话，通过另外的方法判断
                    find_cnt, num_start_idx, num_end_idx = check_num_exactly_match_zero_case(cond[2], question)

                    if find_cnt == 1 and max(mark_list[num_start_idx:num_end_idx+1]) > 0: 
                        good = False; 
                        break 
                    if find_cnt == 1:
                        mark_list[num_start_idx:num_end_idx+1] = [1] * (num_end_idx + 1 - num_start_idx)

                    if find_cnt > 1: 
                        good = False 
                    if find_cnt == 0: 
                        val = most_similar_2(cond[2], question)
                        if not val: 
                            good = False
                            break 
                        if max(mark_list[question.index(val): question.index(val) + len(val)]) > 0: 
                            good = False
                            break 
                        mark_list[question.index(val): question.index(val) + len(val)] = [1] * len(val)

                else: # 文本
                    val = most_similar_2(cond[2], question)
                    # print('val is {} and after sim {}'.format(cond[2], val))
                    if not val: 
                        good = False
                        break  
                    if max(mark_list[question.index(val): question.index(val) + len(val)]) > 0: good = False; break 
                        
                    mark_list[question.index(val): question.index(val) + len(val)] = [1] * len(val)


            if good == True:
                cnt += 1 
                print('-' * 10)
                print(question)

                # 重点取出逻辑
                for cond in conds:
                    if types[cond[0]] == 'real': # 如果是数字的话，通过另外的方法判断
                        find_cnt, num_start_idx, num_end_idx = check_num_exactly_match_zero_case(cond[2], question)
                        if find_cnt == 0: 
                            val = most_similar_2(cond[2], question)
                        else:
                            val = question[num_start_idx: num_end_idx + 1]
                    else: # 文本
                        val = most_similar_2(cond[2], question)


                        
                    print(cond[2], val)
                    
                d_s.add(question + '\n')
        print(cnt)
            
        f_h.writelines(list(d_s))
    elif mode == 'read':
    
        f_h = open(file_path, 'r')
        for line in f_h.readlines():
            d_s.add(line[:-1])
        return d_s
    else: 
        raise ValueError('unsupported mode ')


q_text_contain_similar_set = q_text_contain_similar(q_text_contain_similar_path,
                         mode='read', unwanted=wrong_mark_official|correct_q_set
                         |no_num_similar_set| q_one_vs_more_col_set|q_need_exactly_match_set|
                            q_need_exactly_match_more_strinct_set)



print(len(q_text_contain_similar_set))#1219

## 可以掰着下
# 股票总的市值最小为多少时溢价率大于负30或者上涨的幅度超过11.4%

##
# 在2011年北京人民日报出版社出版的题名有哪些啊？这当中作者有哪些呢？
# 北京人民日报出版社2011 北京人民日报出版社
# 2011 2011
## 

## 映射匹配

def q_need_col_similar(file_path, mode='write', unwanted=set([])):
    """
    需要对列做similar来 最后根据位置而不是值来标记 
    这里只管带数字的
    """
    d_s = set([])
    unwanted = unwanted | set([
        'A股房地产股的最新市值是多少，它的最新股价是大于10块而且本周涨幅前10大于10%的',
        '我可以通过A股房地产股最新股价大于10块而且本周涨幅前10大于10%查询它的最新市值吗'
    ])
    cnt = 0 
    if mode == 'write':
        f_h = open(file_path, 'w')
        for d in train_data:
            question = d['question']
            if question in unwanted: continue
            conds = d['sql']['conds']
            types = table_types[d['table_id']]
            header = table_headers[d['table_id']]
            question = trans_question_acc(question) # 转化是必须的

            # all cond val is not 'real'
            type_set = set([types[cond[0]] for cond in conds ])
            if question in unwanted: continue
            if 'text'  in type_set: continue 
            # cnt += 1 
            # print('-' * 10)
            # print(question)
            # headers = [header[cond[0]] for cond in conds]
            # print(conds)
            # print(headers)
            good = True 
            ## 条件值有多个，并且是相同值的　进行标记
            # 哪些需要留下来? 条件值出现在条件中多次

            # print(conds)
            mark_pos = [0] * len(question)
            cond_set = list(set([cond[2] for cond in conds]))


            if len(cond_set) == 1 and check_num_exactly_match(cond_set[0], question)[0] < len(conds):
                # print(question)
                # print(conds)
                # print(len(cond_set))
                # print(check_num_exactly_match(cond_set[0], question)[0])
                # good = False 
                pass 


            for cond in conds:
                # print(cond[2], most_similar_2(cond[2], question))
                header_name = header[cond[0]]
                header_sim = most_similar_2(header_name, question)
                if not header_sim: good = False; break
                
                # print(header_name, header_sim)
                # 如果是real才需要下面这种，文本的话，直接most_similar !!
                start_idx, end_idx, match_val = alap_an_cn_mark(question, header_name, cond[2])
                if not match_val or match_val != cond[2] : good = False; break 
                if max(mark_pos[start_idx:end_idx]) > 0: good = False; break 
                mark_pos[start_idx: end_idx] = [1] * len(match_val)
                # print(start_idx, end_idx, match_val)

            if good == True:
                print('-' * 10)
                print(question)
                print(conds)
                cnt+= 1 
                # 正确的取数口径
                for cond in conds:
                    # print(cond[2], most_similar_2(cond[2], question))
                    header_name = header[cond[0]]
                    header_sim = most_similar_2(header_name, question)
                    print(header_name, header_sim)
                    # 如果是real才需要下面这种，文本的话，直接most_similar !!
                    start_idx, end_idx, match_val = alap_an_cn_mark(question, header_name, cond[2])
                    print(start_idx, end_idx, match_val)               
                d_s.add(question + '\n')
        print(cnt)
            
        f_h.writelines(list(d_s))
    elif mode == 'read':
        f_h = open(file_path, 'r')
        for line in f_h.readlines():
            d_s.add(line[:-1])
        return d_s | get_val_by_pos_hand_set
    else: 
        raise ValueError('unsupported mode ')

q_need_col_similar_set = q_need_col_similar(q_need_col_similar_path, mode='read', unwanted=wrong_mark_official|correct_q_set|
                    no_num_similar_set| q_one_vs_more_col_set|q_need_exactly_match_set|
                   q_need_exactly_match_more_strinct_set|q_text_contain_similar_set)
print(len(q_need_col_similar_set)) # 1527  +  85? + xx = 1720 

print('-' * 100)






def check_other():
    cnt = 0
    for d in train_data:


        question = d['question']
        conds = d['sql']['conds']
        types = table_types[d['table_id']]
        header = table_headers[d['table_id']]
        question = trans_question_acc(question) # 转化是必须的
        if question in bad_question|wrong_mark_official|correct_q_set|\
                    no_num_similar_set| q_one_vs_more_col_set|q_need_exactly_match_set|\
                   q_need_exactly_match_more_strinct_set|q_text_contain_similar_set|q_need_col_similar_set:
                   continue 
        
        cnt += 1 
        print(question)
        print(conds)
    print(cnt)



# check_other()



'''
# todo 废柴!!!!
def q_real_text_mix(file_path, mode='write', unwanted=set([])):
    """
    　中文和数字混合在一起的，
    　数字在conds中只出现一次
    　数字在q中只出现一次
      real的值可以通过most_similar匹配出来哦
    """
    d_s = set([])
    cnt = 0 
    if mode == 'write':
        f_h = open(file_path, 'w')
        for d in train_data:
            question = d['question']
            if question in unwanted: continue
            conds = d['sql']['conds']
            types = table_types[d['table_id']]
            header = table_headers[d['table_id']]
            question = trans_question_acc(question) # 转化是必须的
            # all cond val is not 'real'
            type_set = set([types[cond[0]] for cond in conds ])
            if question in unwanted: continue
            if 'real' not in type_set: continue 

            headers = [header[cond[0]] for cond in conds]
            good = True 
            # print('-' * 10)
            # print(question)
            for cond in conds:

                if types[cond[0]] == 'real' and check_num_exactly_match(cond[2], question)[0] != 1: good = False 
                if types[cond[0]] == 'text' and question.count(cond[2]) != 1: good = False 



                # print( most_similar_2(cond[2], question))
                if most_similar_2(cond[2], question) is None: 
                    good = False 

            if good:
                print(question)
                print(conds)
                cnt += 1 
                d_s.add(question + '\n')
            continue 
        print(cnt)
            
        # q_need_col_similar_fh.writelines(list(q_no_num_similar_set))
    elif mode == 'read':
        f_h = open(file_path, 'r')
        for line in f_h.readlines():
            d_s.add(line[:-1])
        return d_s
    else: 
        raise ValueError('unsupported mode ')

q_real_text_mix(q_real_text_mix_path, mode='write', unwanted=correct_q_set|no_num_similar_set| q_one_vs_more_col_set|q_need_exactly_match_set|
                q_need_exactly_match_more_strinct_set)









def get_q_num_double_more(mode='write', unwanted=set([])):
    """
        - col_in_q_digit_path_fh
        - val为"real", val出现在问题里面并且出现的次数大于1 
        - col_name需要在question中
        - col_name不能在question中出现多次,只能一次
    """
    q_num_double_more_set = set([])
    if mode == 'read':
        q_num_double_more_fh = open(q_num_double_more_path, 'r')
        for line in q_num_double_more_fh.readlines():
            q_num_double_more_set.add(line[:-1])
        return q_num_double_more_set       

    else:
        raise ValueError('Unsupported mode')

ret = get_q_num_double_more(mode='read')   
print(ret)




    


def q_num_good(mode='write', unwanted=set([])):
    """
     条件值均在问题里面，可以直接采用 q.index()来定位
    """
    pass 





def q_need_upper_val(mode='write', unwanted=set([])):
    """
    包含需要把val转换， 比如val为10000, q中为1万   
    这里只要大于1000都是有问题 
    在北京展出且展览面积小于2万的展会是哪些？
    """
    print('||||||||')
    for d in train_data:
        question = d['question']
        if question in unwanted: continue
        conds = d['sql']['conds']
        types = table_types[d['table_id']]
        header = table_headers[d['table_id']]
        question = trans_question_acc(question) # 转化是必须的

        # all cond val is not 'real'
        type_set = set([types[cond[0]] for cond in conds ])
        if question in unwanted: continue
        if '万' in question:
            # print(question)
            pass 
            # print(conds)
            # print(header)
                





unwanted = set([])
get_q_num_double_more_set = get_q_num_double_more(mode='read')
unwanted = unwanted | get_q_num_double_more_set
correct_set = get_correct_q(mode='read', unwanted=unwanted)
unwanted = unwanted | correct_set
q_no_num_similar_set = get_no_num_similar(mode='read', unwanted=unwanted)
unwanted = unwanted | q_no_num_similar_set
# q_need_col_similar_set = q_need_col_similar(mode='write', unwanted=unwanted)
# unwanted = unwanted | q_need_col_similar_set


q_need_upper_set = q_need_upper_val(mode='write', unwanted=unwanted)

print(q_need_upper_set)
other_cnt = 0 
def get_other():
    print('-*-*-*')
    for d in train_data:
        question = d['question']
        question = trans_question_acc(question)
        if question in unwanted: continue
        print(question)
        continue 
        conds = d['sql']['conds']
        is_good = True 
        for cond in conds:
            if cond[2] in question and question.count(cond[2]) == 1: 
                pass 
            else:
                is_good=False 
        if is_good:
            print(question)
            # print(conds)
            
   
# get_other()

'''
# 影射
val_mapping = {
    '无': ['没有'],

}