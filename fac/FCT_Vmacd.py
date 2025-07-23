
# FCT_Vmacd 

'''
INPUT:LENGTH(10,1,1000,1);
DIFF : MA(VOL,LENGTH) - MA(VOL,2*LENGTH);
DEA  : MA(DIFF,LENGTH);
MACD : (DIFF-DEA)/MA(VOL,LENGTH), COLORSTICK;
OUT:MACD;

'''
import numpy as np
import pandas as pd

from .constants import MIN_MAX
from .factor_template import FactorTemplate

class  FCT_Vmacd(FactorTemplate):
    def __init__(self):
        super().__init__()
        self.factor_name = 'FCT_Vmacd'
        
    
    def formula(self,**param):
        df = param['df'].copy()
        Length = param['Length']

        df['DIFF'] = df['volume'].rolling(window=Length).mean()-df['volume'].rolling(window=2*Length).mean()
        df['DEA'] = df['DIFF'].rolling(window=Length).mean()
        df['MACD'] =np.where(df['volume'].rolling(window=Length).mean()==0,0, (df['DIFF']-df['DEA'])/df['volume'].rolling(window=Length).mean())

        # 计算out
        df['output'] =  df['MACD']
        if MIN_MAX[self.factor_name] !=None and (Length in MIN_MAX[self.factor_name]):
            min_max = MIN_MAX[self.factor_name][Length]
            df['output'] = np.where(df['output']>min_max['max'],min_max['max'],
                                    np.where(df['output']<min_max['min'],min_max['min'],df['output']))
        # TODO 下面的保存需要删除
        if param['save'] is not None:
            df.to_csv(param['save'], index=False)
        return df['output']