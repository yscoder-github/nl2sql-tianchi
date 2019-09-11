# from  calc_acc import * 
from check_input_feature import * 
from post_treat import * 
# from mark_acc_ensure import * 
from new_mark_acc_ensure import * 
from question_prepro import * 
from exceptdata import * 
import sys 
learning_rate = 10e-5 
min_learning_rate = 1e-5
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
toy = True 
toy_data_cnt = 200
except_cnt = 0 
maxlen = 160
num_agg = 7 # agg_sql_dict = {0:"", 1:"AVG", 2:"MAX", 3:"MIN", 4:"COUNT", 5:"SUM", 6:"不被select"}
num_op = 5 # {0:">", 1:"<", 2:"==", 3:"!=", 4:"不被select"}
num_cond_conn_op = 3 # conn_sql_dict = {0:"", 1:"and", 2:"or"}
csel_num = 20 # col cnt 最大为20 


ret = most_similar_2('黄果树风景名胜区旅游发展局', '请问黄果树旅游发展局这个管理岗是招什么学历的啊')
print(ret)


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
            # print(d['keywords'])
            d['all_values'] = set([i for i in d['all_values'] if hasattr(i, '__len__')])
            tables[l['id']] = d
    return data, tables

train_data, train_tables = read_data(
                        os.path.join(base_path, 'train/train.json'),
                        os.path.join(base_path, 'train/train.tables.json')
                        ) # 41522  5013



