
# 一天与5天的atr对比

'''
Input:length(72,1,1000,1);

one_day_atr:= ma(TR,length);

five_day_atr:= ma(TR,length*5);


OUT:one_day_atr/(one_day_atr+five_day_atr);


'''
import numpy as np
import pandas as pd

from .constants import MIN_MAX
from .factor_template import FactorTemplate

class  FCT_Atr_DFive_1(FactorTemplate):
    def __init__(self):
        super().__init__()
        self.factor_name = 'FCT_Atr_DFive_1'
        
    
    def formula(self,**param):
        df = param['df'].copy()
        Length = param['Length']
        oneday = param['one_day']
        fiveday = param['five_day']

        df['Close_prev'] = df['close'].shift(1)
        df['tr'] = df[['high', 'low', 'Close_prev']].apply(lambda x: max(x[0] - x[1], abs(x[0] - x[2]), abs(x[1] - x[2])), axis=1)

        # one_day_atr
        df['one_day_atr'] = df['tr'].rolling(window=oneday).mean()
        df['five_day_atr'] = df['tr'].rolling(window=fiveday).mean()

        # 计算out
        df['output'] =np.where((df['one_day_atr']+df['five_day_atr'])==0,0, df['one_day_atr'] /(df['one_day_atr']+df['five_day_atr']))
        
        if MIN_MAX[self.factor_name] !=None and (Length in MIN_MAX[self.factor_name]):
            min_max = MIN_MAX[self.factor_name][Length]
            df['output'] = np.where(df['output']>min_max['max'],min_max['max'],
                                    np.where(df['output']<min_max['min'],min_max['min'],df['output']))
        # TODO 下面的保存需要删除
        if param['save'] is not None:
            df.to_csv(param['save'], index=False)
        return df['output']