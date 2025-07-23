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

# years_list=[2016,2017,2018,2019,2020,2021,2022,2023,2024]
years_base_path = "./years_pkls"
# 模型深度
DEPTH = 3

# 读取yaml 文件
def get_yaml_data():
    data={}
    with open('config.yaml', 'r') as file:
        lines = file.readlines()  # 按行读取文件内容
        for line in lines:
            line = line.strip()  # 去除行末尾的换行符和空白字符
            if (line.startswith('#') or line==''):
                continue

            config = line.split(': ')
            fac_name = config[0]
            p = pd.Series(eval(config[1]))
            p['name'] = fac_name
            data[p.factor_title] = p
    return data

class Backtesting():
    def __init__(self,step_flag,year):
        self.st = f"{year}-01-01"
        self.et = f"{year}-12-31"
        self.step_flag = step_flag 
        self.minute = minute
        self.year = year
        self.instrument_list = instruments
        self.train_data, self.prediction_data, self.pre_prediction_data = \
            prepare_data(year,self.instrument_list, train_list ,target_list[0], k_line_type)
        self.data_common = Data_Common.create_instance()

    # 获取需要的因子
    def get_train_factor_list(self):
        if self.step_flag ==-1:
            data_0 = self.train_data.iloc[0]
            for column_name, value in data_0.items():
                if column_name not in train_ignore_list:
                    train_list.append(column_name)
            return
        
        # 如果输入因子为空则使用所有因子做回测
        if len(train_list)==0:
            enter_df = pd.read_csv(f'{base_dir}/enter.csv')
            # 对DataFrame进行循环处理
            for index, row in enter_df.iterrows():
                    # 在此处执行你想要的操作，例如输出每一行的值
                    # print(row['feature'], row['importance'])
                train_list.append(row['feature'])
        
        if self.step_flag==0:
            return
        
        pre_enter_df = pd.read_csv(f'{base_dir}/factors.csv')
        # 对字段进行拆分并取第二部分作为新的分组列
        pre_enter_df['fac_back'] = pre_enter_df['feature'].str.split('@').str[0]

        # 按新的分组列进行分组，并获取每个分组的内容，不要排序
        grouped_df = pre_enter_df.groupby('fac_back', sort=False)['feature'].apply(list)
        idx=0
        # 打印每个分组的内容
        for group, content in grouped_df.items():
            if idx==self.step_flag-1:
                train_list.extend(content)
                # 将content 写入临时文件中
                df_temp = pd.DataFrame(list(content), columns=['feature'])
                df_temp.to_csv(f'{base_dir}/df_temp.csv',index=False)
        
            idx+=1
            # 把content 写到临时文件中'''

    def model(self):
        # 划分训练集和测试集
        train_list.sort()
        X_train = self.train_data[train_list].replace([np.inf, -np.inf], np.nan)
        y_train = pd.DataFrame()
        y_train[target_list[0]] = self.train_data[target_list[0]].fillna(0)
        x_test = self.prediction_data[train_list]
        x_pre_test = self.pre_prediction_data

        # 调用模型
        model = MODEL(PRE_FLAG, self.instrument_list, X_train, y_train, x_test, x_pre_test, model_param) 
        model.run()

    def get_instrument_list(self):
        info = self.data_common.get_futures_mul()
        for idx,doc in info.iterrows():
            self.instrument_list.append(doc['instrument'])
        pass
    
    def gen_year_orders(self):
        param = {
        "length":500,
        "open_thr":2.0,
        "close_thr":0.8,
        "st":self.st,
        "et":self.et,
        "pre_flag":24
        }
        a = Trade_Orders(param)
        a.main()
        pass
    

# 拷贝一份base_factors 到factors
# 然后删除factors 里面包含enter的行
# get_group_df 直接读取删除后的数据
def delete_enter_4_base():
    base_factors_df = pd.read_csv(f'{base_dir}/base_factors.csv')
    enter_df = pd.read_csv(f'{base_dir}/enter.csv')
    df_c = pd.merge(enter_df, base_factors_df, on='feature', how='outer', indicator=True)
    df_c = df_c[df_c['_merge'] == 'right_only']
    df_c = df_c.drop('_merge', axis=1)
    df_c.to_csv(f'{base_dir}/factors.csv',index=False)

