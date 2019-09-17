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
            # print(d['keywords'])
            d['all_values'] = set([i for i in d['all_values'] if hasattr(i, '__len__')])
            tables[l['id']] = d
    return data, tables

train_data, train_tables = read_data(
                        os.path.join(train_data_path, 'train.json'),
                        os.path.join(train_data_path, 'train.tables.json')
                        ) # 41522  5013


