import argparse
import joblib
import pandas as pd
from pymongo import UpdateOne
import pandas as pd
from backtesting.gen_orders import Trade_Orders
from backtesting.performance4 import Performance
import numpy as np
import os
from model.import_model import MODEL
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
#from model.xgb import *
#from model.DL_model import *

# 定义多空买
BUY =1
SELL =-1
OPEN=0
CLOSE=1
FEE_FEE=0.0002
TRADE_REPEAT=True
BUY_OR_SELL_RATE=0.05
PRE_FLAG=24
base_dir ='./enter_factors'

import os
import sys
sys.path.append(os.getcwd())
import common.util as zutil
from common.data_common import Data_Common
from config import *
from prepare_data import prepare_data
# 根据因子训练数据

train_ignore_list = ['date','datetime', 'FCT_CHG@1', 'FCT_CHG@3', 'FCT_CHG@5', 'FCT_CHG@10','FCT_CHG@24', 'instrument_id', "_id","trading_date",
                       'instrument','money', 'mul', 'high', 'low', 'open', 'close', 'volume', 'open_interest', 'mindiff', 'factor',
                       "FCT_CHG_Stander@1","FCT_CHG_Stander@3","FCT_CHG_Stander@5","FCT_CHG_Stander@10","FCT_CHG_Stander@24","instrument_num"]

years_base_path = "./years_pkls"

class Backtesting():
    def __init__(self,year):
        self.st = f"{year}-01-01"
        self.et = f"{year}-12-31"
        self.year = year
        self.instrument_list = instruments
        self.train_data, self.prediction_data, self.pre_prediction_data = \
            prepare_data(year,self.instrument_list, train_list ,target_list[0], k_line_type)
        self.data_common = Data_Common.create_instance()

    def model(self):
        # 划分训练集和测试集
        train_list.sort()
        X_train = self.train_data[train_list].replace([np.inf, -np.inf], np.nan)
        y_train = pd.DataFrame()
        y_train[target_list[0]] = self.train_data[target_list[0]].fillna(0)
        x_test = self.prediction_data[train_list]
        x_pre_test = self.pre_prediction_data

        # 调用模型
        model = MODEL(self.instrument_list, X_train, y_train, x_test, x_pre_test, model_param) 
        model.run()

    def get_instrument_list(self):
        info = self.data_common.get_futures_mul()
        for idx,doc in info.iterrows():
            self.instrument_list.append(doc['instrument'])
        pass
    
    def gen_year_orders(self):
        param = {
        "length":10,
        "open_thr":2.0,
        "close_thr":0.8,
        "st":self.st,
        "et":self.et,
        }
        a = Trade_Orders(param)
        a.main()
        pass
    
def step2(start_time,end_time):
    start_time = start_time.replace("-","")
    end_time = end_time.replace("-","")
    param={}
    param['st'] = start_time
    param['et'] = end_time
    param['commission'] = 0.1
    param['risk_free_rate'] =0 # 0.02  # 无风险利率
    param['initial_value'] = 10000000
    param['next_text']=""

    p = Performance(param)
    p.run()
    
    print("Performance end")

def run(i):
    print(f"----------{i}--------")
    tt = zutil.Calc_Time(f"backtesting-- {i}",level=1)
    
    for year in years_list:
        b = Backtesting(year)
        b.model()
        b.gen_year_orders()
    tt.t()
    # 计算费率比数据
    step2(f"{years_list[0]}-01-01",f"{years_list[-1]}-12-31")
    pass

if __name__=="__main__":
    if os.path.exists('./data/order.pkl'):
        os.remove('./data/order.pkl')
    #print(zutil.load_file('./data/pre.pkl'))
    run(0)