
'''
将这个部分的订单生产独立出来，生成订单入库，然后用之前的算法计算后面的回测
'''
import multiprocessing
import os
import sys
sys.path.append(os.getcwd())
import common.back_test_common as bt_common
import common.util as zutil
from common.data_common import Data_Common
import pandas as pd
from config import FEE_FEE,AMOUNT_4_OPEN
import math
import sys
import os
from config import *

# 是否可以重复开仓
TRADE_REPEAT = False

# 定义多空买卖
BUY =1
SELL =-1
OPEN=0
CLOSE=1


class Trade_Orders():
    def __init__(self,param):
        self.length = param['length']
        self.open_thr = param['open_thr']
        self.close_thr = param['close_thr']
        self.t_st = param["st"]
        self.t_et = param["et"]
         # 开仓数量
        self.open_count =0
        self.pre_flag = f"pre_{param['pre_flag']}"

        if 'model_flag' in param:
            self.model_flag=param['model_flag']
        else:
            self.model_flag="pre_1"
        # 预测表
        self.prediction_df = zutil.load_file('./data/pre.pkl')
        # 持仓记录
        self.order_path = "./data/order.pkl"
        self.data_common = Data_Common.create_instance()
        self.df_data={}
        self.order_df = zutil.load_file(self.order_path)
        if len(self.order_df)==0:
            self.order_df=pd.DataFrame(columns=['datetime','order_date','trading_date','instrument_id','instrument','buyOrSell',
                                                'openOrClose','price','openPrice','count','count_back','ID','tradeId','mul',
                                                'flag','model_flag','status','fee'])

        pass

    def calc_orders(self,instrument):
        t = zutil.Calc_Time(instrument)
        industry_df = self.prediction_df[(self.prediction_df['instrument']==instrument) &(self.prediction_df['trading_date']>=self.t_st)&(self.prediction_df['trading_date']<=self.t_et)].sort_values(by=['datetime'])
        industry_df['signal_abs'] = industry_df[self.pre_flag].abs()
        # signal_std列用于保存信号值的标准差
        industry_df['signal_std'] = industry_df['signal_abs'].rolling(self.length).mean()
        # 记录当根k线开仓的这笔交易的收益率、多空标识、持有时长，其列序号为6\7\8
        industry_df['return'] = 0
        industry_df['flag'] = 0
        industry_df['holding'] = 0
        industry_data_length = industry_df.shape[0]
        # 如果不能重复开仓，需要跳过一些数据
        skip_count = 0
        # 采用轮询的方式进行回测 i的取值范围是从0开始，到行数-1，一共的条数等于行数
        # print(f'industry_data_length 循环次数：：{industry_data_length}')
        for i in range(industry_data_length):
            # print(f"product::{instrument}--industry_data_length:::{industry_data_length} -- {i} ,剩余：{industry_data_length-i}")
            # 前置的若干数据直接跳过
            if math.isnan(industry_df['signal_std'].iloc[i]):
                continue
            # 如果属于需要跳过的周期
            if TRADE_REPEAT == False:
                skip_count = skip_count - 1
                if skip_count > 0:
                    continue
            # 满足开多条件
            if industry_df[self.pre_flag].iloc[i] > industry_df['signal_std'].iloc[i] * self.open_thr:
                
            # if industry_df['pre_signal'].iloc[i] > 0.09 and industry_df['pre_signal'].iloc[i] < 0.10:
                # 向后寻找平仓位置
                for j in range(i, industry_data_length):
                    # TODO modify bu xlzhou  <0
                    if industry_df[self.pre_flag].iloc[j] < -self.close_thr*industry_df['signal_std'].iloc[i]:
                        profit = (industry_df['open'].iloc[j] - industry_df['open'].iloc[i]) / industry_df['open'].iloc[i]
                        industry_df.iloc[i, 14] = profit
                        industry_df.iloc[i, 15] = 1
                        industry_df.iloc[i, 16] = j - i
                        skip_count = j - i

                        param = self.get_param(industry_df.iloc[i])
                        param['buyOrSell'] = BUY
                        param['openOrClose'] = OPEN
                        self.insert_order(param)
                        self.open_count +=1

                        param2 = self.get_param(industry_df.iloc[j])
                        param2['openPrice'] = param['price']
                        param2['buyOrSell'] = param['buyOrSell']
                        param2['openOrClose'] =CLOSE
                        param2['count'] = param['count']
                        param2['count_back'] = param['count_back']
                        param2['ID']=param['tradeId']
                        param2['status']="close"
                        self.insert_order(param2)
                        # print(instrument + ' buy at ' + str(industry_df.index[i]) + ' sell at ' + str(industry_df.index[j]) + ' get profit: ' + str(profit))
                        break
            # 满足开空条件
            elif industry_df[self.pre_flag].iloc[i] < industry_df['signal_std'].iloc[i] * (-self.open_thr):
                
            # elif industry_df['pre_signal'].iloc[i] < -0.09 and industry_df['pre_signal'].iloc[i] > -0.10:
                # 向后寻找平仓位置
                for j in range(i, industry_data_length):
                    # TODO modify bu xlzhou  >0
                    if industry_df[self.pre_flag].iloc[j] > self.close_thr*industry_df['signal_std'].iloc[i]:
                        profit = (industry_df['open'].iloc[i] - industry_df['open'].iloc[j]) / industry_df['open'].iloc[i]
                        industry_df.iloc[i, 14] = profit
                        industry_df.iloc[i, 15] = -1
                        industry_df.iloc[i, 16] = j - i
                        skip_count = j - i

                        param = self.get_param(industry_df.iloc[i])
                        param['buyOrSell'] = SELL
                        param['openOrClose'] = OPEN
                        self.insert_order(param)
                        self.open_count +=1

                        param2 = self.get_param(industry_df.iloc[j])
                        param2['openPrice'] = param['price']
                        param2['buyOrSell'] = param['buyOrSell']
                        param2['openOrClose'] =CLOSE
                        param2['count'] = param['count']
                        param2['count_back'] = param['count_back']
                        param2['ID']=param['tradeId']
                        param2['status']="close"
                        self.insert_order(param2)
                        # print(instrument + ' sell short at ' + str(industry_df.index[i]) + ' buy to cover at ' + str(industry_df.index[j]) + ' get profit: ' + str(profit))
                        break
        
        # # 按照成交额过滤交易
        # print(f"---过滤前-----{instrument}----------{len(industry_df[industry_df['return']!=0])}")
        # industry_df.loc[industry_df['FCT_Amount-20'] < 50, ['return', 'flag', 'holding']] = 0
        # print(f"---过滤后-----{instrument}----------{len(industry_df[industry_df['return']!=0])}")

        t.t()
        pass

    def get_param(self,doc):
        # 判断前面有没有未平仓的订单
        # 0买入 1卖出  buyOrSell
        # 0开   1平    openOrClose
        trade_id = bt_common.generate_unique_string()
        price = doc['open']
        try:
            # count = math.floor(self.amount / (price * doc['mul'] * 0.15))
            count = math.floor(AMOUNT_4_OPEN / (price * doc['mul']))
        except Exception as ex:
            count = -1
            print(ex)
            # print(f"doc['instrument']:::{doc['instrument']}   price::{price} amount::{AMOUNT_4_OPEN} mul::{doc['mul']}")
        param={
                'datetime':doc['datetime'],
                'order_date':doc['datetime'],
                'trading_date':doc['trading_date'],
                'instrument':doc['instrument'],
                'instrument_id':doc['instrument_id'],
                'buyOrSell':BUY,
                "openOrClose":OPEN,
                # 开仓价进入
                "price":price,
                "openPrice":price,
                "count":count,
                "count_back":count,
                # 关联ID
                "ID":trade_id,
                # 交易ID
                "tradeId":trade_id,
                "mul":int(doc['mul']),
                "model_flag":self.model_flag,
                "status":"open",
                }           
        return param

    def insert_order(self,param):
        try:
            if param['count']==0:
                return
            fee = param['count']*param['price']*param['mul']*FEE_FEE
            param['fee'] =fee
            self.order_df.loc[len(self.order_df)] = param
            if param['status']=="close":
                self.order_df.loc[self.order_df['ID']==param["ID"],"status"] = "close"
        except Exception as ex:
            print(f"ex::{ex}")
            pass
    

    def main(self):
        #info = self.data_common.get_futures_mul()
        pool = multiprocessing.Pool(processes=4)
        for ins in instruments:
            # pool.apply_async(self.calc_orders,args=(ins,))
            self.calc_orders(ins)
        
        pool.close()
        pool.join()
        zutil.save_file(self.order_df,"./data/order.pkl")