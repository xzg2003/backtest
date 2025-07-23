
# 乖离率除以TR去量纲 带成交量

'''

Input:P1(20,1,1000,1);
signal:=if(MA(TR,P1)<MINDIFF,0,(CLOSE-MA(CLOSE,P1))/MA(TR,P1));
one_day_vol:= ma(Vol,72);
five_day_vol:= ma(Vol,360);
rate:=(one_day_vol)/(one_day_vol+five_day_vol);
OUT:signal*rate;


'''
import numpy as np
import pandas as pd

from .constants import MIN_MAX
from .factor_template import FactorTemplate

class  FCT_Bias_Vol_Dfive(FactorTemplate):
    def __init__(self):
        super().__init__()
        self.factor_name = 'FCT_Bias_Vol_Dfive'
        
    
    def formula(self,**param):
        df = param['df'].copy()
        Length = param['Length']
        oneday = param['one_day']
        fiveday = param['five_day']

        df['Close_prev'] = df['close'].shift(1)
        df['tr'] = df[['high', 'low', 'Close_prev']].apply(lambda x: max(x[0] - x[1], abs(x[0] - x[2]), abs(x[1] - x[2])), axis=1)
        df['atr'] = df['tr'].rolling(window=Length).mean()

        df['signal'] = np.where((df['atr']<df['mindiff'])|(df['atr']==0),0,(df['close']-df['close'].rolling(window=Length).mean())/df['atr'])
        
        df['one_day_vol'] = df['volume'].rolling(window=oneday).mean()
        df['five_day_vol'] = df['volume'].rolling(window=fiveday).mean()

        # 计算输出信号
        df['rate'] =np.where((df['one_day_vol'] + df['five_day_vol'])==0,0, df['one_day_vol'] / (df['one_day_vol'] + df['five_day_vol']))
        df['output'] = df['signal'] * df['rate']
        if MIN_MAX[self.factor_name] !=None and (Length in MIN_MAX[self.factor_name]):
            min_max = MIN_MAX[self.factor_name][Length]
            df['output'] = np.where(df['output']>min_max['max'],min_max['max'],
                                    np.where(df['output']<min_max['min'],min_max['min'],df['output']))
        # TODO 下面的保存需要删除
        if param['save'] is not None:
            df.to_csv(param['save'], index=False)
        return df['output']