class data_generator:

    def __init__(self, data, tables, batch_size=32):
        self.data = data
        self.tables = tables
        self.batch_size = batch_size
        self.steps = len(self.data) // self.batch_size
        if len(self.data) % self.batch_size != 0:
            self.steps += 1
        

    def __len__(self):
        return self.steps

    def __iter__(self):
        while True:
            if PY2:
                idxs = range(len(self.data))
            elif PY3:
                idxs = [x for x in range(len(self.data))]
            np.random.shuffle(idxs)
            X1, X2, XM, H, HM, SEL, CONN, CSEL0, COP = [], [], [], [], [], [], [], [], []
            CSEL1, CSEL2 = [], [] 


            CDIV = []
            for i in idxs:
                d = self.data[i]
                ori_q = d['question']

                d['question'] = trans_question_acc(d['question'])
                t = self.tables[d['table_id']]['headers']
                dtypes = self.tables[d['table_id']]['types']

                conn = [d['sql']['cond_conn_op']]
                csel = np.zeros(len(d['question']) + 2, dtype='int32') # 这里的0既表示padding,表示当前位置不对应任何表中的列
                csel = np.zeros((3, len(d['question']) + 2), dtype='int32') 
                cop = np.zeros(len(d['question']) + 2, dtype='int32') + num_op - 1 

                cdiv = np.zeros(len(d['question']) + 2, dtype='int32')

                question = d['question']
                ex_cnt = 0 
                for cond in d['sql']['conds']:
                    # cond[0] += 1  # 条件所在列从1开始编码
                    # print(dtypes)

                    # 重新在这里面弄
                    # print(d['question'])
                    if d['question'] in correct_q_set:
                        # print(d['question'])
                        if dtypes[cond[0]] == 'real':
                            _, start_pos, end_pos = check_num_exactly_match(cond[2], d['question'])

                            # print(start_pos, end_pos, d['question'][start_pos: end_pos + 1])

                            csel[0][start_pos + 1: end_pos + 1 + 1] = cond[0] + 1 
                            cop[start_pos + 1: end_pos + 1 + 1] = cond[1] 
                        else:
                            start_pos = d['question'].index(cond[2])  if cond[2] in d['question'] else \
                                       d['question'].index(most_similar_2(cond[2], d['question']))
                            # print(start_pos, start_pos + len(cond[2]), d['question'][start_pos: start_pos + len(cond[2])])
                            csel[0][start_pos + 1: start_pos + 1 + len(cond[2])] = cond[0] + 1 
                            cop[start_pos + 1: start_pos + 1 + len(cond[2])] = cond[1]

                    elif d['question'] in no_num_similar_set:
                        # print('cond val is{}'.format(cond[2]))
                        # print('cond val is {}, q is {}  and sim is {}'.format(cond[2],  most_similar_2(cond[2], d['question'])))

                        sim = cond[2] if cond[2] in d['question'] else most_similar_2(cond[2], d['question'])
                        start_pos = d['question'].index(sim)
                        # print(d['question'])
                        # print(start_pos, start_pos + len(sim), d['question'][start_pos: start_pos + len(sim)])
                        csel[0][start_pos + 1: start_pos + len(sim) + 1] = cond[0] + 1 
                        cop[start_pos + 1: start_pos + len(sim) + 1] = cond[1]
                    elif d['question'] in q_one_vs_more_col_set:
                        # print(d['question'])
                        if  check_num_exactly_match(cond[2], d['question'])[0] == 1: 
                            _, start_pos, end_pos = check_num_exactly_match(cond[2], d['question'])
                        elif check_num_exactly_match_zero_case(val, question)[0] == 1:
                            _, start_pos, end_pos = check_num_exactly_match_zero_case(cond[2], d['question'])
                        else:
                            raise ValueError('value error')
                        if max(csel[0][start_pos + 1: end_pos + 1 + 1]) != 0:
                            if max(csel[1][start_pos + 1: end_pos + 1 + 1]) != 0: 
                                csel[2][start_pos + 1: end_pos + 1 + 1] = cond[0] + 1 
                            else:
                                csel[1][start_pos + 1: end_pos + 1 + 1] = cond[0] + 1 
                        else:
                            csel[0][start_pos + 1: end_pos + 1 + 1] = cond[0] + 1 

                        cop[start_pos + 1: end_pos + 1 + 1] = cond[1] 

                        # print(start_pos, end_pos, d['question'][start_pos: end_pos + 1])



                    elif d['question'] in q_need_exactly_match_set:
                        _, start_pos, end_pos = check_num_exactly_match(cond[2], d['question'])
                        # print(d['question'])
                        # print(start_pos, end_pos, d['question'][start_pos: end_pos + 1])
                        csel[0][start_pos + 1: end_pos + 1 + 1] = cond[0] + 1 
                        cop[start_pos + 1: end_pos + 1 + 1] = cond[1] 
                    elif d['question'] in q_need_exactly_match_more_strinct_set:
                        _, start_pos, end_pos = check_num_exactly_match_zero_case(cond[2], d['question'])
                        # print(d['question'])
                        # print(start_pos, end_pos, d['question'][start_pos: end_pos + 1])
                        csel[0][start_pos + 1: end_pos + 1 + 1] = cond[0] + 1 
                        cop[start_pos + 1: end_pos + 1 + 1] = cond[1] 

                    elif d['question'] in q_text_contain_similar_set:
                        if dtypes[cond[0]] == 'real': # 如果是数字的话，通过另外的方法判断
                            # print(d['question'])
                            find_cnt, start_pos, end_pos = check_num_exactly_match_zero_case(cond[2], d['question'])
                            if find_cnt == 1:
                                                        
                                # print(start_pos, end_pos, d['question'][start_pos: end_pos + 1])
                                csel[0][start_pos + 1: end_pos + 1 + 1] = cond[0] + 1 
                                cop[start_pos + 1: end_pos + 1 + 1] = cond[1] 
                            
                            elif find_cnt == 0: 
                                val = most_similar_2(cond[2], d['question'])
                                start_pos = d['question'].index(val)
                                # print(start_pos, start_pos + len(sim), d['question'][start_pos: start_pos + len(sim)])
                                csel[0][start_pos + 1: start_pos + len(val) + 1] = cond[0] + 1 
                                cop[start_pos + 1: start_pos + len(val) + 1] = cond[1]

                        else: # 文本
                            val = most_similar_2(cond[2], d['question'])
                            start_pos = d['question'].index(val)
                            # print(start_pos, start_pos + len(sim), d['question'][start_pos: start_pos + len(sim)])
                            csel[0][start_pos + 1: start_pos + len(val) + 1] = cond[0] + 1 
                            cop[start_pos + 1: start_pos + len(val) + 1] = cond[1]

                    elif d['question'] in q_need_col_similar_set:
                        header_name = t[cond[0]]
                        start_pos, end_pos, match_val = alap_an_cn_mark(d['question'], header_name, cond[2])
                        csel[0][start_pos + 1: end_pos + 1] = cond[0] + 1 
                        cop[start_pos + 1: end_pos + 1] = cond[1] 

                        # print(d['question'])
                        # print(start_pos, end_pos, d['question'][start_pos: end_pos])

                    # new add 
                    ab = True  
                    if ab:
                        for idx in range(1, len(csel[0]) - 1):
                            if csel[0][idx] != csel[0][idx - 1] and csel[0][idx - 1] != 0 and csel[0][idx] != 0:
                                print(d['question'])
                                print( d['sql']['conds'])
                                print(csel[0])
                                # cdiv[idx]  = 1 
                                # print(cdiv)
            print('finish')
            sys.exit(0)

                
                    


train_D = data_generator(train_data, train_tables)  #get Train data 



for d in train_D:
    #print(d)
    pass 


