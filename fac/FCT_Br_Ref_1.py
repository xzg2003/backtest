
# 人气意愿指标减去REF

'''
Input:Length(20,1,1000,10);
up:= if(HIGH - REF(close,1)>0,HIGH - REF(close,1),0);
down:=if(REF(close,1)-low >0,REF(close,1)-low,0);
br1:= sum(up,Length);
br2:= sum(down,Length);
特征值: (br1-br2)/(br1+br2);
OUT:特征值-ref(特征值,length);
'''
import numpy as np
import pandas as pd

from .constants import MIN_MAX
from .factor_template import FactorTemplate

class  FCT_Br_Ref_1(FactorTemplate):
    def __init__(self):
        super().__init__()
        self.factor_name = 'FCT_Br_Ref_1'
        
    
    def formula(self,**param):
        df = param['df'].copy()
        Length = param['Length']

        df['Close_prev'] = df['close'].shift(1)
        df['tr'] = df[['high', 'low', 'Close_prev']].apply(lambda x: max(x[0] - x[1], abs(x[0] - x[2]), abs(x[1] - x[2])), axis=1)

        
        df['up'] = np.where(df['high']-df['close'].shift(1)>0,df['high']-df['close'].shift(1),0)
        df['down'] = np.where(df['close'].shift(1)-df['low']>0,df['close'].shift(1)-df['low'],0)
        df['br1'] = df['up'].rolling(window=Length).sum()
        df['br2'] = df['down'].rolling(window=Length).sum()
        df['factor'] = np.where((df['br1']+df['br2'])==0,0,(df['br1']-df['br2'])/ (df['br1']+df['br2']))

        # 计算out
        df['output'] =  df['factor'] -df['factor'].shift(Length)
        if MIN_MAX[self.factor_name] !=None and (Length in MIN_MAX[self.factor_name]):
            min_max = MIN_MAX[self.factor_name][Length]
            df['output'] = np.where(df['output']>min_max['max'],min_max['max'],
                                    np.where(df['output']<min_max['min'],min_max['min'],df['output']))
        # TODO 下面的保存需要删除
        if param['save'] is not None:
            df.to_csv(param['save'], index=False)
        return df['output']