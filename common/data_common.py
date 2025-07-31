"""
数据通用模块
提供交易日查询、合约乘数查询等通用数据服务
"""

import os
import sys
from datetime import datetime

import pandas as pd

sys.path.append(os.getcwd())
# env_vars = dotenv_values("/data/Finance/Factor/factor/.env")

# 是否使用数据库标志（当前未使用）
USE_DB = False


class IN_CSV:
    """
        CSV数据访问类
        提供对交易日历、期货合约信息等静态数据的访问接口
    """

    def __init__(self):
        """
        初始化数据访问实例
        加载交易日历、期货合约乘数等静态数据
        """
        # 加载交易日历数据
        self.trading_days_path = "./static_data/trading_days.csv"
        self.trading_days_df = pd.read_csv(self.trading_days_path)
        self.trading_days_df['date'] = pd.to_datetime(self.trading_days_df['date'])

        # 加载期货合约乘数数据
        self.futures_path = "./static_data/futures_mul.csv"
        self.futures_df = pd.read_csv(self.futures_path)

        # 加载合约变更日期数据
        self.change_date_path = "./static_data/change_date.csv"
        self.change_date_df = pd.read_csv(self.change_date_path)
        pass

    @staticmethod
    def _get_start_end_time(time):
        """
        将不同格式的时间转换为标准时间格式

        Parameters
        ----------
        time : int, str, or datetime
            输入时间，支持整数(如20200101)、字符串(如'2020-01-01')或datetime对象

        Returns
        -------
        pandas.Timestamp
            标准化的时间戳对象
        """
        if isinstance(time, int):
            t = datetime.strptime(str(time), '%Y%m%d')
        elif isinstance(time, str):
            t = datetime.strptime(str(time), '%Y-%m-%d')
        else:
            t = time
        t = pd.Timestamp(t, tz='UTC')
        return t

    def get_trading_days(self, start_time, end_time):
        """
        根据开始时间和结束时间，获取交易日期列表

        Parameters
        ----------
        start_time : int or str
            开始时间，格式为 2020-01-01 或 20200101(int)
        end_time : int or str
            结束时间，格式为 2020-01-01 或 20200101(int)

        Returns
        -------
        pandas.DataFrame
            包含指定时间范围内所有交易日的数据框，按日期排序
        """
        st = self._get_start_end_time(start_time)
        et = self._get_start_end_time(end_time)
        df = self.trading_days_df[
            (self.trading_days_df['date'] >= st) & (self.trading_days_df['date'] <= et)].sort_values("date")
        return df

    def count_trading_days(self, start_time, end_time):
        """
        计算开始时间与结束时间内的交易天数

        Parameters
        ----------
        start_time : int or str
            开始时间，格式为 2020-01-01 或 20200101(int)
        end_time : int or str
            结束时间，格式为 2020-01-01 或 20200101(int)

        Returns
        -------
        int
            指定时间范围内的交易日数量
        """
        st = self._get_start_end_time(start_time)
        et = self._get_start_end_time(end_time)
        df = self.trading_days_df[(self.trading_days_df['date'] >= st) & (self.trading_days_df['date'] <= et)]
        return len(df)

    def get_next_trading_day(self, time):
        """
        传入时间，获取下一个交易日

        Parameters
        ----------
        time : int or str or datetime
            指定时间

        Returns
        -------
        str
            下一个交易日，格式为 "YYYY-MM-DD"，如果不存在则返回空字符串
        """
        t = self._get_start_end_time(time)
        next_date = ""
        df = self.trading_days_df[(self.trading_days_df['date'] > t)].sort_values('date').head(1).reset_index()
        if len(df) == 1:
            next_date = df.loc[0, "date"].strftime("%Y-%m-%d")
        return next_date

    def get_pre_trading_day(self, time):
        """
        传入时间，获取上一个交易日

        Parameters
        ----------
        time : int or str or datetime
            指定时间

        Returns
        -------
        str
            上一个交易日，格式为 "YYYY-MM-DD"，如果不存在则返回空字符串
        """
        t = self._get_start_end_time(time)
        pre_day = ""
        df = self.trading_days_df[(self.trading_days_df['date'] < t)].sort_values('date').tail(1).reset_index()
        if len(df) == 1:
            pre_day = df.loc[0, "date"].strftime("%Y-%m-%d")
        return pre_day

    def get_futures_mul(self):
        """
        获取所有期货合约的乘数信息

        Returns
        -------
        pandas.DataFrame
            包含所有期货合约乘数信息的数据框，按合约代码排序
        """
        df = self.futures_df.sort_values("instrument")
        # df=df[df['instrument']=="SN"]
        return df

    def get_futures_mul_by_instrument(self, instrument):
        """
        根据合约代码获取期货合约乘数信息

        Parameters
        ----------
        instrument : str
            期货合约代码

        Returns
        -------
        dict
            包含指定合约乘数信息的字典
        """
        mul_df = self.futures_df[self.futures_df['instrument'] == instrument]
        mul = mul_df.iloc[0].to_dict()
        return mul

    def count_change_date_by_end_time(self, end_time, instrument):
        """
        根据结束时间和合约代码统计合约变更记录数量

        Parameters
        ----------
        end_time : str
            结束时间
        instrument : str
            期货合约代码

        Returns
        -------
        int
            符合条件的合约变更记录数量
        """
        info = self.change_date_df[
            (self.change_date_df['endTime'] == end_time) & (self.change_date_df['instrument'] == instrument)]
        check = len(info)
        return check

    def find_change_date_by_start_time(self, start_time, instrument):
        """
        根据开始时间和合约代码查找合约变更记录

        Parameters
        ----------
        start_time : str
            开始时间
        instrument : str
            期货合约代码

        Returns
        -------
        dict or None
            合约变更信息字典，如果未找到则返回None
        """
        change_info_df = self.change_date_df[
            (self.change_date_df['startTime'] == start_time) & (self.change_date_df['instrument'] == instrument)]
        change_info = None
        if len(change_info_df) > 0:
            change_info = change_info_df.iloc[0].to_dict()
        return change_info

    def find_change_date_by_end_time(self, end_time, instrument):
        """
        根据结束时间和合约代码查找合约变更记录

        Parameters
        ----------
        end_time : str
            结束时间
        instrument : str
            期货合约代码

        Returns
        -------
        dict or None
            合约变更信息字典，如果未找到则返回None
        """
        change_date_start_df = self.change_date_df[
            (self.change_date_df['endTime'] == end_time) & (self.change_date_df['instrument'] == instrument)]
        change_date_start = None
        if len(change_date_start_df) > 0:
            change_date_start = change_date_start_df.iloc[0].to_dict()
        return change_date_start

    def fun(self):
        """
        测试函数（未实际使用）
        """
        print(self.trading_days_path)
        print(" this is fun B")


class Data_Common:
    """
    数据通用访问接口类
    提供静态方法用于创建数据访问实例
    """

    @staticmethod
    def create_instance():
        """
        创建数据访问实例

        Returns
        -------
        IN_CSV
            IN_CSV类的实例
        """
        return IN_CSV()
