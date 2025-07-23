

# 读取文件(不压缩)

from datetime import datetime
import io
import pickle
import os
import sys

import pandas as pd
sys.path.append(os.getcwd())
import common.util as zutil


file_path = './data/fundamental/A/A1009/FCT_basis_diff_ma_sec@3.pkl'


# 2023-04-08 01:10:00
def load_file(file_path):
    '''---- load_file :: time spend--00:16.192746 ----'''
    t = zutil.Calc_Time("load_file")
    
    df = zutil.load_file(file_path)
    
    # print(f"总数:  {len(df)}")
    # print(f">0:  {len(df[df['ret.24']>0])}")
    # print(f"<0:  {len(df[df['ret.24']<0])}")
    # print(f"=0:  {len(df[df['ret.24']==0])}")

    # df.head(100).to_csv('test.csv')
    # df = df['ma_selected3_24'].copy()
    df.to_csv('test.csv')
    # print(len(df))
    # print(df.columns)
    # 保持列名
    # df.columns.to_series().to_csv('column_names.txt', index=False)
    t.t()
    return df

if __name__=="__main__":
    print("传入参数，即读取参数传入的文件路径的文件，否则在代码中修改文件路径")
    print("python csgo_common/read_pkl.py [file_path]")
    args = sys.argv
    if len(args)==2:
        file_path = args[1]
        print(file_path)
        load_file(file_path)
    else:
        load_file(file_path)

    pass