def get_group_df():
    base_factors_df = pd.read_csv(f'{base_dir}/factors.csv')
    # 对字段进行拆分并取第二部分作为新的分组列
    base_factors_df['fac_back'] = base_factors_df['feature'].str.split('@').str[0]
    # base_factors_df['fac_back'] = base_factors_df['feature']
    grouped_df = base_factors_df.groupby('fac_back')['feature'].apply(list)
    return len(grouped_df)

def check_record(idx,tp,lp,rate_ratio,total_fee,total_trade_count):
    global enter_count
    flag = True
    df_temp  = pd.read_csv(f"{base_dir}/result_tmp.csv")
    df_list = df_temp.values.tolist()

    # 盈利因子 tp 总盈利 lp 总亏损
    profit_factor  =tp
    if lp !=0:
        profit_factor =tp /  abs(lp)
    

    data = [tp+lp,profit_factor,rate_ratio,total_fee,"",False,idx,total_trade_count]
    df_temp = pd.DataFrame(columns=['total_profit_all','总利润/总亏损','总利润/手续费','fee','factor_name','is_enter','index',"交易次数"])
    df_temp.loc[len(df_temp)] = data
    if len(df_list)==0:
        print("df_list is empty write the fisrt value in csv")
            # 临时存储结果,只保留最高的记录值
        df_temp.to_csv(f'{base_dir}/result_tmp.csv',index=False)
        df_list.append(data)
        flag = False
    
    index_index =idx
    df_factor_temp = pd.read_csv(f'{base_dir}/df_temp.csv')
    is_enter=False
    if profit_factor>df_list[0][1] and rate_ratio>df_list[0][2]:
        if rate_ratio <=0:
            print("<0 pass")
        elif flag==True:
            print("<<<<>>>enter>>><<<<<")
            is_enter=True
            df_factor_temp.to_csv(f'{base_dir}/enter.csv', mode='a', index=False, header=False)
            enter_count+=1
            df_temp.to_csv(f'{base_dir}/result_tmp.csv',index=False)
        else:
            print(">>>no enter>>>")
        # 临时存储结果,只保留最高的记录值
        
    else:
        print(">>>no enter>>>")

    factor_name=""
    if len(df_factor_temp)>0:
        factor_name= df_factor_temp.loc[0]['feature'].split("@")[0]
    df_temp['is_enter'] =  is_enter
    df_temp['factor_name'] = factor_name
    df_temp['index'] = index_index
    # 追加写入结果
    df_temp.to_csv(f'{base_dir}/result.csv',mode='a', index=False,header=False)

def step2(idx,start_time,end_time,title):
    start_time = start_time.replace("-","")
    end_time = end_time.replace("-","")
    param={}
    param['st'] = start_time
    param['et'] = end_time
    param['commission'] = 0.1
    param['risk_free_rate'] =0 # 0.02  # 无风险利率
    param['initial_value'] = 10000000
    param['title'] = title
    param['next_text']=""
    param['model_flag'] = "pre_1"

    p = Performance(param)
    p.run()
    

    # obj = p.obj

    # check_record(idx,obj["long_win_profit"]+obj["short_win_profit"],obj["long_loss_profit"]+obj["short_loss_profit"],obj["rateRatio"],obj["fee"],obj["all_trade_count"])

    print("Performance end")

def run(i):
    print(f"----------{i}--------")
    tt = zutil.Calc_Time(f"backtesting-- {i}",level=1)
    
    for year in years_list:
        b = Backtesting(i,year)
        #b.get_train_factor_list()
        #b.start_train()
        #b.use_model()
        b.model()
        b.gen_year_orders()
    tt.t()
    # 计算费率比数据
    step2(i,f"{years_list[0]}-01-01",f"{years_list[-1]}-12-31",f"depth_{DEPTH}")
    # step2(i,f"{years_list[0]}-01-01",f"2024-04-01","depth_5__666")
    pass

if __name__=="__main__":
    # step2(1,"2016-01-01","2016-12-31","111")
    # exit(0)
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-m', '--minute', type=str, help='开始时间', required=True)
    # parser.add_argument('-et', '--et', type=str, help='结束时间', required=True)
    # args = parser.parse_args()
    minute = 5
    #os.remove('./data/order.pkl')
    run(0)
    pass