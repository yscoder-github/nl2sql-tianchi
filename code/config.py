import sys 
model_path = "../data"
# base_path = "../data"

model_bert_wwm_path = '../data/'
train_data_path = '../data/train/'
valid_data_path = '../data/valid/'
test_file_path = "/tcdata"

test_submit_path = "../result.json"
log_path = '../data/logs'
prepare_data_path = '../data/prepare_data'

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

# data to sqlite 
agg_dict = {0:"", 1:"AVG", 2:"MAX", 3:"MIN", 4:"COUNT", 5:"SUM"}
cond_op_dict = {0:">", 1:"<", 2:"==", 3:"!="}
rela_dict = {0:'', 1:' AND ', 2:' OR '}
