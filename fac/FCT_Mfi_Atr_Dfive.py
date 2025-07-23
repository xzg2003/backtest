
# 资金流量指标带波动率

'''
INPUT:length(20, 1, 1000, 1);
TYP:=(HIGH+LOW+CLOSE)/3;
V1:=SUM(IF(TYP>REF(TYP,1),TYP*VOL,0),length)/SUM(IF(TYP<REF(TYP,1),TYP*VOL,0),length);
MFI:=100-(100/(1+V1));
one_day_atr:= ma(TR,72);
five_day_atr:= ma(TR,360);
RATE:=(one_day_atr)/(one_day_atr+five_day_atr);
OUT:(MFI-50)/100*RATE;



'''
import numpy as np
import pandas as pd

from .constants import MIN_MAX
from .factor_template import FactorTemplate

class  FCT_Mfi_Atr_Dfive(FactorTemplate):
    def __init__(self):
        super().__init__()
        self.factor_name = 'FCT_Mfi_Atr_Dfive'
        
    
    def formula(self,**param):
        df = param['df'].copy()
        Length = param['Length']
        oneday = param['one_day']
        fiveday = param['five_day']
        # 计算中间变量
        df['typ'] = (df['high'] + df['low'] + df['close']) / 3
        #df['v1'] = df['typ'].rolling(Length).apply(lambda x: sum(x[x > x[0]] * df.loc[x > x[0], 'volume']) / sum(x[x < x[0]] * df.loc[x < x[0], 'volume']), raw=True)
        #V1:=SUM(IF(TYP>REF(TYP,1),TYP*VOL,0),length)/SUM(IF(TYP<REF(TYP,1),TYP*VOL,0),length);
        df['temp1'] = np.where(df['typ']>df['typ'].shift(1),df['typ']*df['volume'],0)
        df['temp2'] = np.where(df['typ']<df['typ'].shift(1),df['typ']*df['volume'],0)
        df['v1'] = df['temp1'].rolling(window=Length).sum()/df['temp2'].rolling(window=Length).sum()
        df['mfi'] = 100 - (100 / (1 + df['v1']))

        df['Close_prev'] = df['close'].shift(1)
        df['tr'] = df[['high', 'low', 'Close_prev']].apply(lambda x: max(x[0] - x[1], abs(x[0] - x[2]), abs(x[1] - x[2])), axis=1)
        
        one_day_atr = df['tr'].rolling(oneday).mean()
        five_day_atr = df['tr'].rolling(fiveday).mean()
        df['rate'] =np.where((one_day_atr + five_day_atr)==0,0, one_day_atr / (one_day_atr + five_day_atr))

        # 计算输出列
        df['output'] = (df['mfi'] - 50) / 100 * df['rate']
        if MIN_MAX[self.factor_name] !=None and (Length in MIN_MAX[self.factor_name]):
            min_max = MIN_MAX[self.factor_name][Length]
            df['output'] = np.where(df['output']>min_max['max'],min_max['max'],
                                    np.where(df['output']<min_max['min'],min_max['min'],df['output']))
        # TODO 下面的保存需要删除
        if param['save'] is not None:
            df.to_csv(param['save'], index=False)
        return df['output']