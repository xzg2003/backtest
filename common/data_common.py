from datetime import datetime
import os
import sys

from dotenv import dotenv_values
import pandas as pd
sys.path.append(os.getcwd())
#env_vars = dotenv_values("/data/Finance/Factor/factor/.env")
USE_DB = False

class IN_CSV:
    def __init__(self) :
        self.trading_days_path = "./static_data/trading_days.csv"
        self.trading_days_df = pd.read_csv(self.trading_days_path)
        self.trading_days_df['date'] = pd.to_datetime(self.trading_days_df['date'])

        self.futures_path = "./static_data/futures_mul.csv"
        self.futures_df = pd.read_csv(self.futures_path)

        self.change_date_path = "./static_data/change_date.csv"
        self.change_date_df = pd.read_csv(self.change_date_path)
        pass
    
    # 处理日期为标准时间
    def _get_start_end_time(self,time):
        if isinstance(time,int):
            t = datetime.strptime(str(time), '%Y%m%d')
        elif isinstance(time,str):
            t = datetime.strptime(str(time), '%Y-%m-%d')
        else:
            t = time
        t = pd.Timestamp(t, tz='UTC')
        return t
    
    # 根据开始时间和结束时间，获取交易日期
    def get_trading_days(self,start_time,end_time):
        '''
        start_time : 格式为 2020-01-01 / 20200101(int)
        end_time : 格式为 2020-01-01 / 20200101(int)
        '''
        st = self._get_start_end_time(start_time)
        et = self._get_start_end_time(end_time)
        df = self.trading_days_df[(self.trading_days_df['date']>=st) & (self.trading_days_df['date']<=et)].sort_values("date")
        return df
    
    # 计算开始时间与结束时间内的交易天数
    def count_trading_days(self,start_time,end_time):
        st = self._get_start_end_time(start_time)
        et = self._get_start_end_time(end_time)
        df = self.trading_days_df[(self.trading_days_df['date']>=st) & (self.trading_days_df['date']<=et)]
        return len(df)
        pass

    # 传入时间，获取下一个交易日
    def get_next_trading_day(self,time):
        t = self._get_start_end_time(time)
        next_date=""
        df = self.trading_days_df[(self.trading_days_df['date']>t)].sort_values('date').head(1).reset_index()
        if len(df)==1:
            next_date = df.loc[0,"date"].strftime("%Y-%m-%d")
        return next_date
    
    # 传入时间，获取上一个交易日
    def get_pre_trading_day(self,time):
        t = self._get_start_end_time(time)
        pre_day = ""
        df = self.trading_days_df[(self.trading_days_df['date']<t)].sort_values('date').tail(1).reset_index()
        if len(df)==1:
            pre_day = df.loc[0,"date"].strftime("%Y-%m-%d")
        return pre_day
    
    def get_futures_mul(self):
        df = self.futures_df.sort_values("instrument")
        # df=df[df['instrument']=="SN"]
        return df
    def get_futures_mul_by_instrument(self,instrument):
        mul_df = self.futures_df[self.futures_df['instrument']==instrument]
        mul = mul_df.iloc[0].to_dict()
        return mul
    
    def count_change_date_by_end_time(self,end_time,instrument):
        info = self.change_date_df[(self.change_date_df['endTime']==end_time) & (self.change_date_df['instrument']==instrument)]
        check = len(info)
        return check
    def find_change_date_by_start_time(self,start_time,instrument):
        change_info_df = self.change_date_df[(self.change_date_df['startTime']==start_time) & (self.change_date_df['instrument']==instrument)]
        change_info = None
        if len(change_info_df)>0:
            change_info = change_info_df.iloc[0].to_dict()
        return change_info
    def find_change_date_by_end_time(self,end_time,instrument):
        change_date_start_df =  self.change_date_df[(self.change_date_df['endTime']==end_time) & (self.change_date_df['instrument']==instrument)]
        change_date_start = None
        if len(change_date_start_df)>0:
            change_date_start = change_date_start_df.iloc[0].to_dict()
        return change_date_start
    def fun(self):
        print(self.trading_days_path)
        print(" this is fun B")

class Data_Common:
    @staticmethod
    def create_instance():
        return IN_CSV()
