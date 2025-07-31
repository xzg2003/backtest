import os

import numpy as np
import pandas as pd

from backtesting.gen_orders import Trade_Orders
from backtesting.performance4 import Performance
from model.import_model import MODEL

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# from model.xgb import *
# from model.DL_model import *

# 定义多空买
BUY = 1
SELL = -1
OPEN = 0
CLOSE = 1
FEE_FEE = 0.0002
TRADE_REPEAT = True
BUY_OR_SELL_RATE = 0.05
PRE_FLAG = 24
base_dir = './enter_factors'

import os
import sys

sys.path.append(os.getcwd())
import common.util as zutil
from common.data_common import Data_Common
from config import *
from prepare_data import prepare_data

# 根据因子训练数据

train_ignore_list = ['date', 'datetime', 'FCT_CHG@1', 'FCT_CHG@3', 'FCT_CHG@5', 'FCT_CHG@10', 'FCT_CHG@24',
                     'instrument_id', "_id", "trading_date",
                     'instrument', 'money', 'mul', 'high', 'low', 'open', 'close', 'volume', 'open_interest', 'mindiff',
                     'factor',
                     "FCT_CHG_Stander@1", "FCT_CHG_Stander@3", "FCT_CHG_Stander@5", "FCT_CHG_Stander@10",
                     "FCT_CHG_Stander@24", "instrument_num"]

years_base_path = "./years_pkls"


class Backtesting():
    def __init__(self, year):
        """
        初始化回测实例

        Parameters
        ----------
        year ： int
            回测年份
        """
        self.st = f"{year}-01-01"  # 回测开始时间
        self.et = f"{year}-12-31"  # 回测结束时间
        self.year = year  # 回测年份
        self.instrument_list = instruments  # 交易品种列表

        # 准备训练数据、预测数据和前置预测数据
        self.train_data, self.prediction_data, self.pre_prediction_data = \
            prepare_data(year, self.instrument_list, train_list, target_list[0], k_line_type)

        self.data_common = Data_Common.create_instance()  # 数据通用类实例

    def model(self):
        """
        模型训练和预测阶段
        使用历史数据训练模型，并对未来数据进行预测
        """
        # 划分训练集和测试集

        # 对训练特征列表进行排序
        train_list.sort()

        # 准备训练特征数据，替换无穷值为 NaN
        X_train = self.train_data[train_list].replace([np.inf, -np.inf], np.nan)

        # 准备训练标签数据
        y_train = pd.DataFrame()
        y_train[target_list[0]] = self.train_data[target_list[0]].fillna(0)

        # 准备测试特征数据
        x_test = self.prediction_data[train_list]
        x_pre_test = self.pre_prediction_data

        # 初始化并运行模型
        model = MODEL(self.instrument_list, X_train, y_train, x_test, x_pre_test, model_param)
        model.run()

    def get_instrument_list(self):
        """
        获取交易品种列表
        TODO: 这个函数似乎没有用法
        """
        info = self.data_common.get_futures_mul()
        for idx, doc in info.iterrows():
            self.instrument_list.append(doc['instrument'])
        pass

    def gen_year_orders(self):
        """
        生成年度交易订单
        根据模型预测结果生成具体的交易信号和订单
        """
        # 设置订单生成参数
        param = {
            "length": 10,  # 信号标准差计算周期
            "open_thr": 2.0,  # 开仓阈值
            "close_thr": 0.8,  # 平仓阈值
            "st": self.st,  # 开始时间
            "et": self.et,  # 结束时间
        }

        # 初始化订单生成器并执行主要逻辑
        a = Trade_Orders(param)
        a.main()
        pass


def step2(start_time, end_time):
    """
    绩效评估阶段
    计算并输出回测的整体绩效指标

    Parameters
    ----------
    start_time : str
        绩效评估开始时间，格式为YYYY-MM-DD
    end_time : str
        绩效评估结束时间，格式为YYYY-MM-DD
    """
    # 格式化时间字符串
    start_time = start_time.replace("-", "")
    end_time = end_time.replace("-", "")

    # 设置绩效评估参数
    param = {}
    param['st'] = start_time  # 开始时间
    param['et'] = end_time  # 结束时间
    param['commission'] = 0.1  # 手续费比例
    param['risk_free_rate'] = 0  # 0.02  # 无风险利率
    param['initial_value'] = 10000000  # 初始资金
    param['next_text'] = ""  # 附加文本

    # 初始化绩效评估其并运行
    p = Performance(param)
    p.run()

    print("Performance end")


def run(i):
    """
    主运行函数
    控制整个回测流程的执行

    Parameters
    ----------
    i : int
        运行标识符
    """
    print(f"----------{i}--------")
    # 计时器，用于统计回测耗时
    tt = zutil.Calc_Time(f"backtesting-- {i}", level=1)

    # 遍历所有需要回测的年份
    for year in years_list:
        # 初始化回测实例
        b = Backtesting(year)

        # 模型训练和预测
        b.model()

        # 生成交易订单
        b.gen_year_orders()

    # 输出耗时统计
    tt.t()

    # 计算费率比数据
    step2(f"{years_list[0]}-01-01", f"{years_list[-1]}-12-31")
    pass


if __name__ == "__main__":
    """
    程序入口
    先清楚先前的仓位文件
    然后调用run文件执行回测流程
    """
    if os.path.exists('./data/order.pkl'):
        os.remove('./data/order.pkl')
    # print(zutil.load_file('./data/pre.pkl'))
    run(0)
