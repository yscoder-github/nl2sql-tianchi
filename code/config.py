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







MODEL_PATH = "../data"
MODEL_BERT_WWM_PATH = '../data/'
TRAIN_DATA_PATH = '../data/train'
VALID_DATA_PATH = '../data/valid'
TEST_FILE_PATH = '/tcdata'

TEST_SUBMIT_PATH = '../result.json'
LOG_PATH = '../data/logs'
PREPARE_DATA_PATH = '../data/prepare_data'

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

AGG_DICT =  {0:"", 1:"AVG", 2:"MAX", 3:"MIN", 4:"COUNT", 5:"SUM"}
COND_OP_DICT =  {0:">", 1:"<", 2:"==", 3:"!="}
RELA_DICT = {0:'', 1:' AND ', 2:' OR '}


BERT_CONFIG_PATH = MODEL_BERT_WWM_PATH + 'bert_config.json'
BERT_CKPT_PATH = MODEL_BERT_WWM_PATH + 'bert_model.ckpt'
BERT_VOCAB_PATH = MODEL_BERT_WWM_PATH + 'vocab.txt'

WEIGHT_SAVE_PATH = MODEL_PATH + 'weights/nl2sql_finetune.weights'




class Config(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key, value)
            
    def add_argument(self, key, value):
        self.__setattr__(key, value)
        

config = Config(
    model_path=MODEL_PATH,
    model_bert_wwm_path=MODEL_BERT_WWM_PATH,
    train_data_path=TRAIN_DATA_PATH,
    valid_data_path=VALID_DATA_PATH,
    test_file_path=TEST_FILE_PATH,
    test_submit_path=TEST_SUBMIT_PATH,
    log_path=LOG_PATH,
    prepare_data_path=PREPARE_DATA_PATH,
    agg_dict=AGG_DICT,
    cond_op_dict=COND_OP_DICT,
    rela_dict=RELA_DICT
)




