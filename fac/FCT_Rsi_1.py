
# RSI 技术指标 上涨与绝对涨跌幅总和对比

'''

Input:Length(20,1,1000,10);
收益率:=CLOSE-REF(CLOSE,1);
distance:=IF(收益率<0,0,收益率);
abs收益率:=ABS(收益率);
rsi:=SUM(distance,Length)/SUM(abs收益率,Length);
OUT:rsi-0.5;


'''
import numpy as np
import pandas as pd
from .factor_template import FactorTemplate

class  FCT_Rsi_1(FactorTemplate):
    def __init__(self):
        super().__init__()
        self.factor_name = 'FCT_Rsi_1'
        
    
    def formula(self,**param):
        df = param['df'].copy()
        Length = param['Length']

        # 计算收益率
        df['returns'] = df['close'] - df['close'].shift(1)

        # 计算距离
        df['distance'] = np.where(df['returns'] < 0, 0, df['returns'])

        # 计算绝对值收益率
        df['abs_returns'] = np.abs(df['returns'])

        # 计算rsi
        df['sum_distance'] = df['distance'].rolling(window=Length).sum()
        df['sum_abs_returns'] = df['abs_returns'].rolling(window=Length).sum()
        df['rsi'] =np.where(df['sum_abs_returns']==0,0, df['sum_distance'] / df['sum_abs_returns'])

        # 计算输出值
        df['output'] = df['rsi'] - 0.5

        
        # TODO 下面的保存需要删除
        if param['save'] is not None:
            df.to_csv(param['save'], index=False)
        return df['output']