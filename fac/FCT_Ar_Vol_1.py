
# 人气指标ar 带成交量

'''
Input:Length(20,1,1000,10);
variable:CHANGE_NUM:=0;
variable:DIFF_NUM:=0;

up:= if(HIGH - REF(close,1)>0,HIGH - REF(close,1),0);
down:=if(REF(close,1)-low >0,REF(close,1)-low,0);

br1:= sum(up,Length);
br2:= sum(down,Length);

特征值:=(br1-br2)/(br1+br2);

one_day_vol:= ma(Vol,72);

five_day_vol:= ma(Vol,360);

rate:=(one_day_vol)/(one_day_vol+five_day_vol);


OUT:特征值 * rate;


'''
import numpy as np
import pandas as pd

from .constants import MIN_MAX
from .factor_template import FactorTemplate

class  FCT_Ar_Vol_1(FactorTemplate):
    def __init__(self):
        super().__init__()
        self.factor_name = 'FCT_Ar_Vol_1'
        
    
    def formula(self,**param):
        df = param['df'].copy()
        Length = param['Length']
        oneday = param['one_day']
        fiveday = param['five_day']

        # 计算up和down列
        df['up'] = df['high'].sub(df['close'].shift(1)).clip(lower=0)
        df['down'] = (df['close'].shift(1) - df['low']).clip(lower=0)

        # 计算br1和br2列
        df['br1'] = df['up'].rolling(window=Length).sum()
        df['br2'] = df['down'].rolling(window=Length).sum()

        # 计算特征值
        df['特征值'] = (df['br1'] - df['br2']) / (df['br1'] + df['br2'])

        # 计算one_day_vol和five_day_vol列
        df['one_day_vol'] = df['volume'].rolling(window=oneday).mean()
        df['five_day_vol'] = df['volume'].rolling(window=fiveday).mean()

        # 计算rate列
        df['rate'] =np.where((df['one_day_vol'] + df['five_day_vol'])==0,0,df['one_day_vol'] / (df['one_day_vol'] + df['five_day_vol']))

        # 计算结果OUT列
        df['output'] = df['特征值'] * df['rate']
        if MIN_MAX[self.factor_name] !=None and (Length in MIN_MAX[self.factor_name]):
            min_max = MIN_MAX[self.factor_name][Length]
            df['output'] = np.where(df['output']>min_max['max'],min_max['max'],
                                    np.where(df['output']<min_max['min'],min_max['min'],df['output']))
        
        # TODO 下面的保存需要删除
        if param['save'] is not None:
            df.to_csv(param['save'], index=False)
        return df['output']