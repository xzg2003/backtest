
# CR 减去REF

'''
Input:Length(40,1,1000,10);
中线:=(HIGH+LOW)/2;
正涨幅:=HIGH-REF(中线,1);
上涨:=IF(正涨幅<0,0,正涨幅);
负涨幅:=REF(中线,1)-low;
下跌:=IF(负涨幅<0,0,负涨幅);
上涨累计:=SUM(上涨,Length);
下跌累计:=SUM(下跌,Length);
特征值:(上涨累计-下跌累计)/(上涨累计+下跌累计);
OUT:特征值 - ref(特征值,length)



'''
import numpy as np
import pandas as pd
from .factor_template import FactorTemplate

class  FCT_Cr_Ref_1(FactorTemplate):
    def __init__(self):
        super().__init__()
        self.factor_name = 'FCT_Cr_Ref_1'
        
    
    def formula(self,**param):
        df = param['df'].copy()
        Length = param['Length']

        # 计算中间变量
        df['中线'] = (df['high'] + df['low']) / 2
        df['正涨幅'] = df['high'] - df['中线'].shift(1)
        df['上涨'] = np.where(df['正涨幅'] < 0, 0, df['正涨幅'])
        df['负涨幅'] = df['中线'].shift(1) - df['low']
        df['下跌'] = np.where(df['负涨幅'] < 0, 0, df['负涨幅'])
        df['上涨累计'] = df['上涨'].rolling(window=Length).sum()
        df['下跌累计'] = df['下跌'].rolling(window=Length).sum()

        # 计算特征值和输出
        df['特征值'] =np.where((df['上涨累计'] + df['下跌累计'])==0,0, (df['上涨累计'] - df['下跌累计']) / (df['上涨累计'] + df['下跌累计']))
        df['output'] = df['特征值'] - df['特征值'].shift(Length)

        
        # TODO 下面的保存需要删除
        if param['save'] is not None:
            df.to_csv(param['save'], index=False)
        return df['output']