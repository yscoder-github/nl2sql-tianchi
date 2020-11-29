
## Part0: 参赛成绩
- 平台昵称: yscoder 
- 参赛形式: 个人
- 复赛排名: 15

## Part1:  代码环境
--- 
### 环境配置步骤如下: 

--- 
#### 1. 深度学习相关环境

配置详情
- 显卡: 1080ti
- OS: Ubuntu
- Driver Version: 418.56       
- CUDA Version: 10.1   
- cudnn version 

---
#### 2. Python相关环境

``` shell 
conda create --name nl2sql-yscoder1 python=3.6
source activate
conda activate nl2sql-yscoder1
pip install --upgrade pip  
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple  -r requirements
``` 
root@481c7f8087a2

执行训练任务(训练入口):
``` 
cd code 
sh start_train.sh
```
执行推理任务(推理入口):
``` 
cd code 
sh start_test.sh
```

#### 3.  模型与训练文件信息
  - Bert中文预训练模型(哈工大版) ,该模型存储位置:  ./submit/chinese-bert_chinese_wwm_L-12_H-768_A-12   [下载地址](https://github.com/ymcui/Chinese-BERT-wwm)

  - Bert-finetune模型,该模型为经过finetune之后的，适配于当前nl2sql任务的训练模型, 该模型存储路径         ./data/weights/nl2sql_finetune.weights
  训练好的模型链接: https://pan.baidu.com/s/11tQVSZl9e6VBLPp85c9JRQ 提取码: 4ceg 

  - 数据集位置 



## Part2: 预处理
--- 
###  一. 数值类型转化

   　官方提供的数据集中考虑到用户输入的多样性，所以question包含了各种展现形式的数值类型．模型处理时首先对question进行了格式统一,具体如下: 
   1. 百分数转换，例如**百分之10**转化为**10%**,**百分之十**转换为**10%**, 百分之一点五转化为**1.5%**  

   2. 大写数字转阿拉伯数字，例如**十二**转换为**12**; **二十万**转化为**200000**; 一点二转化为**1.2** 
   3. 年份转换，如将12年转换为2012年

   数值类型转换过程当中用到了大量正则匹配，主要匹配出数字可能出现的位置,以利于后续对**训练集**做标记.  
   具体代码位置: **question_prepro.py**    
   功能汇总函数: **trans_question_acc**


--- 
### 二. 训练集数据清洗与分类 

   具体代码文件:  new_mark_acc_ensure.py     check_input_feature.py     

--- 

## Part3:模型介绍
Todo (这两天把图做好　)


[部分训练日志](https://github.com/yscoder-github/nl2sql-tianchi/blob/master/EXELOG.md)
> 注意，如果执行此代码报错，需要修改一下Keras的backend/tensorflow_backend.py，将sparse_categorical_crossentropy函数中原本是  

``` python 
   logits = tf.reshape(output, [-1, int(output_shape[-1])]) 
``` 
的那一行改为
``` python 
logits = tf.reshape(output, [-1, tf.shape(output)[-1]])
``` 


模型解决的特殊问题: 
- AB型问题
   例如:初一欢乐寒假这本书多少钱。 这个句子当中的初一与欢乐寒假是相邻的两个不同列的候选值  
- 一个候选值对应多列, 例如　eps2011与eps2012均大于10的股票有哪些? 这里的10对应了表中的两个列





--- 
## Part4: 后处理    
   后处理主要包括如下几块:
   1. 数字中的部分**数位缺失**,例如**200000** 模型之预测到**200**,根据数字的性质，可以对缺失的数位做补齐处理
   2. question中数值单位和表中单位进行统一. 例如question当中票房的单位是"亿",而在相关表中该列的单位为"百万". 本数据集中数值相关的单位存储在表的列名称或者表的title中.
   
   代码文件: post_treat.py 


--- 

## Part5: 模型效果评估  
模型效果评估部分，主要采用官方baseline中的方法，并进行了一定封装．主要用于对预测各个部件的准确性进行评估，并存储预测的错误结果以用于后续分析.    
功能所在文件为calc_acc.py   
主要函数为check_part_acc

---
## Part6: TODO 
### 数字通用前后缀挖掘
由于时间关系，原有方案在将文本中的"中文数字"转换为阿拉伯数字时, 用了一种1字前缀+1字后缀的方式来匹配"中文数字" ，例如: 
``` 
'概天','到月', '于元', '在年', '于平', '足平', '过股', '过套', '招位', '前', '前中', '前名', '前个', '于的'
``` 
上面的这几种**词对**也是通过对数据集进行处理而得出的。表面上看，虽然上面的几种**词对**可以将一些数字匹配出来，但是这种1字前缀+1字后缀的方式会将一些**专有名词**中的**中文数字**进行误换. 所以后期需要做**数字通用前后缀挖掘**,即挖掘出更好的**n字前缀+n字后缀**


> 有兴趣的可以看看是否可以将所有的数值相关的训练材料从**阿拉伯数字**转换为**中文数字**，最后评估下模型效果


### 同义词解决方案 
例如如何将问题中的鹅场和腾讯关联起来



### BUGFIX:  (FIXED)
``` 
  File "nl2sql_main.py", line 816, in <module>
    callbacks=[evaluator]
  File "/home/yinshuai/anaconda3/envs/nl2sql-yscoder/lib/python3.6/site-packages/keras/legacy/interfaces.py", line 91, in wrapper
    return func(*args, **kwargs)
  File "/home/yinshuai/anaconda3/envs/nl2sql-yscoder/lib/python3.6/site-packages/keras/engine/training.py", line 1418, in fit_generator
    initial_epoch=initial_epoch)
  File "/home/yinshuai/anaconda3/envs/nl2sql-yscoder/lib/python3.6/site-packages/keras/engine/training_generator.py", line 251, in fit_generator
    callbacks.on_epoch_end(epoch, epoch_logs)
  File "/home/yinshuai/anaconda3/envs/nl2sql-yscoder/lib/python3.6/site-packages/keras/callbacks.py", line 79, in on_epoch_end
    callback.on_epoch_end(epoch, logs)
  File "nl2sql_main.py", line 798, in on_epoch_end
    acc = self.evaluate()
  File "nl2sql_main.py", line 806, in evaluate
    return evaluate(valid_data, valid_tables)
  File "nl2sql_main.py", line 721, in evaluate
    R = nl2sql(question, table)  # 
  File "nl2sql_main.py", line 555, in nl2sql
    if entity_start_pos_list[0] != v_start:
IndexError: list index out of range
2209it [00:25, 86.28it/s]
```

### 部分冗余逻辑重写


## 附录:代码树
```
├── code
│   ├── calc_acc.py
│   ├── check_input_feature.py
│   ├── config.py
│   ├── dbengine.py
│   ├── hand_set.py
│   ├── new_mark_acc_ensure.py
│   ├── nl2sql_main.py
│   ├── post_treat.py
│   ├── question_prepro.py
│   ├── start_test.sh
│   ├── start_train.sh
│   └── utils.py
├── data
│   ├── chinese-bert_chinese_wwm_L-12_H-768_A-12
│   │   ├── bert_config.json
│   │   ├── bert_model.ckpt.data-00000-of-00001
│   │   ├── bert_model.ckpt.index
│   │   ├── bert_model.ckpt.meta
│   │   └── vocab.txt
│   ├── logs
│   │   ├── evaluate_pred.json
│   │   ├── where_cnt_error.log
│   │   ├── where_col_error.log
│   │   ├── where_oper_error.log
│   │   └── where_val_error.log
│   ├── prepare_data
│   │   ├── col_in_text
│   │   ├── new_q_correct
│   │   ├── new_q_exactly_match
│   │   ├── new_q_exactly_more_strict_match
│   │   ├── new_q_need_col_sim
│   │   ├── new_q_no_num_similar
│   │   ├── new_q_one_vs_more_col
│   │   └── new_q_text_contain_similar
│   ├── train
│   │   ├── train.db
│   │   ├── train.json
│   │   └── train.tables.json
│   ├── val.db
│   ├── valid
│   │   ├── val.db
│   │   ├── val.json
│   │   └── val.tables.json
│   └── weights
│       └── nl2sql_finetune.weights
├── Dockerfile
├── requirements
├── img
│   └── nl2sql_model_old.png
├── README.md
└── run.sh
```


