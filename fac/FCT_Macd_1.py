# MACD 除以MA（TR） 去量纲
# Input:S(20,10,1000,10);
# DIFF := MA(CLOSE,S) - MA(CLOSE,2*S);
# DEA  := MA(DIFF,S);
# MACD1 := 2*(DIFF-DEA), COLORSTICK;
# OUT:if(MA(TR,S)<MINDIFF,0,MACD1/MA(TR,S));
import numpy as np
import pandas as pd

from .constants import MIN_MAX
from .factor_template import FactorTemplate

class  FCT_Macd_1(FactorTemplate):
    def __init__(self):
        super().__init__()
        self.factor_name = 'FCT_Macd_1'
        
    
    def formula(self,**param):
        df = param['df'].copy()
        Length = param['Length']
        # 计算DIFF
        df['diff'] = df['close'].rolling(window=Length).mean() - df['close'].rolling(window=2*Length).mean()

        # 计算DEA
        df['dea'] = df['diff'].rolling(window=Length).mean()

        # 计算MACD1
        df['macd1'] = 2 * (df['diff'] - df['dea'])
        
        
        # 计算MA(TR,S)和MINDIFF
        df['Close_prev'] = df['close'].shift(1)
        df['tr'] = df[['high', 'low', 'Close_prev']].apply(lambda x: max(x[0] - x[1], abs(x[0] - x[2]), abs(x[1] - x[2])), axis=1)
        df['ma_tr'] = df['tr'].rolling(window=Length).mean()

        # 计算OUT
        df['output'] = np.where((df['ma_tr'] < df['mindiff'])|(df['ma_tr']==0), 0, df['macd1'] / df['ma_tr'])
        if MIN_MAX[self.factor_name] !=None and (Length in MIN_MAX[self.factor_name]):
            min_max = MIN_MAX[self.factor_name][Length]
            df['output'] = np.where(df['output']>min_max['max'],min_max['max'],
                                    np.where(df['output']<min_max['min'],min_max['min'],df['output']))
        # print(df['output'])
        # TODO 下面的保存需要删除
        if param['save'] is not None:
            df.to_csv(param['save'], index=False)
        # df.to_csv('test_FCT_Ac_Tr_1.csv', index=False)
        return df['output']
