#!/bin/bash
export PATH=/root/anaconda3/bin:$PATH
source ~/.bashrc
source activate
conda activate nl2sql-yscoder
cd ./code 
PYTHONHASHSEED=0 python nl2sql_add_div_m_easy_csel.py --mode='test'