
# close 到 bbi布林下轨的距离

'''
INPUT:LENGTH(10,1,1000,1);
BBI:(MA(CLOSE,3)+MA(CLOSE,6)+MA(CLOSE,12)+MA(CLOSE,24))/4;
DWN:BBI-STD(BBI,LENGTH);
sc:(CLOSE-DWN)/OPEN;

波动率:= ma(TR,200)*100/open;
OUT:sc/波动率;

'''
import numpy as np
import pandas as pd

from .constants import MIN_MAX
from .factor_template import FactorTemplate

class  FCT_Bbiboll_Down(FactorTemplate):
    def __init__(self):
        super().__init__()
        self.factor_name = 'FCT_Bbiboll_Down'
        
    
    def formula(self,**param):
        df = param['df'].copy()
        Length = param['Length']
        TrLength = param['TRLength']

        df['Close_prev'] = df['close'].shift(1)
        df['tr'] = df[['high', 'low', 'Close_prev']].apply(lambda x: max(x[0] - x[1], abs(x[0] - x[2]), abs(x[1] - x[2])), axis=1)

        df['BBI'] =(df['close'].rolling(window=3).mean()+df['close'].rolling(window=6).mean()+df['close'].rolling(window=12).mean()+df['close'].rolling(window=24).mean())/4
        df['DWN'] = df["BBI"] - df['BBI'].rolling(window=Length).std()
        df['sc'] = (df['close']-df['DWN'])/df['open']
        # 波动率
        df['wave_rate'] = df['tr'].rolling(window=TrLength).mean()*100/df['open']
        # 计算out
        df['output'] = np.where(df['wave_rate']==0,0, df['sc'] / df['wave_rate'])
        if MIN_MAX[self.factor_name] !=None and (Length in MIN_MAX[self.factor_name]):
            min_max = MIN_MAX[self.factor_name][Length]
            df['output'] = np.where(df['output']>min_max['max'],min_max['max'],
                                    np.where(df['output']<min_max['min'],min_max['min'],df['output']))
        # TODO 下面的保存需要删除
        if param['save'] is not None:
            df.to_csv(param['save'], index=False)
        return df['output']