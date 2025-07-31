"""
交易订单生成模块

该模块负责根据模型预测结果生成交易订单，是回测系统的核心组件之一。
通过分析预测信号，生成开仓和平仓订单，并保存到订单文件中。

主要功能包括：
1. 根据预测信号判断开仓时机
2. 根据平仓条件判断平仓时机
3. 生成完整的交易订单记录
4. 计算交易费用和收益
"""

import multiprocessing
import os
import sys

sys.path.append(os.getcwd())
import common.back_test_common as bt_common
import common.util as zutil
from common.data_common import Data_Common
import pandas as pd
import math
from config import *

# 是否可以重复开仓
TRADE_REPEAT = False

# 定义多空买卖方向常量
BUY = 1  # 买入（多头）
SELL = -1  # 卖出（空头）
OPEN = 0  # 开仓
CLOSE = 1  # 平仓


class Trade_Orders():
    """
    交易订单生成器类

    该类根据模型预测结果生成交易订单，包括开仓和平仓操作。

    Attributes
    ----------
    length : int
        信号标准差计算周期
    open_thr : float
        开仓阈值
    close_thr : float
        平仓阈值
    t_st : str
        回测开始时间
    t_et : str
        回测结束时间
    open_count : int
        开仓次数计数器
    pre_flag : str
        预测值列名
    model_flag : str
        模型标识
    prediction_df : pandas.DataFrame
        模型预测数据
    order_path : str
        订单文件路径
    data_common : Data_Common
        数据访问实例
    df_data : dict
        数据缓存字典
    order_df : pandas.DataFrame
        订单数据框
    """

    def __init__(self, param):
        """
        初始化交易订单生成器

        Parameters
        ----------
        param : dict
            配置参数字典，包含：
            - length: 信号标准差计算周期
            - open_thr: 开仓阈值
            - close_thr: 平仓阈值
            - st: 开始时间
            - et: 结束时间
        """
        self.length = param['length']
        self.open_thr = param['open_thr']
        self.close_thr = param['close_thr']
        self.t_st = param["st"]
        self.t_et = param["et"]
        # 开仓数量
        self.open_count = 0
        self.pre_flag = "pre"
        self.model_flag = "pre_1"

        # 预测表
        self.prediction_df = zutil.load_file('./data/pre.pkl')
        # 持仓记录
        self.order_path = "./data/order.pkl"
        self.data_common = Data_Common.create_instance()
        self.df_data = {}
        self.order_df = zutil.load_file(self.order_path)
        if len(self.order_df) == 0:
            self.order_df = pd.DataFrame(
                columns=['datetime', 'order_date', 'trading_date', 'instrument_id', 'instrument', 'buyOrSell',
                         'openOrClose', 'price', 'openPrice', 'count', 'count_back', 'ID', 'tradeId', 'mul',
                         'flag', 'model_flag', 'status', 'fee'])

        pass

    def calc_orders(self, instrument):
        """
        计算指定合约的交易订单

        根据模型预测信号，为指定合约生成交易订单，包括开仓和平仓操作。

        Parameters
        ----------
        instrument : str
            期货合约代码
        """
        t = zutil.Calc_Time(instrument)

        # 筛选指定合约在回测时间范围内的数据
        industry_df = self.prediction_df[
            (self.prediction_df['instrument'] == instrument) &
            (self.prediction_df['trading_date'] >= self.t_st) &
            (self.prediction_df['trading_date'] <= self.t_et)
            ].sort_values(by=['datetime'])

        # 计算信号绝对值和标准差
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
            # TODO: 这里有22行的代码重复，建议检查并重新处理
            if industry_df[self.pre_flag].iloc[i] > industry_df['signal_std'].iloc[i] * self.open_thr:

                # if industry_df['pre_signal'].iloc[i] > 0.09 and industry_df['pre_signal'].iloc[i] < 0.10:
                # 向后寻找平仓位置
                for j in range(i, industry_data_length):
                    # TODO modify bu xlzhou  <0
                    if industry_df[self.pre_flag].iloc[j] < -self.close_thr * industry_df['signal_std'].iloc[i]:
                        # 计算收益率
                        profit = (industry_df['open'].iloc[j] - industry_df['open'].iloc[i]) / industry_df['open'].iloc[
                            i]
                        industry_df.iloc[i, 14] = profit
                        industry_df.iloc[i, 15] = 1
                        industry_df.iloc[i, 16] = j - i
                        skip_count = j - i

                        # 生成开仓订单参数
                        param = self.get_param(industry_df.iloc[i])
                        param['buyOrSell'] = BUY
                        param['openOrClose'] = OPEN
                        self.insert_order(param)
                        self.open_count += 1

                        # 生成平仓订单参数
                        param2 = self.get_param(industry_df.iloc[j])
                        param2['openPrice'] = param['price']
                        param2['buyOrSell'] = param['buyOrSell']
                        param2['openOrClose'] = CLOSE
                        param2['count'] = param['count']
                        param2['count_back'] = param['count_back']
                        param2['ID'] = param['tradeId']
                        param2['status'] = "close"
                        self.insert_order(param2)
                        # print(instrument + ' buy at ' + str(industry_df.index[i]) + ' sell at ' + str(industry_df.index[j]) + ' get profit: ' + str(profit))
                        break

            # 满足开空条件
            elif industry_df[self.pre_flag].iloc[i] < industry_df['signal_std'].iloc[i] * (-self.open_thr):

                # elif industry_df['pre_signal'].iloc[i] < -0.09 and industry_df['pre_signal'].iloc[i] > -0.10:
                # 向后寻找平仓位置
                for j in range(i, industry_data_length):
                    # TODO modify bu xlzhou  >0
                    if industry_df[self.pre_flag].iloc[j] > self.close_thr * industry_df['signal_std'].iloc[i]:
                        # 计算收益率
                        profit = (industry_df['open'].iloc[i] - industry_df['open'].iloc[j]) / industry_df['open'].iloc[
                            i]
                        industry_df.iloc[i, 14] = profit
                        industry_df.iloc[i, 15] = -1
                        industry_df.iloc[i, 16] = j - i
                        skip_count = j - i

                        # 生成开仓订单参数
                        param = self.get_param(industry_df.iloc[i])
                        param['buyOrSell'] = SELL
                        param['openOrClose'] = OPEN
                        self.insert_order(param)
                        self.open_count += 1

                        # 生成平仓订单参数
                        param2 = self.get_param(industry_df.iloc[j])
                        param2['openPrice'] = param['price']
                        param2['buyOrSell'] = param['buyOrSell']
                        param2['openOrClose'] = CLOSE
                        param2['count'] = param['count']
                        param2['count_back'] = param['count_back']
                        param2['ID'] = param['tradeId']
                        param2['status'] = "close"
                        self.insert_order(param2)
                        # print(instrument + ' sell short at ' + str(industry_df.index[i]) + ' buy to cover at ' + str(industry_df.index[j]) + ' get profit: ' + str(profit))
                        break

        # # 按照成交额过滤交易
        # print(f"---过滤前-----{instrument}----------{len(industry_df[industry_df['return']!=0])}")
        # industry_df.loc[industry_df['FCT_Amount-20'] < 50, ['return', 'flag', 'holding']] = 0
        # print(f"---过滤后-----{instrument}----------{len(industry_df[industry_df['return']!=0])}")

        t.t()
        pass

    def get_param(self, doc):
        """
        获取订单参数

        根据行情数据生成订单参数，包括交易数量、价格等信息。

        Parameters
        ----------
        doc : pandas.Series
            行情数据行

        Returns
        -------
        dict
            订单参数字典
        """
        # 判断前面有没有未平仓的订单
        # 0买入 1卖出  buyOrSell
        # 0开   1平    openOrClose

        # 生成唯一交易ID
        trade_id = bt_common.generate_unique_string()
        price = doc['open']

        try:
            # 计算交易数量
            # count = math.floor(self.amount / (price * doc['mul'] * 0.15))
            count = math.floor(AMOUNT_4_OPEN / (price * doc['mul']))
        except Exception as ex:
            count = -1
            print(ex)
            # print(f"doc['instrument']:::{doc['instrument']}   price::{price} amount::{AMOUNT_4_OPEN} mul::{doc['mul']}")

        param = {
            'datetime': doc['datetime'],
            'order_date': doc['datetime'],
            'trading_date': doc['trading_date'],
            'instrument': doc['instrument'],
            'instrument_id': doc['instrument_id'],
            'buyOrSell': BUY,
            "openOrClose": OPEN,
            # 开仓价进入
            "price": price,
            "openPrice": price,
            "count": count,
            "count_back": count,
            # 关联ID
            "ID": trade_id,
            # 交易ID
            "tradeId": trade_id,
            "mul": int(doc['mul']),
            "model_flag": self.model_flag,
            "status": "open",
        }
        return param

    def insert_order(self, param):
        """
        插入订单到订单数据框

        将生成的订单参数添加到订单数据框中，并计算交易费用。

        Parameters
        ----------
        param : dict
            订单参数字典
        """
        try:
            if param['count'] == 0:
                return

            # 计算手续费
            fee = param['count'] * param['price'] * param['mul'] * FEE_FEE
            param['fee'] = fee

            # 添加订单到订单数据框
            self.order_df.loc[len(self.order_df)] = param

            # 如果是平仓订单，更新对应开仓订单的状态
            if param['status'] == "close":
                self.order_df.loc[self.order_df['ID'] == param["ID"], "status"] = "close"
        except Exception as ex:
            print(f"ex::{ex}")
            pass

    def main(self):
        """
        主函数

        遍历所有合约，为每个合约生成交易订单，并保存到文件。
        """
        # info = self.data_common.get_futures_mul()

        # 使用多进程池处理（当前被注释）
        pool = multiprocessing.Pool(processes=4)
        for ins in instruments:
            # pool.apply_async(self.calc_orders,args=(ins,))
            self.calc_orders(ins)

        pool.close()
        pool.join()

        # 保存订单数据到文件
        zutil.save_file(self.order_df, "./data/order.pkl")
        # print(zutil.load_file(self.order_df))
