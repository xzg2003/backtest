# 涨跌幅
import numpy as np
import pandas as pd

class  FCT_CHG():
    def __init__(self):
        pass
        
    def formula(self, param):
        df = param['df'].copy()
        step = param['length']
        self.factor_name = f'FCT_CHG@{step}'

        # 计算out
        df[self.factor_name] = np.where(df['open'].shift(-1)==0,0, (df['open'].shift(step-1) -df['open'].shift(-1)) / df['open'].shift(-1) * 100)

        # product_data['ret.'+str(ret)] = (product_data.shift(-ret)['close'] - product_data['close']) * 100 / product_data['close']

        # 空列补0
        # df['output'].fillna(0, inplace=True)
        if 'datetime' in df.columns:
            df = df.rename(columns={'datetime': 'date'})
        result = df[['date', self.factor_name]].copy()
        return result
