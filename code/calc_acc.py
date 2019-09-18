#coding=utf-8
import sys 
from dbengine import DBEngine
import numpy as np 
import os
import json 
from config import *


class Sqlite3Oper():
    def __init__(self, engine):
        self.engine = engine
    
    def is_same_execute(self, tid, sql_gt, sql_pred):
        """
        sql_gt & sql_pred is a dict and must contain sel, agg, conds, cond_conn_op 
        """
        ret_gt = self.engine.execute(tid, sql_gt['sel'], sql_gt['agg'], sql_gt['conds'], sql_gt['cond_conn_op'])
        try:
            ret_pred = self.engine.execute(tid, sql_pred['sel'], sql_pred['agg'], sql_pred['conds'], sql_pred['cond_conn_op'])
        except Exception as e:
            return False
        return ret_gt == ret_pred
        
        
engine = DBEngine(os.path.join(valid_data_path, 'val.db'))
sqlite_oper = Sqlite3Oper(engine)

def check_part_acc(pred_queries, gt_queries, tables_list, valid_data):
    """
        判断各个组件的精确度
        param: 
                pred_queries: array of query
                gt_queries: array of query
                tables_list: 表列表
                valid_data: valid data 带有数据比较多
        ouput: xxx 
 
    """
    NEED_REWRITE_LOG = True
    if NEED_REWRITE_LOG:
        fh_where_val_err = open(os.path.join(log_path, 'where_val_error.log'), 'w')
        fh_where_oper_err = open(os.path.join(log_path, 'where_oper_error.log'), 'w')
        fh_where_col_err = open(os.path.join(log_path, 'where_col_error.log'), 'w')
        fh_where_cnt_err = open(os.path.join(log_path, 'where_cnt_error.log'), 'w')

    tot_err = sel_num_err = agg_err = sel_err = 0.0
    cond_num_err = cond_col_err = cond_op_err = cond_val_err = cond_rela_err = 0.0


    for pred_qry, gt_qry, table_id, valid_d in zip(pred_queries, gt_queries, tables_list, valid_data):


        res = sqlite_oper.is_same_execute(table_id, gt_qry, pred_qry)
        # print(res)
        if res == True:
            continue 
        # else:
        #     print("exe is not good")
        good = True
        sel_pred, agg_pred, where_rela_pred = pred_qry['sel'], pred_qry['agg'], pred_qry['cond_conn_op']
        sel_gt, agg_gt, where_rela_gt = gt_qry['sel'], gt_qry['agg'], gt_qry['cond_conn_op']

        if where_rela_gt != where_rela_pred:
            good = False
            cond_rela_err += 1

        if len(sel_pred) != len(sel_gt):
            good = False
            sel_num_err += 1

        pred_sel_dict = {k:v for k,v in zip(list(sel_pred), list(agg_pred))}
        gt_sel_dict = {k:v for k,v in zip(sel_gt, agg_gt)}
        if set(sel_pred) != set(sel_gt):
            good = False
            sel_err += 1
        agg_pred = [pred_sel_dict[x] for x in sorted(pred_sel_dict.keys())]
        agg_gt = [gt_sel_dict[x] for x in sorted(gt_sel_dict.keys())]
        if agg_pred != agg_gt:
            good = False
            agg_err += 1

        cond_pred = pred_qry['conds']
        cond_gt = gt_qry['conds']
        strs_py3 = json.dumps(eval(str({'question': valid_d['question'], 'table': valid_d['table_id']})), ensure_ascii=False) + '\n' + \
                       json.dumps(eval(str({'sql_right': valid_d['sql']})), ensure_ascii=False) + '\n' + \
                       json.dumps(eval(str({'sql_pred': valid_d['sql_pred']})), ensure_ascii=False) + '\n'
        if len(cond_pred) != len(cond_gt):
            good = False
            cond_num_err += 1
            if PY3 and NEED_REWRITE_LOG: fh_where_cnt_err.write(strs_py3)
            
        else:
            cond_op_pred, cond_op_gt = {}, {}
            cond_val_pred, cond_val_gt = {}, {}
            for p, g in zip(cond_pred, cond_gt):
                cond_op_pred[p[0]] = p[1]
                cond_val_pred[p[0]] = p[2]
                cond_op_gt[g[0]] = g[1]
                cond_val_gt[g[0]] = g[2]

            if set(cond_op_pred.keys()) != set(cond_op_gt.keys()):
                cond_col_err += 1
                good = False
                if PY3 and NEED_REWRITE_LOG: fh_where_col_err.write(strs_py3)

            where_op_pred = [cond_op_pred[x] for x in sorted(cond_op_pred.keys())]
            where_op_gt = [cond_op_gt[x] for x in sorted(cond_op_gt.keys())]
            if where_op_pred != where_op_gt:
                cond_op_err += 1
                good = False
                if PY3 and NEED_REWRITE_LOG: fh_where_oper_err.write(strs_py3)


            where_val_pred = [cond_val_pred[x] for x in sorted(cond_val_pred.keys())]
            where_val_gt = [cond_val_gt[x] for x in sorted(cond_val_gt.keys())]

            if where_val_pred != where_val_gt:
                cond_val_err += 1
                good = False
                if PY3 and NEED_REWRITE_LOG: fh_where_val_err.write(strs_py3)

        if not good:
            tot_err += 1
    q_len = len(pred_queries) # 获取所有的个数
    print('Sel-Num: %.3f, Sel-Col: %.3f, Sel-Agg: %.3f, W-Num: %.3f, W-Col: %.3f, W-Op: %.3f, W-Val: %.3f, W-Rel: %.3f, total_err: %.3f'
                % (sel_num_err / q_len, sel_err / q_len, agg_err / q_len,
                   cond_num_err / q_len, cond_col_err / q_len, cond_op_err / q_len,
                   cond_val_err / q_len, cond_rela_err / q_len, tot_err / q_len))
    return np.array((sel_num_err, sel_err, agg_err, cond_num_err, cond_col_err, cond_op_err, cond_val_err, cond_rela_err)), tot_err, tot_err/q_len  # 这里返回的都是总数哦，需要特殊处理成占比

if __name__ == "__main__":

    table_id  = '4d258a053aaa11e994c3f40f24344a08'
    gt_qry =  {"agg": [0], "cond_conn_op": 2, "sel": [4], "conds": [[1, 2, "搜房网"], [1, 2, "人人网"]]}
    pred_qry = {"agg": [0], "cond_conn_op": 2, "sel": [4], "conds": [[1, 2, "人人网"], [1, 2, "搜房网"]]}
    res = sqlite_oper.is_same_execute(table_id, gt_qry, pred_qry)
    print(res)
    import sys 
    sys.exit(0)

